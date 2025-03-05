import asyncio
import aiohttp
import json
import re

from ..._semantic_router_components import FinalResult
from autogen_core import DefaultTopicId, MessageContext, message_handler
from ._worker_agents import WorkerAgent
from autogen_agentchat.messages import TextMessage

from ...utils.logger import logger


class HTTPWorkerAgent(WorkerAgent):
    """A WorkerAgent that streams API responses to the user in real-time."""

    def __init__(self, name: str, api_url: str) -> None:
        super().__init__(name)
        self.api_url = api_url

    @message_handler
    async def my_message_handler(self, message: TextMessage, ctx: MessageContext) -> None:
        """Handles messages and streams response chunks."""
        assert ctx.topic_id is not None
        logger.debug(f"[HTTPWorker] Received message from {message.source}: {message.content}")

        if "END" in message.content:
            await super().my_message_handler(message, ctx)
            return

        current_chunk = ""
        # Stream response chunk by chunk
        async for chunk in self.fetch_data(message.content):
            if chunk.strip():
                logger.debug(f"[HTTPWorker] Streaming chunk: {chunk}")
                
                if chunk == "[DONE]":
                    # Send any remaining content before final message
                    if current_chunk:
                        await self.publish_message(
                            TextMessage(content=current_chunk, source=ctx.topic_id.type),
                            topic_id=DefaultTopicId(type="response", source=ctx.topic_id.source),
                        )
                    # Send final message
                    await self.publish_message(
                        FinalResult(content="", source=ctx.topic_id.type),
                        topic_id=DefaultTopicId(type="response", source=ctx.topic_id.source),
                    )
                else:
                    current_chunk += chunk
                    # Check if we have a complete sentence or paragraph
                    if any(marker in chunk for marker in ['.', '!', '?', '\n']):
                        await self.publish_message(
                            TextMessage(content=current_chunk, source=ctx.topic_id.type),
                            topic_id=DefaultTopicId(type="response", source=ctx.topic_id.source),
                        )
                        current_chunk = ""

    async def fetch_data(self, user_query: str):
        """Streams responses from an external API."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "text/event-stream"
        }

        source_urls = []  # List to store URLs

        payload = {
            "query": user_query,
            "chatModel": {
                "provider": "openai",
                "model": "gpt-4o-mini"
            },
            "embeddingModel": {
                "provider": "openai",
                "model": "text-embedding-3-large"
            },
            "optimizationMode": "speed",
            "focusMode": "webSearch"
        }

        async with aiohttp.ClientSession() as session:
            try:
                logger.debug(f"[HTTPWorker] Sending API request: {json.dumps(payload, indent=2)}")
                
                async with session.post(
                    self.api_url, 
                    headers=headers, 
                    json=payload, 
                    timeout=1000
                ) as response:
                    logger.debug(f"[HTTPWorker] API Response Status: {response.status}")

                    if response.status == 200:
                        async for chunk in response.content:
                            if chunk:
                                try:
                                    text = chunk.decode('utf-8')
                                    if text.startswith('data: '):
                                        text = text[6:]
                                    
                                    # Extract URLs from SOURCES
                                    if 'SOURCES:' in text:
                                        try:
                                            sources = json.loads(text.replace('SOURCES:', '').strip())
                                            for source in sources:
                                                url = source.get('metadata', {}).get('url')
                                                if url:
                                                    source_urls.append(url)
                                            logger.debug(f"[HTTPWorker] Extracted URLs: {source_urls}")
                                        except json.JSONDecodeError as e:
                                            logger.error(f"[HTTPWorker] JSON parse error: {e}")
                                        yield text
                                    elif '[DONE]' in text:
                                        content = text.split('[DONE]')[0]
                                        if content.strip():
                                            yield content.strip()
                                        yield '[DONE]'
                                    else:
                                        # Regular content chunk - Transform citations to links
                                        text = text.strip()
                                        # Find all citation numbers and replace with markdown links
                                        def replace_citation(match):
                                            num = int(match.group(1))
                                            if 0 < num <= len(source_urls):
                                                return f'[{num}]({source_urls[num-1]})'
                                            return match.group(0)
                                        
                                        text = re.sub(r'\[(\d+)\]', replace_citation, text)
                                        yield text

                                except UnicodeDecodeError as e:
                                    logger.error(f"[HTTPWorker] Decode error: {e}")
                                    continue
                    else:
                        error_msg = f"Error: API returned status {response.status}"
                        logger.error(f"[HTTPWorker] {error_msg}")
                        yield error_msg
                        yield '[DONE]'

            except asyncio.TimeoutError:
                error_msg = "Error: API request timed out"
                logger.error(f"[HTTPWorker] {error_msg}")
                yield error_msg
                yield '[DONE]'
            except Exception as e:
                error_msg = f"Error: {str(e)}"
                logger.error(f"[HTTPWorker] {error_msg}")
                yield error_msg
                yield '[DONE]'
