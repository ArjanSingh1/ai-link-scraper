#!/usr/bin/env python3
"""
AI Link Scraper - Main Entry Point

This script monitors Slack channels for shared links, scrapes their content,
generates AI summaries, and saves them in an organized folder structure.
"""

import argparse
import os
import sys
from datetime import datetime, timedelta
from config.settings import settings
from src.utils import setup_logging, save_summary_to_file, format_summary_data
from src.slack_client import SlackClient
from src.web_scraper import WebScraper
from src.summarizer import Summarizer

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='AI Link Scraper - Automatically scrape and summarize links from Slack'
    )
    
    parser.add_argument(
        '--start-date',
        type=str,
        help='Start date for processing messages (YYYY-MM-DD format)'
    )
    
    parser.add_argument(
        '--end-date', 
        type=str,
        help='End date for processing messages (YYYY-MM-DD format)'
    )
    
    parser.add_argument(
        '--limit',
        type=int,
        help='Maximum number of messages to process'
    )
    
    parser.add_argument(
        '--output-folder',
        type=str,
        default=settings.OUTPUT_FOLDER,
        help='Output folder for summaries'
    )
    
    parser.add_argument(
        '--max-links',
        type=int,
        default=settings.MAX_LINKS_PER_RUN,
        help='Maximum number of links to process'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--send-to-slack',
        action='store_true',
        help='Send summaries back to Slack channel as messages'
    )
    
    parser.add_argument(
        '--upload-to-slack',
        action='store_true',
        help='Upload summary files to Slack channel'
    )
    
    parser.add_argument(
        '--share-digest',
        action='store_true',
        help='Send a digest of recent summaries to Slack'
    )
    
    parser.add_argument(
        '--share-all-summaries',
        action='store_true',
        help='Create and share a complete summary collection file to Slack'
    )
    
    parser.add_argument(
        '--check-mentions',
        action='store_true',
        help='Check for recent mentions and respond with link summaries'
    )
    
    return parser.parse_args()

def parse_date(date_string):
    """Parse date string to datetime object"""
    try:
        return datetime.strptime(date_string, '%Y-%m-%d')
    except ValueError:
        raise ValueError(f"Invalid date format: {date_string}. Use YYYY-MM-DD format.")

