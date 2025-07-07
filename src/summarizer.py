import logging
import openai
from openai import OpenAI
from config.settings import settings
from src.utils import truncate_text
import re

logger = logging.getLogger(__name__)

class Summarizer:
    def __init__(self):
        """Initialize OpenAI client"""
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.max_length = settings.SUMMARY_MAX_LENGTH
        
    def summarize_content(self, content, title=None, url=None):
        """Generate a summary of the given content using OpenAI"""
        try:
            if not content or len(content.strip()) < 50:
                logger.warning("Content too short to summarize")
                return "Content too short for meaningful summarization."
            
            # Prepare the prompt
            prompt = self._create_prompt(content, title, url)
            
            logger.info(f"Generating summary for content ({len(content)} characters)")
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that creates very concise, punchy summaries. Keep summaries to 2-3 complete sentences maximum. Always end with a complete sentence - never use ellipses (...) or trailing off. Focus only on the most important insight or takeaway."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=120,  # Slightly increased to allow for complete sentences
                temperature=0.3,
                top_p=0.9
            )
            
            summary = response.choices[0].message.content.strip()
            
            # Post-process to ensure complete sentences
            summary = self._ensure_complete_sentences(summary)
            
            # Ensure summary doesn't exceed max length (with smart truncation)
            if len(summary) > self.max_length:
                summary = truncate_text(summary, self.max_length)
            
            logger.info(f"Generated summary ({len(summary)} characters)")
            return summary
            
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return f"Error generating summary: {str(e)}"
    
    def _ensure_complete_sentences(self, text):
        """Ensure text ends with complete sentences and remove any trailing ellipses"""
        if not text:
            return text
        
        # Remove any trailing ellipses or incomplete fragments
        text = re.sub(r'\.\.\.$', '', text.strip())
        text = re.sub(r'\s*\.\.\.\s*$', '', text.strip())
        
        # If text doesn't end with proper punctuation, add a period
        if text and not text.endswith(('.', '!', '?')):
            # Check if the last character is part of an incomplete word
            # If so, find the last complete sentence
            sentence_endings = ['.', '!', '?']
            last_complete_sentence = -1
            
            for i in range(len(text) - 1, -1, -1):
                if text[i] in sentence_endings:
                    last_complete_sentence = i
                    break
            
            if last_complete_sentence > 0:
                # Truncate to the last complete sentence
                text = text[:last_complete_sentence + 1]
            else:
                # Add a period to make it complete
                text += '.'
        
        return text

    def _create_prompt(self, content, title=None, url=None):
        """Create an effective prompt for summarization"""
        # Truncate content if it's too long (GPT-3.5-turbo has token limits)
        max_content_length = 3000  # Conservative limit for tokens
        if len(content) > max_content_length:
            content = content[:max_content_length] + "..."
        
        prompt_parts = []
        
        if url:
            prompt_parts.append(f"URL: {url}")
        
        if title:
            prompt_parts.append(f"Title: {title}")
        
        prompt_parts.extend([
            "Please provide a very brief summary in 2-3 sentences maximum.",
            "Focus only on the most important insight or takeaway.",
            "",
            "Content:",
            content,
            "",
            "Summary:"
        ])
        
        return "\n".join(prompt_parts)
    
    def generate_tags(self, content, title=None):
        """Generate relevant tags for the content"""
        try:
            prompt = f"Generate 3-5 relevant tags for this content. Return only the tags separated by commas.\n\n"
            
            if title:
                prompt += f"Title: {title}\n\n"
            
            # Use first 1000 characters for tag generation
            content_sample = content[:1000] if content else ""
            prompt += f"Content: {content_sample}"
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a helpful assistant that generates relevant tags for content. Return only the tags separated by commas, no explanations."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=50,
                temperature=0.3
            )
            
            tags_text = response.choices[0].message.content.strip()
            tags = [tag.strip().lower() for tag in tags_text.split(',') if tag.strip()]
            
            logger.info(f"Generated tags: {tags}")
            return tags[:5]  # Limit to 5 tags
            
        except Exception as e:
            logger.error(f"Error generating tags: {str(e)}")
            return []
    
    def batch_summarize(self, scraped_data):
        """Summarize multiple pieces of content"""
        summaries = []
        
        for i, data in enumerate(scraped_data):
            if data.get('status') != 'success' or not data.get('content'):
                logger.warning(f"Skipping item {i+1}: {data.get('url', 'Unknown URL')}")
                continue
            
            logger.info(f"Summarizing item {i+1}/{len(scraped_data)}: {data.get('url', 'Unknown URL')}")
            
            # Generate summary
            summary = self.summarize_content(
                data['content'],
                data.get('title'),
                data.get('url')
            )
            
            # Generate tags
            tags = self.generate_tags(
                data['content'],
                data.get('title')
            )
            
            summary_data = {
                'url': data['url'],
                'title': data['title'],
                'summary': summary,
                'tags': tags,
                'word_count': data.get('word_count', 0),
                'original_content_length': len(data.get('content', ''))
            }
            
            summaries.append(summary_data)
        
        logger.info(f"Completed summarization of {len(summaries)} items")
        return summaries
