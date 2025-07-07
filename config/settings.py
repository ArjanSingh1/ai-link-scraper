import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    # Slack Configuration
    SLACK_BOT_TOKEN = os.getenv('SLACK_BOT_TOKEN')
    SLACK_CHANNEL_ID = os.getenv('SLACK_CHANNEL_ID')
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # Google Drive Configuration
    GOOGLE_DRIVE_FOLDER_ID = os.getenv('GOOGLE_DRIVE_FOLDER_ID')  # Optional: specific folder ID
    
    # General Configuration
    OUTPUT_FOLDER = os.getenv('OUTPUT_FOLDER', 'summaries')
    MAX_LINKS_PER_RUN = int(os.getenv('MAX_LINKS_PER_RUN', 50))
    SUMMARY_MAX_LENGTH = int(os.getenv('SUMMARY_MAX_LENGTH', 500))
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # Web Scraping Configuration
    REQUEST_TIMEOUT = 10
    MAX_RETRIES = 3
    USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    
    @classmethod
    def validate(cls):
        """Validate that required environment variables are set"""
        required_vars = ['SLACK_BOT_TOKEN', 'SLACK_CHANNEL_ID', 'OPENAI_API_KEY']
        missing_vars = []
        
        for var in required_vars:
            if not getattr(cls, var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        return True

# Create settings instance
settings = Settings()
