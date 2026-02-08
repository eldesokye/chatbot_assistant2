import streamlit as st
import asyncio
import json
from datetime import datetime
from typing import Dict, Any

from config import settings
from agents import agent
from api_client import api_client
from prompts import QUICK_RESPONSES, FOLLOW_UP_QUESTIONS
from utils.validators import validate_query

# Page configuration
st.set_page_config(
    page_title="Retail Analytics Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        animation: fadeIn 0.5s;
    }
    .user-message {
        background-color: #E3F2FD;
        border-left: 4px solid #1E88E5;
    }
    .bot-message {
        background-color: #F5F5F5;
        border-left: 4px solid #4CAF50;
    }
    .quick-action {
        transition: transform 0.2s;
    }
    .quick-action:hover {
        transform: translateY(-2px);
    }
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "agent_initialized" not in st.session_state:
        st.session_state.agent_initialized = False
    
    if "conversation_started" not in st.session_state:
        st.session_state.conversation_started = False
    
    if "backend_status" not in st.session_state:
        st.session_state.backend_status = "unknown"

def initialize_agent():
    """Initialize the LangChain agent"""
    if not st.session_state.agent_initialized:
        with st.spinner("🤖 Initializing AI agent..."):
            try:
                agent.initialize_executor()
                st.session_state.agent_initialized = True
                st.success("✅ Agent initialized successfully!")
            except Exception as e:
                st.error(f"❌ Failed to initialize agent: {str(e)}")

def check_backend_health():
    """Check backend API health"""
    with st.spinner("🔍 Checking backend connection..."):
        try:
            health = api_client.check_backend_health()
            st.session_state.backend_status = health.get("status", "unknown")
            return health
        except Exception as e:
            st.session_state.backend_status = "error"
            return {"status": "error", "error": str(e)}

def display_sidebar():
    """Display sidebar with controls and info"""
    with st.sidebar:
        st.title("⚙️ Control Panel")
        
        # Backend Status
        st.subheader("Backend Status")
        health = check_backend_health()
        
        if health.get("status") == "healthy":
            st.success(f"✅ Connected to: {settings.BACKEND_API_URL}")
            if "tables_available" in health:
                st.caption(f"📊 Tables: {len(health['tables_available'])} available")
        else:
            st.error("❌ Backend Unavailable")
            if "error" in health:
                st.caption(f"Error: {health['error']}")
        
        st.divider()
        
        # Agent Controls
        st.subheader("Agent Controls")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Reset Chat", use_container_width=True):
                st.session_state.messages = []
                agent.clear_memory()
                st.rerun()
        
        with col2:
            if st.button("📊 Test Connection", use_container_width=True):
                test_connection()
        
        # Model Settings
        st.divider()
        st.subheader("Model Settings")
        
        model_name = st.selectbox(
            "Select Model",
            ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"],
            index=0
        )
        
        temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=1.0,
            value=settings.CHATBOT_TEMPERATURE,
            step=0.1
        )
        
        # Quick Actions
        st.divider()
        st.subheader("🚀 Quick Actions")
        
        quick_actions = [
            ("👥 Visitor Count", "How many visitors are in the store now?"),
            ("📍 Busiest Section", "Which section is the busiest right now?"),
            ("⏳ Cashier Queue", "What's the current cashier queue status?"),
            ("🌡️ Store Heatmap", "Show me the store heatmap"),
            ("📈 Daily Report", "Give me today's performance report"),
            ("🔮 Traffic Forecast", "Predict traffic for the next hour")
        ]
        
        for emoji, query in quick_actions:
            if st.button(
                f"{emoji} {query.split('?')[0]}",
                use_container_width=True,
                key=f"quick_{emoji}"
            ):
                process_user_query(query)
        
        # Export Chat
        st.divider()
        if st.button("💾 Export Conversation", use_container_width=True):
            export_conversation()

def test_connection():
    """Test connection to backend endpoints"""
    test_results = {}
    
    with st.spinner("Running connection tests..."):
        endpoints = [
            ("Health", "/health"),
            ("Visitors", "/api/visitors/current"),
            ("Cashier", "/api/cashier/current"),
            ("Heatmap", "/api/heatmap/")
        ]
        
        for name, endpoint in endpoints:
            try:
                response = api_client._make_request(endpoint)
                test_results[name] = "✅ Success" if response else "❌ No data"
            except Exception as e:
                test_results[name] = f"❌ Error: {str(e)[:50]}"
    
    # Display results
    st.info("### Connection Test Results")
    for name, result in test_results.items():
        st.write(f"**{name}**: {result}")

