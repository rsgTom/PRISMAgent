"""
PRISMAgent Streamlit UI
-----------------------

A web interface for interacting with PRISMAgent.
"""

import os
import streamlit as st
from typing import Dict, Any, Optional, List, Tuple

from PRISMAgent.engine.factory import agent_factory
from PRISMAgent.engine.runner import runner_factory
from PRISMAgent.tools.spawn import spawn_agent
from PRISMAgent.tools.code_interpreter import code_interpreter
from PRISMAgent.tools.web_search import web_search, fetch_url
from PRISMAgent.config import OPENAI_API_KEY, SEARCH_API_KEY
from PRISMAgent.tools import list_available_tools

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
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
    
if "available_tools" not in st.session_state:
    st.session_state.available_tools = list_available_tools()
    
if "current_agent" not in st.session_state:
    st.session_state.current_agent = None
    
if "agents" not in st.session_state:
    st.session_state.agents = {}

if "chat_history" not in st.session_state:
    st.session_state.chat_history = {}

# Title and description
col1, col2 = st.columns([3, 1])
with col1:
    st.title("PRISMAgent 🔮")
    st.markdown(
        """
        *A modular, multi-agent framework with plug-and-play storage, tools, and UIs.*
        
        Use this interface to interact with agents and spawn specialized agents for specific tasks.
        """
    )

