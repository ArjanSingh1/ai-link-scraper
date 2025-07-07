import logging
import requests
import time
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from config.settings import settings

logger = logging.getLogger(__name__)

class WebScraper:
    def __init__(self):
        """Initialize web scraper with configuration"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': settings.USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        self.timeout = settings.REQUEST_TIMEOUT
        self.max_retries = settings.MAX_RETRIES
    
    def scrape_url(self, url):
        """Scrape content from a single URL"""
        try:
            logger.info(f"Scraping URL: {url}")
            
            # Get the webpage content
            response = self._fetch_with_retry(url)
            if not response:
                return None
            
            # Parse the HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract content
            title = self._extract_title(soup)
            content = self._extract_main_content(soup)
            
            if not content:
                logger.warning(f"No content extracted from {url}")
                return None
            
            result = {
                'url': url,
                'title': title,
                'content': content,
                'word_count': len(content.split()),
                'status': 'success'
            }
            
            logger.info(f"Successfully scraped {url} - {result['word_count']} words")
            return result
            
        except Exception as e:
            logger.error(f"Error scraping {url}: {str(e)}")
            return {
                'url': url,
                'title': None,
                'content': None,
                'word_count': 0,
                'status': 'error',
                'error': str(e)
            }
    
    def _fetch_with_retry(self, url):
        """Fetch URL with retry logic"""
        for attempt in range(self.max_retries):
            try:
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()
                return response
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Attempt {attempt + 1} failed for {url}: {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error(f"Failed to fetch {url} after {self.max_retries} attempts")
                    return None
    
    def _extract_title(self, soup):
        """Extract page title from HTML"""
        # Try different title sources in order of preference
        title_selectors = [
            'meta[property="og:title"]',
            'meta[name="twitter:title"]',
            'title',
            'h1'
        ]
        
        for selector in title_selectors:
            if selector.startswith('meta'):
                element = soup.select_one(selector)
                if element:
                    title = element.get('content', '').strip()
                    if title:
                        return title
            else:
                element = soup.select_one(selector)
                if element:
                    title = element.get_text().strip()
                    if title:
                        return title
        
        return "No Title Found"
    
    def _extract_main_content(self, soup):
        """Extract main content from HTML"""
        # Remove unwanted elements
        unwanted_tags = ['script', 'style', 'nav', 'header', 'footer', 'aside', 'advertisement']
        for tag in unwanted_tags:
            for element in soup.find_all(tag):
                element.decompose()
        
        # Try to find main content using common selectors
        content_selectors = [
            'article',
            'main',
            '[role="main"]',
            '.content',
            '.main-content',
            '.post-content',
            '.entry-content',
            '.article-body',
            '.story-body'
        ]
        
        for selector in content_selectors:
            content_element = soup.select_one(selector)
            if content_element:
                text = content_element.get_text().strip()
                if len(text) > 200:  # Ensure we have substantial content
                    return self._clean_text(text)
        
        # Fallback: extract all paragraph text
        paragraphs = soup.find_all('p')
        if paragraphs:
            text = ' '.join([p.get_text().strip() for p in paragraphs])
            if len(text) > 100:
                return self._clean_text(text)
        
        # Last resort: get all text from body
        body = soup.find('body')
        if body:
            text = body.get_text().strip()
            if len(text) > 100:
                return self._clean_text(text)
        
        return None
    
    def _clean_text(self, text):
        """Clean and normalize extracted text"""
        import re
        
        # Replace multiple whitespace with single space
        text = re.sub(r'\s+', ' ', text)
        
        # Remove excessive newlines
        text = re.sub(r'\n+', '\n', text)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def batch_scrape(self, urls, delay=1):
        """Scrape multiple URLs with delay between requests"""
        results = []
        
        for i, url in enumerate(urls):
            logger.info(f"Processing URL {i+1}/{len(urls)}: {url}")
            
            result = self.scrape_url(url)
            if result:
                results.append(result)
            
            # Add delay between requests to be respectful
            if i < len(urls) - 1:
                time.sleep(delay)
        
        return results
