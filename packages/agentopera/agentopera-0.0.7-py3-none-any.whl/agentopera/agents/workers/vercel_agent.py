from typing import AsyncGenerator, Sequence
from agentopera.core import CancellationToken
from agentopera.chatflow.messages import (
    AgentEvent, ChatMessage, TextMessage, ModelClientStreamingChunkEvent
)
from agentopera.chatflow.agents import BaseChatAgent
from agentopera.chatflow.base import Response
import aiohttp
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import json



# Define the Streaming Agent
class StreamingEndpointAgent(BaseChatAgent):
    def __init__(self, name: str, endpoint_url: str):
        super().__init__(name=name, description="Agent that streams from endpoint")
        self.endpoint_url = endpoint_url

    @property
    def produced_message_types(self) -> Sequence[type[ChatMessage]]:
        return (TextMessage,)

    async def on_messages(
        self, 
        messages: Sequence[ChatMessage], 
        cancellation_token: CancellationToken
    ) -> Response:
        """Required implementation of abstract method."""
        async for message in self.on_messages_stream(messages, cancellation_token):
            if isinstance(message, Response):
                return message
        raise AssertionError("Stream should have returned final response")

    async def on_reset(self, cancellation_token: CancellationToken) -> None:
        """Required implementation of abstract method."""

    # Simplified streaming method for raw string input
    async def on_messages_stream(
        self, messages: Sequence[ChatMessage], cancellation_token: CancellationToken
    ) -> AsyncGenerator[AgentEvent | ChatMessage | Response, None]:
        try:
            prompt = messages[-1].content if messages else ""

            # Send raw string directly to the endpoint
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.endpoint_url,
                    data=prompt,  # Sending plain text instead of JSON
                    headers={"Accept": "text/event-stream", "Content-Type": "text/plain"}
                ) as response:
                    async for chunk in response.content:
                        if chunk:
                            yield chunk

        except Exception as e:
            raise RuntimeError(f"Streaming failed: {str(e)}") from e


# FastAPI server setup
app = FastAPI()


@app.post("/stream-chat")
async def stream_chat(request: Request):
    body = await request.body()  # Reading raw body content (single string)
    message = body.decode("utf-8").strip()

    vercel_agent = StreamingEndpointAgent(
        name="vercel_ai",
        endpoint_url="http://localhost:3001/api/chat"  # Replace with your real streaming URL
    )

    async def event_generator():
        messages = [TextMessage(content=message, source="user")]
        async for event in vercel_agent.on_messages_stream(messages, CancellationToken()):
            print(f"{event}")
            yield event

    return StreamingResponse(event_generator(), media_type="text/event-stream")
