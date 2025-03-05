from typing import AsyncGenerator, Sequence
from autogen_core import CancellationToken
from autogen_agentchat.messages import (
    AgentEvent, ChatMessage, TextMessage, ModelClientStreamingChunkEvent
)
from autogen_agentchat.agents import BaseChatAgent
from autogen_agentchat.base import Response
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
                            yield ModelClientStreamingChunkEvent(
                                content=chunk.decode(),
                                source=self.name
                            )

            # Signal completion with an empty final response
            yield Response(
                chat_message=TextMessage(
                    content="",  # Empty response at the end of the stream
                    source=self.name
                )
            )

        except Exception as e:
            raise RuntimeError(f"Streaming failed: {str(e)}") from e


# FastAPI server setup
app = FastAPI()


@app.post("/stream-chat")
async def stream_chat(request: Request):
    body = await request.body()  # Reading raw body content (single string)
    message = body.decode("utf-8").strip()

    agent = StreamingEndpointAgent(
        name="streamer",
        endpoint_url="http://localhost:8000/stream"  # Replace with your real streaming URL
    )

    async def event_generator():
        messages = [TextMessage(content=message, source="user")]
        async for event in agent.on_messages_stream(messages, CancellationToken()):
            if isinstance(event, ModelClientStreamingChunkEvent):
                yield f"data: {json.dumps({'chunk': event.content})}\n\n"
            elif isinstance(event, Response):
                yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


# Client to consume the stream
async def stream_chat_client():
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "http://localhost:8001/stream-chat",
            data="Tell me a story",  # Sending a simple string
            headers={"Accept": "text/event-stream", "Content-Type": "text/plain"}
        ) as response:
            async for line in response.content:
                if line:
                    decoded_line = line.decode().strip()
                    if decoded_line.startswith("data: "):
                        event = json.loads(decoded_line[6:])
                        if "chunk" in event:
                            print(event["chunk"], end="", flush=True)
                        elif event == "[DONE]":
                            print("\nStream completed.")
