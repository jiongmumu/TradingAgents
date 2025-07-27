from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

def test_env_loading():
    """Test if environment variables are loaded correctly."""
    print("Testing environment variable loading...")
    
    # Check if OPENAI_API_KEY is loaded
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        print(f"✅ OPENAI_API_KEY is loaded: {api_key[:10]}...")
    else:
        print("❌ OPENAI_API_KEY is not loaded")
    
    # Check other potential environment variables
    finnhub_key = os.getenv("FINNHUB_API_KEY")
    if finnhub_key:
        print(f"✅ FINNHUB_API_KEY is loaded: {finnhub_key[:10]}...")
    else:
        print("ℹ️  FINNHUB_API_KEY is not set (optional)")
    
    # List all environment variables that start with common prefixes
    print("\nAll environment variables:")
    for key, value in os.environ.items():
        if any(prefix in key.upper() for prefix in ['OPENAI', 'FINNHUB', 'REDDIT', 'API']):
            print(f"  {key}: {value[:10] if value else 'None'}...")

if __name__ == "__main__":
    test_env_loading() 