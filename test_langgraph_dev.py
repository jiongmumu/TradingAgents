#!/usr/bin/env python3
"""
Simple test script to verify LangGraph dev setup.
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

def test_graph_creation():
    """Test that we can create the graph successfully."""
    
    print("🧪 Testing graph creation...")
    
    try:
        # Create a minimal config
        config = DEFAULT_CONFIG.copy()
        config["deep_think_llm"] = "gpt-4o-mini"
        config["quick_think_llm"] = "gpt-4o-mini"
        config["online_tools"] = False
        
        # Create the graph with minimal analysts
        ta = TradingAgentsGraph(
            selected_analysts=["market"],  # Just one analyst for testing
            debug=True,
            config=config
        )
        
        print("✅ Graph created successfully!")
        print(f"📊 Graph has {len(ta.graph.nodes)} nodes")
        print(f"🔗 Graph has {len(ta.graph.edges)} edges")
        
        # List the nodes
        print("\n📋 Graph nodes:")
        for node in ta.graph.nodes:
            print(f"   - {node}")
            
        return True
        
    except Exception as e:
        print(f"❌ Error creating graph: {e}")
        return False

def test_langgraph_dev_import():
    """Test that langgraph.dev can be imported."""
    
    print("\n🧪 Testing langgraph.dev import...")
    
    try:
        from langgraph.dev import dev_server
        print("✅ langgraph.dev imported successfully!")
        return True
    except ImportError as e:
        print(f"❌ Error importing langgraph.dev: {e}")
        print("💡 Try installing langgraph with dev extras:")
        print("   pip install 'langgraph[dev]'")
        return False

def main():
    """Main test function."""
    
    print("🚀 Testing LangGraph Dev Setup for TradingAgents")
    print("=" * 50)
    
    # Test imports
    import_success = test_langgraph_dev_import()
    
    # Test graph creation
    graph_success = test_graph_creation()
    
    print("\n" + "=" * 50)
    if import_success and graph_success:
        print("🎉 All tests passed! You can now run:")
        print("   python run_langgraph_dev.py")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
    
    return import_success and graph_success

if __name__ == "__main__":
    main() 