#!/usr/bin/env python3
"""
Setup script for LangSmith configuration to enable input/output visualization.
"""

import os
import sys
from pathlib import Path
import getpass

def check_env_file():
    """Check if .env file exists and has required variables."""
    
    env_file = Path(".env")
    
    if not env_file.exists():
        print("❌ .env file not found")
        return False
    
    print("✅ .env file found")
    
    # Read existing variables
    existing_vars = {}
    if env_file.exists():
        with open(env_file, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    existing_vars[key] = value
    
    return existing_vars

def setup_langsmith_key():
    """Setup LangSmith API key."""
    
    print("\n🔑 LangSmith API Key Setup")
    print("=" * 40)
    
    print("To get your LangSmith API key:")
    print("1. Go to https://smith.langchain.com")
    print("2. Sign up or log in")
    print("3. Go to Settings → API Keys")
    print("4. Create a new API key")
    print()
    
    # Get API key from user
    api_key = getpass.getpass("Enter your LangSmith API key (input will be hidden): ")
    
    if not api_key:
        print("❌ No API key provided")
        return False
    
    # Validate API key format (basic check)
    if not api_key.startswith("ls_"):
        print("⚠️  Warning: LangSmith API keys typically start with 'ls_'")
        print("   Please verify your API key is correct")
    
    return api_key

def update_env_file(api_key):
    """Update .env file with LangSmith configuration."""
    
    env_file = Path(".env")
    
    # Read existing content
    lines = []
    if env_file.exists():
        with open(env_file, "r") as f:
            lines = f.readlines()
    
    # Variables to add/update
    langsmith_vars = {
        "LANGCHAIN_API_KEY": api_key,
        "LANGCHAIN_TRACING_V2": "true",
        "LANGCHAIN_ENDPOINT": "https://api.smith.langchain.com",
        "LANGCHAIN_PROJECT": "trading-agents-io"
    }
    
    # Update existing lines or add new ones
    updated_lines = []
    existing_keys = set()
    
    for line in lines:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key = line.split("=", 1)[0]
            existing_keys.add(key)
            
            if key in langsmith_vars:
                # Update existing variable
                updated_lines.append(f"{key}={langsmith_vars[key]}\n")
                del langsmith_vars[key]
            else:
                # Keep existing variable
                updated_lines.append(line + "\n")
        else:
            # Keep comments and empty lines
            updated_lines.append(line + "\n")
    
    # Add new variables
    for key, value in langsmith_vars.items():
        updated_lines.append(f"{key}={value}\n")
    
    # Write back to file
    with open(env_file, "w") as f:
        f.writelines(updated_lines)
    
    print(f"✅ Updated {env_file} with LangSmith configuration")

def test_langsmith_connection():
    """Test the LangSmith connection."""
    
    print("\n🧪 Testing LangSmith Connection")
    print("=" * 40)
    
    try:
        # Set environment variables
        from dotenv import load_dotenv
        load_dotenv()
        
        if not os.getenv("LANGCHAIN_API_KEY"):
            print("❌ LANGCHAIN_API_KEY not found in environment")
            return False
        
        # Test basic import
        import langsmith
        print("✅ LangSmith package imported successfully")
        
        # Test client creation
        client = langsmith.Client()
        print("✅ LangSmith client created successfully")
        
        # Test API connection
        try:
            # Try to list projects (this will test the API key)
            projects = list(client.list_projects(limit=1))
            print("✅ LangSmith API connection successful")
            return True
        except Exception as e:
            print(f"❌ LangSmith API connection failed: {e}")
            return False
            
    except ImportError:
        print("❌ LangSmith package not installed")
        print("💡 Installing langsmith...")
        os.system("pip install langsmith")
        return False
    except Exception as e:
        print(f"❌ Error testing LangSmith: {e}")
        return False

def main():
    """Main setup function."""
    
    print("🎯 LangSmith Setup for TradingAgents I/O Visualization")
    print("=" * 60)
    
    # Check existing environment
    existing_vars = check_env_file()
    
    # Check if LangSmith is already configured
    if "LANGCHAIN_API_KEY" in existing_vars:
        print("✅ LangSmith API key already configured")
        response = input("Do you want to update it? (y/N): ").lower()
        if response != 'y':
            print("Using existing configuration")
            return
    
    # Setup LangSmith API key
    api_key = setup_langsmith_key()
    if not api_key:
        return
    
    # Update .env file
    update_env_file(api_key)
    
    # Test connection
    if test_langsmith_connection():
        print("\n🎉 LangSmith setup completed successfully!")
        print("\n🚀 You can now run:")
        print("   python run_langchain_studio_detailed.py")
        print("\n📊 This will show detailed input/output in LangChain Studio")
    else:
        print("\n❌ LangSmith setup failed. Please check your API key and try again.")

if __name__ == "__main__":
    main() 