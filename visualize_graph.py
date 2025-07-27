#!/usr/bin/env python3
"""
Script to visualize the TradingAgents graph structure locally.
"""

import os
import sys
from dotenv import load_dotenv
from pathlib import Path
import networkx as nx
import matplotlib.pyplot as plt

# Load environment variables
load_dotenv()

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

def create_graph_visualization():
    """Create a visual representation of the trading agents graph."""
    
    print("🎨 Creating graph visualization...")
    
    try:
        # Create a minimal config
        config = DEFAULT_CONFIG.copy()
        config["deep_think_llm"] = "gpt-4o-mini"
        config["quick_think_llm"] = "gpt-4o-mini"
        config["online_tools"] = False
        
        # Create the graph
        ta = TradingAgentsGraph(
            selected_analysts=["market", "news", "fundamentals"],
            debug=True,
            config=config
        )
        
        # Create a NetworkX graph for visualization
        G = nx.DiGraph()
        
        # Add nodes
        for node in ta.graph.nodes:
            G.add_node(node)
        
        # Add edges based on the graph structure
        # This is a simplified representation of the actual graph flow
        edges = [
            ("START", "Market Analyst"),
            ("Market Analyst", "tools_market"),
            ("tools_market", "Market Analyst"),
            ("Market Analyst", "Msg Clear Market"),
            ("Msg Clear Market", "News Analyst"),
            ("News Analyst", "tools_news"),
            ("tools_news", "News Analyst"),
            ("News Analyst", "Msg Clear News"),
            ("Msg Clear News", "Fundamentals Analyst"),
            ("Fundamentals Analyst", "tools_fundamentals"),
            ("tools_fundamentals", "Fundamentals Analyst"),
            ("Fundamentals Analyst", "Msg Clear Fundamentals"),
            ("Msg Clear Fundamentals", "Bull Researcher"),
            ("Bull Researcher", "Bear Researcher"),
            ("Bear Researcher", "Research Manager"),
            ("Research Manager", "Trader"),
            ("Trader", "Risky Analyst"),
            ("Risky Analyst", "Safe Analyst"),
            ("Safe Analyst", "Neutral Analyst"),
            ("Neutral Analyst", "Risk Judge"),
            ("Risk Judge", "END"),
        ]
        
        for edge in edges:
            if edge[0] in G.nodes and edge[1] in G.nodes:
                G.add_edge(edge[0], edge[1])
        
        # Create the visualization
        plt.figure(figsize=(16, 12))
        
        # Use a hierarchical layout
        pos = nx.spring_layout(G, k=3, iterations=50)
        
        # Draw nodes
        nx.draw_networkx_nodes(G, pos, node_color='lightblue', 
                              node_size=3000, alpha=0.8)
        
        # Draw edges
        nx.draw_networkx_edges(G, pos, edge_color='gray', 
                              arrows=True, arrowsize=20, alpha=0.6)
        
        # Draw labels
        nx.draw_networkx_labels(G, pos, font_size=8, font_weight='bold')
        
        plt.title("TradingAgents Graph Structure", fontsize=16, fontweight='bold')
        plt.axis('off')
        
        # Save the visualization
        output_file = "trading_graph.png"
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.show()
        
        print(f"✅ Graph visualization saved as {output_file}")
        print(f"📊 Graph has {len(G.nodes)} nodes and {len(G.edges)} edges")
        
        # Print node information
        print("\n📋 Graph nodes:")
        for node in sorted(G.nodes):
            print(f"   - {node}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating visualization: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function."""
    
    print("🎨 TradingAgents Graph Visualization")
    print("=" * 50)
    
    # Check if matplotlib is available
    try:
        import matplotlib
        print("✅ Matplotlib is available")
    except ImportError:
        print("❌ Matplotlib not found. Installing...")
        os.system("pip install matplotlib networkx")
        print("✅ Matplotlib installed")
    
    # Create the visualization
    success = create_graph_visualization()
    
    if success:
        print("\n🎉 Visualization completed successfully!")
        print("💡 You can also use LangSmith for more detailed tracing:")
        print("   python run_langchain_studio.py")
    else:
        print("\n❌ Visualization failed. Please check the error messages above.")

if __name__ == "__main__":
    main() 