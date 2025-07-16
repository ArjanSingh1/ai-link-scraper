# Configuration settings for the AI Link Scraper project
import os

class Settings:
    SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
    SLACK_CHANNEL_ID = os.getenv("SLACK_CHANNEL_ID")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    USER_AGENT = os.getenv("USER_AGENT", "Mozilla/5.0")
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", 10))
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", 3))
    SUMMARY_MAX_LENGTH = int(os.getenv("SUMMARY_MAX_LENGTH", 500))

settings = Settings()
