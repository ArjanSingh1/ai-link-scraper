# update_all.py
import sys
import os
# Ensure project root is in sys.path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from src.slack_client import SlackClient
from website.app import scrape_b2b_vault, db

def update_slack():
    slack = SlackClient()
    messages = slack.get_channel_messages(limit=100)
    links = slack.extract_links_from_messages(messages)
    # Save or process links as needed

def update_b2b_vault():
    articles = scrape_b2b_vault()
    for article in articles:
        db.add_b2b_article(article)

if __name__ == "__main__":
    update_slack()
    update_b2b_vault()
    print("✅ Updated Slack links and B2B Vault articles.")