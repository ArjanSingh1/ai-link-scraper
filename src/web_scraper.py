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
        
        # Sites that require JavaScript or have special handling
        self.js_dependent_sites = {
            'x.com', 'twitter.com', 'linkedin.com', 'facebook.com', 
            'instagram.com', 'tiktok.com', 'reddit.com'
        }
    
    def _is_js_dependent_site(self, url):
        """Check if URL is from a JavaScript-dependent site"""
        try:
            domain = urlparse(url).netloc.lower()
            # Remove www. prefix if present
            domain = domain.replace('www.', '')
            
            for js_site in self.js_dependent_sites:
                if js_site in domain:
                    return True
            return False
        except:
            return False
    
    def _detect_js_requirement(self, soup, url):
        """Detect if page requires JavaScript to function properly"""
        # Check for common JavaScript requirement indicators
        js_indicators = [
            "javascript is disabled",
            "enable javascript", 
            "javascript is required",
            "javascript must be enabled",
            "please enable javascript",
            "browser doesn't support javascript"
        ]
        
        page_text = soup.get_text().lower()
        
        for indicator in js_indicators:
            if indicator in page_text:
                logger.warning(f"JavaScript required for {url} - detected: '{indicator}'")
                return True
        
        # Check if page has very little content (common for JS-dependent sites)
        if len(page_text.strip()) < 200 and self._is_js_dependent_site(url):
            logger.warning(f"JavaScript likely required for {url} - minimal content detected")
            return True
            
        return False
    
    def scrape_url(self, url):
        """Scrape content from a single URL"""
        try:
            logger.info(f"Scraping URL: {url}")
            
            # Check if this is a known JS-dependent site
            if self._is_js_dependent_site(url):
                logger.info(f"Detected JavaScript-dependent site: {url}")
                # Use more sophisticated headers for social media
                original_user_agent = self.session.headers.get('User-Agent')
                self.session.headers.update({
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                })
            
            # Get the webpage content
            response = self._fetch_with_retry(url)
            if not response:
                return None
            
            # Parse the HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Check if JavaScript is required
            if self._detect_js_requirement(soup, url):
                # Restore original user agent
                if self._is_js_dependent_site(url):
                    self.session.headers['User-Agent'] = original_user_agent
                
                # Return a special result indicating JS dependency
                return {
                    'url': url,
                    'title': 'JavaScript Required',
                    'content': f'This content from {urlparse(url).netloc} requires JavaScript to load properly. The scraper cannot access the full content from this social media or dynamic website.',
                    'word_count': 0,
                    'status': 'js_required',
                    'domain': urlparse(url).netloc
                }
            
            # Extract content
            title = self._extract_title(soup)
            content = self._extract_main_content(soup)
            
            # Restore original user agent
            if self._is_js_dependent_site(url):
                self.session.headers['User-Agent'] = original_user_agent
            
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
        """Extract complete main content from HTML with enhanced extraction"""
        # Remove unwanted elements
        unwanted_tags = ['script', 'style', 'nav', 'header', 'footer', 'aside', 'advertisement', 'ads']
        unwanted_classes = ['ad', 'ads', 'advertisement', 'sidebar', 'menu', 'navigation', 'footer', 'header']
        
        for tag in unwanted_tags:
            for element in soup.find_all(tag):
                element.decompose()
        
        # Remove elements with unwanted classes
        for class_name in unwanted_classes:
            for element in soup.find_all(class_=lambda x: x and class_name in ' '.join(x).lower()):
                element.decompose()
        
        # Enhanced content selectors for better extraction
        content_selectors = [
            'article',
            'main', 
            '[role="main"]',
            '.post-content',
            '.entry-content',
            '.article-body',
            '.story-body',
            '.content',
            '.main-content',
            '.article-content',
            '.post-body',
            '.blog-content',
            '.markdown-body',  # GitHub
            '.readme',         # GitHub README
            '.discussion-content', # Forums
            '.message-content'     # Forums/discussions
        ]
        
        best_content = ""
        best_length = 0
        
        # Try each selector and keep the longest content
        for selector in content_selectors:
            content_element = soup.select_one(selector)
            if content_element:
                # Extract text while preserving some structure
                text = self._extract_structured_text(content_element)
                if len(text) > best_length and len(text) > 200:
                    best_content = text
                    best_length = len(text)
        
        if best_content:
            return self._clean_text(best_content)
        
        # Fallback: extract all paragraph and heading content
        content_elements = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'blockquote', 'pre', 'code'])
        if content_elements:
            text_parts = []
            for element in content_elements:
                element_text = element.get_text().strip()
                if len(element_text) > 10:  # Skip very short elements
                    # Add some structure markers
                    if element.name.startswith('h'):
                        text_parts.append(f"\n{element_text}\n")
                    elif element.name in ['blockquote']:
                        text_parts.append(f"\n> {element_text}\n")
                    else:
                        text_parts.append(element_text)
            
            text = '\n'.join(text_parts)
            if len(text) > 500:
                return self._clean_text(text)
        
        # Last resort: get all text from body but filter out navigation/menu items
        body = soup.find('body')
        if body:
            text = body.get_text().strip()
            if len(text) > 300:
                return self._clean_text(text)
        
        return None
    
    def _clean_text(self, text):
        """Clean and normalize extracted text while preserving structure and readability"""
        import re
        
        # Remove unicode box characters and other formatting artifacts (comprehensive)
        text = re.sub(r'[■□▪▫●○◆◇▲△▼▽★☆♦♧♢♤♠♡♣♥]', '', text)  # Basic symbols
        text = re.sub(r'[\u2580-\u259F]', '', text)  # Block characters
        text = re.sub(r'[\u25A0-\u25FF]', '', text)  # Geometric shapes
        text = re.sub(r'[\u2600-\u26FF]', '', text)  # Miscellaneous symbols
        text = re.sub(r'[\u2700-\u27BF]', '', text)  # Dingbats
        text = re.sub(r'[\u2190-\u21FF]', '', text)  # Arrows
        text = re.sub(r'[\u2500-\u257F]', '', text)  # Box drawing characters
        
        # Remove specific problematic characters
        text = re.sub(r'[‌‍‎‏]', '', text)  # Zero-width characters
        text = re.sub(r'[\uFEFF]', '', text)  # Byte order mark
        text = re.sub(r'[\u200B-\u200D]', '', text)  # Zero-width spaces
        
        # Replace multiple whitespace with single space, but preserve paragraph breaks
        text = re.sub(r'[ \t]+', ' ', text)  # Multiple spaces/tabs to single space
        text = re.sub(r'\n[ \t]+', '\n', text)  # Remove leading whitespace on lines
        text = re.sub(r'[ \t]+\n', '\n', text)  # Remove trailing whitespace on lines
        
        # Better paragraph spacing - ensure good separation between paragraphs
        text = re.sub(r'\n{3,}', '\n\n', text)  # Max 2 line breaks
        text = re.sub(r'([.!?])\s*\n([A-Z])', r'\1\n\n\2', text)  # Add paragraph breaks after sentences
        
        # Clean up common formatting issues
        text = re.sub(r'\s+([.!?,:;])', r'\1', text)  # Remove space before punctuation
        text = re.sub(r'([.!?])\s*([A-Z])', r'\1 \2', text)  # Ensure space after sentence endings
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        # No truncation - return full article content
        return text
    
    def _extract_structured_text(self, element):
        """Extract text while preserving readable structure with better spacing"""
        text_parts = []
        
        for child in element.descendants:
            if child.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                text = child.get_text().strip()
                if text:
                    text_parts.append(f"\n\n{text}\n\n")
            elif child.name == 'p':
                text = child.get_text().strip()
                if text and len(text) > 10:
                    text_parts.append(f"{text}\n\n")
            elif child.name == 'blockquote':
                text = child.get_text().strip()
                if text:
                    text_parts.append(f"\n{text}\n\n")
            elif child.name in ['li']:
                text = child.get_text().strip()
                if text:
                    text_parts.append(f"• {text}\n")
            elif child.name in ['pre', 'code']:
                text = child.get_text().strip()
                if text:
                    text_parts.append(f"\n{text}\n\n")
            elif child.name == 'br':
                text_parts.append("\n")
            elif child.name is None and isinstance(child, str):
                # Text node
                text = child.strip()
                if text and len(text) > 5:
                    text_parts.append(text + " ")
        
        result = ''.join(text_parts)
        
        # Additional spacing improvements
        import re
        # Ensure proper spacing around headings
        result = re.sub(r'\n{4,}', '\n\n\n', result)  # Max 3 line breaks
        # Add space after periods before capital letters (for better sentence flow)
        result = re.sub(r'\.([A-Z])', r'. \1', result)
        # Ensure list items have proper spacing
        result = re.sub(r'(\n•[^\n]+)\n([^•\n])', r'\1\n\n\2', result)
        
        return result

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
