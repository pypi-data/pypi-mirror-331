import json
from typing import Optional
from ._semantic_router_components import IntentClassifierBase, IntentResponse
from .config_loader import ConfigLoader

from agentopera.agents.models.openai import OpenAIChatCompletionClient
from agentopera.core.models import (
    SystemMessage,
    UserMessage,
)

class LLMIntentClassifier(IntentClassifierBase):
    def __init__(self, agent_registry):
        self.agent_registry = agent_registry
        config = ConfigLoader.get_openai_config()
        
        # Extract the first config from the config_list
        openai_config = config["config_list"][0]
        self.client = OpenAIChatCompletionClient(
            model=openai_config["model"],
            api_key=openai_config["api_key"],
            temperature=openai_config["temperature"],
            max_tokens=10, # We only need a short response
            response_format=IntentResponse
        )
        self.system_prompt = self._generate_system_prompt()
        # self.routing_agent = GPTAssistantAgent(
        #     name="routing_agent",
        #     instructions=self._generate_system_prompt(),
        #     llm_config=ConfigLoader.get_openai_config(),
        #     assistant_config={}
        # )

    def _generate_system_prompt(self) -> str:
        """Generates an optimized system prompt for accurate intent classification."""
        agent_descriptions = {
            "finance_intent": "Handles any message that mentions finance-related topics, including the words: finance, money, budget, investment, banking, bank, saving, loans, or financial planning.",
            "hr_intent": "Handles any message related to human resources, including the words: hiring, job, recruitment, HR, interview, employee benefits, and workplace policies.",
            "search_intent": "Handles any message that involves searching for specific topics, definitions, or general knowledge inquiries, including: define, explain, meaning of, and facts about.",
            "deep_research_intent": "Handles any message that involves researching a specific topic, including: research, study, and explore.",
            "chat_intent": "Handles any message that involves basic LLM chat completion without using deep research or web search."
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
    - deep_research_intent
    - general
    - chat_intent

    ### Examples:
    - **User Message**: "How should I invest my savings?"  
    **Response**: finance_intent

    - **User Message**: "I'm looking for job opportunities."  
    **Response**: hr_intent

     - **User Message**: "What is Machine Learning."  
    **Response**: search_intent

    - **User Message**: "Research about the history of AI?"  
    **Response**: deep_research_intent

    - **User Message**: "What's the weather like today?"  
    **Response**: general
    
    - **User Message**: "Hi, nice to meet you!"  
    **Response**: chat_intent

    User's message: "{{message}}"
    Intent:
    """


    async def classify_intent(self, message: str, timeout: Optional[float] = 5.0) -> str:
        """Uses GPTAssistantAgent to classify the intent of a message."""
        # Create the request payload for GPT
        # Disable the internal memory
        try: 
            messages = [
                SystemMessage(content=self.system_prompt),
                UserMessage(content=message.strip(), source="user"),
            ]
            response = await self.client.create(messages=messages)
            json_content = json.loads(response.content)
            intent = IntentResponse(**json_content).intent.strip().lower()
            # return intent
            return "chat_intent"
        
        except Exception as e:
            print(f"Intent classification failed: {str(e)}")
            return "general" 
