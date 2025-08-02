#!/usr/bin/env python3
"""
Setup script for Google GenAI configuration.
This script helps set up the necessary credentials for using Google's Gemini models.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

def setup_google_credentials():
    """Setup Google Cloud credentials for GenAI."""
    
    print("🔧 Google GenAI Setup")
    print("=" * 50)
    
    # Check if GOOGLE_API_KEY is set
    if os.getenv("GOOGLE_API_KEY"):
        print("✅ GOOGLE_API_KEY is already set")
        return True
    
    # Check if GOOGLE_APPLICATION_CREDENTIALS is set
    if os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        print("✅ GOOGLE_APPLICATION_CREDENTIALS is set")
        return True
    
    print("❌ No Google credentials found")
    print("\n🔑 You need to set up Google Cloud credentials:")
    print("\nOption 1: Set GOOGLE_API_KEY (Recommended for simple use)")
    print("   1. Go to https://makersuite.google.com/app/apikey")
    print("   2. Create a new API key")
    print("   3. Add to your .env file:")
    print("      GOOGLE_API_KEY=your_api_key_here")
    
    print("\nOption 2: Use Google Cloud Service Account (For advanced use)")
    print("   1. Go to https://console.cloud.google.com/")
    print("   2. Create a new project or select existing")
    print("   3. Enable the Generative Language API")
    print("   4. Create a service account and download the JSON key")
    print("   5. Set GOOGLE_APPLICATION_CREDENTIALS to the JSON file path")
    
    return False

def test_google_genai():
    """Test Google GenAI functionality."""
    
    print("\n🧪 Testing Google GenAI...")
    
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        print("✅ langchain_google_genai imported successfully")
        
        # Try to create a model instance
        llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
        print("✅ ChatGoogleGenerativeAI model created successfully")
        
        # Test a simple query
        response = llm.invoke("Hello, how are you?")
        print("✅ Google GenAI is working correctly!")
        print(f"Response: {response.content[:100]}...")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Try: pip install langchain-google-genai")
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if "credentials" in str(e).lower():
            print("💡 This is a credentials issue. Please set up Google Cloud credentials.")
        return False

def update_env_file():
    """Update .env file with Google configuration."""
    
    env_file = Path(".env")
    
    if not env_file.exists():
        print("📝 Creating .env file...")
        env_file.touch()
    
    # Read existing content
    with open(env_file, "r") as f:
        lines = f.readlines()
    
    # Check if GOOGLE_API_KEY already exists
    google_key_exists = any(line.startswith("GOOGLE_API_KEY=") for line in lines)
    
    if not google_key_exists:
        print("📝 Adding GOOGLE_API_KEY placeholder to .env file...")
        lines.append("\n# Google GenAI Configuration\n")
        lines.append("GOOGLE_API_KEY=your_google_api_key_here\n")
        
        with open(env_file, "w") as f:
            f.writelines(lines)
        
        print("✅ Added GOOGLE_API_KEY placeholder to .env file")
        print("💡 Please replace 'your_google_api_key_here' with your actual API key")
    else:
        print("✅ GOOGLE_API_KEY already exists in .env file")

def main():
    """Main setup function."""
    
    print("🎯 Google GenAI Setup for TradingAgents")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Check current setup
    if setup_google_credentials():
        print("\n✅ Google credentials are configured!")
    else:
        print("\n❌ Google credentials need to be configured")
        update_env_file()
        return
    
    # Test the setup
    if test_google_genai():
        print("\n🎉 Google GenAI setup completed successfully!")
        print("\n💡 You can now use Google's Gemini models in your trading agents")
        print("   Example: config['llm_provider'] = 'google'")
    else:
        print("\n❌ Google GenAI setup failed")
        print("💡 Please check your credentials and try again")

if __name__ == "__main__":
    main() 