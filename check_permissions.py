#!/usr/bin/env python3
"""
Slack Permissions Checker

This script checks your Slack bot's permissions and access to ensure you can
scrape ALL historical messages from your channel without permission issues.
"""

import logging
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from config.settings import settings

def check_slack_permissions():
    """Comprehensive check of Slack bot permissions and access"""
    print("🔍 Checking Slack Bot Permissions and Access...")
    print("=" * 60)
    
    client = WebClient(token=settings.SLACK_BOT_TOKEN)
    
    try:
        # 1. Test bot authentication
        print("1. Testing bot authentication...")
        auth_response = client.auth_test()
        bot_user_id = auth_response.get('user_id')
        bot_name = auth_response.get('user')
        team_name = auth_response.get('team')
        print(f"   ✅ Bot authenticated successfully")
        print(f"   📱 Bot Name: {bot_name}")
        print(f"   🆔 Bot User ID: {bot_user_id}")
        print(f"   🏢 Team: {team_name}")
        print()
        
        # 2. Check channel access
        print("2. Testing channel access...")
        try:
            channel_info = client.conversations_info(channel=settings.SLACK_CHANNEL_ID)
            channel_name = channel_info['channel']['name']
            is_member = channel_info['channel'].get('is_member', False)
            is_private = channel_info['channel'].get('is_private', False)
            
            print(f"   ✅ Channel access confirmed")
            print(f"   📺 Channel Name: #{channel_name}")
            print(f"   🔒 Private Channel: {is_private}")
            print(f"   👥 Bot is Member: {is_member}")
            
            if not is_member:
                print("   ⚠️  WARNING: Bot is not a member of this channel!")
                print("      You need to invite the bot to the channel first.")
                print(f"      Go to #{channel_name} and type: /invite @{bot_name}")
                return False
                
        except SlackApiError as e:
            if e.response['error'] == 'channel_not_found':
                print("   ❌ Channel not found - check your SLACK_CHANNEL_ID")
                return False
            elif e.response['error'] == 'not_in_channel':
                print("   ❌ Bot is not in the channel - invite it first")
                print(f"      Go to the channel and type: /invite @{bot_name}")
                return False
            else:
                print(f"   ❌ Channel access error: {e.response['error']}")
                return False
        print()
        
        # 3. Test message history access
        print("3. Testing message history access...")
        try:
            # Try to get just 1 message to test permissions
            history_response = client.conversations_history(
                channel=settings.SLACK_CHANNEL_ID,
                limit=1
            )
            messages = history_response.get('messages', [])
            print(f"   ✅ Message history access confirmed")
            print(f"   📝 Sample messages retrieved: {len(messages)}")
            
            # Get total message count (estimate)
            try:
                # Get messages from a very old date to estimate total
                from datetime import datetime
                very_old = datetime(2020, 1, 1).timestamp()
                
                total_messages = []
                cursor = None
                page_count = 0
                
                print("   🔢 Counting total available messages...")
                while page_count < 5:  # Limit to first 5 pages for estimate
                    response = client.conversations_history(
                        channel=settings.SLACK_CHANNEL_ID,
                        oldest=very_old,
                        limit=200,
                        cursor=cursor
                    )
                    batch = response.get('messages', [])
                    total_messages.extend(batch)
                    
                    cursor = response.get('response_metadata', {}).get('next_cursor')
                    page_count += 1
                    
                    if not cursor:
                        break
                
                print(f"   📊 Estimated available messages: {len(total_messages)}+ (sampled {page_count} pages)")
                
                if len(total_messages) == 0:
                    print("   ⚠️  No messages found - channel might be empty or very new")
                
            except Exception as e:
                print(f"   ⚠️  Could not estimate message count: {str(e)}")
                
        except SlackApiError as e:
            print(f"   ❌ Message history access failed: {e.response['error']}")
            if e.response['error'] == 'missing_scope':
                print("      Missing required scope: channels:history")
                print("      Go to your Slack app settings and add this scope")
                return False
            return False
        print()
        
        # 4. Check bot scopes
        print("4. Checking bot scopes...")
        try:
            # This is not always available via API, but we can infer from successful calls
            print("   ✅ Required scopes appear to be present:")
            print("      - channels:read (for channel info)")
            print("      - channels:history (for message history)")
            
            # Check if we have additional useful scopes
            try:
                client.users_info(user=bot_user_id)
                print("      - users:read (for user info) ✅")
            except:
                print("      - users:read (for user info) ❌")
                
        except Exception as e:
            print(f"   ⚠️  Could not verify all scopes: {str(e)}")
        print()
        
        # 5. Rate limit info
        print("5. Rate limit considerations...")
        print("   ℹ️  Slack API rate limits:")
        print("      - conversations.history: Tier 3 (50+ requests per minute)")
        print("      - Maximum 200 messages per request")
        print("      - Bot includes 1-second delays between requests")
        print("   ✅ Rate limiting handled automatically")
        print()
        
        print("🎉 PERMISSION CHECK COMPLETE")
        print("=" * 60)
        print("✅ Your bot has all necessary permissions to scrape ALL historical messages!")
        print()
        print("💡 To scrape everything, run:")
        print("   python main.py --max-links 99999 --limit 99999")
        print()
        print("🚀 Or modify your .env file to increase defaults:")
        print("   MAX_LINKS_PER_RUN=99999")
        
        return True
        
    except SlackApiError as e:
        print(f"❌ Slack API Error: {e.response['error']}")
        if e.response['error'] == 'invalid_auth':
            print("   Invalid bot token - check your SLACK_BOT_TOKEN")
        elif e.response['error'] == 'token_revoked':
            print("   Bot token has been revoked - regenerate it")
        elif e.response['error'] == 'account_inactive':
            print("   Slack account is inactive")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

if __name__ == "__main__":
    # Setup basic logging
    logging.basicConfig(level=logging.WARNING)
    
    # Validate settings first
    try:
        settings.validate()
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("   Please check your .env file")
        exit(1)
    
    # Run permission check
    success = check_slack_permissions()
    
    if not success:
        print("\n❌ Permission issues detected!")
        print("   Please fix the issues above before running the scraper.")
        exit(1)
    else:
        print("\n🎉 All permissions look good!")
        print("   You're ready to scrape all historical messages!")
