import asyncio
import aiohttp
import json
import time

from .._semantic_router_components import FinalResult
from agentopera.core import DefaultTopicId, MessageContext, message_handler
from ._worker_agents import WorkerAgent
from agentopera.chatflow.messages import TextMessage

from ...utils.logger import logger


class DeepResearchAgent(WorkerAgent):
    """A specialized agent for conducting deep research via an external API."""

    def __init__(self, name: str, api_url: str) -> None:
        super().__init__(name)
        self.api_url = api_url

    @message_handler
    async def my_message_handler(self, message: TextMessage, ctx: MessageContext) -> None:
        """Handles messages, performing deep research and streaming responses."""
        assert ctx.topic_id is not None
        logger.debug(f"[DeepResearchAgent] Received message from {message.source}: {message.content}")

        if "END" in message.content:
            await super().my_message_handler(message, ctx)
            return

        current_chunk = ""
        last_flush_time = time.time()  # Track last message sent time

        async for chunk in self.fetch_deep_research(message.content):
            if chunk.strip():  # Ignore empty chunks
                logger.debug(f"[DeepResearchAgent] Streaming chunk: {chunk}")

                if chunk == "[DONE]":
                    # Send remaining content if any
                    if current_chunk:
                        await self.publish_message(
                            TextMessage(content=current_chunk, source=ctx.topic_id.type),
                            topic_id=DefaultTopicId(type="response", source=ctx.topic_id.source),
                        )
                    # Send final completion message
                    await self.publish_message(
                        FinalResult(content="", source=ctx.topic_id.type),
                        topic_id=DefaultTopicId(type="response", source=ctx.topic_id.source),
                    )
                    return  # Exit loop when stream is complete

                else:
                    current_chunk += chunk  # Accumulate chunk data

                    # **Flush conditions**
                    if len(current_chunk) > 300 or (time.time() - last_flush_time) > 2:
                        await self.publish_message(
                            TextMessage(content=current_chunk, source=ctx.topic_id.type),
                            topic_id=DefaultTopicId(type="response", source=ctx.topic_id.source),
                        )
                        current_chunk = ""  # Reset chunk buffer
                        last_flush_time = time.time()  # Reset timer

    async def fetch_deep_research(self, prompt: str):
        """Queries the external research API and streams the response."""
        # headers = {
        #     "Content-Type": "application/json",
        #     "Accept": "text/event-stream"
        # }

        payload = {"prompt": prompt}

        async with aiohttp.ClientSession() as session:
            try:
                logger.debug(f"[DeepResearchAgent] Sending API request: {json.dumps(payload, indent=2)}")

                async with session.post(
                    self.api_url, 
                    #headers=headers, 
                    json=payload, 
                    timeout=1000
                ) as response:
                    logger.debug(f"[DeepResearchAgent] API Response Status: {response.status}")

                    if response.status == 200:
                        async for chunk in response.content.iter_any():  # Streaming response
                            if chunk:
                                try:
                                    text = chunk.decode('utf-8')
                                    if text.startswith('data: '):
                                        text = text[6:]

                                    if 'TERMINATE' in text:
                                        content = text.split('TERMINATE')[0]
                                        if content.strip():
                                            yield content.strip()
                                        yield '[DONE]'
                                    else:
                                        yield text.strip()
                                except UnicodeDecodeError as e:
                                    logger.error(f"[DeepResearchAgent] Decode error: {e}")
                                    continue
                    else:
                        error_msg = f"Error: API returned status {response.status}"
                        logger.error(f"[DeepResearchAgent] {error_msg}")
                        yield error_msg
                        yield '[DONE]'

            except asyncio.TimeoutError:
                error_msg = "Error: API request timed out"
                logger.error(f"[DeepResearchAgent] {error_msg}")
                yield error_msg
                yield '[DONE]'
            except Exception as e:
                error_msg = f"Error: {str(e)}"
                logger.error(f"[DeepResearchAgent] {error_msg}")
                yield error_msg
                yield '[DONE]'
