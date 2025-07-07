import re
import json
import logging
from datetime import datetime
from urllib.parse import urlparse

def setup_logging(log_level="INFO", log_file="logs/app.log"):
    """Setup logging configuration"""
    # Create handlers
    handlers = [logging.StreamHandler()]
    
    # Add file handler if log_file is specified
    if log_file:
        handlers.append(logging.FileHandler(log_file))
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers,
        force=True  # Override any existing configuration
    )
    return logging.getLogger(__name__)

def extract_urls_from_text(text):
    """Extract URLs from text using regex"""
    url_pattern = re.compile(
        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    )
    urls = url_pattern.findall(text)
    
    # Clean up URLs (remove trailing characters that Slack adds)
    cleaned_urls = []
    for url in urls:
        # Remove trailing characters like > | ) ] etc that Slack formatting can add
        url = re.sub(r'[>\|\)\]]+$', '', url)
        cleaned_urls.append(url)
    
    # Filter out common non-content URLs
    filtered_urls = []
    skip_domains = ['slack.com', 'tenor.com', 'giphy.com', 't.co']
    
    for url in cleaned_urls:
        domain = urlparse(url).netloc.lower()
        if not any(skip_domain in domain for skip_domain in skip_domains):
            filtered_urls.append(url)
    
    return filtered_urls

def clean_text(text):
    """Clean and normalize text content"""
    if not text:
        return ""
    
    # Remove extra whitespace and normalize
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove common HTML entities
    html_entities = {
        '&nbsp;': ' ',
        '&amp;': '&',
        '&lt;': '<',
        '&gt;': '>',
        '&quot;': '"',
        '&#39;': "'"
    }
    
    for entity, replacement in html_entities.items():
        text = text.replace(entity, replacement)
    
    return text

def sanitize_filename(filename):
    """Sanitize filename for safe file system usage"""
    # Remove or replace unsafe characters
    unsafe_chars = '<>:"/\\|?*'
    for char in unsafe_chars:
        filename = filename.replace(char, '_')
    
    # Limit length and remove leading/trailing periods
    filename = filename.strip('.')[:200]
    
    return filename if filename else 'unnamed_link'

def save_summary_to_file(summary_data, output_folder):
    """Save summary data to JSON file"""
    import os
    
    # Ensure output folder exists
    os.makedirs(output_folder, exist_ok=True)
    
    # Create filename based on title and timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    title = sanitize_filename(summary_data.get('title', 'untitled'))
    filename = f"{timestamp}_{title}.json"
    
    filepath = os.path.join(output_folder, filename)
    
    # Save as JSON
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(summary_data, f, indent=2, ensure_ascii=False)
    
    return filepath

def format_summary_data(url, title, summary, slack_message_id=None, word_count=0, tags=None):
    """Format summary data into standard structure"""
    return {
        "url": url,
        "title": title or "No Title",
        "summary": summary,
        "timestamp": datetime.now().isoformat(),
        "slack_message_id": slack_message_id,
        "word_count": word_count,
        "tags": tags or [],
        "processed_date": datetime.now().strftime("%Y-%m-%d"),
        "processed_time": datetime.now().strftime("%H:%M:%S")
    }

def is_valid_url(url):
    """Check if URL is valid and accessible"""
    try:
        parsed = urlparse(url)
        return all([parsed.scheme, parsed.netloc])
    except Exception:
        return False

def truncate_text(text, max_length):
    """Truncate text to specified length while preserving sentence boundaries"""
    if len(text) <= max_length:
        return text
    
    # First try to find the last complete sentence within the limit
    sentence_endings = ['.', '!', '?']
    
    # Look for sentence endings within the max_length
    for i in range(max_length, 0, -1):
        if i < len(text) and text[i] in sentence_endings:
            # Found a sentence ending, return text up to and including it
            return text[:i+1]
    
    # If no sentence ending found, find the last space before the max length
    # and don't add "..." to avoid incomplete sentences
    truncated = text[:max_length].rsplit(' ', 1)[0]
    
    # Add a period to make it a complete sentence
    if truncated and not truncated.endswith(('.', '!', '?')):
        truncated += '.'
    
    return truncated
