from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from .runtime_manager import runtime_manager

from starlette.responses import StreamingResponse

from .ui.vercel_ai_request import ChatRequest


router = APIRouter()
    
    
@router.post("/api/chat")
async def chat_for_vercel_ai_protocol(request: ChatRequest):
    
    try:
        return StreamingResponse(
            runtime_manager.stream_user_message_for_vercel_ai_web(
                content=request.messages[-1].content,
                message_id=request.id,
            ),
            media_type='text/event-stream'
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))