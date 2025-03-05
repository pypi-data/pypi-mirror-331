from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse


from ..ui.vercel_ai_request import ChatRequest
from .runtime_manager import runtime_manager

from agentopera.utils.logger import logger

from dotenv import load_dotenv

load_dotenv()
# Initialize FastAPI app
app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (for development)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Start the runtime and register agents on startup
@app.on_event("startup")
async def startup_event():
    logger.info("Starting router service and runtime manager.")
    await runtime_manager.start_runtime()

# Handle graceful shutdown
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down router service.")
    await runtime_manager.agent_runtime.stop()

# Health check endpoint
@app.get("/")
async def health_check():
    return {"status": "Router Service Running", "message": "All systems operational."}

@app.post("/api/chat")
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