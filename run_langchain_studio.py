#!/usr/bin/env python3
"""
Script to run TradingAgents with LangSmith tracing for visualization in LangChain Studio.
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

def setup_langsmith():
    """Setup LangSmith for tracing."""
    
    # Set LangSmith environment variables if not already set
    if not os.getenv("LANGCHAIN_TRACING_V2"):
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
    
    if not os.getenv("LANGCHAIN_ENDPOINT"):
        os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
    
    if not os.getenv("LANGCHAIN_API_KEY"):
        print("⚠️  LANGCHAIN_API_KEY not found in environment variables")
        print("💡 Please set your LangSmith API key:")
        print("   export LANGCHAIN_API_KEY='your-api-key-here'")
        print("   Or add it to your .env file")
        return False
    
    if not os.getenv("LANGCHAIN_PROJECT"):
        os.environ["LANGCHAIN_PROJECT"] = "trading-agents-dev"
    
    return True

def run_trading_agents_with_tracing():
    """Run the trading agents with LangSmith tracing."""
    
    print("🚀 Starting TradingAgents with LangSmith tracing...")
    print("📊 This will allow you to visualize your graph in LangChain Studio")
    print("🌐 Open https://smith.langchain.com to view traces")
    print()
    
    # Setup LangSmith
    if not setup_langsmith():
        print("❌ LangSmith setup failed. Please check your API key.")
        return
    
    try:
        # Create a custom config for development
        config = DEFAULT_CONFIG.copy()
        config["deep_think_llm"] = "gpt-4o-mini"
        config["quick_think_llm"] = "gpt-4o-mini"
        config["max_debate_rounds"] = 1
        config["online_tools"] = False  # Disable online tools for faster execution
        
        print("🔧 Creating TradingAgents graph...")
        
        # Initialize with minimal analysts for faster execution
        ta = TradingAgentsGraph(
            selected_analysts=["market", "news"],  # Use fewer analysts for dev
            debug=True, 
            config=config
        )
        
        print("✅ Graph created successfully!")
        print(f"📊 Graph has {len(ta.graph.nodes)} nodes")
        
        # List the nodes
        print("\n📋 Graph nodes:")
        for node in ta.graph.nodes:
            print(f"   - {node}")
        
        print("\n🔄 Running trading agents with tracing...")
        print("💡 Check https://smith.langchain.com for the trace")
        
        # Run the graph with a test company
        final_state, decision = ta.propagate("AAPL", "2025-07-28")
        
        print(f"\n🎯 Final decision: {decision}")
        print("✅ Execution completed! Check LangSmith for detailed traces.")
        
    except Exception as e:
        print(f"❌ Error running trading agents: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main function."""
    
    print("🎯 TradingAgents LangSmith Tracing Setup")
    print("=" * 50)
    
    # Check if we have the required environment variables
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  OPENAI_API_KEY not found")
        print("💡 Please set your OpenAI API key in your .env file")
        return
    
    # Run the trading agents with tracing
    run_trading_agents_with_tracing()

if __name__ == "__main__":
    main() 