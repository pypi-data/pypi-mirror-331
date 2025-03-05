"""
This example showcases using a Semantic Router
to dynamically route user messages to the most appropraite agent
for a conversation.

The Semantic Router Agent is responsible for receiving messages from the user,
identifying the intent of the message, and then routing the message to the
agent, by referencing an "Agent Registry". Using the
pub-sub model, messages are broadcast to the most appropriate agent.

In this example, the Agent Registry is a simple dictionary which maps
string-matched intents to agent names. In a more complex example, the
intent classifier may be more robust, and the agent registry could use a
technology such as Azure AI Search to host definitions for many agents.

For this example, there are 2 agents available, an "hr" agent and a "finance" agent.
Any requests that can not be classified as "hr" or "finance" will result in the conversation
ending with a Termination message.

"""

import asyncio
import logging
import os

from super_agent..agents._worker_agents import UserProxyAgent, WorkerAgent
from ._semantic_router_agent import SemanticRouterAgent
from ._semantic_router_components import (
    AgentRegistryBase,
    FinalResult,
    IntentClassifierBase,
)
from autogen import config_list_from_json
from autogen.agentchat.contrib.gpt_assistant_agent import GPTAssistantAgent
from autogen_core import ClosureAgent, ClosureContext, DefaultSubscription, DefaultTopicId, MessageContext
from autogen_ext.runtimes.grpc import GrpcWorkerAgentRuntime
from autogen_agentchat.messages import TextMessage



from super_agent..agents.httpwokers import HTTPWorkerAgent

# Setup logging for better observability
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("semantic_router")


# Singleton Factory for Config Loading
class ConfigLoader:
    """Loads and caches OpenAI assistant configuration."""
    _config_list = None

    @classmethod
    def get_openai_config(cls, config_path="./app/openai_assistant_config.json"):
        if cls._config_list is None:
            if not os.path.exists(config_path):
                raise FileNotFoundError(f"Config file not found: {config_path}")
            cls._config_list = config_list_from_json(config_path)
        return {"config_list": cls._config_list}


# Factory Pattern for Creating Agents
class AgentFactory:
    """Handles agent creation dynamically."""
    AGENT_TYPES = {
        "finance_intent": "finance",
        "hr_intent": "hr",
        "search_intent" : "search",
        "general": "search"
    }

    @classmethod
    def create_agent_registry(cls) -> AgentRegistryBase:
        """Creates an agent registry dynamically."""
        return AgentRegistry(cls.AGENT_TYPES)

    @classmethod
    def create_intent_classifier(cls, agent_registry: AgentRegistryBase) -> IntentClassifierBase:
        """Creates an LLM-based intent classifier using OpenAI Assistant."""
        return LLMIntentClassifier(agent_registry)


# Agent Registry
class AgentRegistry(AgentRegistryBase):
    """Manages available agents and their descriptions."""
    def __init__(self, agents: dict):
        self.agents = agents

    async def get_agent(self, intent: str) -> str:
        return self.agents.get(intent, "general")  # Fallback to "general" if intent not found
    
    async def get_agent_descriptions(self) -> dict:
        return self.agents

    def register_agent(self, intent: str, agent: WorkerAgent):
        self.agents[intent] = agent.name