def export_conversation():
    """Export conversation history"""
    if not st.session_state.messages:
        st.warning("No conversation to export")
        return
    
    export_data = {
        "exported_at": datetime.now().isoformat(),
        "backend_url": settings.BACKEND_API_URL,
        "chatbot_name": settings.CHATBOT_NAME,
        "messages": st.session_state.messages
    }
    
    # Create downloadable JSON
    json_str = json.dumps(export_data, indent=2, ensure_ascii=False)
    
    st.download_button(
        label="📥 Download Conversation",
        data=json_str,
        file_name=f"retail_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json"
    )

async def process_user_query(query: str):
    """Process user query with the agent"""
    # Validate query
    is_valid, error_msg = validate_query(query)
    if not is_valid:
        st.error(f"Invalid query: {error_msg}")
        return
    
    # Add user message to chat
    st.session_state.messages.append({
        "role": "user",
        "content": query,
        "timestamp": datetime.now().isoformat()
    })
    
    # Process with agent
    with st.spinner("🤔 Analyzing store data..."):
        try:
            response = await agent.process_query(query)
            
            # Add bot response to chat
            st.session_state.messages.append({
                "role": "assistant",
                "content": response.get("response", "No response"),
                "sources": response.get("sources", []),
                "confidence": response.get("confidence", 0.5),
                "timestamp": response.get("timestamp")
            })
            
        except Exception as e:
            error_response = {
                "role": "assistant",
                "content": f"❌ Error processing query: {str(e)}",
                "error": True,
                "timestamp": datetime.now().isoformat()
            }
            st.session_state.messages.append(error_response)

def display_chat_messages():
    """Display chat messages"""
    chat_container = st.container()
    
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                # Display message content
                st.markdown(message["content"])
                
                # Display metadata
                cols = st.columns([4, 1])
                with cols[0]:
                    if "timestamp" in message:
                        timestamp = datetime.fromisoformat(message["timestamp"])
                        st.caption(timestamp.strftime("%H:%M:%S"))
                
                with cols[1]:
                    if message["role"] == "assistant" and "confidence" in message:
                        confidence = message["confidence"]
                        color = "green" if confidence > 0.7 else "orange" if confidence > 0.4 else "red"
                        st.markdown(f"<span style='color:{color}'>Confidence: {confidence:.0%}</span>", 
                                   unsafe_allow_html=True)
                
                # Display sources if available
                if message["role"] == "assistant" and "sources" in message and message["sources"]:
                    with st.expander("📊 Data Sources"):
                        for source in message["sources"]:
                            st.caption(f"• {source}")

def display_main_interface():
    """Display main chat interface"""
    # Header
    st.markdown(f"<h1 class='main-header'>🛍️ {settings.CHATBOT_NAME}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p class='sub-header'>Your AI assistant for retail store analytics</p>", unsafe_allow_html=True)
    
    # Welcome message if no conversation
    if not st.session_state.conversation_started and not st.session_state.messages:
        st.info(QUICK_RESPONSES["greeting"])
        st.session_state.conversation_started = True
    
    # Display chat messages
    display_chat_messages()
    
    # Chat input
    query = st.chat_input("Ask about your store analytics...")
    
    if query:
        # Process query asynchronously
        asyncio.run(process_user_query(query))
        st.rerun()
    
    # Follow-up suggestions
    if st.session_state.messages and len(st.session_state.messages) > 0:
        st.divider()
        st.subheader("💡 Suggested Follow-ups")
        
        cols = st.columns(3)
        for i, question in enumerate(FOLLOW_UP_QUESTIONS[:3]):
            with cols[i]:
                if st.button(question, use_container_width=True, key=f"followup_{i}"):
                    asyncio.run(process_user_query(question))
                    st.rerun()

def main():
    """Main application"""
    initialize_session_state()
    initialize_agent()
    
    # Layout
    display_sidebar()
    display_main_interface()

if __name__ == "__main__":
    main()