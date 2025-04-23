"""Model configuration for PRISMAgent."""

from typing import Dict, Optional, List
from pydantic import BaseModel, Field


class ModelCostConfig(BaseModel):
    """Configuration for model cost tracking."""
    
    cost_per_1k_tokens_input: float = Field(
        ..., 
        description="Cost per 1000 input tokens"
    )
    cost_per_1k_tokens_output: float = Field(
        ..., 
        description="Cost per 1000 output tokens"
    )
    max_daily_cost: Optional[float] = Field(
        None, 
        description="Maximum daily cost allowed, None for unlimited"
    )


class ModelConfig(BaseModel):
    """Configuration for OpenAI model settings."""
    
    model_name: str = Field(
        ..., 
        description="OpenAI model name"
    )
    max_tokens: int = Field(
        1000, 
        description="Maximum tokens for model response"
    )
    temperature: float = Field(
        0.7, 
        description="Temperature for model responses"
    )
    top_p: float = Field(
        1.0, 
        description="Top-p for nucleus sampling"
    )
    frequency_penalty: float = Field(
        0.0, 
        description="Frequency penalty for responses"
    )
    presence_penalty: float = Field(
        0.0, 
        description="Presence penalty for responses"
    )
    stop_sequences: Optional[List[str]] = Field(
        None, 
        description="Optional sequences to stop generation"
    )
    costs: Optional[ModelCostConfig] = Field(
        None, 
        description="Cost configuration for this model"
    )
    
    @classmethod
    def presets(cls) -> Dict[str, "ModelConfig"]:
        """Return preset configurations for common models."""
        gpt4_costs = ModelCostConfig(
            cost_per_1k_tokens_input=0.03, 
            cost_per_1k_tokens_output=0.06,
            max_daily_cost=5.0
        )
        
        gpt35_costs = ModelCostConfig(
            cost_per_1k_tokens_input=0.0015, 
            cost_per_1k_tokens_output=0.002,
            max_daily_cost=1.0
        )
        
        return {
            "gpt-4": cls(
                model_name="gpt-4",
                max_tokens=8192,
                costs=gpt4_costs
            ),
            "gpt-4-turbo": cls(
                model_name="gpt-4-1106-preview",
                max_tokens=4096,
                costs=ModelCostConfig(
                    cost_per_1k_tokens_input=0.01, 
                    cost_per_1k_tokens_output=0.03,
                    max_daily_cost=5.0
                )
            ),
            "gpt-3.5-turbo": cls(
                model_name="gpt-3.5-turbo",
                max_tokens=4096,
                costs=gpt35_costs
            )
        } 