class LLMIntentClassifier(IntentClassifierBase):
    """Routes user messages to the correct department using GPTAssistantAgent."""
    
    def __init__(self, agent_registry: AgentRegistryBase):
        self.agent_registry = agent_registry
        self.routing_agent = GPTAssistantAgent(
            name="routing_agent",
            instructions=self._generate_system_prompt(),
            llm_config=ConfigLoader.get_openai_config(),
            assistant_config={}
        )

    def _generate_system_prompt(self) -> str:
        """Generates an optimized system prompt for accurate intent classification."""
        agent_descriptions = {
            "finance_intent": "finance, money, budget, bank, invest",
            "hr_intent": "job hunting, hire people, HR, interview.",
            "search_intent": "find, search, response, answer"
        }

        agent_list = "\n".join([f"- **{intent}**: {description}" for intent, description in agent_descriptions.items()])

        return f"""
    You are an AI assistant responsible for classifying user intent based on their message. Below are the available intents and their corresponding descriptions:

    {agent_list}

    ### Classification Rules:
    1. Carefully analyze the user's message and determine which intent matches the message based on keywords and context.
    2. If the message contains words directly related to finance or HR, classify it accordingly.
    3. If the user's message does not clearly match any of the available intents, classify it as **'general'**.

    ### Output Format:
    Respond with only the **intent name**:
    - finance_intent
    - hr_intent
    - search_intent
    - general

    ### Examples:
    - **User Message**: "How should I invest my savings?"  
    **Response**: finance_intent

    - **User Message**: "I'm looking for job opportunities."  
    **Response**: hr_intent

    - **User Message**: "What's the weather like today?"  
    **Response**: general

    User's message: "{{message}}"
    Intent:
    """


    async def classify_intent(self, message: str) -> str:
        """Uses GPTAssistantAgent to classify the intent of a message."""
        # Create the request payload for GPT
        # Disable the internal memory
        self.routing_agent.reset()

        request = {"content": message.strip(), "role": "user"}

        response = self.routing_agent.generate_reply(messages=[request])

        # Handle coroutine responses
        if asyncio.iscoroutine(response):
            response = await response

    
        if isinstance(response, dict):
            intent = response.get("content", "general").strip().lower()
            return intent
        else:
            raise TypeError(f"Unexpected response type: {type(response)}, expected dict")



# Output Handler
async def output_result(closure_ctx: ClosureContext, message: TextMessage | FinalResult, ctx: MessageContext) -> None:
    """Handles user interactions and outputs results."""
    logger.info(f"{message.source} Agent: {message.content}")

    if isinstance(message, TextMessage):
        new_message = input("User response: ").strip()
        await closure_ctx.publish_message(
            TextMessage(content=new_message, source="user"),
            topic_id=DefaultTopicId(type=message.source, source="user"),
        )
    else:
        logger.info("Conversation ended.")
        new_message = input("Enter a new conversation start: ").strip()
        await closure_ctx.publish_message(
            TextMessage(content=new_message, source="user"),
            topic_id=DefaultTopicId(type="default", source="user"),
        )


async def main():
    """Initializes and runs the semantic routing system."""
    agent_runtime = GrpcWorkerAgentRuntime(host_address="localhost:50051")

    if not hasattr(agent_runtime, "start"):
        raise AttributeError("GrpcWorkerAgentRuntime is missing a start() method!")

    logger.info("Starting agent runtime...")

    # Create and Register Agent Registry
    agent_registry = AgentFactory.create_agent_registry()

    # Initialize HTTP Worker for streaming responses
    http_worker = HTTPWorkerAgent(
        name="http_worker",
        api_url="your_api_endpoint_here"  # Replace with your actual API endpoint
    )

    # Register the HTTP worker with your agent registry
    agent_registry.register_agent("search_intent", http_worker)

    # Register User Proxy Agent
    await UserProxyAgent.register(agent_runtime, "user_proxy", lambda: UserProxyAgent("user_proxy"))
    await agent_runtime.add_subscription(DefaultSubscription(topic_type="user_proxy", agent_type="user_proxy"))

    # Register Closure Agent (Final Result Handler)
    await ClosureAgent.register_closure(
        agent_runtime,
        "closure_agent",
        output_result,
        subscriptions=lambda: [DefaultSubscription(topic_type="response", agent_type="closure_agent")],
    )

    # Create and Register Semantic Router
    intent_classifier = AgentFactory.create_intent_classifier(agent_registry)
    await SemanticRouterAgent.register(
        agent_runtime,
        "router",
        lambda: SemanticRouterAgent(name="router", agent_registry=agent_registry, intent_classifier=intent_classifier),
    )

    try:
        # Start the runtime
        await agent_runtime.start()
        logger.info("Semantic router is running. Press Ctrl+C to exit.")
        
        # Keep the application running
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down semantic router...")
        await agent_runtime.stop()
    except Exception as e:
        logger.error(f"Error in semantic router: {e}")
        await agent_runtime.stop()
        raise


if __name__ == "__main__":
    asyncio.run(main())
