#!/usr/bin/env python3
"""
Setup script for AI Link Scraper
Helps with initial configuration and environment setup
"""

import os
import shutil
import subprocess
import sys

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def create_directories():
    """Create necessary directories"""
    directories = ['logs', 'summaries']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def setup_environment():
    """Setup environment file"""
    env_example = '.env.example'
    env_file = '.env'
    
    if not os.path.exists(env_file):
        if os.path.exists(env_example):
            shutil.copy(env_example, env_file)
            print(f"✅ Created {env_file} from {env_example}")
            print(f"📝 Please edit {env_file} with your API keys and configuration")
        else:
            print(f"❌ {env_example} not found")
            return False
    else:
        print(f"✅ {env_file} already exists")
    
    return True

def install_dependencies():
    """Install Python dependencies"""
    try:
        print("📦 Installing dependencies...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def display_setup_instructions():
    """Display setup instructions"""
    print("\n" + "="*60)
    print("🎉 SETUP COMPLETE!")
    print("="*60)
    print("\n📋 Next Steps:")
    print("1. Edit the .env file with your API keys:")
    print("   - SLACK_BOT_TOKEN: Your Slack bot token")
    print("   - SLACK_CHANNEL_ID: Your target Slack channel ID")
    print("   - OPENAI_API_KEY: Your OpenAI API key")
    print("\n2. Set up your Slack bot:")
    print("   - Go to https://api.slack.com/apps")
    print("   - Create a new app")
    print("   - Add bot token scopes: channels:history, channels:read, users:read")
    print("   - Install the app to your workspace")
    print("\n3. Run the scraper:")
    print("   python main.py")
    print("\n4. Optional: Run with custom parameters:")
    print("   python main.py --start-date 2024-01-01 --limit 50")
    print("\n📖 For more details, see README.md")

def main():
    """Main setup function"""
    print("🚀 AI Link Scraper Setup")
    print("=" * 30)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Setup environment file
    if not setup_environment():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Display instructions
    display_setup_instructions()

if __name__ == "__main__":
    main()
