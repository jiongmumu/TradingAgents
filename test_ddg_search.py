from langchain_community.tools import DuckDuckGoSearchRun
from dotenv import load_dotenv
import os
import time

# Load environment variables (optional, but good practice)
load_dotenv()

def test_duckduckgo_search():
    """Run a simple test of the DuckDuckGoSearchRun tool."""
    print("Initializing DuckDuckGoSearchRun...")
    search = DuckDuckGoSearchRun()
    
    # --- Example 1: Basic Search ---
    print("\n--- Running Basic Search ---")
    query1 = "What is the latest news on Apple stock?"
    print(f"Query: {query1}")
    results1 = search.run(query1)
    print("Results:")
    print(results1)
    
    # Wait for a moment to avoid rate limiting
    print("\n...waiting to avoid rate limit...")
    time.sleep(5)

    # --- Example 2: More Specific Query ---
    print("\n--- Running Specific Query ---")
    query2 = "Latest advancements in AI for financial trading"
    print(f"Query: {query2}")
    results2 = search.run(query2)
    print("Results:")
    print(results2)

if __name__ == "__main__":
    test_duckduckgo_search() 