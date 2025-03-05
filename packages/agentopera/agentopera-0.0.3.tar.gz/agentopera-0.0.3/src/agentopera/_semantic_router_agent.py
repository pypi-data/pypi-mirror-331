
from autogen_agentchat.messages import TextMessage
    
from ._semantic_router_components import AgentRegistryBase, IntentClassifierBase, TerminationMessage
from autogen_core import (
    DefaultTopicId,
    MessageContext,
    RoutedAgent,
    message_handler,
)

from .utils.logger import logger


class SemanticRouterAgent(RoutedAgent):
    def __init__(self, name: str, agent_registry: AgentRegistryBase, intent_classifier: IntentClassifierBase) -> None:
        super().__init__("Semantic Router Agent")
        self._name = name
        self._registry = agent_registry
        self._classifier = intent_classifier

    # The User has sent a message that needs to be routed
    @message_handler
    async def route_to_agent(self, message: TextMessage, ctx: MessageContext) -> None:
        assert ctx.topic_id is not None
        logger.info(f"Received message from {message.source}: {message.content}")
        session_id = ctx.topic_id.source
       # print(f"***************** session_id is {session_id} ****************")
        intent = await self._identify_intent(message)
        #print(f"***************** for {message} intent is {intent} ****************")
        agent_type = await self._find_agent(intent)
       # print(f"***************** agent is {agent} ****************")
        logger.info(f"Router =================================> agent_type = {agent_type}, session_id = {session_id}")
        await self.contact_agent(agent_type, message, ctx, session_id)


    ## Identify the intent of the user message
    async def _identify_intent(self, message: TextMessage) -> str:
        return await self._classifier.classify_intent(message.content)

    ## Use a lookup, search, or LLM to identify the most relevant agent for the intent
    async def _find_agent(self, intent: str) -> str:
        logger.debug(f"Identified intent: {intent}")
        try:
            agent = await self._registry.get_agent(intent)
            return agent
        except KeyError:
            logger.debug("No relevant agent found for intent: " + intent)
            return "termination"

    ## Forward user message to the appropriate agent, or end the thread.
    async def contact_agent(self, agent_type: str, message: TextMessage, ctx: MessageContext, session_id: str) -> None:
        if agent_type == "termination":
            logger.debug("No relevant agent found")
            await self.publish_message(
                TerminationMessage(reason="No relevant agent found", content=message.content, source=self.type),
                DefaultTopicId(type="user_proxy", source=session_id),
                message_id=ctx.message_id,
            )
        else:
            logger.info("Routing to agent_type {}, content = {}".format(agent_type, message.content))
            await self.publish_message(
                TextMessage(content=message.content, source=message.source),
                DefaultTopicId(type=agent_type, source=session_id),
                message_id=ctx.message_id,
            )
            logger.info("publish_message is done for agent_type {}, message_id = {}".format(agent_type, ctx.message_id))
