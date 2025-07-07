#!/usr/bin/env python3
"""
Slack Token Validator
Quick script to test your Slack configuration
"""

import os
import sys
sys.path.append('.')

from config.settings import settings
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

def validate_token():
    """Validate Slack token and show detailed information"""
    print("🔍 Slack Token Validator")
    print("=" * 30)
    
    # Check if token exists
    token = settings.SLACK_BOT_TOKEN
    if not token:
        print("❌ No SLACK_BOT_TOKEN found in .env file")
        return False
    
    # Check token format
    print(f"📝 Token format: {token[:20]}...")
    
    if token.startswith('xoxb-'):
        print("✅ Token type: Bot User OAuth Token (correct)")
    elif token.startswith('xapp-'):
        print("❌ Token type: App-Level Token (wrong - need Bot token)")
        print("💡 You need a Bot User OAuth Token starting with 'xoxb-'")
        return False
    elif token.startswith('xoxp-'):
        print("❌ Token type: User OAuth Token (wrong - need Bot token)")
        print("💡 You need a Bot User OAuth Token starting with 'xoxb-'")
        return False
    else:
        print("❌ Unknown token type")
        return False
    
    # Test connection
    print("\n🔗 Testing connection...")
    try:
        client = WebClient(token=token)
        response = client.auth_test()
        
        print("✅ Connection successful!")
        print(f"📱 Bot Name: {response.get('user', 'Unknown')}")
        print(f"🏢 Team: {response.get('team', 'Unknown')}")
        print(f"🆔 User ID: {response.get('user_id', 'Unknown')}")
        
        return True
        
    except SlackApiError as e:
        print(f"❌ Slack API Error: {e.response['error']}")
        
        error_code = e.response['error']
        if error_code == 'invalid_auth':
            print("💡 This usually means:")
            print("   - Token is incorrect or expired")
            print("   - Wrong token type (need xoxb- Bot token)")
            print("   - App not properly installed")
        elif error_code == 'account_inactive':
            print("💡 The Slack workspace may be inactive")
        elif error_code == 'token_revoked':
            print("💡 The token has been revoked - regenerate it")
        
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def validate_channel():
    """Validate channel access"""
    print("\n📺 Testing channel access...")
    
    channel_id = settings.SLACK_CHANNEL_ID
    if not channel_id:
        print("❌ No SLACK_CHANNEL_ID found in .env file")
        return False
    
    print(f"🆔 Channel ID: {channel_id}")
    
    try:
        client = WebClient(token=settings.SLACK_BOT_TOKEN)
        
        # Test channel info
        response = client.conversations_info(channel=channel_id)
        channel_info = response.get('channel', {})
        
        print(f"✅ Channel found: #{channel_info.get('name', 'Unknown')}")
        print(f"📝 Channel type: {channel_info.get('purpose', {}).get('value', 'No description')}")
        
        # Test message history access
        history_response = client.conversations_history(
            channel=channel_id,
            limit=1
        )
        
        print("✅ Can read message history")
        
        return True
        
    except SlackApiError as e:
        error_code = e.response['error']
        print(f"❌ Channel Error: {error_code}")
        
        if error_code == 'channel_not_found':
            print("💡 Channel not found - check the channel ID")
        elif error_code == 'not_in_channel':
            print("💡 Bot is not in the channel - invite it with:")
            print(f"   /invite @YourBotName in #{channel_id}")
        elif error_code == 'missing_scope':
            print("💡 Missing required permissions:")
            print("   - Add 'channels:history' scope")
            print("   - Add 'channels:read' scope")
            print("   - Reinstall the app")
        
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Run all validations"""
    token_valid = validate_token()
    
    if token_valid:
        channel_valid = validate_channel()
        
        if channel_valid:
            print("\n🎉 All validations passed!")
            print("✅ Ready to run: python main.py")
        else:
            print("\n⚠️  Token works but channel access failed")
            print("📖 See SLACK_SETUP.md for troubleshooting")
    else:
        print("\n❌ Token validation failed")
        print("📖 See SLACK_SETUP.md for setup instructions")

if __name__ == "__main__":
    main()
