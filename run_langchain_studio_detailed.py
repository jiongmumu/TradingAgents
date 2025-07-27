#!/usr/bin/env python3
"""
Detailed script to run TradingAgents with comprehensive LangSmith tracing 
for input/output visualization in LangChain Studio.
"""

import os
import sys
from dotenv import load_dotenv
from pathlib import Path
import json
from datetime import datetime

# Load environment variables
load_dotenv()

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

def setup_langsmith():
    """Setup LangSmith for detailed tracing."""
    
    print("🔧 Setting up LangSmith for detailed tracing...")
    
    # Set LangSmith environment variables
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
    os.environ["LANGCHAIN_PROJECT"] = f"trading-agents-io-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    
    if not os.getenv("LANGCHAIN_API_KEY"):
        print("⚠️  LANGCHAIN_API_KEY not found in environment variables")
        print("💡 Please set your LangSmith API key:")
        print("   export LANGCHAIN_API_KEY='your-api-key-here'")
        print("   Or add it to your .env file")
        return False
    
    print(f"✅ LangSmith project: {os.environ['LANGCHAIN_PROJECT']}")
    return True

def create_detailed_config():
    """Create a configuration optimized for detailed tracing."""
    
    config = DEFAULT_CONFIG.copy()
    
    # Use faster models for quicker execution
    config["deep_think_llm"] = "gpt-4o-mini"
    config["quick_think_llm"] = "gpt-4o-mini"
    
    # Reduce complexity for clearer tracing
    config["max_debate_rounds"] = 1
    config["max_risk_discuss_rounds"] = 1
    
    # Disable online tools for faster execution
    config["online_tools"] = False
    
    return config

def run_detailed_tracing():
    """Run the trading agents with detailed input/output tracing."""
    
    print("🚀 Starting TradingAgents with Detailed I/O Tracing")
    print("=" * 60)
    
    # Setup LangSmith
    if not setup_langsmith():
        print("❌ LangSmith setup failed. Please check your API key.")
        return
    
    try:
        # Create configuration
        config = create_detailed_config()
        
        print("🔧 Creating TradingAgents graph with detailed tracing...")
        
        # Initialize with all analysts for comprehensive tracing
        ta = TradingAgentsGraph(
            selected_analysts=["market", "news", "fundamentals"],
            debug=True, 
            config=config
        )
        
        print("✅ Graph created successfully!")
        print(f"📊 Graph has {len(ta.graph.nodes)} nodes")
        
        # List all nodes for reference
        print("\n📋 Graph nodes (agents):")
        for i, node in enumerate(sorted(ta.graph.nodes), 1):
            print(f"   {i:2d}. {node}")
        
        print("\n🔄 Running trading agents with detailed I/O tracing...")
        print("💡 Check LangSmith for detailed input/output visualization:")
        print(f"   https://smith.langchain.com/o/{os.getenv('LANGCHAIN_ENDPOINT', 'default')}/projects/p/{os.environ['LANGCHAIN_PROJECT']}")
        print()
        
        # Test with a well-known company for better results
        test_company = "AAPL"
        test_date = "2024-01-15"
        
        print(f"📈 Analyzing {test_company} for {test_date}...")
        
        # Run the graph
        final_state, decision = ta.propagate(test_company, test_date)
        
        print(f"\n🎯 Final Decision: {decision}")
        print("✅ Execution completed!")
        
        # Print summary of what was captured
        print("\n📊 What was captured in LangSmith:")
        print("   • Input messages to each agent")
        print("   • Output responses from each agent")
        print("   • Tool calls and their results")
        print("   • State transitions between agents")
        print("   • Memory retrievals and updates")
        print("   • Conditional logic decisions")
        
        # Save final state for reference
        state_summary = {
            "company": test_company,
            "date": test_date,
            "final_decision": decision,
            "market_report": final_state.get("market_report", "")[:200] + "...",
            "news_report": final_state.get("news_report", "")[:200] + "...",
            "fundamentals_report": final_state.get("fundamentals_report", "")[:200] + "...",
            "investment_plan": final_state.get("investment_plan", "")[:200] + "...",
            "final_trade_decision": final_state.get("final_trade_decision", "")[:200] + "...",
        }
        
        with open("langsmith_trace_summary.json", "w") as f:
            json.dump(state_summary, f, indent=2)
        
        print(f"\n📄 Trace summary saved to: langsmith_trace_summary.json")
        
    except Exception as e:
        print(f"❌ Error running detailed tracing: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main function."""
    
    print("🎯 TradingAgents Detailed I/O Visualization")
    print("=" * 60)
    
    # Check required environment variables
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  OPENAI_API_KEY not found")
        print("💡 Please set your OpenAI API key in your .env file")
        return
    
    if not os.getenv("LANGCHAIN_API_KEY"):
        print("⚠️  LANGCHAIN_API_KEY not found")
        print("💡 Please get your LangSmith API key from:")
        print("   https://smith.langchain.com/settings")
        print("   Then set it as an environment variable:")
        print("   export LANGCHAIN_API_KEY='your-api-key-here'")
        return
    
    # Run the detailed tracing
    run_detailed_tracing()

if __name__ == "__main__":
    main() 