import logging
import time
import os
from datetime import datetime, timedelta
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from config.settings import settings
from src.utils import extract_urls_from_text

logger = logging.getLogger(__name__)

class SlackClient:
    def __init__(self):
        """Initialize Slack client with bot token"""
        self.client = WebClient(token=settings.SLACK_BOT_TOKEN)
        self.channel_id = settings.SLACK_CHANNEL_ID
        
    def get_channel_messages(self, start_date=None, end_date=None, limit=None):
        """Fetch messages from the specified Slack channel"""
        try:
            # Convert dates to timestamps if provided
            oldest = None
            latest = None
            
            if start_date:
                oldest = start_date.timestamp()
            if end_date:
                latest = end_date.timestamp()
            
            # If no dates provided, get messages from last 7 days
            if not oldest and not latest:
                week_ago = datetime.now() - timedelta(days=7)
                oldest = week_ago.timestamp()
            
            logger.info(f"Fetching messages from channel {self.channel_id}")
            
            messages = []
            cursor = None
            
            while True:
                try:
                    response = self.client.conversations_history(
                        channel=self.channel_id,
                        oldest=oldest,
                        latest=latest,
                        limit=min(limit or 200, 200),  # Slack API limit is 200
                        cursor=cursor
                    )
                    
                    batch_messages = response.get('messages', [])
                    messages.extend(batch_messages)
                    
                    logger.info(f"Retrieved {len(batch_messages)} messages")
                    
                    # Check if we have more messages to fetch
                    cursor = response.get('response_metadata', {}).get('next_cursor')
                    if not cursor or (limit and len(messages) >= limit):
                        break
                        
                    # Respect rate limits
                    time.sleep(1)
                    
                except SlackApiError as e:
                    logger.error(f"Error fetching messages: {e.response['error']}")
                    break
            
            if limit:
                messages = messages[:limit]
                
            logger.info(f"Total messages retrieved: {len(messages)}")
            return messages
            
        except Exception as e:
            logger.error(f"Error in get_channel_messages: {str(e)}")
            return []
    
    def extract_links_from_messages(self, messages):
        """Extract all URLs from Slack messages"""
        links_data = []
        
        for message in messages:
            # Skip bot messages and messages without text
            if message.get('bot_id') or not message.get('text'):
                continue
                
            text = message.get('text', '')
            urls = extract_urls_from_text(text)
            
            if urls:
                for url in urls:
                    link_data = {
                        'url': url,
                        'slack_message_id': message.get('ts'),
                        'message_text': text,
                        'user': message.get('user'),
                        'timestamp': datetime.fromtimestamp(float(message.get('ts', 0)))
                    }
                    links_data.append(link_data)
        
        logger.info(f"Extracted {len(links_data)} links from {len(messages)} messages")
        return links_data
    
    def get_channel_info(self):
        """Get information about the channel"""
        try:
            response = self.client.conversations_info(channel=self.channel_id)
            return response.get('channel', {})
        except SlackApiError as e:
            logger.error(f"Error getting channel info: {e.response['error']}")
            return {}
    
    def test_connection(self):
        """Test the Slack API connection"""
        try:
            response = self.client.auth_test()
            logger.info(f"Connected to Slack as: {response.get('user')}")
            return True
        except SlackApiError as e:
            logger.error(f"Slack connection failed: {e.response['error']}")
            return False
    
    def send_message(self, text, thread_ts=None):
        """Send a message to the channel"""
        try:
            response = self.client.chat_postMessage(
                channel=self.channel_id,
                text=text,
                thread_ts=thread_ts
            )
            logger.info(f"Message sent successfully: {response.get('ts')}")
            return response.get('ts')
        except SlackApiError as e:
            logger.error(f"Error sending message: {e.response['error']}")
            return None
    
    def send_summary_to_channel(self, summary_data, reply_to_message=True):
        """Send a formatted summary back to the Slack channel"""
        try:
            # Create formatted message
            message = self._format_summary_message(summary_data)
            
            # If replying to original message, use thread
            thread_ts = None
            if reply_to_message and summary_data.get('slack_message_id'):
                thread_ts = summary_data['slack_message_id']
            
            # Send the message
            message_ts = self.send_message(message, thread_ts)
            
            if message_ts:
                logger.info(f"Summary sent to channel for: {summary_data.get('title', 'Unknown')}")
                return message_ts
            else:
                logger.error(f"Failed to send summary for: {summary_data.get('title', 'Unknown')}")
                return None
                
        except Exception as e:
            logger.error(f"Error in send_summary_to_channel: {str(e)}")
            return None
    
    def _format_summary_message(self, summary_data):
        """Format summary data into a nice Slack message"""
        title = summary_data.get('title', 'Unknown Title')
        url = summary_data.get('url', '')
        summary = summary_data.get('summary', 'No summary available')
        tags = summary_data.get('tags', [])
        
        # Create a clean, simple message without formatting
        message = f"📄 {title}\n"
        message += f"🔗 {url}\n\n"
        message += f"{summary}\n\n"
        
        if tags:
            # Limit to 3 most relevant tags
            limited_tags = tags[:3]
            message += f"🏷️ {', '.join(limited_tags)}\n"
        
        message += f"🤖 AI Summary"
        
        return message
    
    def upload_file_to_channel(self, file_path, title=None, comment=None, thread_ts=None):
        """Upload a file to the Slack channel"""
        try:
            with open(file_path, 'rb') as file_content:
                response = self.client.files_upload_v2(
                    channel=self.channel_id,
                    file=file_content,
                    title=title or f"Summary - {os.path.basename(file_path)}",
                    initial_comment=comment,
                    thread_ts=thread_ts
                )
            
            logger.info(f"File uploaded successfully: {file_path}")
            return response.get('file', {}).get('id')
            
        except SlackApiError as e:
            logger.error(f"Error uploading file: {e.response['error']}")
            return None
        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error uploading file: {str(e)}")
            return None
    
    def send_summary_digest(self, summaries_folder, max_summaries=5):
        """Send a digest of recent summaries to the channel"""
        try:
            from src.summary_organizer import create_summary_digest
            
            digest = create_summary_digest(summaries_folder, max_summaries)
            
            # Send the digest
            message_ts = self.send_message(digest)
            
            if message_ts:
                logger.info(f"Summary digest sent to channel")
                return message_ts
            else:
                logger.error(f"Failed to send summary digest")
                return None
                
        except Exception as e:
            logger.error(f"Error in send_summary_digest: {str(e)}")
            return None
    
    def share_complete_summary_folder(self, summaries_folder):
        """Create and share a complete summary file to the channel"""
        try:
            from src.summary_organizer import create_shared_summary_folder
            
            # Create the consolidated markdown file
            output_file = create_shared_summary_folder(summaries_folder)
            
            if not output_file:
                logger.warning("No summaries found to share")
                return None
            
            # Upload to Slack
            comment = "📚 Complete Summary Collection - All scraped and summarized links in one place!"
            file_id = self.upload_file_to_channel(
                output_file,
                title="AI Link Summaries - Complete Collection",
                comment=comment
            )
            
            if file_id:
                logger.info(f"Complete summary folder shared successfully")
                return file_id
            else:
                logger.error(f"Failed to share summary folder")
                return None
                
        except Exception as e:
            logger.error(f"Error in share_complete_summary_folder: {str(e)}")
            return None
    
    def get_all_channels(self):
        """Get list of all channels the bot has access to"""
        try:
            response = self.client.conversations_list(
                types="public_channel,private_channel",
                limit=1000
            )
            channels = response.get('channels', [])
            logger.info(f"Found {len(channels)} accessible channels")
            return channels
        except SlackApiError as e:
            logger.error(f"Error getting channels: {e.response['error']}")
            return []
    
    def check_all_channels_for_mentions(self, limit=50):
        """Check all accessible channels for mentions and respond"""
        try:
            bot_user_id = self.get_bot_user_id()
            if not bot_user_id:
                logger.error("Could not get bot user ID")
                return 0
            
            channels = self.get_all_channels()
            total_mentions_processed = 0
            
            # Get recent messages (last 2 hours to catch mentions)
            from datetime import datetime, timedelta
            two_hours_ago = datetime.now() - timedelta(hours=2)
            
            for channel in channels:
                channel_id = channel['id']
                channel_name = channel.get('name', 'Unknown')
                
                logger.info(f"Checking channel #{channel_name} for mentions...")
                
                try:
                    # Temporarily switch to this channel
                    original_channel = self.channel_id
                    self.channel_id = channel_id
                    
                    # Get messages from this channel
                    messages = self.get_channel_messages(
                        start_date=two_hours_ago,
                        limit=limit
                    )
                    
                    channel_mentions = 0
                    for message in messages:
                        # Skip bot's own messages
                        if message.get('user') == bot_user_id:
                            continue
                        
                        message_text = message.get('text', '')
                        
                        if self.is_mention(message_text, bot_user_id):
                            logger.info(f"Found mention in #{channel_name}: {message.get('ts')}")
                            self.respond_to_mention(message, bot_user_id)
                            channel_mentions += 1
                            total_mentions_processed += 1
                    
                    if channel_mentions > 0:
                        logger.info(f"Processed {channel_mentions} mentions in #{channel_name}")
                    
                    # Restore original channel
                    self.channel_id = original_channel
                    
                except Exception as e:
                    logger.error(f"Error checking channel #{channel_name}: {str(e)}")
                    # Restore original channel on error
                    self.channel_id = original_channel
                    continue
            
            logger.info(f"Total mentions processed across all channels: {total_mentions_processed}")
            return total_mentions_processed
            
        except Exception as e:
            logger.error(f"Error checking all channels for mentions: {str(e)}")
            return 0

    def get_bot_user_id(self):
        """Get the bot's user ID for mention detection"""
        try:
            response = self.client.auth_test()
            return response.get('user_id')
        except SlackApiError as e:
            logger.error(f"Error getting bot user ID: {e.response['error']}")
            return None
    
    def is_mention(self, message_text, bot_user_id=None):
        """Check if the message mentions the bot"""
        if not bot_user_id:
            bot_user_id = self.get_bot_user_id()
        
        if not bot_user_id:
            return False
        
        # Check for direct user ID mention
        mention_pattern = f"<@{bot_user_id}>"
        if mention_pattern in message_text:
            return True
        
        # Check for @ailinkscraper mention (case insensitive)
        if "@ailinkscraper" in message_text.lower():
            return True
        
        return False
    
    def respond_to_mention(self, message, bot_user_id=None):
        """Process a mention and respond with link summaries"""
        try:
            message_text = message.get('text', '')
            message_ts = message.get('ts')
            
            logger.info(f"Processing mention in message: {message_text[:100]}...")
            
            # Extract URLs from the mentioned message
            from src.utils import extract_urls_from_text
            urls = extract_urls_from_text(message_text)
            
            if not urls:
                # No links in mention, provide helpful response
                response = "👋 Hi! I'm your AI Link Scraper bot.\\n\\n" \
                          "📝 **How to use me:**\\n" \
                          "• Share a link and mention @ailinkscraper to get an instant summary\\n" \
                          "• I automatically process all links every Monday at 1 PM\\n" \
                          "• Check threaded replies for summaries\\n\\n" \
                          "💡 Try: @ailinkscraper https://example.com/article"
                
                self.send_message(response, thread_ts=message_ts)
                return
            
            # Process each URL mentioned
            from src.web_scraper import WebScraper
            from src.summarizer import Summarizer
            
            scraper = WebScraper()
            summarizer = Summarizer()
            
            for url in urls:
                logger.info(f"Processing mentioned URL: {url}")
                
                # Scrape the URL
                scraped_data = scraper.scrape_url(url)
                
                if scraped_data and scraped_data.get('status') == 'success':
                    # Generate summary
                    summary = summarizer.summarize_content(
                        scraped_data['content'],
                        scraped_data.get('title'),
                        scraped_data.get('url')
                    )
                    
                    # Generate tags
                    tags = summarizer.generate_tags(
                        scraped_data['content'],
                        scraped_data.get('title')
                    )
                    
                    # Format summary data
                    summary_data = {
                        'url': url,
                        'title': scraped_data.get('title'),
                        'summary': summary,
                        'tags': tags,
                        'word_count': scraped_data.get('word_count', 0),
                        'slack_message_id': message_ts
                    }
                    
                    # Send summary as threaded reply
                    self.send_summary_to_channel(summary_data, reply_to_message=True)
                    
                    # Save summary to file
                    from src.utils import save_summary_to_file
                    save_summary_to_file(summary_data, 'summaries')
                    
                    logger.info(f"Successfully processed mention for URL: {url}")
                    
                else:
                    # Failed to scrape
                    error_message = f"❌ Sorry, I couldn't access or process this link: {url}\\n" \
                                   f"The site might be down, require authentication, or block automated access."
                    self.send_message(error_message, thread_ts=message_ts)
            
        except Exception as e:
            logger.error(f"Error processing mention: {str(e)}")
            error_response = "❌ Sorry, I encountered an error processing your request. Please try again later."
            self.send_message(error_response, thread_ts=message.get('ts'))
    
    def check_for_mentions(self, limit=50):
        """Check recent messages for mentions and respond"""
        try:
            bot_user_id = self.get_bot_user_id()
            if not bot_user_id:
                logger.error("Could not get bot user ID")
                return
            
            # Get recent messages (last hour)
            from datetime import datetime, timedelta
            one_hour_ago = datetime.now() - timedelta(hours=1)
            
            messages = self.get_channel_messages(
                start_date=one_hour_ago,
                limit=limit
            )
            
            mentions_processed = 0
            
            for message in messages:
                # Skip bot's own messages
                if message.get('user') == bot_user_id:
                    continue
                
                message_text = message.get('text', '')
                
                if self.is_mention(message_text, bot_user_id):
                    logger.info(f"Found mention in message: {message.get('ts')}")
                    self.respond_to_mention(message, bot_user_id)
                    mentions_processed += 1
            
            logger.info(f"Processed {mentions_processed} mentions")
            return mentions_processed
            
        except Exception as e:
            logger.error(f"Error checking for mentions: {str(e)}")
            return 0
