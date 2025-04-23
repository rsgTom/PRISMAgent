"""
PRISMAgent.config.model
-----------------------

Dynamic model–selection logic.

Sources
-------
o-series capabilities/pricing:
* OpenAI changelog (Apr 16 2025) :contentReference[oaicite:0]{index=0}
* Reuters GPT-4o-mini launch article :contentReference[oaicite:1]{index=1}
* Internal third-party table supplied by user.
"""

from __future__ import annotations

from typing import Dict, Literal, Optional
from pydantic import BaseModel, Field, PositiveInt

# ──────────────────────────────────────────────────────────────────────────────
# 1.  Model registry
# ──────────────────────────────────────────────────────────────────────────────

class ModelProfile(BaseModel, frozen=True):
    name: str
    max_tokens: PositiveInt
    input_cost: float            # $ per 1 M input tokens
    output_cost: float           # $ per 1 M output tokens
    reasoning_score: float       # AIME baseline %
    coding_score: float          # SWE-bench %
    tier: Literal["basic", "advanced"]

# Hand-rolled values from table + public docs
_MODEL_REGISTRY: Dict[str, ModelProfile] = {
    "o1": ModelProfile(
        name="o1",
        max_tokens=8192,
        input_cost=0.40,
        output_cost=1.20,
        reasoning_score=74.3,
        coding_score=48.9,
        tier="basic",
    ),
    "o1-mini": ModelProfile(
        name="o1-mini",
        max_tokens=4096,
        input_cost=0.10,
        output_cost=0.30,
        reasoning_score=70.0,
        coding_score=45.0,
        tier="basic",
    ),
    "o3": ModelProfile(
        name="o3",
        max_tokens=16384,
        input_cost=0.90,      # placeholder until OpenAI publishes
        output_cost=2.70,
        reasoning_score=91.6,
        coding_score=69.1,
        tier="advanced",
    ),
    "o3-mini": ModelProfile(
        name="o3-mini",
        max_tokens=8192,
        input_cost=0.45,
        output_cost=1.35,
        reasoning_score=90.0,
        coding_score=67.0,
        tier="advanced",
    ),
    "o4-mini": ModelProfile(
        name="o4-mini",
        max_tokens=8192,
        input_cost=0.15,      # Reuters :contentReference[oaicite:2]{index=2}
        output_cost=0.60,
        reasoning_score=93.4,
        coding_score=68.1,
        tier="advanced",
    ),
    "o4-mini-high": ModelProfile(
        name="o4-mini-high",
        max_tokens=16384,
        input_cost=0.30,
        output_cost=1.20,
        reasoning_score=93.4,
        coding_score=68.1,
        tier="advanced",
    ),
}

DEFAULT_MODEL = "o3-mini"   # sensible middle-ground

# ──────────────────────────────────────────────────────────────────────────────
# 2.  Task → model heuristics
# ──────────────────────────────────────────────────────────────────────────────
# You can freely extend this mapping.
_TASK_MATRIX: Dict[str, str] = {
    "chat": DEFAULT_MODEL,
    "cheap": "o1-mini",
    "code": "o3",
    "math": "o4-mini",
    "analysis": "o3",
    "vision": "o4-mini-high",
}

# ──────────────────────────────────────────────────────────────────────────────
# 3.  Public helper
# ──────────────────────────────────────────────────────────────────────────────

class _ModelSettings(BaseModel, frozen=True):
    default_model: str = DEFAULT_MODEL

    def get_model_for_task(
        self,
        task: str,
        *,
        complexity: Literal["auto", "basic", "advanced"] = "auto",
    ) -> str:
        """
        Pick an OpenAI model for a given logical task.

        Parameters
        ----------
        task : str
            e.g. "chat", "code", "vision", "cheap".
        complexity : "auto" | "basic" | "advanced"
            Force a tier, or let the matrix decide.

        Returns
        -------
        str
            Model name (e.g. "o3-mini").
        """
        if complexity != "auto":
            candidates = [
                m.name for m in _MODEL_REGISTRY.values() if m.tier == complexity
            ]
            # fall back to default if task’s preferred model not in desired tier
            return _TASK_MATRIX.get(task, DEFAULT_MODEL) if _TASK_MATRIX.get(task) in candidates else candidates[0]

        return _TASK_MATRIX.get(task, DEFAULT_MODEL)


MODEL_SETTINGS = _ModelSettings()

__all__ = ["ModelProfile", "MODEL_SETTINGS"]
