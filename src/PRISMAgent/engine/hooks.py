"""
PRISMAgent.engine.hooks
-----------------------

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

# -------------------------------------------------------------------- #
# 0 · Registry singleton (unchanged)                                   #
# -------------------------------------------------------------------- #
_REGISTRY = registry_factory()  # falls back to InMemory if env missing


# -------------------------------------------------------------------- #
# 1 · Existing hook: dynamic hand-off when an already-registered agent  #
#    spawned.                                                          #
# -------------------------------------------------------------------- #
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
            logger.debug(f"Dynamic handoff: found agent {result} in registry", agent_name=result)
            agent.handoffs.append(_REGISTRY.get(result))


# -------------------------------------------------------------------- #
# 2 · NEW: long-term memory hooks                                      #
# -------------------------------------------------------------------- #
# pick vector backend via env:  STORAGE_BACKEND=vector  VECTOR_PROVIDER=pinecone|redis
if os.getenv("STORAGE_BACKEND", "memory") == "vector":
    logger.debug("Initializing vector storage for long-term memory")
    _MEM = registry_factory("vector")  # Pinecone or RedisVector behind one API
else:
    logger.debug("Vector storage not configured, memory features will be limited")
    _MEM = None  # keep working even if vector store not configured

_OPENAI = OpenAI()
_EMBED_MODEL = os.getenv("EMBED_MODEL", "text-embedding-3-small")


def _embed(text: str) -> List[float]:
    """Embed text with OpenAI; returns 512-d float list."""
    logger.debug(f"Embedding text ({len(text)} chars) with model {_EMBED_MODEL}")
    resp = _OPENAI.embeddings.create(model=_EMBED_MODEL, input=text)
    return resp.data[0].embedding


@with_log_context(component="memory_hook")
def after_step(step_summary: str, meta: Dict[str, Any]) -> None:
    """
    Persist a short summary + metadata after every completed agent step.
    Called automatically by the runner's `after_step` hook.
    """
    if _MEM is None:
        logger.debug("Vector memory not configured, skipping after_step hook")
        return
    
    logger.info(f"Storing memory: {meta.get('id', 'unknown')}", 
                step_id=meta.get('id'),
                step_type=meta.get('type'),
                agent_name=meta.get('agent_name'))
    _MEM.upsert(meta["id"], _embed(step_summary), meta)


@with_log_context(component="memory_hook")
def before_plan(user_query: str, k: int = 3):
    """
    Retrieve the top-k memories most relevant to the upcoming planning
    query.  The runner injects these summaries into the system prompt.
    """
    if _MEM is None:
        logger.debug("Vector memory not configured, skipping before_plan hook")
        return []
    
    logger.info(f"Retrieving top {k} relevant memories for query", query_length=len(user_query), top_k=k)
    return _MEM.query(_embed(user_query), k=k)


# -------------------------------------------------------------------- #
# 3 · Auto-register the new hooks with the runner (if it exists).      #
# -------------------------------------------------------------------- #
try:
    from PRISMAgent.engine.runner import runner_factory

    _RUNNER = runner_factory()
    logger.debug("Registering memory hooks with runner")
    _RUNNER.add_after_step(after_step)
    _RUNNER.add_before_plan(before_plan)
except ImportError:
    # Runner not yet initialised (unit tests / static analysis)
    logger.debug("Runner not initialized, skipping hook registration")
    pass


# -------------------------------------------------------------------- #
# 4 · Factory helper (kept for backward compatibility)                 #
# -------------------------------------------------------------------- #
def hook_factory(hook_cls: type[AgentHooks], **kwargs) -> AgentHooks:
    """Return a new hook instance—deprecated but still exported."""
    logger.debug(f"Creating hook instance: {hook_cls.__name__}")
    return hook_cls(**kwargs)


__all__: List[str] = [
    "DynamicHandoffHook",
    "after_step",
    "before_plan",
    "hook_factory",
]
