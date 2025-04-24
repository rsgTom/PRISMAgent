"""
PRISMAgent Streamlit UI
----------------------

A simple web interface for interacting with PRISMAgent.
"""

import os
import streamlit as st
from typing import Dict, Any, Optional

from PRISMAgent.engine.factory import agent_factory
from PRISMAgent.engine.runner import runner_factory
from PRISMAgent.tools.spawn import spawn_agent
from PRISMAgent.config import OPENAI_API_KEY

# Load custom CSS
def load_css():
    css_file = os.path.join(os.path.dirname(__file__), "style.css")
    if os.path.exists(css_file):
        with open(css_file) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Load CSS
load_css()

# Page config
st.set_page_config(
    page_title="PRISMAgent",
    page_icon="🚀",
    layout="wide",
)

# Title and description
st.title("PRISMAgent 🚀")
st.markdown(
    """
    *A modular, multi-agent framework with plug-and-play storage, tools, and UIs.*
    
    Use this interface to interact with agents and spawn specialized agents for specific tasks.
    """
)

# Check for API key
if not OPENAI_API_KEY:
    st.error("⚠️ OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
    st.stop()

# Sidebar for agent configuration
with st.sidebar:
    st.header("Agent Configuration")
    
    # Agent type selection
    agent_type = st.selectbox(
        "Agent Type",
        ["assistant", "coder", "researcher"],
        help="Select the type of agent to interact with",
    )
    
    # Model selection
    model = st.selectbox(
        "Model",
        ["gpt-o3-mini", "gpt-4.1"],
        help="Select the model to use",
    )
    
    # Task complexity
    complexity = st.selectbox(
        "Task Complexity",
        ["auto", "basic", "advanced"],
        help="Select the complexity level for the task",
    )
    
    # System prompt
    system_prompt = st.text_area(
        "System Prompt",
        value="You are a helpful AI assistant.",
        help="Custom instructions for the agent",
    )

# Main chat interface
st.header("Chat Interface")

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("What would you like help with?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get agent response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # Create or get agent
            agent_name = f"{agent_type}_agent"
            agent = agent_factory(
                name=agent_name,
                instructions=system_prompt,
                tools=[spawn_agent],  # Allow agent to spawn other agents
            )
            
            # Create runner
            runner = runner_factory(stream=False)
            
            # Get response
            response = runner.run(agent, prompt)
            
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.markdown(response)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center'>
        <p>Made with ❤️ using PRISMAgent</p>
    </div>
    """,
    unsafe_allow_html=True,
) 