# LangGraph Visualization Guide for TradingAgents

This guide explains how to visualize your TradingAgents project using LangGraph and LangChain Studio.

## 🎯 Overview

Your TradingAgents project uses LangGraph to create a multi-agent trading system with the following components:

- **Analysts**: Market, News, Social Media, and Fundamentals analysts
- **Researchers**: Bull and Bear researchers for investment debate
- **Managers**: Research Manager and Risk Manager
- **Trader**: Final trading decision maker
- **Risk Analysts**: Risky, Safe, and Neutral analysts for risk assessment

## 📊 Visualization Options

### Option 1: Local Graph Visualization (Recommended for Start)

Run the local visualization script to see the graph structure:

```bash
python visualize_graph.py
```

This will:
- Create a visual representation of your graph structure
- Save it as `trading_graph.png`
- Show the flow between different agents
- Display all 18 nodes and their connections

### Option 2: LangSmith Tracing (Recommended for Detailed Analysis)

For detailed tracing and visualization in LangChain Studio:

1. **Get a LangSmith API Key**:
   - Sign up at [https://smith.langchain.com](https://smith.langchain.com)
   - Get your API key from the settings

2. **Set up environment variables**:
   ```bash
   export LANGCHAIN_API_KEY="your-api-key-here"
   export LANGCHAIN_PROJECT="trading-agents-dev"
   export LANGCHAIN_TRACING_V2="true"
   ```

3. **Run with tracing**:
   ```bash
   python run_langchain_studio.py
   ```

4. **View in LangChain Studio**:
   - Open [https://smith.langchain.com](https://smith.langchain.com)
   - Navigate to your project
   - See detailed traces of each agent's execution

## 🔧 Graph Structure

Your TradingAgents graph has the following structure:

```
START
  ↓
Market Analyst → tools_market → Market Analyst → Msg Clear Market
  ↓
News Analyst → tools_news → News Analyst → Msg Clear News
  ↓
Fundamentals Analyst → tools_fundamentals → Fundamentals Analyst → Msg Clear Fundamentals
  ↓
Bull Researcher ↔ Bear Researcher
  ↓
Research Manager
  ↓
Trader
  ↓
Risky Analyst ↔ Safe Analyst ↔ Neutral Analyst
  ↓
Risk Judge
  ↓
END
```

## 🚀 Quick Start

1. **Test the setup**:
   ```bash
   python test_langgraph_dev.py
   ```

2. **Create local visualization**:
   ```bash
   python visualize_graph.py
   ```

3. **Run with LangSmith tracing** (requires API key):
   ```bash
   python run_langchain_studio.py
   ```

## 📋 Available Scripts

- `visualize_graph.py` - Creates local graph visualization
- `run_langchain_studio.py` - Runs with LangSmith tracing
- `test_langgraph_dev.py` - Tests the setup
- `run_langgraph_dev.py` - Alternative dev server (may not work with current LangGraph version)

## 🔍 Understanding the Visualization

### Node Types:
- **Analysts**: Market, News, Social Media, Fundamentals analysts
- **Tools**: Tool nodes for data retrieval (`tools_market`, `tools_news`, etc.)
- **Message Clear**: Cleanup nodes to prevent message overflow
- **Researchers**: Bull and Bear researchers for debate
- **Managers**: Research and Risk managers for decision making
- **Risk Analysts**: Risky, Safe, and Neutral analysts

### Edge Types:
- **Sequential**: Most edges show the flow from one agent to the next
- **Conditional**: Some edges are conditional based on agent decisions
- **Loopback**: Tool nodes loop back to their respective analysts

## 🛠️ Troubleshooting

### Common Issues:

1. **LangGraph dev module not found**:
   - The `langgraph.dev` module is not available in all versions
   - Use the LangSmith tracing approach instead

2. **Missing dependencies**:
   ```bash
   pip install matplotlib networkx
   ```

3. **API key issues**:
   - Make sure your OpenAI API key is set in `.env`
   - For LangSmith, ensure your API key is correctly set

4. **Graph creation errors**:
   - Check that all required environment variables are set
   - Ensure the project structure is correct

## 📈 Next Steps

1. **Explore the graph structure** using the local visualization
2. **Set up LangSmith** for detailed tracing and analysis
3. **Modify the graph** by editing the `setup.py` file
4. **Add new agents** by extending the existing structure
5. **Analyze performance** using LangSmith traces

## 🔗 Useful Links

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LangSmith Platform](https://smith.langchain.com)
- [LangChain Studio](https://studio.langchain.com)
- [TradingAgents Project](https://github.com/your-repo/tradingagents)

## 📝 Notes

- The current LangGraph version (0.4.10) doesn't include the `langgraph.dev` module
- Use LangSmith tracing for the most detailed visualization
- Local visualization is great for understanding the graph structure
- The graph can be modified by changing the `selected_analysts` parameter 