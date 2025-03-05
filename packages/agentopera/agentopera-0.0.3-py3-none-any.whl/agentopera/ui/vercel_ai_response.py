# create a virtual env e.g conda create -n autogen python=3.12
# pip install -U autogen-agentchat autogen-ext[openai,web-surfer]
# playwright install
# This snippet uses the Google Search API. You need to set your google search engine id and api key
# os.environ["GOOGLE_CSE_ID"] = "your_google_cse_id"
# os.environ["GOOGLE_API_KEY"] = "your_google_api_key"

from pydantic import BaseModel, Field
import json


from enum import Enum
from autogen_agentchat.messages import TextMessage, StopMessage, ModelClientStreamingChunkEvent
from autogen_core import MessageContext
from ..utils.logger import logger

# reference: https://sdk.vercel.ai/docs/ai-sdk-ui/stream-protocol

class StreamMessageType(Enum):
    TEXT_PART = '0'                         # Text Part. Example: 0:"example"\n
    SOURCE_PART = 'h'                       # Source Part
    DATA_PART = '2'                         # Data Part
    MESSAGE_ANNOTATION_PART = '8'           # Message Annotation Part
    TOOL_CALL_STREAMING_START_PART = 'b'    # 
    TOOL_CALL_DELTA_PART = 'c'              #
    
    TOOL_CALL_PART = '9'                    # start to call function Format: 9:{toolCallId:string; toolName:string; args:object}\n Example: 9:{"toolCallId":"call_fXWE5k6lhcZDkLEAT0vlZN0V","toolName":"get_weather_data","args":{"lat":37.4419,"lon":-122.143}}

    TOOL_RESULT_PART = 'a'                  # get call result. Format: a:{toolCallId:string; result:object}\n Example: a:{"toolCallId":"call-123","result":"tool output"}\n
 
    ERROR_PART = '3'
    START_STEP_PART = 'f'               # Example: f:{"messageId":"step_123"}\n
    FINISH_STEP_PART = 'e'              # e:{finishReason:'stop' | 'length' | 'content-filter' | 'tool-calls' | 'error' | 'other' | 'unknown';usage:{promptTokens:number; completionTokens:number;},isContinued:boolean}\n. Example: e:{"finishReason":"stop","usage":{"promptTokens":10,"completionTokens":20},"isContinued":false}\n
    FINISH_MESSAGE_PART = 'd'               # Format: d:{finishReason:'stop' | 'length' | 'content-filter' | 'tool-calls' | 'error' | 'other' | 'unknown';usage:{promptTokens:number; completionTokens:number;}}\n; Example: d:{"finishReason":"stop","usage":{"promptTokens":10,"completionTokens":20}}\n
    
    REASONING_PART = 'g'                # Format: g:string\n Example: g:"I will open the conversation with witty banter."\n
    REDACTED_REASONING_PART = 'i'       # Format: i:{"data": string}\n Example: i:{"data": "This reasoning has been redacted for security purposes."}\n
    REASONING_SIGNATURE_PART = 'j'      # Format: j:{"signature": string}\n Example: j:{"signature": "abc123xyz"}\n Example: j:{"signature": "abc123xyz"}\n
    
    
from pydantic import BaseModel, Field
from typing import Any, Dict
from enum import Enum


from pydantic import BaseModel, Field, field_validator
from typing import Any, Dict, Union
import json
from enum import Enum


class UserResponseVercelAI(BaseModel):
    type_id: StreamMessageType = Field(default=StreamMessageType.TEXT_PART)
    content_json: Union[Dict[str, Any], str] = Field(default={})  # Supports both json dict & str

    def to_string(self) -> str:
        """Returns the response in 'TYPE_ID:CONTENT_JSON' string format"""
        return f"{self.type_id.value}:{json.dumps(self.content_json)}\n"
        # if isinstance(self.content_json, dict):
        #     return f"{self.type_id.value}:{json.dumps(self.content_json)}\n"
        # if isinstance(self.content_json, str):
        #     logger.info(f"debug UserResponseVercelAI format. self.content_json = {self.content_json}")
        #     str_ret = f"{self.type_id.value}:\"{self.content_json}\""
        #     str_ret = str_ret.replace("\n", "\\n").replace("\t", "\\t")
        #     str_ret = str_ret + "\n"

    def __str__(self):
        """Ensures that printing the object returns the formatted string"""
        return self.to_string()
    
def is_streaming_finished(response: str):
    return response.split(":")[0] == StreamMessageType.FINISH_MESSAGE_PART.value
        
def transform_autogen_message_to_vercel_ai_streaming_message(
    message: TextMessage | StopMessage | ModelClientStreamingChunkEvent, 
    ctx: MessageContext
    ):

    if isinstance(message, StopMessage):
        # content_json = {
        #     "finishReason": "stop",
        #     "usage": {
        #         "promptTokens": message.models_usage.prompt_tokens,
        #         "completionTokens": message.models_usage.completion_tokens
        #     }
        # }
        content_json = {
            "finishReason": "stop",
            "usage": {
                "promptTokens": 0,
                "completionTokens": 0
            }
        }
        response = UserResponseVercelAI(type_id=StreamMessageType.FINISH_MESSAGE_PART, content_json=content_json)
    elif isinstance(message, ModelClientStreamingChunkEvent):
        content_json = message.content
        response = UserResponseVercelAI(type_id=StreamMessageType.TEXT_PART, content_json=content_json)
    elif isinstance(message, TextMessage):
        logger.info(f"parser debug message.source = {message.source}. message = {message}")
        if isinstance(message.source, str) and message.source == 'user':
            logger.info("The source is 'user'")
            content_json = {"messageId": ctx.message_id}
            response = UserResponseVercelAI(type_id=StreamMessageType.START_STEP_PART, content_json=content_json)
        else:
            # content_json = {
            #     "finishReason": "stop",
            #     "usage": {
            #         "promptTokens": message.models_usage.prompt_tokens,
            #         "completionTokens": message.models_usage.completion_tokens
            #     },
            #     "isContinued": False
            # }
            content_json = {
                "finishReason": "stop",
                "usage": {
                    "promptTokens": 0,
                    "completionTokens": 0,
                },
                "isContinued": False
            }
            response = UserResponseVercelAI(type_id=StreamMessageType.FINISH_STEP_PART, content_json=content_json)
    else:
        # do nothing
        logger.info(f"message = {message}")
    return response.to_string()
        
