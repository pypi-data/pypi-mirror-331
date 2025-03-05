
from agentopera.core import DefaultTopicId, MessageContext, message_handler
from agentopera.agents.models.openai import OpenAIChatCompletionClient
from agentopera.chatflow.agents import AssistantAgent
from ._worker_agents import WorkerAgent
from ...config_loader import ConfigLoader
from agentopera.chatflow.messages import TextMessage, StopMessage, ModelClientStreamingChunkEvent
from agentopera.chatflow.base import TaskResult
from agentopera.core.memory import ListMemory, MemoryContent
from agentopera.core import CancellationToken

from ...utils.logger import logger


class ChatAgent(WorkerAgent):
    """A specialized agent for conducting deep research via an external API."""

    def __init__(self, name: str) -> None:
        super().__init__(name)
        config = ConfigLoader.get_openai_config()
        
        # Extract the first config from the config_list
        openai_config = config["config_list"][0]
        
        """init the agent instance"""
        # Initialize the model client
        model_client = OpenAIChatCompletionClient(
            model="gpt-4o",
            temperature=0.7,
            api_key=openai_config["api_key"],
        )
        
        memory = ListMemory()
        memory.add(MemoryContent(content="User likes pizza.", mime_type="text/plain"))
        memory.add(MemoryContent(content="User dislikes cheese.", mime_type="text/plain"))

        self.agent = AssistantAgent(
            name="chat_agent",
            model_client=model_client,
            system_message="You are a helpful assistant.",
            memory=[memory],
            model_client_stream=True,  # Enable streaming tokens from the model client.
        )

    @message_handler
    async def my_message_handler(self, message: TextMessage, ctx: MessageContext) -> None:
        """Handles messages, performing deep research and streaming responses."""
        assert ctx.topic_id is not None



        # task_messages = [TextMessage(source=m.role, content=m.content) for m in request.messages]
        try:
            async for chunk in self.agent.run_stream(task=[message], cancellation_token=CancellationToken()):
                logger.info(f"[ChatAgent] Chunk message from {message.source}: message: {message}")
            # async for chunk in self.agent.run_stream(task=message):
                # if isinstance(chunk, (ToolCallRequestEvent, ToolCallExecutionEvent, 
                #                     ToolCallSummaryMessage, TextMessage)):
                    # Create a formatted string message
                if isinstance(chunk, TextMessage):
                    logger.info(f"chat agent - TextMessage: chunk.source = {chunk.source} | ctx.topic_id.source = {ctx.topic_id.source}. ")
                    await self.publish_message(
                        TextMessage(content=chunk.content, source=chunk.source),
                        topic_id=DefaultTopicId(type="response", source=chunk.source),
                        message_id=ctx.message_id,
                    )
                    # if chunk.source == 'user':
                    #     logger.info(f"[user] debug chat_agent. chunk.source = {chunk.source} | ctx.topic_id.source = {ctx.topic_id.source}. ")

                    # )
                    # else:
                    #     logger.info(f"[NOT USER] debug chat_agent. chunk.source = {chunk.source} | ctx.topic_id.source = {ctx.topic_id.source}. ")
                    #     await self.publish_message(
                    #         TextMessage(content=chunk.content, source=ctx.topic_id.type),
                    #         topic_id=DefaultTopicId(type="response", source=ctx.topic_id.type),
                    #         message_id=ctx.message_id,
                    #     )
                elif isinstance(chunk, ModelClientStreamingChunkEvent):
                    # logger.info(f"ctx.topic_id.type = {ctx.topic_id.type}, ctx.topic_id.source = {ctx.topic_id.source}. \
                    # currrent chunk: {chunk}, message_id = {ctx.message_id}")
                    await self.publish_message(
                        ModelClientStreamingChunkEvent(content=chunk.content, source=ctx.topic_id.type),
                        topic_id=DefaultTopicId(type="response", source=ctx.topic_id.type),
                        message_id=ctx.message_id,
                    )
                elif isinstance(chunk, TaskResult):
                    logger.info(f"ctx.topic_id.type = {ctx.topic_id.type}, ctx.topic_id.source = {ctx.topic_id.source}. \
                    currrent chunk: {chunk}, message_id = {ctx.message_id}")
                    await self.publish_message(
                        StopMessage(content=chunk.messages[-1].content, source=ctx.topic_id.type),
                        topic_id=DefaultTopicId(type="response", source=ctx.topic_id.source),
                        message_id=ctx.message_id,
                    )
                else:
                    logger.info(f"do nothing... currrent chunk: {chunk}, message_id = {ctx.message_id}")

                # else:
                #     # **Flush conditions**

    
        except Exception as e:
            logger.info(f"Error in generate: {e}")
            # message = {"type": "error", "content": str(e)}
            # yield f"data: {json.dumps(message)}\n\n".encode('utf-8')