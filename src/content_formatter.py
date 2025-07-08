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
    
    def classify_content_type(self, content: str, title: str, url: str) -> Dict[str, Any]:
        """Classify content as 'website' or 'article' using OpenAI"""
        if not self.client:
            return self._basic_content_classification(content, title, url)
        
        try:
            prompt = f"""
Analyze this web content and classify it as either "website" or "article".

**WEBSITE**: A homepage, landing page, product page, service page, or general website content that describes a company, product, or service. Usually has navigation elements, multiple sections, and is not primarily a single piece of written content.

**ARTICLE**: A blog post, news article, research paper, tutorial, guide, or any single piece of written content that tells a story, explains a concept, or provides detailed information on a specific topic.

TITLE: {title}
URL: {url}
CONTENT SAMPLE: {content[:1500]}

Respond with JSON:
{{
    "content_type": "website" or "article",
    "confidence": 0.0-1.0,
    "reasoning": "Brief explanation of why this is classified as website or article",
    "primary_purpose": "What is the main purpose of this content?"
}}
"""
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert content classifier. Classify web content as either 'website' (homepage, product page, landing page) or 'article' (blog post, news article, tutorial, guide). Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.1
            )
            
            import json
            response_content = response.choices[0].message.content.strip()
            
            # Parse JSON response
            if response_content.startswith('```json'):
                response_content = response_content.split('```json')[1].split('```')[0].strip()
            elif response_content.startswith('```'):
                response_content = response_content.split('```')[1].split('```')[0].strip()
            
            classification = json.loads(response_content)
            
            logger.info(f"Content classified as: {classification.get('content_type')} (confidence: {classification.get('confidence', 0):.2f})")
            return classification
            
        except Exception as e:
            logger.error(f"Error classifying content with OpenAI: {e}")
            return self._basic_content_classification(content, title, url)
    
    def format_for_pdf(self, content: str, title: str, url: str) -> Dict[str, Any]:
        """Format content for PDF presentation - different handling for websites vs articles"""
        if not self.client:
            return self._basic_format_full_article(content, title, url)
        
        try:
            # First, classify the content type using OpenAI
            classification = self.classify_content_type(content, title, url)
            content_type = classification.get('content_type', 'article')
            
            logger.info(f"Content classified as: {content_type} with confidence {classification.get('confidence', 0):.2f}")
            
            if content_type == 'website':
                return self._format_website_content(content, title, url, classification)
            else:
                return self._format_article_content(content, title, url, classification)
                
        except Exception as e:
            logger.error(f"Error in format_for_pdf: {e}")
            return self._basic_format_full_article(content, title, url)
    
    def _format_website_content(self, content: str, title: str, url: str, classification: Dict[str, Any]) -> Dict[str, Any]:
        """Format website content with a brief description"""
        try:
            prompt = f"""
This is a WEBSITE (not an article). Create a brief, professional description for a PDF report.

TITLE: {title}
URL: {url}
CLASSIFICATION: {classification.get('reasoning', '')}

WEBSITE CONTENT:
{content[:2000]}  # Sample for description

Create a concise description that explains:
1. What this website is about
2. What services/products/information it provides
3. Who the target audience is
4. Key features or offerings

Response format (JSON):
{{
    "content_type": "website",
    "formatted_content": "**Website Description:**\n\n[Professional 2-3 paragraph description of the website]",
    "brief_description": "One sentence summary of what this website offers",
    "target_audience": "Who this website is for",
    "key_features": ["feature1", "feature2", "feature3"],
    "website_category": "e.g., SaaS, E-commerce, Blog, Company, Tool, etc."
}}
"""
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert at analyzing websites and creating professional descriptions. Create concise, informative descriptions for PDF reports. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.2
            )
            
            import json
            response_content = response.choices[0].message.content.strip()
            
            if response_content.startswith('```json'):
                response_content = response_content.split('```json')[1].split('```')[0].strip()
            elif response_content.startswith('```'):
                response_content = response_content.split('```')[1].split('```')[0].strip()
            
            formatted_data = json.loads(response_content)
            
            # Add metadata
            formatted_data['original_content'] = content
            formatted_data['word_count_original'] = len(content.split())
            formatted_data['content_complete'] = True
            formatted_data['formatting_notes'] = "Website content summarized with key information"
            
            logger.info(f"Successfully formatted website content for: {title}")
            return formatted_data
            
        except Exception as e:
            logger.error(f"Error formatting website content: {e}")
            return self._basic_format_website(content, title, url)
    
    def _format_article_content(self, content: str, title: str, url: str, classification: Dict[str, Any]) -> Dict[str, Any]:
        """Format article content with full transcription and formatting"""
        try:
            # Calculate appropriate max_tokens based on content length
            content_tokens = len(content) // 3  # Conservative estimate
            
            # For very long content, use chunk-based processing
            if content_tokens > 12000:
                logger.info(f"Article too long ({content_tokens} tokens), using chunk-based formatting")
                return self._format_long_content_in_chunks(content, title, url)
            
            max_tokens = min(16000, max(8000, content_tokens + 2000))
            
            prompt = f"""
This is an ARTICLE. Your task is to transcribe and format the COMPLETE article for a PDF report.

CRITICAL REQUIREMENTS:
- NEVER summarize, truncate, or omit ANY part of the article content
- Include EVERY sentence, paragraph, and detail from the original
- Only clean up formatting artifacts and improve readability
- Generate ultra-specific, detailed tags based on the exact content

FORMATTING TASKS - CRITICAL SPACING REQUIREMENTS:
1. Remove unicode artifacts: ■□▪▫●○◆◇ and similar characters
2. **MANDATORY**: Add double line breaks (\\n\\n) between ALL paragraphs
3. **MANDATORY**: Break up any paragraph longer than 5 sentences into smaller paragraphs
4. **MANDATORY**: Add spacing around lists, bullet points, and sections (\\n\\n before and after)
5. **MANDATORY**: Ensure no paragraph runs for more than 8-10 lines without a break
6. Add proper spacing after headings and subheadings
7. Improve sentence flow and readability with better punctuation spacing
8. Preserve ALL original information and context - DO NOT SUMMARIZE

SPACING EXAMPLE:
First paragraph with sentences.

Second paragraph starts here after double line break.

Third paragraph continues the content.

- Bullet point with proper spacing
- Another bullet point

Final paragraph after the list.

TITLE: {title}
URL: {url}

COMPLETE ARTICLE CONTENT TO TRANSCRIBE AND FORMAT:
{content}

Response format (JSON):
{{
    "content_type": "article",
    "formatted_content": "[COMPLETE formatted article with mandatory double spacing between paragraphs and broken up long paragraphs]",
    "article_summary": "One sentence describing what this article is about",
    "content_complete": true,
    "word_count_original": {len(content.split())},
    "formatting_notes": "Brief note about spacing and formatting improvements made"
}}

REMINDER: The formatted_content MUST contain the complete article. Do not create a summary - transcribe the entire content with better formatting.
"""
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert content formatter specializing in article readability. Your mission: 1) Preserve EVERY word of the original article, 2) Add mandatory double line breaks between ALL paragraphs, 3) Break up any paragraph longer than 5 sentences, 4) Ensure excellent readability with proper spacing. Never summarize - only improve formatting and spacing. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.1
            )
            
            import json
            response_content = response.choices[0].message.content.strip()
            
            if response_content.startswith('```json'):
                response_content = response_content.split('```json')[1].split('```')[0].strip()
            elif response_content.startswith('```'):
                response_content = response_content.split('```')[1].split('```')[0].strip()
            
            formatted_data = json.loads(response_content)
            
            # Verify content completeness
            original_word_count = len(content.split())
            formatted_word_count = len(formatted_data.get('formatted_content', '').split())
            
            # If content appears significantly truncated, fall back to basic formatting
            if formatted_word_count < original_word_count * 0.8:
                logger.warning(f"OpenAI may have truncated article content ({formatted_word_count}/{original_word_count} words). Using basic formatting.")
                return self._basic_format_full_article(content, title, url)
            
            # Add metadata and verification
            formatted_data['original_content'] = content
            formatted_data['word_count_original'] = original_word_count
            formatted_data['word_count_formatted'] = formatted_word_count
            formatted_data['completeness_ratio'] = formatted_word_count / original_word_count
            
            logger.info(f"Successfully formatted complete article for: {title} ({formatted_word_count}/{original_word_count} words preserved)")
            return formatted_data
            
        except Exception as e:
            logger.error(f"Error formatting article content: {e}")
            return self._basic_format_full_article(content, title, url)
    
    def format_for_csv(self, content: str, title: str, url: str) -> Dict[str, Any]:
        """Format content specifically for CSV presentation (simplified but full content)"""
        if not self.client:
            return self._basic_format_csv_full(content, title, url)
        
        try:
            # Use first part of content for analysis to generate ultra-specific tags
            content_sample = content[:3000] if len(content) > 3000 else content
            
            prompt = f"""
Analyze this article and generate detailed metadata for CSV export (no tags needed).

TITLE: {title}
URL: {url}

CONTENT SAMPLE:
{content_sample}

FULL CONTENT WORD COUNT: {len(content.split())}

Generate comprehensive metadata as JSON:
{{
    "category": "Specific Category",
    "subcategory": "Detailed Subcategory", 
    "primary_focus": "Main topic/technology discussed",
    "technical_level": "beginner|intermediate|advanced|expert",
    "content_type": "tutorial|research|news|analysis|documentation|tool-review|case-study",
    "key_technologies": ["tech1", "tech2", "tech3"],
    "key_concepts": ["concept1", "concept2", "concept3"]
}}
"""
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert content analyst who creates detailed metadata for articles. Focus on precise technical terms, specific technologies, exact methodologies, and detailed categorization."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
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
            
            # Ensure we have the required fields with fallbacks
            if 'category' not in formatted_data:
                formatted_data['category'] = self._determine_basic_category(content, title, url)
            
            # Add comprehensive metadata
            formatted_data['word_count'] = len(content.split())
            formatted_data['full_content'] = content  # Keep full content for CSV
            formatted_data['title'] = title
            formatted_data['url'] = url
            
            logger.info(f"Successfully generated detailed metadata for: {title}")
            return formatted_data
            
        except Exception as e:
            logger.error(f"Error formatting CSV content with OpenAI: {e}")
            return self._basic_format_csv_full(content, title, url)
    
    def _format_long_content_in_chunks(self, content: str, title: str, url: str) -> Dict[str, Any]:
        """Format very long content by processing it in chunks and combining results"""
        try:
            # Split content into manageable chunks (approximately 8000 characters each)
            chunk_size = 8000
            content_chunks = []
            
            for i in range(0, len(content), chunk_size):
                chunk = content[i:i + chunk_size]
                # Ensure we don't cut in the middle of a word
                if i + chunk_size < len(content) and not chunk.endswith(' '):
                    # Find the last space to avoid cutting words
                    last_space = chunk.rfind(' ')
                    if last_space > chunk_size * 0.8:  # Only if it's not too far back
                        chunk = chunk[:last_space]
                content_chunks.append(chunk)
            
            logger.info(f"Processing long content in {len(content_chunks)} chunks")
            
            # Process each chunk
            formatted_chunks = []
            all_tags = set()
            
            for i, chunk in enumerate(content_chunks):
                chunk_prompt = f"""
Format this chunk of a larger article. Keep ALL content exactly as provided, only clean formatting:

CHUNK {i+1}/{len(content_chunks)} of article: {title}

Content to format:
{chunk}

Return JSON:
{{
    "formatted_chunk": "[cleaned content with improved paragraph spacing - no changes to actual text]"
}}

Clean formatting artifacts, improve paragraph spacing, but preserve every word and detail.
"""
                
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "Format article chunks while preserving all content. Focus on paragraph spacing and readability. Only clean artifacts, never summarize."},
                        {"role": "user", "content": chunk_prompt}
                    ],
                    max_tokens=4000,
                    temperature=0.1
                )
                
                import json
                response_content = response.choices[0].message.content.strip()
                
                # Extract JSON
                if response_content.startswith('```json'):
                    response_content = response_content.split('```json')[1].split('```')[0].strip()
                elif response_content.startswith('```'):
                    response_content = response_content.split('```')[1].split('```')[0].strip()
                
                chunk_data = json.loads(response_content)
                formatted_chunks.append(chunk_data.get('formatted_chunk', chunk))
            
            # Combine all chunks
            formatted_content = '\n\n'.join(formatted_chunks)
            
            # Verify completeness
            original_word_count = len(content.split())
            formatted_word_count = len(formatted_content.split())
            
            logger.info(f"Chunk-based formatting complete: {formatted_word_count}/{original_word_count} words preserved")
            
            return {
                "formatted_content": formatted_content,
                "content_complete": True,
                "word_count_original": original_word_count,
                "word_count_formatted": formatted_word_count,
                "completeness_ratio": formatted_word_count / original_word_count,
                "formatting_notes": f"Processed in {len(content_chunks)} chunks to preserve full content with improved spacing"
            }
            
        except Exception as e:
            logger.error(f"Error in chunk-based formatting: {e}")
            return self._basic_format_full_article(content, title, url)

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
        
        # Better paragraph spacing and readability - ENHANCED
        cleaned_content = re.sub(r'\n{3,}', '\n\n', cleaned_content)  # Max 2 line breaks
        cleaned_content = re.sub(r'([.!?])\s*\n([A-Z])', r'\1\n\n\2', cleaned_content)  # Paragraph breaks
        cleaned_content = re.sub(r'([.!?])\s*([A-Z])', r'\1 \2', cleaned_content)  # Space after sentences
        
        # Break up very long paragraphs for much better readability
        paragraphs = cleaned_content.split('\n\n')
        improved_paragraphs = []
        
        for para in paragraphs:
            if len(para) > 400:  # Break up long paragraphs (reduced threshold)
                sentences = para.split('. ')
                current_chunk = ""
                sentence_count = 0
                
                for sentence in sentences:
                    if sentence_count < 4 and len(current_chunk + sentence + '. ') < 250:  # Max 4 sentences per paragraph
                        current_chunk += sentence + '. '
                        sentence_count += 1
                    else:
                        if current_chunk:
                            improved_paragraphs.append(current_chunk.strip())
                        current_chunk = sentence + '. '
                        sentence_count = 1
                        
                if current_chunk:
                    improved_paragraphs.append(current_chunk.strip())
            else:
                improved_paragraphs.append(para)
        
        cleaned_content = '\n\n'.join(improved_paragraphs)
        
        # Clean up spacing
        cleaned_content = re.sub(r'[ \t]+', ' ', cleaned_content)  # Multiple spaces to single
        cleaned_content = re.sub(r'\n[ \t]+', '\n', cleaned_content)  # Remove leading whitespace
        cleaned_content = re.sub(r'[ \t]+\n', '\n', cleaned_content)  # Remove trailing whitespace
        
        return {
            "formatted_content": cleaned_content.strip(),
            "original_content": content,
            "word_count_original": len(content.split()),
            "word_count_formatted": len(cleaned_content.split()),
            "content_complete": True,
            "formatting_notes": "Enhanced formatting: removed artifacts, improved paragraph spacing, broke up long paragraphs"
        }
    
    def _basic_format_csv_full(self, content: str, title: str, url: str) -> Dict[str, Any]:
        """Basic CSV formatting with full content and enhanced metadata"""
        # Basic category and metadata only - no tags
        category = self._determine_basic_category(content, title, url)
        
        return {
            "category": category,
            "subcategory": self._determine_subcategory(content, title),
            "primary_focus": self._extract_primary_focus(content, title),
            "technical_level": self._assess_technical_level(content),
            "content_type": self._determine_content_type(content, title),
            "key_technologies": self._extract_technologies(content, title),
            "key_concepts": self._extract_key_concepts(content, title),
            "word_count": len(content.split()),
            "full_content": content,
            "title": title,
            "url": url
        }
    
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
    
    def _determine_subcategory(self, content: str, title: str) -> str:
        """Determine subcategory for basic classification"""
        text = (title + " " + content).lower()
        
        if any(word in text for word in ["tutorial", "guide", "how to", "step by step"]):
            return "Tutorial/Guide"
        elif any(word in text for word in ["research", "paper", "study", "arxiv"]):
            return "Research/Academic"
        elif any(word in text for word in ["tool", "library", "framework", "package"]):
            return "Tools/Libraries"
        elif any(word in text for word in ["news", "announcement", "release", "update"]):
            return "News/Updates"
        elif any(word in text for word in ["review", "comparison", "analysis"]):
            return "Reviews/Analysis"
        else:
            return "General"
    
    def _extract_primary_focus(self, content: str, title: str) -> str:
        """Extract primary focus/topic"""
        text = (title + " " + content).lower()
        
        # Look for specific technologies or concepts mentioned frequently
        focus_keywords = {
            "Machine Learning": ["machine learning", "ml", "neural network", "training"],
            "Web Development": ["web development", "frontend", "backend", "javascript"],
            "Data Science": ["data science", "analytics", "visualization", "dataset"],
            "API Development": ["api", "rest", "graphql", "endpoint"],
            "Cloud Computing": ["cloud", "aws", "azure", "kubernetes", "docker"],
            "Cybersecurity": ["security", "cybersecurity", "encryption", "vulnerability"],
            "Artificial Intelligence": ["ai", "artificial intelligence", "gpt", "llm"],
            "Software Engineering": ["software", "programming", "development", "code"]
        }
        
        for focus, keywords in focus_keywords.items():
            if sum(1 for keyword in keywords if keyword in text) >= 2:
                return focus
        
        return "Technology"
    
    def _assess_technical_level(self, content: str) -> str:
        """Assess technical complexity level"""
        text = content.lower()
        
        # Count technical indicators
        beginner_indicators = ["introduction", "getting started", "basics", "tutorial", "simple"]
        intermediate_indicators = ["implementation", "configure", "setup", "install", "example"]
        advanced_indicators = ["optimization", "performance", "architecture", "scalability", "algorithm"]
        expert_indicators = ["research", "novel", "cutting-edge", "breakthrough", "theorem"]
        
        beginner_count = sum(1 for indicator in beginner_indicators if indicator in text)
        intermediate_count = sum(1 for indicator in intermediate_indicators if indicator in text)
        advanced_count = sum(1 for indicator in advanced_indicators if indicator in text)
        expert_count = sum(1 for indicator in expert_indicators if indicator in text)
        
        if expert_count >= 2:
            return "expert"
        elif advanced_count >= 2:
            return "advanced"
        elif intermediate_count >= 2:
            return "intermediate"
        else:
            return "beginner"
    
    def _determine_content_type(self, content: str, title: str) -> str:
        """Determine content type"""
        text = (title + " " + content).lower()
        
        if any(word in text for word in ["tutorial", "how to", "guide", "step by step"]):
            return "tutorial"
        elif any(word in text for word in ["research", "paper", "study", "findings"]):
            return "research"
        elif any(word in text for word in ["news", "announcement", "released", "launched"]):
            return "news"
        elif any(word in text for word in ["analysis", "comparison", "review", "evaluation"]):
            return "analysis"
        elif any(word in text for word in ["documentation", "docs", "reference", "api"]):
            return "documentation"
        elif any(word in text for word in ["tool", "library", "framework", "using"]):
            return "tool-review"
        elif any(word in text for word in ["case study", "implementation", "experience"]):
            return "case-study"
        else:
            return "article"
    
    def _extract_technologies(self, content: str, title: str) -> list:
        """Extract specific technologies mentioned"""
        text = (title + " " + content).lower()
        
        technologies = {
            "Python", "JavaScript", "TypeScript", "React", "Vue.js", "Angular", "Node.js",
            "TensorFlow", "PyTorch", "Keras", "Scikit-learn", "Pandas", "NumPy",
            "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Git", "GitHub",
            "PostgreSQL", "MongoDB", "Redis", "MySQL", "SQLite",
            "OpenAI", "GPT", "BERT", "Transformer", "LLM", "API", "REST", "GraphQL"
        }
        
        found_tech = []
        for tech in technologies:
            if tech.lower() in text:
                found_tech.append(tech)
        
        return found_tech[:5]  # Limit to top 5
    
    def _extract_key_concepts(self, content: str, title: str) -> list:
        """Extract key concepts from content"""
        text = (title + " " + content).lower()
        
        concepts = {
            "machine learning", "deep learning", "neural networks", "natural language processing",
            "computer vision", "data analysis", "web development", "api design",
            "cloud computing", "microservices", "containerization", "automation",
            "cybersecurity", "blockchain", "artificial intelligence", "software engineering",
            "data science", "big data", "distributed systems", "performance optimization"
        }
        
        found_concepts = []
        for concept in concepts:
            if concept in text:
                found_concepts.append(concept.title())
        
        return found_concepts[:5]  # Limit to top 5

    def _basic_content_classification(self, content: str, title: str, url: str) -> Dict[str, Any]:
        """Basic content classification without OpenAI"""
        text = (title + " " + content).lower()
        
        # Article indicators
        article_indicators = [
            "published", "author", "read more", "continue reading", "posted on",
            "written by", "article", "blog post", "tutorial", "guide", "how to",
            "step by step", "introduction", "conclusion", "in this post",
            "today we", "learn about", "research", "study", "analysis"
        ]
        
        # Website indicators  
        website_indicators = [
            "home", "about us", "contact us", "services", "products", "pricing",
            "portfolio", "team", "company", "welcome to", "we are", "our mission",
            "get started", "sign up", "login", "register", "download", "buy now",
            "features", "solutions", "enterprise", "business"
        ]
        
        article_score = sum(1 for indicator in article_indicators if indicator in text)
        website_score = sum(1 for indicator in website_indicators if indicator in text)
        
        # Check URL patterns
        if any(pattern in url.lower() for pattern in ['/blog/', '/article/', '/post/', '/news/', '/tutorial/']):
            article_score += 2
        if any(pattern in url.lower() for pattern in ['/', '/home', '/index', '/about', '/products', '/services']):
            website_score += 1
            
        # Check content length (articles tend to be longer)
        word_count = len(content.split())
        if word_count > 800:
            article_score += 1
        elif word_count < 300:
            website_score += 1
        
        # Determine classification
        if article_score > website_score:
            content_type = "article"
            confidence = min(0.8, 0.5 + (article_score - website_score) * 0.1)
        else:
            content_type = "website"
            confidence = min(0.8, 0.5 + (website_score - article_score) * 0.1)
        
        return {
            "content_type": content_type,
            "confidence": confidence,
            "reasoning": f"Basic classification based on indicators: article({article_score}) vs website({website_score})",
            "primary_purpose": "Content classification" if content_type == "article" else "Website/service description"
        }
    
    def _basic_format_website(self, content: str, title: str, url: str) -> Dict[str, Any]:
        """Basic website formatting without OpenAI"""
        # Create a simple description
        word_count = len(content.split())
        domain = url.split('/')[2] if '//' in url else url
        
        description = f"""**Website Description:**

This is the website for {title}, hosted at {domain}.

**Content Overview:**
The website contains approximately {word_count} words of content covering various sections and information about their services, products, or offerings.

**Key Information:**
- Website Title: {title}
- Domain: {domain}
- Content Length: {word_count} words
- Content Type: Website/Landing Page

**Note:** This is a website rather than a standalone article, so the full site content has been summarized above rather than transcribed in its entirety."""
        
        return {
            "content_type": "website",
            "formatted_content": description,
            "brief_description": f"Website for {title}",
            "target_audience": "General visitors",
            "key_features": self._extract_basic_features(content),
            "website_category": self._determine_website_category(content, title, url),
            "original_content": content,
            "word_count_original": word_count,
            "content_complete": True,
            "formatting_notes": "Basic website description generated"
        }
    
    def _extract_basic_features(self, content: str) -> list:
        """Extract basic features from website content"""
        text = content.lower()
        
        feature_keywords = {
            "User Authentication": ["login", "sign up", "register", "account"],
            "Contact Information": ["contact", "phone", "email", "address"],
            "Product Catalog": ["products", "catalog", "shop", "store"],
            "Service Offerings": ["services", "solutions", "offerings"],
            "About Information": ["about", "company", "team", "mission"],
            "Support": ["support", "help", "faq", "documentation"],
            "Blog/News": ["blog", "news", "articles", "posts"],
            "Pricing": ["pricing", "plans", "cost", "price"]
        }
        
        found_features = []
        for feature, keywords in feature_keywords.items():
            if any(keyword in text for keyword in keywords):
                found_features.append(feature)
        
        return found_features[:5] if found_features else ["General Website Content"]
    
    def _determine_website_category(self, content: str, title: str, url: str) -> str:
        """Determine website category"""
        text = (title + " " + content).lower()
        
        if any(word in text for word in ["saas", "software as a service", "subscription", "api"]):
            return "SaaS Platform"
        elif any(word in text for word in ["shop", "store", "buy", "cart", "ecommerce"]):
            return "E-commerce"
        elif any(word in text for word in ["company", "corporation", "business", "enterprise"]):
            return "Corporate Website"
        elif any(word in text for word in ["blog", "articles", "posts", "writing"]):
            return "Blog/Content Site"
        elif any(word in text for word in ["tool", "utility", "generator", "calculator"]):
            return "Online Tool"
        elif any(word in text for word in ["portfolio", "work", "projects", "designer"]):
            return "Portfolio"
        elif any(word in text for word in ["documentation", "docs", "guide", "reference"]):
            return "Documentation"
        else:
            return "General Website"
