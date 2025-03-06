"""Utils for working with model serving"""

from enum import Enum
from typing import Dict, NamedTuple, Optional

from mlflow import MlflowClient

MODEL_CONTEXT_LENGTH = 131072


class ModelSpecs(NamedTuple):
    name: str
    endpoint: Optional[str]
    cost_per_hour: float  # This is measured in DBUs instead of dollars, since customers may have different DBU rates
    ft_model_name: str
    is_hosted: bool = True
    uc_schema: Optional[str] = None
    version: Optional[str] = None
    cost_per_m_ft_tokens: Optional[float] = None
    alias: Optional[str] = None
    throughput_tok_per_sec: Optional[int] = None


class ModelSpecKey(Enum):
    """Enumeration of model specification keys for model serving."""
    # 70B variants
    BALANCED = 'balanced'
    LLAMA_3_3_70B_INSTRUCT = 'llama-3-3-70b-instruct'

    # 8B variants
    COST_OPTIMIZED_MEDIUM = 'cost-optimized-medium'
    LLAMA_3_1_8B_INSTRUCT = 'llama-3-1-8b-instruct'

    # 3B variants
    COST_OPTIMIZED_SMALL = 'cost-optimized-small'
    LLAMA_3_2_3B_INSTRUCT = 'llama-3-2-3b-instruct'


def get_latest_model_version(model_name: str) -> str:
    """Get the latest version of a model using Mlflow

    Args:
        model_name (str): The name of the model

    Returns:
        str: The latest version of the model
    """
    client = MlflowClient()
    model_versions = client.search_model_versions(f"name='{model_name}'")

    if not model_versions:
        raise ValueError(f"No model versions found for model '{model_name}'")

    version_numbers = [int(model.version) for model in model_versions]
    most_recent_version = max(version_numbers)
    return str(most_recent_version)


def create_model_specs(name: str,
                       endpoint: Optional[str],
                       cost_per_hour: float,
                       ft_model_name: str,
                       uc_schema: Optional[str] = None,
                       is_hosted: bool = True,
                       cost_per_m_ft_tokens: Optional[float] = None,
                       throughput_tok_per_sec: Optional[int] = None,
                       alias: Optional[str] = None) -> ModelSpecs:
    """Creates a model specification with optional automatic version lookup.

    Args:
        name (str): Model spec name.
        endpoint (Optional[str]): PayGo serving endpoint.
        cost_per_hour (float): Cost per hour in DBUs.
        ft_model_name (str): Finetuning API model name.
        uc_schema (Optional[str]): Unity Catalog schema name.
        is_hosted (bool, optional): Whether the model is hosted. Defaults to True.
        cost_per_m_ft_tokens (Optional[float], optional): Cost per million fine-tuned tokens.
        throughput_tok_per_sec (Optional[int], optional): Model throughput in tokens per second.
        alias (Optional[str], optional): Friendly alias for the model.

    Returns:
        ModelSpecs: A structured model specification.
    """
    version = None
    if uc_schema:
        try:
            version = get_latest_model_version(uc_schema)
        except ValueError as e:
            print(f"Failed to get latest model version for {uc_schema}: {e}")
    return ModelSpecs(name=name,
                      endpoint=endpoint,
                      cost_per_hour=cost_per_hour,
                      ft_model_name=ft_model_name,
                      is_hosted=is_hosted,
                      uc_schema=uc_schema,
                      version=version,
                      cost_per_m_ft_tokens=cost_per_m_ft_tokens,
                      throughput_tok_per_sec=throughput_tok_per_sec,
                      alias=alias)


BASE_MODELS: Dict[str, ModelSpecs] = {
    # 70B variants
    ModelSpecKey.LLAMA_3_3_70B_INSTRUCT.value:
        create_model_specs(name="llama-3-3-70b-instruct",
                           endpoint="databricks-meta-llama-3-3-70b-instruct",
                           cost_per_hour=342.857,
                           ft_model_name="meta-llama/Llama-3.3-70B-Instruct",
                           uc_schema="system.ai.llama_v3_3_70b_instruct",
                           throughput_tok_per_sec=670,
                           alias="elephant"),

    # 8B variants
    ModelSpecKey.LLAMA_3_1_8B_INSTRUCT.value:
        create_model_specs(name="llama-3-1-8b-instruct",
                           endpoint="databricks-meta-llama-3-1-8b-instruct",
                           cost_per_hour=106.0,
                           ft_model_name="meta-llama/Meta-Llama-3.1-8B-Instruct",
                           uc_schema="system.ai.meta_llama_v3_1_8b_instruct",
                           cost_per_m_ft_tokens=4.0,
                           throughput_tok_per_sec=19000,
                           alias="zebra"),

    # 3B variants
    ModelSpecKey.LLAMA_3_2_3B_INSTRUCT.value:
        create_model_specs(name="llama-3-2-3b-instruct",
                           endpoint=None,
                           cost_per_hour=92.857,
                           ft_model_name="meta-llama/Llama-3.2-3B-Instruct",
                           uc_schema="system.ai.llama_v3_2_3b_instruct",
                           is_hosted=False,
                           cost_per_m_ft_tokens=2.50,
                           throughput_tok_per_sec=22000,
                           alias="squirrel"),
}


def get_model_specs():
    """Retrieves all available model specifications.

    Returns:
        Dict[ModelSpecKey, ModelSpecs]: A dictionary mapping model keys to their corresponding model specifications.
    """
    return {
        **BASE_MODELS,
        ModelSpecKey.BALANCED.value: BASE_MODELS[ModelSpecKey.LLAMA_3_3_70B_INSTRUCT.value],
        ModelSpecKey.COST_OPTIMIZED_MEDIUM.value: BASE_MODELS[ModelSpecKey.LLAMA_3_1_8B_INSTRUCT.value],
        ModelSpecKey.COST_OPTIMIZED_SMALL.value: BASE_MODELS[ModelSpecKey.LLAMA_3_2_3B_INSTRUCT.value],
    }
