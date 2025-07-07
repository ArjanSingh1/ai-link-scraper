#!/usr/bin/env python3
"""
AI Link Scraper Daemon

A persistent process that continuously monitors for @ai-link scraper mentions
across all accessible Slack channels and responds with link summaries.
"""

import argparse
import os
import sys
import time
import signal
from datetime import datetime, timedelta
from config.settings import settings
from src.utils import setup_logging
from src.slack_client import SlackClient

class DaemonProcess:
    """Persistent daemon process for mention monitoring"""
    
    def __init__(self, check_interval=60, verbose=False):
        """
        Initialize daemon
        
        Args:
            check_interval: Time in seconds between mention checks (default: 60)
            verbose: Enable verbose logging
        """
        self.check_interval = check_interval
        self.running = False
        self.slack_client = None
        
        # Setup logging
        log_level = "DEBUG" if verbose else settings.LOG_LEVEL
        os.makedirs('logs', exist_ok=True)
        self.logger = setup_logging(log_level, log_file="logs/daemon.log")
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        self.logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.stop()
        
    def start(self):
        """Start the daemon process"""
        self.logger.info("Starting AI Link Scraper Daemon")
        self.logger.info(f"Check interval: {self.check_interval} seconds")
        
        try:
            # Validate settings
            settings.validate()
            self.logger.info("Configuration validated successfully")
            
            # Initialize Slack client
            self.logger.info("Initializing Slack client...")
            self.slack_client = SlackClient()
            
            # Test Slack connection
            if not self.slack_client.test_connection():
                self.logger.error("Failed to connect to Slack. Please check your configuration.")
                return 1
                
            self.logger.info("✅ Connected to Slack successfully")
            
            # Start monitoring loop
            self.running = True
            self._monitoring_loop()
            
        except Exception as e:
            self.logger.error(f"Failed to start daemon: {str(e)}", exc_info=True)
            return 1
            
        return 0
        
    def stop(self):
        """Stop the daemon process"""
        self.running = False
        self.logger.info("Daemon stopping...")
        
    def _monitoring_loop(self):
        """Main monitoring loop"""
        self.logger.info("🤖 Daemon started - monitoring for mentions...")
        last_check_time = datetime.now() - timedelta(minutes=5)  # Start with 5min lookback
        
        while self.running:
            try:
                start_time = time.time()
                
                # Check for mentions since last check
                self.logger.debug(f"Checking for mentions since {last_check_time}")
                mentions_processed = self.slack_client.check_all_channels_for_mentions(start_date=last_check_time)
                
                if mentions_processed > 0:
                    self.logger.info(f"✅ Processed {mentions_processed} mentions")
                else:
                    self.logger.debug("No new mentions found")
                
                # Update last check time
                last_check_time = datetime.now()
                
                # Calculate sleep time to maintain consistent interval
                elapsed_time = time.time() - start_time
                sleep_time = max(0, self.check_interval - elapsed_time)
                
                if sleep_time > 0:
                    self.logger.debug(f"Sleeping for {sleep_time:.1f} seconds...")
                    time.sleep(sleep_time)
                else:
                    self.logger.warning(f"Check took {elapsed_time:.1f}s, longer than interval of {self.check_interval}s")
                    
            except KeyboardInterrupt:
                self.logger.info("Received keyboard interrupt")
                break
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {str(e)}", exc_info=True)
                # Sleep before retrying to avoid rapid error loops
                time.sleep(min(60, self.check_interval))
                
        self.logger.info("Monitoring loop ended")

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='AI Link Scraper Daemon - Continuous mention monitoring'
    )
    
    parser.add_argument(
        '--interval',
        type=int,
        default=60,
        help='Check interval in seconds (default: 60)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--test',
        action='store_true',
        help='Run a single check and exit (for testing)'
    )
    
    return parser.parse_args()

def main():
    """Main entry point"""
    args = parse_arguments()
    
    # Test mode - run single check
    if args.test:
        print("Running single mention check...")
        try:
            settings.validate()
            slack_client = SlackClient()
            if not slack_client.test_connection():
                print("❌ Failed to connect to Slack")
                return 1
            
            mentions = slack_client.check_all_channels_for_mentions()
            print(f"✅ Processed {mentions} mentions")
            return 0
        except Exception as e:
            print(f"❌ Test failed: {str(e)}")
            return 1
    
    # Normal daemon mode
    daemon = DaemonProcess(
        check_interval=args.interval,
        verbose=args.verbose
    )
    
    try:
        return daemon.start()
    except KeyboardInterrupt:
        print("\nDaemon interrupted by user")
        return 0
    except Exception as e:
        print(f"Daemon failed: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
