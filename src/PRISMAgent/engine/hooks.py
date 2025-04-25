"""
PRISMAgent.engine.hooks
----------------------

Reusable AgentHooks implementations **plus** two runtime-registered
memory hooks that persist step summaries to a vector store (Pinecone
or RedisVector) and retrieve the top-k related memories before each
planning cycle.

• <200 LOC  • no synchronous network calls in engine layer
"""

from __future__ import annotations

import os
from typing import Any, Dict, List

from agents import Agent, AgentHooks, RunContextWrapper, Tool
from openai import OpenAI

from PRISMAgent.storage import registry_factory
from PRISMAgent.util import get_logger, with_log_context

# Get a logger for this module
logger = get_logger(__name__)

# ---------------------------------------------------------------------- #
# 0 · Registry singleton (unchanged)                                     #
# ---------------------------------------------------------------------- #
_REGISTRY = registry_factory()  # falls back to InMemory if env missing


# ---------------------------------------------------------------------- #
# 1 · Existing hook: dynamic hand-off when an already-registered agent   #
#     spawned.                                                           #
# ---------------------------------------------------------------------- #
class DynamicHandoffHook(AgentHooks):
    """Attach an existing agent instance instead of spawning duplicates."""

    def after_tool_call(
        self,
        agent: Agent,
        context: RunContextWrapper,
        tool: Tool,
        result: str,
    ) -> None:
        if tool.name == "spawn_agent" and _REGISTRY.exists(result):
            logger.debug(f"Dynamically attaching existing agent: {result}", 
                         agent_name=result, 
                         tool_name=tool.name)
            agent.handoffs.append(_REGISTRY.get(result))
            logger.info(f"Agent {result} attached as handoff", 
                        agent_name=result, 
                        parent_agent=agent.name)


# ---------------------------------------------------------------------- #
# 2 · NEW: long-term memory hooks                                        #
# ---------------------------------------------------------------------- #
# pick vector backend via env:  STORAGE_BACKEND=vector  VECTOR_PROVIDER=pinecone|redis
if os.getenv("STORAGE_BACKEND", "memory") == "vector":
    logger.info("Initializing vector storage for long-term memory")
    _MEM = registry_factory("vector")  # Pinecone or RedisVector behind one API
else:
    logger.debug("Vector storage not configured, memory features disabled")
    _MEM = None  # keep working even if vector store not configured

_OPENAI = OpenAI()
_EMBED_MODEL = os.getenv("EMBED_MODEL", "text-embedding-3-small")


@with_log_context(component="memory_hooks")
def _embed(text: str) -> List[float]:
    """Embed text with OpenAI; returns 512-d float list."""
    logger.debug("Embedding text", text_length=len(text))
    resp = _OPENAI.embeddings.create(model=_EMBED_MODEL, input=text)
    logger.debug("Text embedded successfully")
    return resp.data[0].embedding


@with_log_context(component="memory_hooks")
def after_step(step_summary: str, meta: Dict[str, Any]) -> None:
    """
    Persist a short summary + metadata after every completed agent step.
    Called automatically by the runner's `after_step` hook.
    """
    if _MEM is None:
        logger.debug("Memory storage disabled, skipping after_step hook")
        return
    
    logger.info(f"Persisting step summary for {meta.get('id', 'unknown')}", 
                step_id=meta.get('id'),
                summary_length=len(step_summary))
    _MEM.upsert(meta["id"], _embed(step_summary), meta)
    logger.debug("Step summary persisted successfully")


@with_log_context(component="memory_hooks")
def before_plan(user_query: str, k: int = 3):
    """
    Retrieve the top-k memories most relevant to the upcoming planning
    query.  The runner injects these summaries into the system prompt.
    """
    if _MEM is None:
        logger.debug("Memory storage disabled, skipping before_plan hook")
        return []
    
    logger.info(f"Retrieving {k} relevant memories for planning", 
                query_length=len(user_query), 
                k=k)
    memories = _MEM.query(_embed(user_query), k=k)
    logger.debug(f"Retrieved {len(memories)} memories")
    return memories


# ---------------------------------------------------------------------- #
# 3 · Auto-register the new hooks with the runner (if it exists).        #
# ---------------------------------------------------------------------- #
try:
    from PRISMAgent.engine.runner import runner_factory

    logger.debug("Registering memory hooks with runner")
    _RUNNER = runner_factory()
    _RUNNER.add_after_step(after_step)
    _RUNNER.add_before_plan(before_plan)
    logger.info("Memory hooks registered successfully")
except ImportError:
    # Runner not yet initialised (unit tests / static analysis)
    logger.warning("Failed to register memory hooks: runner not initialized")
    pass


# ---------------------------------------------------------------------- #
# 4 · Factory helper (kept for backward compatibility)                   #
# ---------------------------------------------------------------------- #
@with_log_context(component="hook_factory")
def hook_factory(hook_cls: type[AgentHooks], **kwargs) -> AgentHooks:
    """Return a new hook instance—deprecated but still exported."""
    logger.debug(f"Creating hook instance: {hook_cls.__name__}", 
                 hook_class=hook_cls.__name__)
    return hook_cls(**kwargs)


__all__: List[str] = [
    "DynamicHandoffHook",
    "after_step",
    "before_plan",
    "hook_factory",
]
