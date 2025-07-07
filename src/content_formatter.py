"""
Content Formatter using OpenAI API

Formats scraped content for better readability in PDF and CSV outputs.
"""

import logging
from typing import Dict, Any, Optional
from config.settings import settings

logger = logging.getLogger(__name__)

class ContentFormatter:
    """Format content using OpenAI API for better presentation"""
    
    def __init__(self):
        """Initialize OpenAI client"""
        if not settings.OPENAI_API_KEY:
            logger.warning("OpenAI API key not configured. Content formatting will be basic.")
            self.client = None
        else:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
            except ImportError:
                logger.warning("OpenAI library not available. Content formatting will be basic.")
                self.client = None
    
    def format_for_pdf(self, content: str, title: str, url: str) -> Dict[str, Any]:
        """Format content specifically for PDF presentation - full article only"""
        if not self.client:
            return self._basic_format_full_article(content, title, url)
        
        try:
            prompt = f"""
Please clean and format this article content for a professional PDF report. I want the COMPLETE FULL article content, not a summary. Please:

1. Remove any formatting artifacts, unicode boxes (■□▪▫●○◆◇), special characters, and unnecessary symbols
2. Improve paragraph spacing and readability with proper line breaks
3. Keep ALL the content - do not summarize, truncate, or remove any part of the article
4. Add proper spacing between paragraphs (double line breaks)
5. Ensure sentences flow well and are easy to read
6. Generate 3-5 relevant tags/categories for the article

TITLE: {title}
URL: {url}

FULL ARTICLE CONTENT:
{content}

Please provide the response as JSON:
{{
    "formatted_content": "...",
    "tags": ["tag1", "tag2", "tag3"]
}}

CRITICAL: The formatted_content must contain the COMPLETE article - every paragraph, every sentence. Do not create summaries, highlights, or truncate anything. Just clean it up and make it more readable with better spacing.
"""
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a content formatting expert. Format the COMPLETE article content for professional PDF reports. Do not summarize - include the full article with better formatting and spacing. Always respond with valid JSON. Never truncate or summarize content."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=4000,  # Increased for full content
                temperature=0.1
            )
            
            import json
            response_content = response.choices[0].message.content.strip()
            
            # Try to extract JSON from the response if it's wrapped in markdown
            if response_content.startswith('```json'):
                response_content = response_content.split('```json')[1].split('```')[0].strip()
            elif response_content.startswith('```'):
                response_content = response_content.split('```')[1].split('```')[0].strip()
            
            formatted_data = json.loads(response_content)
            
            # Add original content as fallback
            formatted_data['original_content'] = content
            formatted_data['word_count'] = len(content.split())
            
            logger.info(f"Successfully formatted full article content for: {title}")
            return formatted_data
            
        except Exception as e:
            logger.error(f"Error formatting content with OpenAI: {e}")
            return self._basic_format_full_article(content, title, url)
    
    def format_for_csv(self, content: str, title: str, url: str) -> Dict[str, Any]:
        """Format content specifically for CSV presentation (simplified but full content)"""
        if not self.client:
            return self._basic_format_csv_full(content, title, url)
        
        try:
            prompt = f"""
Please analyze this article and provide metadata for CSV export:

TITLE: {title}
URL: {url}

CONTENT:
{content[:2000]}  # Just for analysis

Please provide:
1. 3-5 relevant tags
2. Content category (e.g., "AI/ML", "Technology", "Business", "Research", etc.)

Format as JSON:
{{
    "tags": ["tag1", "tag2", "tag3"],
    "category": "..."
}}
"""
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a content categorization expert. Analyze content and provide tags and categories. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.2
            )
            
            import json
            response_content = response.choices[0].message.content.strip()
            
            # Try to extract JSON from the response if it's wrapped in markdown
            if response_content.startswith('```json'):
                response_content = response_content.split('```json')[1].split('```')[0].strip()
            elif response_content.startswith('```'):
                response_content = response_content.split('```')[1].split('```')[0].strip()
            
            formatted_data = json.loads(response_content)
            
            # Add metadata
            formatted_data['word_count'] = len(content.split())
            formatted_data['full_content'] = content  # Keep full content for CSV
            
            logger.info(f"Successfully formatted CSV content for: {title}")
            return formatted_data
            
        except Exception as e:
            logger.error(f"Error formatting CSV content with OpenAI: {e}")
            return self._basic_format_csv_full(content, title, url)
    
    def _basic_format_full_article(self, content: str, title: str, url: str) -> Dict[str, Any]:
        """Basic full article formatting without OpenAI API"""
        # Clean the content using the same comprehensive logic as web scraper
        import re
        
        # Remove unicode box characters and other formatting artifacts (comprehensive)
        cleaned_content = re.sub(r'[■□▪▫●○◆◇▲△▼▽★☆♦♧♢♤♠♡♣♥]', '', content)  # Basic symbols
        cleaned_content = re.sub(r'[\u2580-\u259F]', '', cleaned_content)  # Block characters
        cleaned_content = re.sub(r'[\u25A0-\u25FF]', '', cleaned_content)  # Geometric shapes
        cleaned_content = re.sub(r'[\u2600-\u26FF]', '', cleaned_content)  # Miscellaneous symbols
        cleaned_content = re.sub(r'[\u2700-\u27BF]', '', cleaned_content)  # Dingbats
        cleaned_content = re.sub(r'[\u2190-\u21FF]', '', cleaned_content)  # Arrows
        cleaned_content = re.sub(r'[\u2500-\u257F]', '', cleaned_content)  # Box drawing characters
        
        # Remove specific problematic characters
        cleaned_content = re.sub(r'[‌‍‎‏]', '', cleaned_content)  # Zero-width characters
        cleaned_content = re.sub(r'[\uFEFF]', '', cleaned_content)  # Byte order mark
        cleaned_content = re.sub(r'[\u200B-\u200D]', '', cleaned_content)  # Zero-width spaces
        
        # Better paragraph spacing and readability
        cleaned_content = re.sub(r'\n{3,}', '\n\n', cleaned_content)  # Max 2 line breaks
        cleaned_content = re.sub(r'([.!?])\s*\n([A-Z])', r'\1\n\n\2', cleaned_content)  # Paragraph breaks
        cleaned_content = re.sub(r'([.!?])\s*([A-Z])', r'\1 \2', cleaned_content)  # Space after sentences
        
        # Clean up spacing
        cleaned_content = re.sub(r'[ \t]+', ' ', cleaned_content)  # Multiple spaces to single
        cleaned_content = re.sub(r'\n[ \t]+', '\n', cleaned_content)  # Remove leading whitespace
        cleaned_content = re.sub(r'[ \t]+\n', '\n', cleaned_content)  # Remove trailing whitespace
        
        # Basic tags based on content
        tags = self._extract_basic_tags(content, title)
        
        return {
            "formatted_content": cleaned_content.strip(),
            "tags": tags,
            "original_content": content,
            "word_count": len(content.split())
        }
    
    def _basic_format_csv_full(self, content: str, title: str, url: str) -> Dict[str, Any]:
        """Basic CSV formatting with full content"""
        # Basic tags and category
        tags = self._extract_basic_tags(content, title)
        category = self._determine_basic_category(content, title, url)
        
        return {
            "tags": tags,
            "category": category,
            "word_count": len(content.split()),
            "full_content": content
        }
    
    def _extract_basic_tags(self, content: str, title: str) -> list:
        """Extract basic tags from content without AI"""
        text = (title + " " + content).lower()
        
        tag_keywords = {
            "ai": ["artificial intelligence", "machine learning", "ai", "ml", "neural", "deep learning"],
            "technology": ["technology", "tech", "software", "development", "programming"],
            "research": ["research", "study", "analysis", "findings", "paper"],
            "business": ["business", "company", "startup", "enterprise", "market"],
            "code": ["code", "programming", "github", "python", "javascript"],
            "data": ["data", "dataset", "analytics", "database"],
            "api": ["api", "integration", "endpoint", "service"],
            "automation": ["automation", "workflow", "process", "efficiency"],
            "security": ["security", "privacy", "encryption", "cybersecurity"]
        }
        
        found_tags = []
        for tag, keywords in tag_keywords.items():
            if any(keyword in text for keyword in keywords):
                found_tags.append(tag)
        
        return found_tags[:5] if found_tags else ["general"]
    
    def _determine_basic_category(self, content: str, title: str, url: str) -> str:
        """Determine basic category without AI"""
        text = (title + " " + content).lower()
        
        if any(word in text for word in ["ai", "artificial intelligence", "machine learning", "neural"]):
            return "AI/ML"
        elif any(word in text for word in ["github", "code", "programming", "software"]):
            return "Development"
        elif any(word in text for word in ["research", "study", "paper", "arxiv"]):
            return "Research"
        elif any(word in text for word in ["business", "startup", "company", "market"]):
            return "Business"
        elif any(word in text for word in ["security", "privacy", "cybersecurity"]):
            return "Security"
        else:
            return "Technology"
