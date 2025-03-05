from .intent_classifier import LLMIntentClassifier
from ._semantic_router_components import AgentRegistryBase

class AgentFactory:
    AGENT_TYPES = {
        "finance_intent": "finance",
        "hr_intent": "hr",
        "search_intent": "search",
        "deep_research_intent": "deep_research",
        "general": "search",
        "chat_intent": "chat",
    }

    @classmethod
    def create_agent_registry(cls) -> AgentRegistryBase:
        return AgentRegistry(cls.AGENT_TYPES)

    @classmethod
    def create_intent_classifier(cls, agent_registry: AgentRegistryBase) -> LLMIntentClassifier:
        return LLMIntentClassifier(agent_registry)

class AgentRegistry(AgentRegistryBase):
    def __init__(self, agents: dict):
        self.agents = agents

    async def get_agent(self, intent: str) -> str:
        return self.agents.get(intent, "general")
