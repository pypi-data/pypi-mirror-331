"""Provisioned throughput endpoint for model serving"""

import json
import logging
import re
import threading
import time
from abc import abstractmethod
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import contextmanager
from enum import Enum
from functools import partial
from typing import Any, Dict, Generator, List, NamedTuple, Optional, Tuple, Type, TypeVar, cast

import requests
from mlflow.deployments import DatabricksDeploymentClient, DatabricksEndpoint, get_deploy_client
from pydantic import BaseModel
from pyspark.sql import functions as F
from requests import RequestException
from requests.exceptions import HTTPError
from rich.progress import BarColumn, Progress, TaskProgressColumn, TextColumn, TimeElapsedColumn, TimeRemainingColumn
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

from databricks.kie.inference_utils import format_ai_query, format_ai_query_tiles
from databricks.kie.kie_state import DataFrame
from databricks.model_serving.utils import BASE_MODELS, get_latest_model_version
from databricks.model_training.api.utils import get_host_and_token_from_env, get_me, get_spark, md5_hash
from databricks.model_training.logging import console

logger = logging.getLogger(__name__)

DEFAULT_MAX_RETRIES = 5
DEFAULT_BACKOFF_EXPONENTIAL = 1

DEFAULT_MAX_TOKENS = 8192
DEFAULT_TEMPERATURE = 0.3


class EndpointTask(str, Enum):
    COMPLETIONS = 'llm/v1/completions'
    CHAT = 'llm/v1/chat'


class EndpointClass(str, Enum):
    QUERY = '/serving-endpoints'
    BATCH = '/batch-inference'


class GenerationOutput(NamedTuple):
    response: str
    total_tokens: int


def should_retry_http(exception: BaseException) -> bool:
    """Only retry on specific HTTP status codes."""
    if isinstance(exception, HTTPError):
        # Don't retry on client errors except 429 (rate limit)
        if 400 <= exception.response.status_code < 500:
            return exception.response.status_code == 429
        # Retry on server errors
        return 500 <= exception.response.status_code < 600
    # Retry on connection errors, timeouts etc
    return isinstance(exception, RequestException)


T = TypeVar('T', bound='BaseEndpoint')


