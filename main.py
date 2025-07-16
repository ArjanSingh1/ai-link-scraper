import os
import argparse
from dotenv import load_dotenv
from src.slack_client import SlackClient
from src.web_scraper import WebScraper
from src.summarizer import Summarizer
from src.utils import save_summary_to_file, format_summary_data
from src.summary_organizer import create_shared_summary_folder
import logging

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def main():
    parser = argparse.ArgumentParser(description="Scrape and summarize all links from a Slack channel.")
    parser.add_argument('--channel', type=str, default=os.environ.get('SLACK_CHANNEL_ID'), help='Slack channel ID to scrape')
    parser.add_argument('--limit', type=int, default=200, help='Max messages to fetch')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    args = parser.parse_args()

    if not args.channel:
        print("❌ SLACK_CHANNEL_ID not set. Exiting.")
        return

    slack = SlackClient()
    scraper = WebScraper()
    summarizer = Summarizer()

    # Fetch messages from the channel
    messages = slack.get_channel_messages(limit=args.limit)
    print(f"[DEBUG] Fetched {len(messages)} messages from channel {args.channel}")
    if not messages:
        print("[ERROR] No messages found in the channel. Check SLACK_CHANNEL_ID and bot permissions.")
        return

    # Extract unique links
    unique_links = slack.extract_unique_links_from_messages(messages)
    print(f"[DEBUG] Found {len(unique_links)} unique links in channel")
    if not unique_links:
        print("[ERROR] No links found in channel messages. Nothing to scrape.")
        return

    # Summarize and save each link
    saved_count = 0
    for link_data in unique_links:
        url = link_data['url']
        print(f"Scraping: {url}")
        scraped = scraper.scrape_url(url)
        if scraped and scraped.get('status') == 'success':
            summary = summarizer.summarize_content(scraped['content'], scraped.get('title'), url)
            tags = summarizer.generate_tags(scraped['content'], scraped.get('title'))
            summary_data = format_summary_data(
                url=url,
                title=scraped.get('title'),
                summary=summary,
                slack_message_id=link_data.get('slack_message_id'),
                word_count=scraped.get('word_count', 0),
                tags=tags
            )
            save_summary_to_file(summary_data, 'summaries')
            print(f"✅ Saved summary for: {url}")
            saved_count += 1
        else:
            print(f"❌ Failed to scrape: {url}")

    print(f"[DEBUG] Total summaries saved: {saved_count}")
    if saved_count == 0:
        print("[ERROR] No summaries were saved. Check scraping and summarization logic.")
        return

    # Generate/update website HTML dashboard
    from src.generate_website import generate_website_from_summaries
    generate_website_from_summaries('summaries', 'website/index.html')
    print("[DEBUG] Website/index.html updated.")

if __name__ == "__main__":
    main()
