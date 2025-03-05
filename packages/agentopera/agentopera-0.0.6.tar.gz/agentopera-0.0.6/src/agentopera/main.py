from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .runtime_manager import runtime_manager
from .router import router

from .utils.logger import logger

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


# Attach the API router for handling requests
app.include_router(router)

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
