#!/usr/bin/env python3
"""
Daily Update Script - Incremental Data Processing

This script updates both Slack links and B2B Vault articles by:
1. Processing only the previous day's Slack messages
2. Adding new data to existing datasets (append mode)
3. Avoiding duplicate processing
"""

import sys
import os
import csv
import json
from datetime import datetime, timedelta
from pathlib import Path

# Ensure project root is in sys.path for imports
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.append(project_root)

from src.slack_client import SlackClient
from src.web_scraper import WebScraper
from src.summarizer import Summarizer
from config.settings import settings

class DailyDataUpdater:
    """Handles daily incremental updates for Slack and B2B Vault data"""
    
    def __init__(self):
        self.master_data_file = os.path.join(project_root, "master_links_data.csv")
        self.slack_client = SlackClient()
        self.web_scraper = WebScraper()
        self.summarizer = Summarizer()
        
    def update_slack_daily(self, target_date=None):
        """Update Slack data for a specific day (default: yesterday)"""
        print("🔄 Starting daily Slack update...")
        
        # Use yesterday if no date specified
        if target_date is None:
            target_date = datetime.now() - timedelta(days=1)
        
        # Calculate date range for the target day
        start_date = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = target_date.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        print(f"📅 Processing Slack messages from {start_date.strftime('%Y-%m-%d')}")
        
        # Get messages for the target day
        messages = self.slack_client.get_channel_messages(
            start_date=start_date,
            end_date=end_date
        )
        
        if not messages:
            print(f"📭 No messages found for {start_date.strftime('%Y-%m-%d')}")
            return 0
            
        print(f"📬 Found {len(messages)} messages")
        
        # Extract links
        links_data = self.slack_client.extract_links_from_messages(messages)
        
        if not links_data:
            print("🔗 No links found in messages")
            return 0
            
        print(f"🔗 Found {len(links_data)} links")
        
        # Filter out already processed links
        new_links = self._filter_new_links(links_data)
        
        if not new_links:
            print("✅ All links already processed")
            return 0
            
        print(f"🆕 Processing {len(new_links)} new links...")
        
        # Process new links
        processed_count = 0
        for i, link_data in enumerate(new_links, 1):
            try:
                print(f"📄 Processing {i}/{len(new_links)}: {link_data.get('url', 'Unknown')}")
                
                # Scrape content
                content_data = self.web_scraper.scrape_url(link_data['url'])
                
                if content_data and content_data.get('content'):
                    # Generate summary
                    summary = self.summarizer.summarize_content(
                        content_data['content'],
                        max_length=settings.SUMMARY_MAX_LENGTH
                    )
                    content_data['summary'] = summary
                    
                    # Combine data
                    processed_link = {**link_data, **content_data}
                    processed_link['date_processed'] = target_date.isoformat()
                    processed_link['processing_date'] = datetime.now().isoformat()
                    
                    # Add to master file
                    self._add_to_master_file(processed_link)
                    processed_count += 1
                    
                    print(f"✅ Processed: {processed_link.get('title', 'Unknown')}")
                else:
                    print(f"⚠️ Failed to scrape: {link_data.get('url')}")
                    
            except Exception as e:
                print(f"❌ Error processing {link_data.get('url')}: {e}")
                continue
                
        print(f"✅ Slack update complete: {processed_count} new links processed")
        return processed_count
        
    def update_b2b_vault_daily(self, max_articles=10):
        """Update B2B Vault with a small daily batch"""
        print("🔄 Starting daily B2B Vault update...")
        
        try:
            # Import B2B Vault scraper
            sys.path.append(os.path.join(project_root, 'b2bvault-repo'))
            from B2Bscraper import B2BVaultAgent
            
            # Create agent with minimal settings for daily updates
            agent = B2BVaultAgent(max_workers=1)
            
            # Scrape a small batch of random articles
            print(f"📄 Scraping {max_articles} B2B Vault articles...")
            articles = agent.scrape_all_articles_from_homepage(
                preview=False, 
                max_articles=max_articles
            )
            
            if articles:
                # Process articles with AI
                processed_articles = agent.process_multiple_articles(articles, preview=False)
                
                if processed_articles:
                    # Save to database
                    self._save_b2b_articles(processed_articles)
                    print(f"✅ B2B Vault update complete: {len(processed_articles)} articles processed")
                    return len(processed_articles)
                else:
                    print("⚠️ No B2B articles were successfully processed")
                    return 0
            else:
                print("📭 No B2B articles found")
                return 0
                
        except ImportError:
            print("⚠️ B2B Vault integration not available")
            return 0
        except Exception as e:
            print(f"❌ Error updating B2B Vault: {e}")
            return 0
            
    def _filter_new_links(self, links_data):
        """Filter out links that have already been processed"""
        if not os.path.exists(self.master_data_file):
            return links_data
            
        try:
            existing_urls = set()
            with open(self.master_data_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if 'url' in row:
                        existing_urls.add(row['url'])
                        
            new_links = [link for link in links_data if link.get('url') not in existing_urls]
            print(f"🔍 Filtered out {len(links_data) - len(new_links)} already processed links")
            return new_links
            
        except Exception as e:
            print(f"⚠️ Error filtering links: {e}")
            return links_data
            
    def _add_to_master_file(self, processed_link):
        """Add a single processed link to the master CSV file"""
        file_exists = os.path.exists(self.master_data_file)
        
        headers = [
            'title', 'url', 'domain', 'content_type', 'word_count',
            'date_shared', 'shared_by', 'summary', 'content',
            'date_processed', 'processing_date'
        ]
        
        with open(self.master_data_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            
            if not file_exists:
                writer.writeheader()
                
            # Ensure all fields exist
            row = {}
            for header in headers:
                row[header] = processed_link.get(header, '')
            writer.writerow(row)
            
    def _save_b2b_articles(self, articles):
        """Save B2B articles to database"""
        try:
            from website.app import SalesIntelligenceDB
            db = SalesIntelligenceDB()
            
            for article in articles:
                # Add B2B article to database (avoiding duplicates)
                db.add_b2b_article({
                    'title': article.get('title', ''),
                    'url': article.get('url', ''),
                    'content': article.get('content', ''),
                    'summary': article.get('summary', ''),
                    'category': article.get('tab', 'General'),
                    'publisher': article.get('publisher', ''),
                    'date_scraped': datetime.now().isoformat()
                })
                
        except Exception as e:
            print(f"⚠️ Error saving B2B articles to database: {e}")


def update_slack(target_date=None):
    """Update Slack data for a specific day"""
    updater = DailyDataUpdater()
    return updater.update_slack_daily(target_date)

def update_b2b_vault(max_articles=10):
    """Update B2B Vault with daily batch"""
    updater = DailyDataUpdater()
    return updater.update_b2b_vault_daily(max_articles)

def main():
    """Main function for command-line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Daily Data Updater')
    parser.add_argument('--date', type=str, help='Target date (YYYY-MM-DD), default: yesterday')
    parser.add_argument('--slack-only', action='store_true', help='Update only Slack data')
    parser.add_argument('--b2b-only', action='store_true', help='Update only B2B Vault data')
    parser.add_argument('--b2b-articles', type=int, default=10, help='Number of B2B articles to process')
    
    args = parser.parse_args()
    
    # Parse target date
    target_date = None
    if args.date:
        try:
            target_date = datetime.strptime(args.date, '%Y-%m-%d')
        except ValueError:
            print(f"❌ Invalid date format: {args.date}. Use YYYY-MM-DD")
            return 1
            
    print("🚀 Starting daily data update...")
    print(f"📅 Target date: {(target_date or datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')}")
    
    total_processed = 0
    
    # Update Slack data
    if not args.b2b_only:
        slack_count = update_slack(target_date)
        total_processed += slack_count
        
    # Update B2B Vault data
    if not args.slack_only:
        b2b_count = update_b2b_vault(args.b2b_articles)
        total_processed += b2b_count
        
    print(f"🎉 Daily update complete! Total items processed: {total_processed}")
    return 0

if __name__ == "__main__":
    sys.exit(main())