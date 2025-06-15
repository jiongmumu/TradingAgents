from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
import graphviz

# Set up custom configuration
config = DEFAULT_CONFIG.copy()
config.update({
    "deep_think_llm": "gpt-4.1-nano",
    "quick_think_llm": "gpt-4.1-nano",
    "max_debate_rounds": 1,
    "online_tools": True
})

# Initialize the trading graph
graph = TradingAgentsGraph(config=config, debug=True)

# Get the compiled state graph
compiled_graph = graph.graph
# Get the underlying networkx graph
nx_graph = compiled_graph.get_graph()

# Create a new directed graph
dot = graphviz.Digraph(comment='Trading Agents Graph')
dot.attr(rankdir='LR')  # Left to right layout

# Add nodes with different styles based on their type
for node in nx_graph.nodes:
    if "analyst" in node.lower():
        dot.node(node, node, shape='box', style='filled', fillcolor='lightblue')
    elif "researcher" in node.lower():
        dot.node(node, node, shape='box', style='filled', fillcolor='lightgreen')
    elif "manager" in node.lower():
        dot.node(node, node, shape='box', style='filled', fillcolor='lightyellow')
    elif "clear" in node.lower():
        dot.node(node, node, shape='diamond', style='filled', fillcolor='lightgrey')
    else:
        dot.node(node, node, shape='box')

# Add edges
for edge in nx_graph.edges:
    dot.edge(edge[0], edge[1])

# Save the visualization
dot.render('trading_graph', format='png', cleanup=True)
print("Graph visualization has been saved as 'trading_graph.png'") 