class BaseEndpoint:
    """Base endpoint class to query PayGo and PT endpoints
    """
    endpoint: DatabricksEndpoint
    endpoint_name: str
    client: DatabricksDeploymentClient
    tokens_processed: int = 0
    __endpoint_class: EndpointClass = EndpointClass.QUERY

    def __init__(self):
        dbx_client = get_deploy_client('databricks')
        if dbx_client is None:
            raise RuntimeError('Failed to get Databricks deploy client.')
        self.client = cast(DatabricksDeploymentClient, dbx_client)

        self._token_lock = threading.Lock()

        self.endpoint = self.setup_endpoint()

        if not hasattr(self, 'endpoint_name'):
            raise ValueError("Subclasses of BaseEndpoint must set self.endpoint_name in __init__")

        if self.endpoint.get("task") and self.endpoint.get("task") not in set(EndpointTask):
            # This really shouldn't happen but just in case.
            raise ValueError(
                f'Unsupported task type configured for endpoint {self.endpoint.name}: {self.endpoint.task}')

    @abstractmethod
    def setup_endpoint(self) -> DatabricksEndpoint:
        """Perform any required setup and return an endpoint object from a call to client.get_endpoint()
        """

    def __str__(self):
        return f'endpoints:/{self.endpoint.name} ({self.endpoint.ready})'

    def __enter__(self: T) -> T:
        return self

    def __exit__(self, _exc_type, _exc_value, _traceback) -> None:
        del _exc_type, _exc_value, _traceback

    def _get_deployment_endpoint(self) -> str:
        assert self.endpoint.name is not None and isinstance(self.endpoint.name,
                                                             str)  # If self.endpoint is set, it'll have a str name
        return '/'.join([self.__endpoint_class.value, self.endpoint.name])

    def is_endpoint_ready(self) -> bool:
        """
        Returns True if the endpoint is scaled from zero and ready to serve
        requests. Returns False otherwise.
        """
        return self.endpoint.state.ready == 'READY' and self.endpoint.state.config_update == 'NOT_UPDATING'

    def _set_endpoint_class(self, endpoint_class: EndpointClass) -> None:
        self.__endpoint_class = endpoint_class

    @abstractmethod
    def get_dbu_cost_per_hour(self) -> float:
        """Get the cost per hour for the endpoint"""

    def query(
        self,
        input_data: dict,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_exponential: float = DEFAULT_BACKOFF_EXPONENTIAL,
    ) -> GenerationOutput:
        """
        Queries the PT endpoint with the given input.

        Args:
            input_data (dict): Input data (or arguments) to pass to the deployment or model endpoint for inference.
        """

        @retry(retry=retry_if_exception(should_retry_http),
               stop=stop_after_attempt(max_retries),
               wait=wait_exponential(multiplier=backoff_exponential),
               reraise=True)
        def retry_query(input_data: dict) -> GenerationOutput:
            result = self.client.predict(
                endpoint=self._get_deployment_endpoint(),
                inputs=input_data,
            )
            if not result:
                raise RuntimeError(f'Failed to generate completion for input: {input_data}')

            if self.endpoint.get("task") == EndpointTask.COMPLETIONS:
                response = result['choices'][0]['text']
            else:
                response = result['choices'][0]['message']['content']

            total_tokens = result['usage']['total_tokens']
            return GenerationOutput(response=response, total_tokens=total_tokens)

        return retry_query(input_data)

    def generate_completion(self,
                            prompt: str,
                            system_prompt: Optional[str] = None,
                            response_format: Optional[Type[BaseModel]] = None,
                            temperature: float = DEFAULT_TEMPERATURE,
                            max_tokens: int = DEFAULT_MAX_TOKENS) -> GenerationOutput:
        """
        Uses PT endpoint to generate completion for a given prompt string.

        Args:
            prompt (str): The prompt to generate completion for.
            temperature (float): The temperature to use for sampling. Default is 1.0.
            max_tokens (int): The maximum number of tokens to generate. Default is 128.
        """
        if self.endpoint.get("task") == EndpointTask.COMPLETIONS:  # completions endpoint
            if response_format:
                raise ValueError('response_format is not supported for completions endpoint')
            if system_prompt:
                prompt = f'{system_prompt} {prompt}'
            inputs = {
                'prompt': prompt,
                'temperature': temperature,
                'max_tokens': max_tokens,
            }
        else:  # chat endpoint
            sys_prompt_addition = f'\n\n{system_prompt}' if system_prompt else ''
            messages = [{
                'role': 'user',
                'content': prompt.replace('"', '').replace('“', '').replace('”', '') + sys_prompt_addition,
            }]
            if system_prompt:
                messages.insert(0, {
                    'role': 'system',
                    'content': system_prompt,
                })

            inputs = {
                'messages': messages,
                'temperature': temperature,
                'max_tokens': max_tokens,
            }

            if response_format:
                inputs['response_format'] = self._build_response_format(response_format)

        output = self.query(inputs)
        with self._token_lock:
            self.tokens_processed += output.total_tokens
        return output

    def _build_response_format(self,
                               response_format: Type[BaseModel],
                               disable_prompt_injection: Optional[bool] = True) -> Dict[str, Any]:
        schema = response_format.model_json_schema()
        schema['additionalProperties'] = False
        response_format_dict = {
            'type': 'json_schema',
            'json_schema': {
                'name': 'structured_output',
                'strict': True,
                'schema': schema,
            },
        }
        if disable_prompt_injection:
            response_format_dict['json_schema']['disable_prompt_injection'] = disable_prompt_injection

        return response_format_dict

    def generate_batch(
        self,
        prompts: List[str],
        system_prompt: Optional[str] = None,
        response_format: Optional[Type[BaseModel]] = None,
        temperature: float = 0.3,
        max_tokens: int = 1024,
        batch_size: int = 32,
        show_progress: bool = True,
        total_max_tokens: Optional[int] = None,
    ) -> List[GenerationOutput]:
        """
        Generate completions for a batch of prompts with optional token limit.
        Returns partial results if token limit is reached.
        """
        results: List[Tuple[int, GenerationOutput]] = []
        message_dict = dict(enumerate(prompts))
        pending_futures = set()

        @contextmanager
        def optional_progress(enabled: bool = True) -> Generator[Progress, Any, Any]:
            if enabled:
                with Progress(
                        TextColumn('[bold blue]{task.description}'),
                        BarColumn(bar_width=50),
                        TaskProgressColumn(),
                        TextColumn(
                            '•'),  # TODO: Likely want to remove the following because auto-refresh is off. We'll see
                        TimeElapsedColumn(),
                        TextColumn('•'),
                        TimeRemainingColumn(),
                        expand=False,
                        auto_refresh=False,
                        console=console) as progress:
                    yield progress
            else:

                class DummyConsole:
                    """Dummy console doesn't do anything"""

                    def print(self, *args, **kwargs):
                        print(*args, **kwargs)

                class DummyProgress:
                    """Dummy progress doesn't do anything"""
                    console = DummyConsole()

                    def add_task(self, *args, **kwargs):
                        del args, kwargs
                        return 0

                    def advance(self, *args, **kwargs):
                        del args, kwargs
                        pass

                    def update(self, *args, **kwargs):
                        del args, kwargs
                        pass

                    def stop(self):
                        pass

                yield cast(Progress, DummyProgress())

        single_query = partial(
            self.generate_completion,
            system_prompt=system_prompt,
            response_format=response_format,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        total_tokens_processed = 0
        with optional_progress(show_progress) as progress:  # pylint: disable=contextmanager-generator-missing-cleanup
            task = progress.add_task('Generating outputs...', total=len(prompts))

            with ThreadPoolExecutor(max_workers=batch_size) as executor:
                future_to_index = {}
                for idx, message in message_dict.items():
                    future = executor.submit(single_query, message)
                    future_to_index[future] = idx
                    pending_futures.add(future)

                try:
                    for future in as_completed(pending_futures):
                        idx = future_to_index[future]
                        try:
                            response = future.result()
                            results.append((idx, response))
                            pending_futures.remove(future)
                            total_tokens_processed += response[1]

                            if total_max_tokens and total_tokens_processed > total_max_tokens:
                                progress.console.print('Token limit reached. Stopping further completions.')
                                break
                        except Exception as e:  # pylint: disable=broad-exception-caught
                            progress.console.print(f'Error processing message {idx}: {e}')
                            pending_futures.remove(future)
                            raise e
                        progress.advance(task)
                        progress.update(task, refresh=True)
                finally:
                    # Make sure we clean up any remaining futures
                    for future in pending_futures:
                        future.cancel()

                # Update progress to show actual completion
                progress.update(task, completed=len(results), refresh=True)

        return [r[1] for r in sorted(results, key=lambda x: x[0])]

    def format_ai_query(
        self,
        data_path: str,
        system_prompt: str,
        output_column: str = 'response',
        trailing_prompt: Optional[str] = None,
        response_format: Optional[type[BaseModel]] = None,
        max_tokens: int = 1024,
        temperature: float = 0.3,
        disable_prompt_injection: bool = True,
    ):
        json_schema_arg = json.dumps(self._build_response_format(response_format,
                                                                 disable_prompt_injection)) if response_format else None
        return format_ai_query(source=data_path,
                               endpoint=self,
                               system_prompt=system_prompt,
                               output_column=output_column,
                               trailing_prompt=trailing_prompt,
                               response_format_str=json_schema_arg,
                               max_tokens=max_tokens,
                               temperature=temperature)

    def generate_ai_query(
        self,
        data_path: str,
        system_prompt: str,
        output_column: str = 'response',
        trailing_prompt: Optional[str] = None,
        response_format: Optional[type[BaseModel]] = None,
        max_tokens: int = 1024,
        temperature: float = 0.3,
        disable_prompt_injection: bool = True,
    ) -> DataFrame:
        """
        Calls the endpoint with ai_query command and returns the results in a dataframe.
        Note that total_max_tokens is not supported in ai_query right now, so we need to filter
        the data passed in to this function to prevent ballooning costs.

        Args:
            data_path: The UC table of data to generate responses from
            system_prompt: The system prompt to use for the ai query
            output_column: The column name that AI query will use to create a new 
                column with generated responses.
            trailing_prompt: The trailing prompt to use for the ai query
            response_format: The response format to use for the ai query
            max_tokens: The maximum number of tokens to generate
            temperature: The temperature to use for the ai query
            disable_prompt_injection: Whether to disable prompt injection for response formatting.
        """
        ai_query = self.format_ai_query(data_path=data_path,
                                        system_prompt=system_prompt,
                                        output_column=output_column,
                                        trailing_prompt=trailing_prompt,
                                        response_format=response_format,
                                        max_tokens=max_tokens,
                                        temperature=temperature,
                                        disable_prompt_injection=disable_prompt_injection)

        print(f"Running ai_query:\n\n{ai_query}")
        spark = get_spark()
        model_df = spark.createDataFrame(spark.sql(ai_query).toPandas())
        return model_df


class PayGoEndpoint(BaseEndpoint):
    """PayGo endpoint for model serving
    """

    def __init__(self, endpoint_name: str):
        self.endpoint_name = endpoint_name
        super().__init__()

    def setup_endpoint(self) -> DatabricksEndpoint:
        return self.client.get_endpoint(self.endpoint_name)

    def get_dbu_cost_per_hour(self) -> float:
        # TODO: pass model spec key to tile batch endpoint instead of looking up in the dict
        for model_spec in BASE_MODELS.values():
            if model_spec.endpoint == self.endpoint_name:
                return model_spec.cost_per_hour
        raise KeyError(f'No cost information found for endpoint {self.endpoint_name}')


class ProvisionedThroughputEndpoint(BaseEndpoint):
    """
    Represents a provisioned throughput endpoint of a fine-tuned model that can generate text from a
    model. The endpoint is accessed through the Databricks Model Serving REST
    API and MLFlow Deployments library.

    Args:
        uc_model_path (str): The UC location of the model to be served. Ex: 'system.ai.dbrx_instruct'
        model_version (str): The version of the model to be served. Ex: '3'
        task_type (str): The task type of the model. Default is 'CHAT_COMPLETION'.
        scale_to_zero_enabled (bool): If True, the endpoint will scale to zero when not in use. Default is True.
        chunk_size_multiplier (int): The multiplier for the serving throughput chunk size. Default is 1.
        block_until_ready (bool): If True, the endpoint will block on returning until it is ready. Default is True.
    """

    def __init__(
        self,
        uc_model_path: str,
        model_version: Optional[str] = None,
        scale_to_zero_enabled: bool = True,
        chunk_size_multiplier: int = 1,
        block_until_ready: bool = True,
        teardown_on_exit: bool = True,
        warmup_after_ready_iters: int = 100,
    ) -> None:
        self._validate_inputs(uc_model_path, chunk_size_multiplier)

        if model_version is None:
            # Default to latest model version
            model_version = get_latest_model_version(uc_model_path)

        self.endpoint_name = self._generate_endpoint_name(uc_model_path, model_version)

        # PT Config
        throughput_chunk_size = self._get_throughput_chunk_size(uc_model_path, model_version)
        self.config = {
            'served_entities': [{
                'name': self.endpoint_name,
                'entity_name': uc_model_path,
                'entity_version': model_version,
                'workload_size': 'Small',
                'workload_type': 'GPU_SMALL',
                'scale_to_zero_enabled': scale_to_zero_enabled,
                'min_provisioned_throughput': 0,
                'max_provisioned_throughput': chunk_size_multiplier * throughput_chunk_size,
            }],
        }

        self.block_until_ready = block_until_ready
        self.teardown_on_exit = teardown_on_exit
        self.warmup_after_ready_iters = warmup_after_ready_iters

        super().__init__()

    def setup_endpoint(self) -> DatabricksEndpoint:
        self.endpoint = self.start_pt_endpoint()

        if not self.is_endpoint_ready():
            if self.block_until_ready:
                logger.info(f'Provisioned throughput endpoint is starting at {self.endpoint.name}. ' +
                            'Waiting for it to be ready...')
                self.wait_for_pt_endpoint_ready()
                logger.info(f'Provisioned throughput endpoint is ready at {self.endpoint.name}')
            else:
                print(f'Provisioned throughput endpoint is starting at {self.endpoint.name}. '
                      'Please wait for endpoint to be ready with '
                      f'{self.__class__.wait_for_pt_endpoint_ready.__name__} before use.')

        return self.endpoint

    def __exit__(self, _exc_type, _exc_value, _traceback) -> None:
        if self.teardown_on_exit:
            self.teardown_pt_endpoint()

    @staticmethod
    def _validate_inputs(uc_model_path: str, chunk_size_multiplier: int) -> None:
        """
        Validates input arguments for initialization.
        """
        model_path_regex = r'^[^/. ]+\.[^/. ]+\.[^/. ]+$'
        if not re.match(model_path_regex, uc_model_path):
            raise ValueError(
                f'Invalid uc_model_path {uc_model_path}. ' \
                "Please specify a UC location in the format '<catalog>.<schema>.<model>'. " \
                "This should be indicated under the 'Details' section on the model's page in your workspace.")

        if chunk_size_multiplier <= 0:
            raise ValueError('Please specify a chunk size multiplier greater than 0.')

    @staticmethod
    def _generate_endpoint_name(uc_model_path: str, model_version: str) -> str:
        """
        Helper function that generates a unique endpoint name for the PT
        endpoint. Name is unique per-user and model to avoid conflicts.
        """
        workspace_id = str(get_me())
        hashed_name = md5_hash(workspace_id, num_digits=8)
        model_name = uc_model_path.split('.')[-1]
        # rules: must be alphanumeric w/ hyphens and less than 64 characters
        endpoint_name = '-'.join([model_name[:44], f'v{model_version[:3]}', 'eval', hashed_name])
        endpoint_name = ''.join([c if c.isalnum() or c == '-' else '-' for c in endpoint_name])
        return endpoint_name

    @staticmethod
    def _get_throughput_chunk_size(uc_model_path: str, model_version: str) -> int:
        """
        Makes an request to the `serving_endpoints` API endpoint to get the
        optimized throughput chunk size. This is required for PT serving of
        fine-tuned models.
        """
        host, token = get_host_and_token_from_env()

        base_url = f'{host}/api/2.0/serving-endpoints'
        optimization_info_url = base_url + f'/get-model-optimization-info/{uc_model_path}/{model_version}'
        request_headers = {
            'Context-Type': 'text/json',
            'Authorization': f'Bearer {token}',
        }
        response = requests.get(url=optimization_info_url, headers=request_headers, timeout=10)
        if response.status_code != 200:
            raise HTTPError(f'Failed to retrieve throughput chunk size. Error {response.status_code}: {response.text}')

        throughput_information = response.json()
        throughput_chunk_size = throughput_information.get('throughput_chunk_size')

        # If `optimizable` is False, then we can't get `throughput_chunk_size`
        # because the model isn't supported by Databricks Model Serving.
        if throughput_chunk_size is None:
            optimizable = throughput_information.get('optimizable', False)
            if not optimizable:
                raise ValueError('Please use a model that is currently supported by Databricks Model serving: '
                                 'https://docs.databricks.com/en/machine-learning/foundation-models/index.html'
                                 '#provisioned-throughput-foundation-model-apis')
            raise ValueError('Could not retrieve throughput chunk size from '
                             '`serving-endpoints/model-optimization-info`. '
                             f'{json.dumps(throughput_information)}')

        return throughput_chunk_size

    def get_dbu_cost_per_hour(self) -> float:
        """
        Calls PT service with endpoint name to get endpoint price info.
        """
        host, token = get_host_and_token_from_env()
        endpoint_name = self.endpoint_name

        url = f'{host}/api/2.0/serving-endpoints/{endpoint_name}'
        request_headers = {
            'Context-Type': 'application/json',
            'Authorization': f'Bearer {token}',
        }
        response = requests.get(url=url, headers=request_headers, timeout=10)

        if response is None or response.status_code != 200:
            raise HTTPError(f'Failed to retrieve endpoint cost for {endpoint_name}. '
                            'Error {response.status_code}: {response.text}.')

        res_json = response.json()

        try:
            return res_json['config']['served_entities'][0]['max_dbus']
        except (KeyError, IndexError) as e:
            raise KeyError(f'Failed to retrieve endpoint cost for {endpoint_name}.') from e

    def start_pt_endpoint(self) -> DatabricksEndpoint:
        """
        Spins up a provisioned throughput endpoint on behalf of the user's
        provided model.
        """
        try:

            existing_endpoint = self.client.get_endpoint(self.endpoint_name)
            print(f'Endpoint {self.endpoint_name} already exists. Skipping endpoint creation. '
                  f"Please wait for endpoint to be ready with '{self.__class__.wait_for_pt_endpoint_ready.__name__}' "
                  'before use.')
            return existing_endpoint
        except HTTPError as e:
            if e.response.status_code != 404:
                raise e

        # Create the endpoint through a POST request
        endpoint = self.client.create_endpoint(name=self.endpoint_name, config=self.config)

        return endpoint

    def wait_for_pt_endpoint_ready(self, timeout_mins: int = 30, check_interval_secs: int = 30) -> DatabricksEndpoint:
        """
        Waits for the PT endpoint to be ready before returning to the user.
        """
        t0 = time.time()
        timeout_secs = timeout_mins * 60
        while time.time() - t0 < timeout_secs:
            # refresh endpoint state
            try:
                self.endpoint = self.client.get_endpoint(self.endpoint.name)
            except HTTPError as e:
                if e.response.status_code == 404:
                    print(f'Endpoint {self.endpoint.name} does not exist. Please validate your served model endpoint '
                          'and spin it up manually if necessary.')
                    return self.endpoint
            state = self.endpoint.state
            if state['ready'] == 'READY' and state['config_update'] == 'NOT_UPDATING':
                if self.warmup_after_ready_iters > 0:
                    for _ in range(self.warmup_after_ready_iters):
                        try:
                            self.generate_completion('TESTING ENDPOINT READY', max_tokens=5)
                        except HTTPError as e:
                            if not e.response.status_code == 404:
                                raise e
                self.tokens_processed = 0
                return self.endpoint
            if state['config_update'] == 'UPDATE_FAILED':
                raise RuntimeError('Endpoint update failed. Please validate your served model endpoint and spin'
                                   ' it down manually if necessary.')
            if state['config_update'] == 'UPDATE_CANCELED':
                raise RuntimeError('Endpoint update was canceled. Please validate your served model endpoint and spin'
                                   ' it down manually if necessary.')
            time.sleep(check_interval_secs)

        raise TimeoutError(f'Provisioned throughput endpoint was not ready within {timeout_mins} minutes.')

    # TODO: Remove method once this code is not used in notebooks anymore.
    def teardown_pt_endpoint(self):
        self.client.delete_endpoint(self.endpoint.name)

    def query(self,
              input_data: dict,
              max_retries: int = DEFAULT_MAX_RETRIES,
              backoff_exponential: float = DEFAULT_BACKOFF_EXPONENTIAL) -> GenerationOutput:
        """
        Queries the PT endpoint with the given input.

        Args:
            input_data (dict): Input data (or arguments) to pass to the deployment or model endpoint for inference.
        """

        if not self.is_endpoint_ready():
            raise RuntimeError('Provisioned throughput endpoint is not ready.'
                               'Please start it with `start_pt_endpoint`.')

        return super().query(input_data, max_retries, backoff_exponential)

    def generate_batch(
        self,
        *args,
        **kwargs,
    ) -> List[GenerationOutput]:

        if not self.is_endpoint_ready():
            raise RuntimeError('Provisioned throughput endpoint is not ready.'
                               'Please start it with `start_pt_endpoint`.')

        self._set_endpoint_class(EndpointClass.BATCH)
        responses = super().generate_batch(*args, **kwargs)
        self._set_endpoint_class(EndpointClass.QUERY)
        return responses


class KIETileEndpointConfig(NamedTuple):
    """System config for KIE Tile endpoints"""
    system_prompt_header: Optional[str] = None
    system_prompt_footer: Optional[str] = None
    response_format: Optional[type[BaseModel]] = None


class TileMTBatchEndpoint(BaseEndpoint):
    """
    Represents a MTPT Tile (AI Brick) endpoint of a potentially fine-tuned (PEFT) model that can generate text.
    The endpoint is accessed through the Databricks Model Serving REST API and MLFlow Deployments library.

    We won't worry about the real-time path since that doesn't work right now for these endpoints. We can add if needed
    once it's available.

    Args:
        equivalent_paygo_endpoint (str): For cost estimation, give the equivalent PAYGO endpoint name
            (e.g. "databricks-meta-llama-3-1-8b-instruct" if you are creating an 8b PEFT endpoint)
        uc_model_path (str): The UC location of the model to be served. Ex: 'system.ai.dbrx_instruct'
        model_version (str): The version of the model to be served. Ex: '3'
    """

    system_config: KIETileEndpointConfig

    def __init__(
        self,
        equivalent_paygo_endpoint: str,
        tile_id: str,
        uc_model_path: str,
        model_version: Optional[str] = None,
        system_prompt_header: Optional[str] = None,
        system_prompt_footer: Optional[str] = None,
        response_format: Optional[type[BaseModel]] = None,
        disable_prompt_injection: bool = True,
    ) -> None:
        self._set_endpoint_class(EndpointClass.BATCH)
        self._validate_inputs(uc_model_path)
        if model_version is None:
            model_version = get_latest_model_version(uc_model_path)
        self.equivalent_paygo_endpoint = equivalent_paygo_endpoint
        if response_format:
            response_format_str = json.dumps(
                self._build_response_format(response_format, disable_prompt_injection=disable_prompt_injection))
        else:
            response_format_str = None

        self.system_config = KIETileEndpointConfig(system_prompt_header=system_prompt_header,
                                                   system_prompt_footer=system_prompt_footer,
                                                   response_format=response_format)

        input_config = {
            'model_name': uc_model_path,  # very brittle code - will break if this doesn't exist
            'model_version': model_version,  # very brittle code - will break if this doesn't exist
            'tile_id': tile_id,
            'system_prompt_header': system_prompt_header,
            'system_prompt_footer': system_prompt_footer,
            'response_format': response_format_str,
        }
        self.endpoint_name = self._generate_endpoint_name(input_config)
        config = input_config | {
            'endpoint_name': self.endpoint_name,
        }
        self.config = {k: v for k, v in config.items() if v is not None}
        super().__init__()

    def setup_endpoint(self) -> DatabricksEndpoint:
        try:
            existing_endpoint = self.client.get_endpoint(self.endpoint_name)
            print(f'Endpoint {self.endpoint_name} already exists. Skipping endpoint creation.')
            return existing_endpoint
        except HTTPError as e:
            if e.response.status_code != 404:
                raise e

        _, token = get_host_and_token_from_env()
        response = requests.post(
            # TODO: probably should use the official(?) client for the DP->CP communication
            url='http://127.0.0.1:7073/api/2.0/tile-endpoints',
            headers={
                'Context-Type': 'application/json',
                'Authorization': f'Bearer {token}',
            },
            timeout=20,
            json=self.config,
        )

        if response is None or response.status_code != 200:
            raise HTTPError(f'Failed to create Tile endpoint {self.endpoint_name}. '
                            f'Error {response.status_code}: {response.text}.')

        self.endpoint = DatabricksEndpoint(response.json())
        return self.endpoint

    def __exit__(self, _exc_type, _exc_value, _traceback) -> None:
        _, token = get_host_and_token_from_env()
        response = requests.delete(
            url=f'http://127.0.0.1:7073/api/2.0/tile-endpoints/{self.endpoint_name}',
            headers={
                'Context-Type': 'application/json',
                'Authorization': f'Bearer {token}',
            },
            timeout=10,
        )
        if response is None or response.status_code != 200:
            raise HTTPError(f'Failed to delete Tile endpoint {self.endpoint_name}. '
                            f'Error {response.status_code}: {response.text}.')

    @staticmethod
    def _validate_inputs(uc_model_path: str) -> None:
        model_path_regex = r'^[^/. ]+\.[^/. ]+\.[^/. ]+$'
        if not re.match(model_path_regex, uc_model_path):
            raise ValueError(
                f'Invalid uc_model_path {uc_model_path}. ' \
                "Please specify a UC location in the format '<catalog>.<schema>.<model>'. " \
                "This should be indicated under the 'Details' section on the model's page in your workspace.")

    @staticmethod
    def _generate_endpoint_name(input_config: dict) -> str:
        """
        Generate a unique name per-user and model to avoid conflicts.
        """
        workspace_id = str(get_me())
        hashed_name = md5_hash(str(input_config | {'workspace_id': workspace_id}), num_digits=8)
        model_name = input_config['model_name'].split('.')[-1]
        # rules: must be alphanumeric w/ hyphens and less than 64 characters
        endpoint_name = '-'.join([model_name[:44], f"v{input_config['model_version'][:3]}", 'eval', hashed_name])
        endpoint_name = ''.join([c if c.isalnum() or c == '-' else '-' for c in endpoint_name])
        return endpoint_name

    def get_dbu_cost_per_hour(self) -> float:
        # TODO: pass model spec key to tile batch endpoint instead of looking up in the dict
        for model_spec in BASE_MODELS.values():
            if model_spec.endpoint == self.equivalent_paygo_endpoint:
                return model_spec.cost_per_hour
        raise KeyError(f'No cost information found for endpoint {self.equivalent_paygo_endpoint}')

    def format_ai_query(
        self,
        data_path: str,
        system_prompt: str,
        output_column: str = 'response',
        trailing_prompt: Optional[str] = None,
        response_format: Optional[type[BaseModel]] = None,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        temperature: float = DEFAULT_TEMPERATURE,
        disable_prompt_injection: bool = True,
    ):
        del system_prompt, trailing_prompt, response_format, disable_prompt_injection

        return format_ai_query_tiles(
            source=data_path,
            endpoint=self,
            output_column=output_column,
            max_tokens=max_tokens,
            temperature=temperature,
        )

    def generate_ai_query(
        self,
        data_path: str,
        system_prompt: str = "",
        output_column: str = 'response',
        trailing_prompt: Optional[str] = None,
        response_format: Optional[type[BaseModel]] = None,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        temperature: float = DEFAULT_TEMPERATURE,
        disable_prompt_injection: bool = True,
    ) -> DataFrame:
        model_df = super().generate_ai_query(
            data_path,
            system_prompt=system_prompt,
            output_column=output_column,
            trailing_prompt=trailing_prompt,
            response_format=response_format,
            max_tokens=max_tokens,
            temperature=temperature,
            disable_prompt_injection=disable_prompt_injection,
        )

        # Inject system prompt into the dataframe to keep it consistent with other endpoint types
        if self.system_config.system_prompt_header:
            model_df = model_df.withColumn('system_prompt', F.lit(self.system_config.system_prompt_header))
        if self.system_config.system_prompt_footer:
            model_df = model_df.withColumn('trailing_prompt', F.lit(self.system_config.system_prompt_footer))
        return model_df
