from langchain_community.tools.tavily_search import TavilySearchResults
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def test_tavily_search():
    """Run a simple test of the TavilySearchResults tool."""
    # Check for API key
    if not os.getenv("TAVILY_API_KEY"):
        print("🔴 TAVILY_API_KEY not found. Please set it in your .env file.")
        return

    print("Initializing TavilySearchResults...")
    search = TavilySearchResults()
    
    # --- Example 1: Basic Search ---
    print("\n--- Running Basic Search ---")
    query1 = "What is the latest news on Apple stock?"
    print(f"Query: {query1}")
    results1 = search.invoke(query1)
    print("Results:")
    print(results1)
    
    # --- Example 2: More Specific Query ---
    print("\n--- Running Specific Query ---")
    query2 = "Latest advancements in AI for financial trading"
    print(f"Query: {query2}")
    results2 = search.invoke(query2)
    print("Results:")
    print(results2)

if __name__ == "__main__":
    test_tavily_search() 