
from typing import Union, Mapping, Literal, TypeVar, cast
from typing import Any, Dict, Optional, List
from typing_extensions import override
import httpx
from httpx import Timeout

try:
    import openai
except ImportError:
    ERROR: Optional[ImportError] = ImportError("Please install openai>=1 and diskcache to use autogen.OpenAIWrapper.")
    OpenAI = object
    AzureOpenAI = object
else:
    # raises exception if openai>=1 is installed and something is wrong with imports
    from openai import OpenAI, AzureOpenAI

from openai.types.chat import ChatCompletion
from openai import OpenAI
from DrSai.apis.autogen_api import OpenAIWrapper, PlaceHolderClient, OpenAIClient, ModelClient
from DrSai.configs import CONST

DEFAULT_TIMEOUT = httpx.Timeout(timeout=600.0, connect=5.0)
DEFAULT_MAX_RETRIES = 2
DEFAULT_LIMITS = httpx.Limits(max_connections=100, max_keepalive_connections=20)

# Sentinel class used until PEP 0661 is accepted
class NotGiven:
    """
    A sentinel singleton class used to distinguish omitted keyword arguments
    from those passed in with the value None (which may have different behavior).

    For example:

    ```py
    def get(timeout: Union[int, NotGiven, None] = NotGiven()) -> Response: ...

    get(timout=1) # 1s timeout
    get(timout=None) # No timeout
    get() # Default timeout behavior, which may not be statically known at the method definition.
    ```
    """

    def __bool__(self) -> Literal[False]:
        return False

    @override
    def __repr__(self) -> str:
        return "NOT_GIVEN"

_T = TypeVar("_T")
NotGivenOr = Union[_T, NotGiven]
NOT_GIVEN = NotGiven()


class HepAIInheritedFromOpenAI(OpenAI):

    def __init__(
        self,
        *,
        api_key: str | None = None,
        organization: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: Union[float, Timeout, None, NotGiven] = NOT_GIVEN,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        # Configure a custom httpx client. See the [httpx documentation](https://www.python-httpx.org/api/#client) for more details.
        http_client: httpx.Client | None = None,
        # Enable or disable schema validation for data returned by the API.
        # When enabled an error APIResponseValidationError is raised
        # if the API responds with invalid data for the expected schema.
        #
        # This parameter may be removed or changed in the future.
        # If you rely on this feature, please open a GitHub issue
        # outlining your use-case to help us decide if it should be
        # part of our public interface in the future.
        _strict_response_validation: bool = False,
        proxy: str | None = None,
    ) -> None:
        http_client = self.get_http_client(proxy, base_url=base_url, timeout=timeout)
       
        super().__init__(
            api_key=api_key,
            organization=organization,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            default_headers=default_headers,
            default_query=default_query,
            http_client=http_client,
            _strict_response_validation=_strict_response_validation,
        )


    def get_http_client(self, proxy, **kwargs) -> httpx.Client:
        if proxy is None:
            return None
        else:
            proxies = {
                "http://": proxy,
                "https://": proxy,
            }
        base_url = kwargs.get("base_url", None)
        base_url = base_url or CONST.BASE_URL
        timeout = kwargs.get("timeout", DEFAULT_TIMEOUT)
        timeout = DEFAULT_TIMEOUT if (timeout == NOT_GIVEN or timeout is None) else timeout
        transport = kwargs.get("transport", None)
        limits = kwargs.get("limits", DEFAULT_LIMITS)
        limits = DEFAULT_LIMITS if (limits == NOT_GIVEN or limits is None) else limits
        http_client = httpx.Client(
            base_url=base_url,
            timeout=timeout,
            proxy=proxies,
            transport=transport,
            limits=limits,
        )
        return http_client
    
    def a(self):
        self.chat.completions.create()


class HepAIClient(OpenAIClient):
    # def __init__(self, client: Union[OpenAI, AzureOpenAI]):
    def __init__(self, client):
        super().__init__(client)
        pass

    @property
    def base_url(self) -> str:
        return f'<HepAIClient base_url={self._client.base_url}>'

    def __repr__(self) -> str:
        return super().__repr__()

    def create(self, params: Dict[str, Any]) -> ChatCompletion:
        need_stream_obj = params.pop("need_stream_obj", False)
        if need_stream_obj:
             return self.create_stream_obj(params)
        return super().create(params)
    
    def create_stream_obj(self, params: Dict[str, Any]) -> ChatCompletion:
        completions: Completions = self._oai_client.chat.completions if "messages" in params else self._oai_client.completions  # type: ignore [attr-defined]
        # If streaming is enabled and has messages, then iterate over the chunks of the response.
        assert params.get("stream", False) == True, "stream must be True"
        assert "messages" in params
        try:
            oai_stream_obj = completions.create(**params)
        except Exception as e:
            # logger.error(f"Failed to create stream object: {e}")
            raise e
        return oai_stream_obj
    