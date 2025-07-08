#!/usr/bin/env python3
"""
Test script for the updated formatting system
"""

import os
import sys
from datetime import datetime, timedelta
from src.slack_client import SlackClient
from src.link_processor import LinkProcessor

def test_formatting():
    """Test the new formatting with recent links"""
    try:
        # Initialize clients
        slack_client = SlackClient()
        processor = LinkProcessor(slack_client)
        
        # Get recent links (last 1 day)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=1)
        
        print(f"Fetching links from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        
        # Fetch messages and extract links
        messages = slack_client.get_channel_messages(start_date=start_date, end_date=end_date, limit=20)
        links_data = slack_client.extract_links_from_messages(messages)
        
        # Limit to 2 links for testing
        links_data = links_data[:2]
        
        print(f"Processing {len(links_data)} links")
        
        # Process links
        output_folder = processor.scrape_links_for_drive(links_data)
        
        print(f"✅ Processing complete! Output saved to: {output_folder}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_formatting()
