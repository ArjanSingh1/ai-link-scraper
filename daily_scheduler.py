#!/usr/bin/env python3
"""
AI Link Scraper Daily Scheduler

Runs automatically every 24 hours to:
1. Scrape the previous day's Slack messages for links
2. Process and summarize new links
3. Add data to existing files (append mode)
4. Maintain a continuous, growing dataset
"""

import os
import sys
import time
import signal
import schedule
import json
import csv
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
import logging

# Add project paths
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from config.settings import settings
from src.utils import setup_logging, save_summary_to_file, format_summary_data
from src.slack_client import SlackClient
from src.web_scraper import WebScraper
from src.summarizer import Summarizer

class DailyLinkScraperScheduler:
    """Daily scheduler for AI Link Scraper that accumulates data over time"""
    
    def __init__(self):
        self.running = False
        self.last_run_file = "last_run.json"
        self.master_data_file = "master_links_data.csv"
        self.master_summaries_dir = "daily_summaries"
        
        # Setup logging
        os.makedirs('logs', exist_ok=True)
        self.logger = setup_logging("INFO", log_file="logs/daily_scheduler.log")
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        # Initialize components
        self.slack_client = SlackClient()
        self.web_scraper = WebScraper()
        self.summarizer = Summarizer()
        
        # Ensure directories exist
        os.makedirs(self.master_summaries_dir, exist_ok=True)
        
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        self.logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.stop()
        
    def start(self):
        """Start the daily scheduler"""
        self.logger.info("🤖 Starting AI Link Scraper Daily Scheduler")
        self.logger.info("📅 Scheduled to run every day at 9:00 AM")
        
        try:
            # Validate settings
            settings.validate()
            self.logger.info("✅ Configuration validated successfully")
            
            # Test Slack connection
            if not self.slack_client.test_connection():
                self.logger.error("❌ Failed to connect to Slack. Please check your configuration.")
                return 1
                
            self.logger.info("✅ Connected to Slack successfully")
            
            # Schedule daily run at 9:00 AM
            schedule.every().day.at("09:00").do(self._daily_scrape_job)
            
            # Also allow manual trigger for testing
            self.logger.info("💡 To run manually, send SIGUSR1 signal to this process")
            signal.signal(signal.SIGUSR1, lambda s, f: self._daily_scrape_job())
            
            # Start scheduler loop
            self.running = True
            self._scheduler_loop()
            
        except Exception as e:
            self.logger.error(f"❌ Failed to start scheduler: {str(e)}", exc_info=True)
            return 1
            
        return 0
        
    def stop(self):
        """Stop the scheduler"""
        self.running = False
        self.logger.info("🛑 Daily scheduler stopping...")
        
    def _scheduler_loop(self):
        """Main scheduler loop"""
        self.logger.info("🔄 Scheduler running - waiting for scheduled times...")
        
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except Exception as e:
                self.logger.error(f"Error in scheduler loop: {e}", exc_info=True)
                time.sleep(60)
                
    def _daily_scrape_job(self):
        """Daily scraping job that processes yesterday's messages"""
        job_start_time = datetime.now()
        self.logger.info("=" * 70)
        self.logger.info(f"🚀 DAILY SCRAPE JOB STARTED - {job_start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info("=" * 70)
        
        try:
            # Calculate yesterday's date range
            yesterday = datetime.now() - timedelta(days=1)
            start_date = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            self.logger.info(f"📅 Processing messages from: {start_date.strftime('%Y-%m-%d %H:%M:%S')}")
            self.logger.info(f"📅 Processing messages to: {end_date.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Get yesterday's messages from Slack
            self.logger.info("📥 Fetching messages from Slack...")
            messages = self.slack_client.get_channel_messages(
                start_date=start_date,
                end_date=end_date
            )
            
            if not messages:
                self.logger.info("📭 No messages found for yesterday - nothing to process")
                self._update_last_run(job_start_time, 0, 0, "No messages found")
                return
                
            self.logger.info(f"📬 Found {len(messages)} messages from yesterday")
            
            # Extract links from messages
            self.logger.info("🔗 Extracting links from messages...")
            links_data = self.slack_client.extract_links_from_messages(messages)
            
            if not links_data:
                self.logger.info("🔗 No links found in yesterday's messages")
                self._update_last_run(job_start_time, len(messages), 0, "No links found")
                return
                
            self.logger.info(f"🔗 Found {len(links_data)} links to process")
            
            # Filter out links we've already processed
            new_links = self._filter_new_links(links_data)
            
            if not new_links:
                self.logger.info("✅ All links from yesterday have already been processed")
                self._update_last_run(job_start_time, len(messages), len(links_data), "All links already processed")
                return
                
            self.logger.info(f"🆕 Processing {len(new_links)} new links")
            
            # Process the new links
            processed_links = self._process_links(new_links, start_date)
            
            if processed_links:
                # Add to master data files
                self._add_to_master_data(processed_links, start_date)
                
                # Save daily summaries
                self._save_daily_summaries(processed_links, start_date)
                
                self.logger.info(f"✅ Successfully processed {len(processed_links)} new links")
                self._update_last_run(job_start_time, len(messages), len(processed_links), "Success")
            else:
                self.logger.warning("⚠️ No links were successfully processed")
                self._update_last_run(job_start_time, len(messages), 0, "Processing failed")
                
        except Exception as e:
            self.logger.error(f"❌ Error in daily scrape job: {e}", exc_info=True)
            self._update_last_run(job_start_time, 0, 0, f"Error: {str(e)}")
            
        finally:
            job_end_time = datetime.now()
            duration = (job_end_time - job_start_time).total_seconds()
            self.logger.info("=" * 70)
            self.logger.info(f"🏁 DAILY SCRAPE JOB COMPLETED - Duration: {duration:.1f} seconds")
            self.logger.info("=" * 70)
            
    def _filter_new_links(self, links_data):
        """Filter out links that have already been processed"""
        if not os.path.exists(self.master_data_file):
            return links_data  # No master file yet, all links are new
            
        try:
            # Read existing URLs from master file
            existing_urls = set()
            with open(self.master_data_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if 'url' in row:
                        existing_urls.add(row['url'])
                        
            # Filter out existing URLs
            new_links = []
            for link in links_data:
                if link.get('url') not in existing_urls:
                    new_links.append(link)
                    
            self.logger.info(f"🔍 Filtered out {len(links_data) - len(new_links)} already processed links")
            return new_links
            
        except Exception as e:
            self.logger.error(f"Error filtering links: {e}")
            return links_data  # Return all links if filtering fails
            
    def _process_links(self, links_data, date):
        """Process links by scraping content and generating summaries"""
        processed_links = []
        
        for i, link_data in enumerate(links_data, 1):
            try:
                self.logger.info(f"📄 Processing link {i}/{len(links_data)}: {link_data.get('url', 'Unknown')}")
                
                # Scrape content
                content_data = self.web_scraper.scrape_url(link_data['url'])
                
                if content_data:
                    # Generate summary
                    if content_data.get('content'):
                        summary = self.summarizer.summarize_content(
                            content_data['content'],
                            max_length=settings.SUMMARY_MAX_LENGTH
                        )
                        content_data['summary'] = summary
                    
                    # Combine link data with content data
                    processed_link = {**link_data, **content_data}
                    processed_link['date_processed'] = date.isoformat()
                    processed_link['processing_date'] = datetime.now().isoformat()
                    
                    processed_links.append(processed_link)
                    self.logger.info(f"✅ Successfully processed: {processed_link.get('title', 'Unknown')}")
                else:
                    self.logger.warning(f"⚠️ Failed to scrape content for: {link_data.get('url')}")
                    
                # Small delay to be respectful
                time.sleep(1)
                
            except Exception as e:
                self.logger.error(f"❌ Error processing link {link_data.get('url')}: {e}")
                continue
                
        return processed_links
        
    def _add_to_master_data(self, processed_links, date):
        """Add new links to the master CSV data file"""
        try:
            file_exists = os.path.exists(self.master_data_file)
            
            # Define CSV headers
            headers = [
                'title', 'url', 'domain', 'content_type', 'word_count', 
                'date_shared', 'shared_by', 'summary', 'content',
                'date_processed', 'processing_date'
            ]
            
            with open(self.master_data_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                
                # Write header if file is new
                if not file_exists:
                    writer.writeheader()
                    self.logger.info(f"📄 Created new master data file: {self.master_data_file}")
                
                # Write new data
                for link in processed_links:
                    # Ensure all required fields exist
                    row = {}
                    for header in headers:
                        row[header] = link.get(header, '')
                    writer.writerow(row)
                    
            self.logger.info(f"📊 Added {len(processed_links)} links to master data file")
            
        except Exception as e:
            self.logger.error(f"❌ Error adding to master data: {e}")
            
    def _save_daily_summaries(self, processed_links, date):
        """Save daily summaries in organized folder structure"""
        try:
            # Create date-based folder
            date_folder = os.path.join(self.master_summaries_dir, date.strftime('%Y-%m-%d'))
            os.makedirs(date_folder, exist_ok=True)
            
            # Save each summary as individual file
            for i, link in enumerate(processed_links, 1):
                if link.get('summary'):
                    summary_data = format_summary_data(link)
                    filename = f"summary_{i:03d}_{link.get('title', 'untitled')[:50]}.txt"
                    # Clean filename
                    filename = "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_', '.')).rstrip()
                    filepath = os.path.join(date_folder, filename)
                    
                    save_summary_to_file(summary_data, filepath)
                    
            self.logger.info(f"💾 Saved {len(processed_links)} daily summaries to {date_folder}")
            
        except Exception as e:
            self.logger.error(f"❌ Error saving daily summaries: {e}")
            
    def _update_last_run(self, timestamp, messages_count, links_processed, status):
        """Update last run information"""
        try:
            last_run_data = {
                'timestamp': timestamp.isoformat(),
                'messages_processed': messages_count,
                'links_processed': links_processed,
                'status': status
            }
            
            with open(self.last_run_file, 'w') as f:
                json.dump(last_run_data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Error updating last run data: {e}")
            
    def get_status(self):
        """Get current status and last run information"""
        status = {
            'running': self.running,
            'next_run': None,
            'last_run': None
        }
        
        # Get next scheduled run
        jobs = schedule.get_jobs()
        if jobs:
            status['next_run'] = jobs[0].next_run.isoformat() if jobs[0].next_run else None
            
        # Get last run data
        if os.path.exists(self.last_run_file):
            try:
                with open(self.last_run_file, 'r') as f:
                    status['last_run'] = json.load(f)
            except Exception as e:
                self.logger.error(f"Error reading last run data: {e}")
                
        return status
        
    def manual_run(self):
        """Manually trigger a daily scrape job"""
        self.logger.info("🔧 Manual run triggered")
        self._daily_scrape_job()


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='AI Link Scraper Daily Scheduler')
    parser.add_argument(
        '--run-now',
        action='store_true',
        help='Run the daily scrape job immediately and exit'
    )
    parser.add_argument(
        '--status',
        action='store_true',
        help='Show current status and exit'
    )
    
    args = parser.parse_args()
    
    scheduler = DailyLinkScraperScheduler()
    
    if args.status:
        status = scheduler.get_status()
        print("Daily Scheduler Status:")
        print(f"  Running: {status['running']}")
        print(f"  Next Run: {status['next_run']}")
        if status['last_run']:
            print(f"  Last Run: {status['last_run']['timestamp']}")
            print(f"  Last Status: {status['last_run']['status']}")
            print(f"  Links Processed: {status['last_run']['links_processed']}")
        return 0
        
    if args.run_now:
        print("Running daily scrape job now...")
        scheduler.manual_run()
        return 0
        
    # Start the scheduler daemon
    return scheduler.start()


if __name__ == "__main__":
    sys.exit(main())
