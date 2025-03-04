

import os, sys
from pathlib import Path
here = Path(__file__).parent
try:
    from autogen.version import __version__
except:
    local_autogen = f"{here.parent}/repos/autogen"
    sys.path.insert(0, f"{here.parent}/repos/autogen")
    from autogen.version import __version__
    print(f'`autogen` is not installed, load from {local_autogen}, version: {__version__}')


from autogen import (
    GroupChat, GroupChatManager,
    Agent, ConversableAgent, AssistantAgent, UserProxyAgent,
    register_function,
    config_list_from_json,
    oai, coding
)

from autogen.oai.client import (
    PlaceHolderClient, OpenAIWrapper, OpenAIClient, ModelClient
    )

from autogen.runtime_logging import (
    logging_enabled, start, stop, log_chat_completion, log_new_agent, log_new_wrapper, log_new_client, get_connection
    )

from autogen.cache.cache import Cache, AbstractCache

from autogen.agentchat.chat import ChatResult
from autogen.agentchat.agent import LLMAgent

from autogen.coding import (
    CodeBlock, CodeExecutor, CodeExtractor, CodeResult, MarkdownCodeExtractor, LocalCommandLineCodeExecutor
    )
from autogen.coding.factory import CodeExecutorFactory

from autogen.code_utils import (
    content_str, CODE_BLOCK_PATTERN, UNKNOWN, content_str, infer_lang
)

from autogen.types import (
    UserMessageImageContentPart, UserMessageTextContentPart
)

from autogen.logger.logger_utils import (
    get_current_ts
    )
# from autogen._pydantic import model_dump


from autogen.runtime_logging import (
    logging_enabled, start, stop, log_chat_completion, log_new_agent, 
    log_new_wrapper, log_new_client, get_connection, log_event
    )

from autogen.io.websockets import IOStream, IOWebsockets

from autogen.agentchat.utils import (
    consolidate_chat_info, gather_usage_summary
)


# __all__ = [
#     'GroupChat', 'GroupChatManager',
#     'Agent', 'ConversableAgent', 'AssistantAgent', 'UserProxyAgent',
#     'register_function',
#     'config_list_from_json',
# ]





