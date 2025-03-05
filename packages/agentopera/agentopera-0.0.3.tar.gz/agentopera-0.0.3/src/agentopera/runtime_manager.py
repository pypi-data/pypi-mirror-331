import asyncio
import json
from typing import Dict
from autogen_ext.runtimes.grpc import GrpcWorkerAgentRuntime
from autogen_core import DefaultSubscription, DefaultTopicId, ClosureAgent, \
    MessageContext, ClosureContext, MessageSerializer, try_get_known_serializers_for_type
from .agent_registry import AgentFactory
from .ui.vercel_ai_response import is_streaming_finished, transform_autogen_message_to_vercel_ai_streaming_message
from .agents.workers._worker_agents import WorkerAgent, UserProxyAgent
from ._semantic_router_agent import SemanticRouterAgent
from ._semantic_router_components import TextMessage
from ._semantic_router_components import UserResponse
from .agents.workers.httpwokers import HTTPWorkerAgent
from .agents.workers.deep_search_agent import DeepResearchAgent
from .agents.workers.chat_agent import ChatAgent
from autogen_agentchat.messages import TextMessage, StopMessage, ModelClientStreamingChunkEvent
from typing import Any, Iterable, Type

from typing import Any

from .utils.logger import logger

# Standalone closure function
async def output_result(
    closure_ctx: ClosureContext, 
    message: TextMessage | StopMessage | ModelClientStreamingChunkEvent, 
    ctx: MessageContext
) -> UserResponse:
    """Returns response directly - runtime handles routing."""
    response = transform_autogen_message_to_vercel_ai_streaming_message(message, ctx)
    logger.info("output_result: response = {} for message_id {}".format(response, ctx.message_id))
    response_queue = await runtime_manager.get_response_queue(ctx.message_id)
    await response_queue.put(response)

class RuntimeManager:
    def __init__(self, host_address="localhost:50051"):
        self.agent_runtime = GrpcWorkerAgentRuntime(host_address=host_address)
        self.agent_runtime.add_message_serializer(self._get_serializers([TextMessage, StopMessage])) 
        self.is_running = False
        self.response_queues: Dict[str, asyncio.Queue[UserResponse]] = {}

    def _get_serializers(self, types: Iterable[Type[Any]]) -> list[MessageSerializer[Any]]:
        serializers = []
        for type in types:
            serializers.extend(try_get_known_serializers_for_type(type))  # type: ignore
        return serializers  # type: ignore [reportUnknownVariableType]

    async def get_response_queue(self, user_id: str) -> asyncio.Queue[UserResponse]:
        """Get or create a response queue for a user."""
        if user_id not in self.response_queues:
            self.response_queues[user_id] = asyncio.Queue()
        return self.response_queues[user_id]

    async def start_runtime(self):
        logger.info("Connecting to host runtime...")
        await self.agent_runtime.start()
    
        await self.register_agents()
        self.is_running = True
        logger.info("All agents successfully registered and runtime initialized.")

    async def register_agents(self):
        # Register Worker Agents
        await WorkerAgent.register(
            self.agent_runtime, 
            "finance", 
            lambda: WorkerAgent("finance_agent")
        )
        await self.agent_runtime.add_subscription(
            DefaultSubscription(topic_type="finance", agent_type="finance")
        )

        await WorkerAgent.register(
            self.agent_runtime, 
            "hr", 
            lambda: WorkerAgent("hr_agent")
        )
        await self.agent_runtime.add_subscription(
            DefaultSubscription(topic_type="hr", agent_type="hr")
        )

        # Register HTTPWorkerAgent
        await HTTPWorkerAgent.register(
            self.agent_runtime,
            "search",
            lambda: HTTPWorkerAgent("search", "http://host.docker.internal:3001/api/search")
        )
        await self.agent_runtime.add_subscription(DefaultSubscription(topic_type="search", agent_type="search"))

        # Register DeepResearchAgent
        await DeepResearchAgent.register(
            self.agent_runtime,
            "deep_research",
            lambda: DeepResearchAgent("deep_research", "http://host.docker.internal:8005/agent/deep-research")
        )
        await self.agent_runtime.add_subscription(DefaultSubscription(topic_type="deep_research", agent_type="deep_research"))

        await ChatAgent.register(
            self.agent_runtime,
            "chat",
            lambda: ChatAgent("chat")
        )
        await self.agent_runtime.add_subscription(DefaultSubscription(topic_type="chat", agent_type="chat"))

        # Register User Proxy Agent
        await UserProxyAgent.register(
            self.agent_runtime, 
            "user_proxy", 
            lambda: UserProxyAgent("user_proxy")
        )
        await self.agent_runtime.add_subscription(
            DefaultSubscription(topic_type="user_proxy", agent_type="user_proxy")
        )

        # Register Closure Agent and store its ID
        await ClosureAgent.register_closure(
            self.agent_runtime,
            "closure_agent",
            output_result,
            subscriptions=lambda: [
                DefaultSubscription(topic_type="response", agent_type="closure_agent")
            ],
        )

        # Register Semantic Router Agent
        agent_registry = AgentFactory.create_agent_registry()
        intent_classifier = AgentFactory.create_intent_classifier(agent_registry)
        await SemanticRouterAgent.register(
            self.agent_runtime,
            "router",
            lambda: SemanticRouterAgent(
                name="router", 
                agent_registry=agent_registry, 
                intent_classifier=intent_classifier
            )
        )
        await self.agent_runtime.add_subscription(
            DefaultSubscription(
                topic_type="router",
                agent_type="router"
            )
        )

    async def cleanup(self):
        """Cleanup resources when shutting down."""
        if self.is_running:
            await self.agent_runtime.disconnect()
            self.is_running = False

    async def stream_user_message_for_vercel_ai_web(self, content: str, message_id: str):
        """Stream responses back to the client."""
        if not self.is_running:
            raise RuntimeError("Agent runtime is not running.")

        logger.info(f"Publishing streaming message: {content} for message_id: {message_id}")
        response_queue = await self.get_response_queue(message_id)
        
        # Send message to router
        await self.agent_runtime.publish_message(
            message=TextMessage(
                content=content, 
                source="user"
            ),
            message_id=message_id,
            topic_id=DefaultTopicId(type="router", source="user")
        )
        logger.info("start to stream for message_id: {}\n\n".format(message_id))
        # Stream responses
        while True:
            try:
                response = await asyncio.wait_for(
                    response_queue.get(),
                    timeout=100
                )
                yield response
                
                if is_streaming_finished(response):
                    logger.info("================= STREAMING SI FINISHED ========================")
                    break
                    
            except asyncio.TimeoutError:
                yield "data: {\"error\": \"Timeout waiting for response\"}\n\n"
                break
            except Exception as e:
                yield f"data: {{\"error\": \"{str(e)}\"}}\n\n"
                break
            
runtime_manager = RuntimeManager()
