"""Inference utility functions to invoke LLM's using ChatCompletionsRequest."""
import json
from typing import TYPE_CHECKING, Any, Dict, List, Optional

import requests as request_lib
from pydantic import BaseModel
from tenacity import Retrying, retry_if_exception, stop_after_attempt, wait_exponential

from databricks.model_training.api.utils import get_host_and_token_from_env, normalize_table_name

if TYPE_CHECKING:
    from databricks.model_serving.types.pt_endpoint import BaseEndpoint, TileMTBatchEndpoint

try:
    from openai.lib._parsing._completions import type_to_response_format_param
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# TODO(jun.choi): Make client ID configurable per usecase.
CLIENT_ID = 'finetuning-t2t'

# Constants
MARKDOWN_JSON_PATTERN = r'(?s).*?```(?:json)?\s*(.*?)\s*```\s*.*'
DOCUMENT_TEMPLATE = "\\n\\nDocument:\\n\\n"

RETRY_WAIT_EXPONENTIAL_MULTIPLIER = 1
RETRY_WAIT_EXPONENTIAL_MIN = 1
RETRY_WAIT_EXPONENTIAL_MAX = 10
DEFAULT_NUM_RETRIES = 5


class LLMProxyRateLimitError(Exception):

    def __init__(self, message):
        super().__init__(message)


def clean_request_text(text_col: str) -> str:
    """Create SQL to clean request text.

    Args:
        text_col: Column containing text to clean
    """
    return rf"""REPLACE(REPLACE(REPLACE({text_col}, '"', ''), '“', ''), '”', '')"""


def format_json_for_sql(json_str: str) -> str:
    """
    Escapes a JSON string for safe inclusion in a SQL query string.
    - Replaces single quotes with two single quotes (SQL string escape)
    - Removes any existing backslashes used for escaping single quotes

    Args:
        json_str (str): The JSON string to be escaped.

    Returns:
        str: The escaped string ready for SQL insertion.
    """
    # Remove backslashes before single quotes (e.g., \' -> ')
    cleaned_str = json_str.replace(r"\'", "'")

    # Escape single quotes for SQL by doubling them
    escaped_str = cleaned_str.replace("'", "''")

    return escaped_str


def format_ai_query_tiles(
    source: str,
    endpoint: "TileMTBatchEndpoint",
    input_column: str = 'request',
    output_column: str = 'response',
    max_tokens: int = 1024,
    temperature: float = 0.3,
) -> str:

    # Handle table name quoting
    table_name = normalize_table_name(source)

    # Build query components
    clean_request = clean_request_text(input_column)

    return f"""
    SELECT 
        *,
        ai_query(
            '{endpoint.endpoint_name}',
            {clean_request},
            failOnError => true,
            modelParameters => named_struct('max_tokens', {max_tokens}, 'temperature', {temperature})
        ) AS {output_column}
    FROM {table_name}
    """


def format_ai_query(
    source: str,
    endpoint: "BaseEndpoint",
    system_prompt: str,
    input_column: str = 'request',
    output_column: str = 'response',
    max_tokens: int = 1024,
    temperature: float = 0.3,
    trailing_prompt: Optional[str] = None,
    response_format_str: Optional[str] = None,
) -> str:
    """Format SQL query for AI extraction.

    Args:
        source: Source table name
        endpoint: Endpoint for AI queries
        system_prompt: System prompt for extraction


    Example:
        >>> query = format_ai_query(
        ...     source="my_table",
        ...     endpoint=my_endpoint,
        ...     system_prompt="Extract entities",
        ...     max_tokens=2048,
        ...     temperature=0.5,
        ... )

    Returns:
        Formatted SQL query string
    """

    # Handle table name quoting
    table_name = normalize_table_name(source)

    # Handle trailing prompt
    trailing_prompt = trailing_prompt or system_prompt

    # Build query components
    model_params = f"named_struct('max_tokens', {max_tokens}, 'temperature', {temperature})"
    clean_request = clean_request_text(input_column)
    clean_response_format = format_json_for_sql(response_format_str) if response_format_str else None

    full_prompt = f"""
        system_prompt || 
        '{DOCUMENT_TEMPLATE}' ||
        {clean_request} ||
        '\\n\\n' || 
        trailing_prompt
    """

    # Build AI query string
    if clean_response_format is not None:
        return f"""
        SELECT 
            *,
            ai_query(
                '{endpoint.endpoint.name}',
                {full_prompt},
                failOnError => true,
                modelParameters => {model_params},
                responseFormat => '{clean_response_format}'
            ) AS {output_column}
        FROM {table_name}
        CROSS JOIN (
            SELECT 
                '{system_prompt}' AS system_prompt,
                '{trailing_prompt}' AS trailing_prompt
        )
        """
    return f"""
    SELECT 
        *,
        CASE 
            WHEN extracted_response != '' THEN extracted_response 
            ELSE raw_response 
        END AS {output_column}
    FROM (
        SELECT 
            *,
            ai_query(
                '{endpoint.endpoint.name}',
                {full_prompt},
                failOnError => true,
                modelParameters => {model_params}
            ) AS raw_response,
            regexp_extract(raw_response, r'{MARKDOWN_JSON_PATTERN}', 1) AS extracted_response
        FROM {table_name}
        CROSS JOIN (
            SELECT 
                '{system_prompt}' AS system_prompt,
                '{trailing_prompt}' AS trailing_prompt
        )
    )
    """


