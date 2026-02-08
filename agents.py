from typing import List, Dict, Any
from langchain.agents import AgentExecutor, create_structured_chat_agent
from langchain.memory import ConversationBufferMemory
from langchain.prompts import MessagesPlaceholder
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_openai import ChatOpenAI
from config import settings
from tools import tools
from prompts import SYSTEM_PROMPT

class RetailAgent:
    """Main agent for retail analytics chatbot"""
    
    def __init__(self, use_openrouter: bool = False):
        self.use_openrouter = use_openrouter
        self.llm = self._initialize_llm()
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="output"
        )
        self.agent = self._create_agent()
        self.agent_executor = None
        
    def _initialize_llm(self):
        """Initialize the LLM with appropriate configuration"""
        if self.use_openrouter and settings.OPENROUTER_API_KEY:
            return ChatOpenAI(
                model=settings.MODEL_NAME,
                temperature=settings.CHATBOT_TEMPERATURE,
                openai_api_key=settings.OPENROUTER_API_KEY,
                openai_api_base=settings.OPENROUTER_BASE_URL
            )
        elif settings.OPENAI_API_KEY:
            return ChatOpenAI(
                model=settings.MODEL_NAME,
                temperature=settings.CHATBOT_TEMPERATURE,
                openai_api_key=settings.OPENAI_API_KEY
            )
        else:
            raise ValueError("No API key provided for LLM")
    
    def _create_agent(self):
        """Create the structured chat agent"""
        prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            HumanMessagePromptTemplate.from_template("{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        agent = create_structured_chat_agent(
            llm=self.llm,
            tools=tools,
            prompt=prompt
        )
        
        return agent
    
    def initialize_executor(self):
        """Initialize the agent executor"""
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=tools,
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=10,
            early_stopping_method="generate",
            return_intermediate_steps=True
        )
        
        return self.agent_executor
    
    async def process_query(self, query: str) -> Dict[str, Any]:
        """Process a user query asynchronously"""
        if not self.agent_executor:
            self.initialize_executor()
        
        try:
            result = await self.agent_executor.ainvoke({"input": query})
            
            # Format the response
            response = {
                "query": query,
                "response": result.get("output", "No response generated"),
                "sources": self._extract_sources(result),
                "timestamp": datetime.now().isoformat(),
                "confidence": self._calculate_confidence(result)
            }
            
            return response
            
        except Exception as e:
            return {
                "query": query,
                "response": f"Sorry, I encountered an error: {str(e)}",
                "error": True,
                "timestamp": datetime.now().isoformat()
            }
    
    def _extract_sources(self, result: Dict) -> List[str]:
        """Extract tool sources from agent result"""
        sources = []
        if "intermediate_steps" in result:
            for step in result["intermediate_steps"]:
                if isinstance(step, tuple) and len(step) > 1:
                    tool_name = str(step[0].tool)
                    sources.append(tool_name)
        
        return list(set(sources))  # Remove duplicates
    
    def _calculate_confidence(self, result: Dict) -> float:
        """Calculate confidence score for response"""
        if "intermediate_steps" not in result or not result["intermediate_steps"]:
            return 0.5
        
        # Simple confidence calculation based on successful tool usage
        successful_steps = sum(1 for step in result["intermediate_steps"] 
                             if isinstance(step, tuple) and len(step) > 1)
        total_steps = len(result["intermediate_steps"])
        
        if total_steps == 0:
            return 0.5
        
        return min(0.9, 0.5 + (successful_steps / total_steps) * 0.4)
    
    def clear_memory(self):
        """Clear the conversation memory"""
        self.memory.clear()
        print("Memory cleared")
    
    def get_conversation_summary(self) -> str:
        """Get a summary of the conversation"""
        if not self.memory.buffer:
            return "No conversation history"
        
        messages = self.memory.buffer
        summary = f"Conversation Summary ({len(messages)} messages):\n\n"
        
        for i, msg in enumerate(messages, 1):
            role = "User" if msg.type == "human" else "Assistant"
            summary += f"{i}. {role}: {msg.content[:100]}...\n"
        
        return summary

# Global agent instance
agent = RetailAgent()