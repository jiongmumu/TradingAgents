#!/usr/bin/env python3
"""
Script to run LangGraph dev server for visualizing the TradingAgents project in LangChain Studio.
"""

import os
import sys
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode

def create_dev_graph():
    """Create a simplified graph for development visualization."""
    
    # Create a custom config for dev
    config = DEFAULT_CONFIG.copy()
    config["deep_think_llm"] = "gpt-4o-mini"  # Use a faster model for dev
    config["quick_think_llm"] = "gpt-4o-mini"
    config["max_debate_rounds"] = 1
    config["online_tools"] = False  # Disable online tools for dev
    
    # Initialize the trading graph
    ta = TradingAgentsGraph(
        selected_analysts=["market", "news"],  # Use fewer analysts for dev
        debug=True, 
        config=config
    )
    
    return ta.graph

def main():
    """Main function to run LangGraph dev server."""
    
    print("🚀 Starting LangGraph Dev Server for TradingAgents...")
    print("📊 This will allow you to visualize your graph in LangChain Studio")
    print("🌐 Open http://localhost:8123 in your browser")
    print("📝 Press Ctrl+C to stop the server")
    print()
    
    # Create the graph
    graph = create_dev_graph()
    
    # Create a memory saver for checkpointing
    memory = MemorySaver()
    
    # Start the dev server
    try:
        from langgraph.dev import dev_server
        
        # Run the dev server
        dev_server(
            graph,
            port=8123,
            memory=memory,
            open_browser=True
        )
        
    except KeyboardInterrupt:
        print("\n🛑 LangGraph Dev Server stopped by user")
    except Exception as e:
        print(f"❌ Error running LangGraph dev server: {e}")
        print("💡 Make sure you have the latest version of langgraph installed:")
        print("   pip install --upgrade langgraph")

if __name__ == "__main__":
    main() 