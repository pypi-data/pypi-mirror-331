from pydantic import BaseModel
from typing import List, Optional


# Vercel AI SDK format:

# {
# 	"id": "ZWToutqeUawzfaR7",
# 	"messages": [{
# 		"role": "user",
# 		"content": "tensoropera ai",
# 		"parts": [{
# 			"type": "text",
# 			"text": "tensoropera ai"
# 		}]
# 	}],
# 	"model": "chainopera-default",
# 	"group": "extreme"
# }

class MessagePart(BaseModel):
    type: str
    text: str

class Message(BaseModel):
    role: str
    content: str
    parts: List[MessagePart]

class ChatRequest(BaseModel):
    id: str
    messages: List[Message]
    model: str
    group: Optional[str]  # Optional in case it's missing in some cases