def main():
    """Main execution function"""
    try:
        # Parse arguments
        args = parse_arguments()
        
        # Setup logging
        log_level = "DEBUG" if args.verbose else settings.LOG_LEVEL
        os.makedirs('logs', exist_ok=True)
        logger = setup_logging(log_level)
        
        logger.info("Starting AI Link Scraper")
        logger.info(f"Output folder: {args.output_folder}")
        
        # Validate settings
        settings.validate()
        logger.info("Configuration validated successfully")
        
        # Parse dates if provided
        start_date = None
        end_date = None
        
        if args.start_date:
            start_date = parse_date(args.start_date)
            logger.info(f"Start date: {start_date}")
            
        if args.end_date:
            end_date = parse_date(args.end_date)
            logger.info(f"End date: {end_date}")
        
        # Initialize components
        logger.info("Initializing Slack client...")
        slack_client = SlackClient()
        
        # Test Slack connection
        if not slack_client.test_connection():
            logger.error("Failed to connect to Slack. Please check your configuration.")
            return 1
        
        # Get channel info
        channel_info = slack_client.get_channel_info()
        if channel_info:
            logger.info(f"Connected to channel: {channel_info.get('name', 'Unknown')}")
        
        # Handle mention checking (separate from regular processing)
        if args.check_mentions:
            logger.info("Checking for recent mentions...")
            mentions_processed = slack_client.check_for_mentions()
            logger.info(f"Processed {mentions_processed} mentions")
            return 0
        
        # Regular processing continues below...
        
        # Fetch messages from Slack
        logger.info("Fetching messages from Slack...")
        messages = slack_client.get_channel_messages(
            start_date=start_date,
            end_date=end_date,
            limit=args.limit
        )
        
        if not messages:
            logger.warning("No messages found in the specified time range")
            return 0
        
        # Extract links from messages
        logger.info("Extracting links from messages...")
        links_data = slack_client.extract_links_from_messages(messages)
        
        if not links_data:
            logger.warning("No links found in messages")
            return 0
        
        # Limit number of links to process
        if len(links_data) > args.max_links:
            logger.info(f"Limiting to {args.max_links} links (found {len(links_data)})")
            links_data = links_data[:args.max_links]
        
        # Extract unique URLs
        urls = list(set([link['url'] for link in links_data]))
        logger.info(f"Processing {len(urls)} unique URLs")
        
        # Initialize web scraper and scrape content
        logger.info("Initializing web scraper...")
        scraper = WebScraper()
        
        logger.info("Scraping web content...")
        scraped_data = scraper.batch_scrape(urls)
        
        if not scraped_data:
            logger.warning("No content was successfully scraped")
            return 0
        
        successful_scrapes = [data for data in scraped_data if data.get('status') == 'success']
        logger.info(f"Successfully scraped {len(successful_scrapes)} out of {len(urls)} URLs")
        
        # Initialize summarizer and generate summaries
        logger.info("Initializing AI summarizer...")
        summarizer = Summarizer()
        
        logger.info("Generating summaries...")
        summaries = summarizer.batch_summarize(successful_scrapes)
        
        if not summaries:
            logger.warning("No summaries were generated")
            return 0
        
        # Save summaries to files
        logger.info(f"Saving {len(summaries)} summaries to {args.output_folder}")
        saved_files = []
        
        for summary in summaries:
            # Find corresponding Slack message data
            slack_data = next(
                (link for link in links_data if link['url'] == summary['url']),
                {}
            )
            
            # Format summary data
            formatted_summary = format_summary_data(
                url=summary['url'],
                title=summary['title'],
                summary=summary['summary'],
                slack_message_id=slack_data.get('slack_message_id'),
                word_count=summary.get('word_count', 0),
                tags=summary.get('tags', [])
            )
            
            # Add additional metadata
            formatted_summary['slack_user'] = slack_data.get('user')
            formatted_summary['slack_timestamp'] = slack_data.get('timestamp').isoformat() if slack_data.get('timestamp') else None
            formatted_summary['original_message'] = slack_data.get('message_text')
            
            # Save to file
            filepath = save_summary_to_file(formatted_summary, args.output_folder)
            saved_files.append(filepath)
            logger.info(f"Saved summary: {os.path.basename(filepath)}")
            
            # Send to Slack if requested
            if args.send_to_slack:
                logger.info(f"Sending summary to Slack: {formatted_summary['title']}")
                message_ts = slack_client.send_summary_to_channel(formatted_summary, reply_to_message=True)
                if message_ts:
                    logger.info(f"✅ Successfully sent to Slack")
                else:
                    logger.warning(f"❌ Failed to send to Slack")
            
            # Upload file to Slack if requested
            if args.upload_to_slack:
                logger.info(f"Uploading file to Slack: {os.path.basename(filepath)}")
                comment = f"📄 Summary for: {formatted_summary['title']}"
                thread_ts = formatted_summary.get('slack_message_id') if args.send_to_slack else None
                file_id = slack_client.upload_file_to_channel(
                    filepath, 
                    title=f"Summary - {formatted_summary['title']}", 
                    comment=comment,
                    thread_ts=thread_ts
                )
                if file_id:
                    logger.info(f"✅ Successfully uploaded to Slack")
                else:
                    logger.warning(f"❌ Failed to upload to Slack")
        
        # Summary report
        logger.info("=== PROCESSING COMPLETE ===")
        logger.info(f"Messages processed: {len(messages)}")
        logger.info(f"Links found: {len(links_data)}")
        logger.info(f"URLs scraped: {len(urls)}")
        logger.info(f"Successful scrapes: {len(successful_scrapes)}")
        logger.info(f"Summaries generated: {len(summaries)}")
        logger.info(f"Files saved: {len(saved_files)}")
        logger.info(f"Output folder: {os.path.abspath(args.output_folder)}")
        
        if args.send_to_slack:
            logger.info("📨 Summaries sent to Slack as messages")
        if args.upload_to_slack:
            logger.info("📎 Summary files uploaded to Slack")
        
        # Handle additional sharing options
        if args.share_digest:
            logger.info("Creating summary digest...")
            digest_ts = slack_client.send_summary_digest(args.output_folder, max_summaries=5)
            if digest_ts:
                logger.info("✅ Summary digest sent to Slack")
            else:
                logger.warning("❌ Failed to send summary digest")
        
        if args.share_all_summaries:
            logger.info("Creating complete summary collection...")
            file_id = slack_client.share_complete_summary_folder(args.output_folder)
            if file_id:
                logger.info("✅ Complete summary collection shared to Slack")
            else:
                logger.warning("❌ Failed to share complete summary collection")
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())
