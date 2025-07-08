#!/usr/bin/env python3
"""
Example usage of the AI Link Scraper components
This script demonstrates how to use individual components
"""

import os
import sys
from datetime import datetime, timedelta

# Add src to path
sys.path.append('.')

from config.settings import settings
from src.utils import setup_logging
from src.slack_client import SlackClient
from src.web_scraper import WebScraper
from src.summarizer import Summarizer

def example_slack_integration():
    """Example of using Slack integration"""
    print("🔗 Slack Integration Example")
    print("-" * 30)
    
    try:
        # Initialize Slack client
        slack = SlackClient()
        
        # Test connection
        if slack.test_connection():
            print("✅ Successfully connected to Slack")
        else:
            print("❌ Failed to connect to Slack")
            return
        
        # Get channel info
        channel_info = slack.get_channel_info()
        if channel_info:
            print(f"📺 Channel: {channel_info.get('name', 'Unknown')}")
        
        # Get recent messages (last 24 hours)
        yesterday = datetime.now() - timedelta(days=1)
        messages = slack.get_channel_messages(start_date=yesterday, limit=10)
        print(f"💬 Found {len(messages)} recent messages")
        
        # Extract links
        links = slack.extract_links_from_messages(messages)
        print(f"🔗 Found {len(links)} links")
        
        if links:
            print("Links found:")
            for i, link in enumerate(links[:3], 1):  # Show first 3
                print(f"  {i}. {link['url']}")
    
    except Exception as e:
        print(f"❌ Error: {e}")

def example_web_scraping():
    """Example of web scraping"""
    print("\n🌐 Web Scraping Example")
    print("-" * 30)
    
    # Example URLs to scrape
    test_urls = [
        "https://example.com",
        "https://httpbin.org/html"
    ]
    
    try:
        scraper = WebScraper()
        
        for url in test_urls:
            print(f"📄 Scraping: {url}")
            result = scraper.scrape_url(url)
            
            if result and result.get('status') == 'success':
                print(f"  ✅ Title: {result.get('title', 'No title')}")
                print(f"  📝 Content length: {len(result.get('content', ''))} characters")
                print(f"  📊 Word count: {result.get('word_count', 0)}")
            else:
                print(f"  ❌ Failed to scrape")
    
    except Exception as e:
        print(f"❌ Error: {e}")

def example_summarization():
    """Example of AI summarization"""
    print("\n🤖 AI Summarization Example")
    print("-" * 30)
    
    # Example content to summarize
    sample_content = """
    Artificial Intelligence (AI) is rapidly transforming various industries and aspects of our daily lives. 
    From healthcare and finance to transportation and entertainment, AI technologies are being integrated 
    to improve efficiency, accuracy, and user experience. Machine learning algorithms can now process 
    vast amounts of data to identify patterns and make predictions that were previously impossible for 
    humans to achieve. However, with these advancements come important ethical considerations around 
    privacy, bias, and the future of work. As AI continues to evolve, it's crucial for society to 
    develop frameworks that ensure these technologies are used responsibly and benefit everyone.
    """
    
    try:
        summarizer = Summarizer()
        
        print("📝 Original content length:", len(sample_content))
        
        # Generate summary
        summary = summarizer.summarize_content(
            content=sample_content,
            title="The Impact of AI on Society"
        )
        
        print("📄 Generated summary:")
        print(f"  {summary}")
        
        # Generate tags
        tags = summarizer.generate_tags(sample_content, "The Impact of AI on Society")
        print(f"🏷️  Generated tags: {', '.join(tags)}")
    
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Run all examples"""
    print("🚀 AI Link Scraper - Component Examples")
    print("=" * 50)
    
    # Setup logging
    logger = setup_logging("INFO")
    
    # Check if environment is configured
    try:
        settings.validate()
        print("✅ Configuration validated")
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("💡 Please run 'python setup.py' first")
        return
    
    # Run examples
    example_slack_integration()
    example_web_scraping()
    example_summarization()
    
    print("\n" + "=" * 50)
    print("🎉 Examples completed!")
    print("💡 Run 'python main.py' to start the full scraper")

if __name__ == "__main__":
    main()