# Check for API keys
if not OPENAI_API_KEY:
    st.error("⚠️ OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
    st.stop()

# Sidebar for agent configuration
with st.sidebar:
    st.header("Agent Configuration")
    
    # Agent type selection
    agent_type = st.selectbox(
        "Agent Type",
        ["assistant", "coder", "researcher", "custom"],
        help="Select the type of agent to interact with",
    )
    
    # Agent name
    if agent_type == "custom":
        agent_name = st.text_input(
            "Agent Name",
            value="custom_agent",
            help="Enter a unique name for your custom agent"
        )
    else:
        agent_name = f"{agent_type}_agent"
    
    # Model selection
    model = st.selectbox(
        "Model",
        ["gpt-o3-mini", "gpt-4.1"],
        help="Select the model to use",
    )
    
    # System prompt
    system_prompt = st.text_area(
        "System Prompt",
        value=("You are a helpful AI assistant." if agent_type == "assistant" else
               "You are an expert programmer and software developer." if agent_type == "coder" else
               "You are a thorough researcher who provides detailed information." if agent_type == "researcher" else
               "You are a specialized AI agent."),
        help="Custom instructions for the agent",
    )
    
    # Available tools
    st.subheader("Available Tools")
    tool_options = ["spawn_agent", "code_interpreter", "web_search", "fetch_url"] + st.session_state.available_tools
    # Remove duplicates while preserving order
    tool_options = list(dict.fromkeys(tool_options))
    
    selected_tools = st.multiselect(
        "Tools",
        tool_options,
        default=["spawn_agent"],
        help="Select tools this agent can use"
    )
    
    # Set default tools based on agent type
    if agent_type == "coder":
        if "code_interpreter" not in selected_tools:
            selected_tools.append("code_interpreter")
            st.info("Added code_interpreter tool for the coder agent.")
            
    if agent_type == "researcher":
        if "web_search" not in selected_tools:
            selected_tools.append("web_search")
            st.info("Added web_search tool for the researcher agent.")
    
    # Advanced settings (collapsed by default)
    with st.expander("Advanced Settings"):
        stream_output = st.checkbox("Stream Output", value=True, 
                                 help="Enable streaming responses from the agent")
        
        max_tools_per_run = st.number_input(
            "Max Tools Per Run", 
            min_value=1, 
            max_value=10, 
            value=5,
            help="Maximum number of tool calls allowed per agent run"
        )
        
        memory_provider = st.selectbox(
            "Memory Provider",
            ["none", "in_memory", "redis", "database"],
            help="Choose how agent memory is stored"
        )
    
    # Create/update agent button
    if st.button("Create/Update Agent"):
        with st.spinner(f"Creating agent: {agent_name}..."):
            try:
                # Convert tool names to actual tool objects
                tool_list = []
                for tool_name in selected_tools:
                    if tool_name == "spawn_agent":
                        tool_list.append(spawn_agent)
                    elif tool_name == "code_interpreter":
                        tool_list.append(code_interpreter)
                    elif tool_name == "web_search":
                        tool_list.append(web_search)
                    elif tool_name == "fetch_url":
                        tool_list.append(fetch_url)
                
                # Create the agent
                agent = agent_factory(
                    name=agent_name,
                    instructions=system_prompt,
                    tools=tool_list if tool_list else None,
                )
                
                # Store in session state
                st.session_state.current_agent = agent_name
                st.session_state.agents[agent_name] = agent
                
                # Initialize or preserve chat history
                if agent_name not in st.session_state.chat_history:
                    st.session_state.chat_history[agent_name] = []
                
                # Set messages to current agent's history
                st.session_state.messages = st.session_state.chat_history[agent_name]
                
                st.success(f"Agent '{agent_name}' created successfully!")
            except Exception as e:
                st.error(f"Error creating agent: {str(e)}")
                
    # Agent selection (if multiple agents exist)
    if len(st.session_state.agents) > 0:
        st.subheader("Select Agent")
        agent_names = list(st.session_state.agents.keys())
        current_agent = st.selectbox(
            "Active Agent",
            agent_names,
            index=agent_names.index(st.session_state.current_agent) if st.session_state.current_agent in agent_names else 0
        )
        
        # Update current agent if changed
        if current_agent != st.session_state.current_agent:
            st.session_state.current_agent = current_agent
            st.session_state.messages = st.session_state.chat_history.get(current_agent, [])
            st.experimental_rerun()
        
        # Clear chat button
        if st.button("Clear Chat History"):
            st.session_state.chat_history[current_agent] = []
            st.session_state.messages = []
            st.experimental_rerun()

# Main chat interface
st.header("Chat Interface")

# Display agent info
if st.session_state.current_agent and st.session_state.current_agent in st.session_state.agents:
    current_agent = st.session_state.agents[st.session_state.current_agent]
    
    # Display available tools for the current agent
    tool_names = []
    if hasattr(current_agent, 'tools') and current_agent.tools:
        for tool in current_agent.tools:
            tool_name = getattr(tool, "__prism_name__", getattr(tool, "__name__", "unknown"))
            tool_names.append(tool_name)
    
    with st.expander("Current Agent Details", expanded=False):
        st.markdown(f"**Name:** {current_agent.name}")
        st.markdown(f"**Tools:** {', '.join(tool_names) if tool_names else 'None'}")
        st.markdown(f"**Instructions:** {current_agent.instructions}")

    # Add a visual indicator for the current agent
    st.info(f"Active Agent: **{current_agent.name}**")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("What would you like help with?"):
    # Ensure we have a current agent
    if not st.session_state.current_agent or st.session_state.current_agent not in st.session_state.agents:
        st.warning("Please create an agent first.")
        st.stop()
        
    # Get the current agent
    agent = st.session_state.agents[st.session_state.current_agent]
    
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.chat_history[st.session_state.current_agent] = st.session_state.messages
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get agent response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # Create runner
            runner = runner_factory(
                stream=stream_output if 'stream_output' in locals() else True,
                max_tools_per_run=max_tools_per_run if 'max_tools_per_run' in locals() else 5
            )
            
            # Create a placeholder for streaming output
            response_placeholder = st.empty()
            
            if stream_output if 'stream_output' in locals() else True:
                # Stream the response
                full_response = ""
                for event in runner.run_streamed(agent, prompt):
                    if hasattr(event, 'content') and event.content:
                        full_response += event.content
                        response_placeholder.markdown(full_response)
                
                # Add the complete response to chat history
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                st.session_state.chat_history[st.session_state.current_agent] = st.session_state.messages
            else:
                # Get non-streaming response
                response = runner.run(agent, prompt)
                
                # Add to chat history
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.session_state.chat_history[st.session_state.current_agent] = st.session_state.messages
                
                # Display response
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