def _create_request_db(chat_completions, model_id, timeout=None, temperature=None):
    api_url, api_token = get_host_and_token_from_env()
    headers = {
        'Authorization': f'Bearer {api_token}',
        'Content-Type': 'application/json',
    }
    api_path = f'{api_url}/api/2.0/conversation/proxy/chat/completions'
    payload = {
        '@method': 'databricksChatCompletionRequest',
        'params': {
            **chat_completions
        },
        'model': model_id,
        'metadata': {
            'clientId': CLIENT_ID
        },
    }

    if temperature is not None:
        payload['params']['temperature'] = temperature

    return request_lib.post(api_path, headers=headers, json=payload, timeout=timeout)


def _create_request_ext(chat_completions, model_id, timeout=None, temperature=None):
    api_url, api_token = get_host_and_token_from_env()
    headers = {
        'Authorization': f'Bearer {api_token}',
        'Content-Type': 'application/json',
    }
    api_path = f'{api_url}/api/2.0/conversation/proxy/chat/completions'

    payload = {
        '@method': 'openAiServiceChatCompletionRequest',
        'params': {
            **chat_completions
        },
        'model': model_id,
        'apiVersion': '2024-09-01-preview',
        'metadata': {
            'clientId': CLIENT_ID
        },
    }

    if temperature is not None:
        payload['params']['temperature'] = temperature

    return request_lib.post(api_path, headers=headers, json=payload, timeout=timeout)


_MODEL_FN_DICT = {
    # Common / shared models
    'databricks-meta-llama-3-70b-instruct': _create_request_db,
    'llama-3-1-405b': _create_request_db,
    'gpt-4o-2024-08-06': _create_request_ext,
    'gpt-4o-mini-2024-07-18': _create_request_ext,
    'gpt-4-0613': _create_request_ext,
    'gpt-4-turbo-2024-04-09': _create_request_ext,
    'gpt-35-turbo-1106': _create_request_ext,

    # Client specific models
    'gpt-4o-2024-08-06-text2text': _create_request_ext,
    'gpt-4o-mini-2024-07-18-text2text': _create_request_ext,
}


def get_llm_proxy_chat_completion_response(model_id: str,
                                           req: Dict,
                                           timeout: Optional[float] = None,
                                           temperature: Optional[float] = None,
                                           num_retries: int = 0) -> str:
    """Retrieves the chat completion response from a specified language model.

        Args:
            model_id (str): The identifier of the language model to use.
            req (dict): The request payload to be sent to the language model.
            timeout (float, optional): The timeout for the request. Defaults to None.
            temperature (float, optional): The temperature for the request. Defaults to None.
            num_retries (int, optional): The number of retries for the request. Defaults to 0.

        Returns:
            str: The content of the chat completion response.
    """

    def _fn():
        if model_id not in _MODEL_FN_DICT:
            raise ValueError(f'Model id {model_id} is not supported. Please use one of {_MODEL_FN_DICT.keys()}')

        llm_proxy_model_id = model_id
        response = _MODEL_FN_DICT[model_id](req, llm_proxy_model_id, timeout=timeout, temperature=temperature)

        if response.status_code != 200:
            if response.status_code == 429:
                raise LLMProxyRateLimitError(f'Request failed with status code {response.status_code}: {response.text}')
            raise RuntimeError(f'Request failed with status code {response.status_code}: {response.text}')

        out = json.loads(response.json()['completion'])['choices'][0]['message']['content']
        return out

    if not num_retries:
        return _fn()

    retry_policy = Retrying(stop=stop_after_attempt(num_retries + 1),
                            wait=wait_exponential(multiplier=RETRY_WAIT_EXPONENTIAL_MULTIPLIER,
                                                  min=RETRY_WAIT_EXPONENTIAL_MIN,
                                                  max=RETRY_WAIT_EXPONENTIAL_MAX),
                            retry=retry_if_exception(lambda e: isinstance(e, LLMProxyRateLimitError)))
    return retry_policy(_fn)


def generate_base_model_using_chat_completion_messages(messages: List[Dict[str, str]],
                                                       model_clz: Any,
                                                       model_id: Optional[str] = None,
                                                       num_retries: int = 0) -> BaseModel:
    """Generates a base model using chat completion messages using structured output.

    Args:
        messages (list): A list of dictionaries representing the chat messages.
        model_clz (Any): The Pydantic model class to use for the response.
        model_id_suffix (str, optional): The suffix to append to the model id. Defaults to None.
        num_retries (int, optional): The number of retries for the request. Defaults to 0.

    Returns:
        BaseModel: The generated Pydantic model.
    """
    if not OPENAI_AVAILABLE:
        raise ImportError("openai library is not available. Please install it to use this")

    req: Dict = {
        'messages': messages,
        'response_format': type_to_response_format_param(model_clz),
    }
    llm_proxy_model_id = model_id or 'gpt-4o-2024-08-06'
    res = get_llm_proxy_chat_completion_response(llm_proxy_model_id, req, num_retries=num_retries)
    return model_clz(**json.loads(res))
