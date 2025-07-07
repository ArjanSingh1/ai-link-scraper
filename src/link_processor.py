import os
import csv
import json
import logging
from datetime import datetime
from src.web_scraper import WebScraper
from src.summarizer import Summarizer
from src.google_drive_client import GoogleDriveClient
from src.pdf_generator import create_pdf_report
from src.content_formatter import ContentFormatter  # Add this import

logger = logging.getLogger(__name__)

class LinkProcessor:
    """Process links for Google Drive export with enhanced content extraction and formatting"""
    
    def __init__(self, slack_client=None):
        self.scraper = WebScraper()
        self.summarizer = Summarizer()
        self.drive_client = GoogleDriveClient()
        self.slack_client = slack_client
        self.formatter = ContentFormatter()  # Add formatter
    
    def scrape_links_for_drive(self, links_data, output_folder='scraped_links'):
        """Scrape links and prepare data for Google Drive export with organized folder structure"""
        try:
            # Create main output folder with timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
            main_folder = os.path.join(output_folder, f"AI_Links_Export_{timestamp}")
            os.makedirs(main_folder, exist_ok=True)
            
            # Create organized subfolders
            subfolders = {
                'csv': os.path.join(main_folder, '📊_CSV_Data'),
                'json': os.path.join(main_folder, '🔗_JSON_Raw'),
                'html': os.path.join(main_folder, '🌐_HTML_Preview'),
                'pdf': os.path.join(main_folder, '📄_PDF_Report'),
                'summaries': os.path.join(main_folder, '📝_Article_Summaries')
            }
            
            for folder in subfolders.values():
                os.makedirs(folder, exist_ok=True)
            
            # Extract unique URLs
            urls = list(set([link['url'] for link in links_data]))
            logger.info(f"Processing {len(urls)} unique URLs for Google Drive export")
            
            # Scrape content
            scraped_data = self.scraper.batch_scrape(urls)
            successful_scrapes = [data for data in scraped_data if data.get('status') == 'success']
            
            logger.info(f"Successfully scraped {len(successful_scrapes)} out of {len(urls)} URLs")
            
            # Process each scraped item with enhanced formatting
            processed_items = []
            
            for scraped in successful_scrapes:
                # Find corresponding Slack data
                slack_data = next(
                    (link for link in links_data if link['url'] == scraped['url']),
                    {}
                )
                
                # Get display name for the user
                user_id = slack_data.get('user')
                if self.slack_client and user_id:
                    try:
                        user_display_name = self.slack_client.get_user_display_name(user_id)
                    except AttributeError:
                        # Fallback if method not available
                        user_display_name = user_id
                else:
                    user_display_name = user_id if user_id else 'Unknown'
                
                # Format content using OpenAI for better presentation
                content = scraped.get('content', '')
                title = scraped.get('title', 'No Title')
                url = scraped['url']
                
                # Get formatted content for both PDF and CSV
                pdf_formatted = self.formatter.format_for_pdf(content, title, url)
                csv_formatted = self.formatter.format_for_csv(content, title, url)
                
                # Create processed item with enhanced data
                item = {
                    'url': url,
                    'title': title,
                    'tags': csv_formatted.get('tags', self._generate_lightweight_tags(scraped)),
                    'category': csv_formatted.get('category', 'General'),
                    'word_count': scraped.get('word_count', 0),
                    'scraped_at': datetime.now().isoformat(),
                    'domain': self._extract_domain(url),
                    'slack_user': user_display_name,
                    'slack_user_id': user_id,
                    'slack_timestamp': slack_data['timestamp'].isoformat() if slack_data.get('timestamp') else None,
                    'slack_channel': slack_data.get('channel'),
                    
                    # Content variations for different outputs - NO summaries or highlights
                    'full_content': content,  # Full article content for both CSV and PDF
                    'formatted_content': pdf_formatted.get('formatted_content', content)  # Cleaned full content
                }
                
                processed_items.append(item)
                logger.info(f"Processed: {item['title'][:50]}...")
            
            # Save to organized files
            csv_file = self._save_as_csv(processed_items, subfolders['csv'])
            json_file = self._save_as_json(processed_items, subfolders['json'])
            html_file = self._save_as_html(processed_items, subfolders['html'])
            pdf_file = self._save_as_pdf(processed_items, subfolders['pdf'])
            
            # Create a summary file with full articles in the summaries folder
            summary_file = self._save_full_articles(processed_items, subfolders['summaries'])
            
            # Create a README file explaining the structure
            readme_file = self._create_readme(main_folder, len(processed_items))
            
            return {
                'processed_items': processed_items,
                'csv_file': csv_file,
                'json_file': json_file,
                'html_file': html_file,
                'pdf_file': pdf_file,
                'summary_file': summary_file,
                'readme_file': readme_file,
                'main_folder': main_folder,
                'total_processed': len(processed_items)
            }
            
        except Exception as e:
            logger.error(f"Error processing links for Google Drive: {str(e)}")
            return None
    
    def upload_to_google_drive(self, processed_data, folder_name=None):
        """Upload processed link data to Google Drive"""
        try:
            if not processed_data:
                logger.error("No processed data to upload")
                return None
            
            # Authenticate with Google Drive
            if not self.drive_client.authenticate():
                return None
            
            # Create or use folder
            if folder_name:
                # Create a new folder for this batch
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
                full_folder_name = f"{folder_name}_{timestamp}"
                folder_id = self.drive_client.create_folder(full_folder_name)
            else:
                folder_id = self.drive_client.folder_id
            
            upload_results = {}
            
            # Upload CSV file
            if processed_data.get('csv_file'):
                csv_result = self.drive_client.upload_file(
                    processed_data['csv_file'], 
                    folder_id,
                    f"scraped_links_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
                )
                if csv_result:
                    self.drive_client.make_file_public(csv_result['file_id'])
                    upload_results['csv'] = csv_result
            
            # Upload JSON file
            if processed_data.get('json_file'):
                json_result = self.drive_client.upload_file(
                    processed_data['json_file'], 
                    folder_id,
                    f"scraped_links_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
                )
                if json_result:
                    self.drive_client.make_file_public(json_result['file_id'])
                    upload_results['json'] = json_result
            
            # Upload HTML file
            if processed_data.get('html_file'):
                html_result = self.drive_client.upload_file(
                    processed_data['html_file'], 
                    folder_id,
                    f"scraped_links_{datetime.now().strftime('%Y%m%d_%H%M')}.html"
                )
                if html_result:
                    self.drive_client.make_file_public(html_result['file_id'])
                    upload_results['html'] = html_result
            
            # Upload PDF file
            if processed_data.get('pdf_file'):
                pdf_result = self.drive_client.upload_file(
                    processed_data['pdf_file'], 
                    folder_id,
                    f"scraped_links_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
                )
                if pdf_result:
                    self.drive_client.make_file_public(pdf_result['file_id'])
                    upload_results['pdf'] = pdf_result
            
            # Get folder link
            folder_link = self.drive_client.get_folder_link(folder_id)
            
            upload_results['folder_link'] = folder_link
            upload_results['folder_id'] = folder_id
            upload_results['total_items'] = processed_data['total_processed']
            
            logger.info(f"✅ Successfully uploaded {len(upload_results)-2} files to Google Drive")
            if folder_link:
                logger.info(f"📁 Folder link: {folder_link}")
            
            return upload_results
            
        except Exception as e:
            logger.error(f"Error uploading to Google Drive: {str(e)}")
            return None
    
    def _generate_lightweight_tags(self, scraped_data):
        """Generate more specific and accurate tags without full AI analysis"""
        try:
            title = scraped_data.get('title', '').lower()
            content = scraped_data.get('content', '').lower()
            url = scraped_data.get('url', '').lower()
            domain = self._extract_domain(scraped_data.get('url', ''))
            
            tags = []
            
            # AI & Machine Learning Keywords (more specific)
            ai_keywords = {
                'ai': ['artificial intelligence', 'machine learning', 'deep learning', 'neural network', 'llm', 'gpt', 'claude', 'openai', 'anthropic'],
                'ml-tools': ['pytorch', 'tensorflow', 'huggingface', 'transformers', 'diffusion', 'stable diffusion'],
                'ai-agents': ['agent', 'autonomous', 'multi-agent', 'orchestrator', 'workflow automation'],
                'prompt-engineering': ['prompt', 'few-shot', 'chain-of-thought', 'reasoning'],
                'computer-vision': ['computer vision', 'image recognition', 'object detection', 'diffusion'],
                'nlp': ['natural language', 'text generation', 'sentiment analysis', 'language model']
            }
            
            # Development & Technical Keywords
            dev_keywords = {
                'python': ['python', 'django', 'flask', 'fastapi', 'pandas', 'numpy'],
                'javascript': ['javascript', 'nodejs', 'react', 'vue', 'angular', 'typescript'],
                'api-dev': ['api', 'rest', 'graphql', 'microservices', 'backend'],
                'devops': ['docker', 'kubernetes', 'aws', 'gcp', 'azure', 'terraform', 'ci/cd'],
                'data-science': ['data science', 'analytics', 'visualization', 'jupyter', 'notebook'],
                'blockchain': ['blockchain', 'crypto', 'web3', 'ethereum', 'bitcoin']
            }
            
            # Business & Industry Keywords
            business_keywords = {
                'startup': ['startup', 'entrepreneur', 'funding', 'seed', 'series a', 'venture capital'],
                'product-mgmt': ['product management', 'product strategy', 'roadmap', 'user experience'],
                'business-strategy': ['strategy', 'market analysis', 'competition', 'growth'],
                'finance': ['finance', 'investment', 'fintech', 'banking', 'economics'],
                'evals': ['evaluation', 'testing', 'benchmark', 'metrics', 'assessment']
            }
            
            # Content Type Keywords
            content_type_keywords = {
                'tutorial': ['tutorial', 'how to', 'guide', 'step by step', 'walkthrough'],
                'research': ['research', 'paper', 'study', 'analysis', 'findings'],
                'tool-review': ['review', 'comparison', 'vs', 'best', 'top'],
                'announcement': ['announcement', 'release', 'launch', 'introducing', 'new'],
                'opinion': ['opinion', 'thoughts', 'perspective', 'believe', 'think']
            }
            
            # Check AI keywords first (most specific)
            for tag, keywords in ai_keywords.items():
                if any(keyword in title or keyword in content[:1000] for keyword in keywords):
                    tags.append(tag)
            
            # Check development keywords
            for tag, keywords in dev_keywords.items():
                if any(keyword in title or keyword in content[:1000] or keyword in url for keyword in keywords):
                    tags.append(tag)
            
            # Check business keywords
            for tag, keywords in business_keywords.items():
                if any(keyword in title or keyword in content[:1000] for keyword in keywords):
                    tags.append(tag)
            
            # Check content type keywords
            for tag, keywords in content_type_keywords.items():
                if any(keyword in title or keyword in content[:500] for keyword in keywords):
                    tags.append(tag)
            
            # Add platform-specific tags
            platform_tags = {
                'github.com': 'open-source',
                'arxiv.org': 'academic',
                'medium.com': 'blog',
                'substack.com': 'newsletter',
                'youtube.com': 'video',
                'youtu.be': 'video',
                'linkedin.com': 'professional',
                'twitter.com': 'social',
                'x.com': 'social',
                'huggingface.co': 'ml-models',
                'kaggle.com': 'data-science',
                'stackoverflow.com': 'q-and-a',
                'reddit.com': 'discussion',
                'techcrunch.com': 'tech-news',
                'coda.io': 'productivity'
            }
            
            for platform, tag in platform_tags.items():
                if platform in domain:
                    tags.append(tag)
            
            # Add content length and complexity tags
            word_count = scraped_data.get('word_count', 0)
            if word_count > 3000:
                tags.append('long-read')
            elif word_count > 1000:
                tags.append('in-depth')
            elif word_count > 300:
                tags.append('medium-read')
            elif word_count > 0:
                tags.append('quick-read')
            
            # Add trending/hot topic tags based on current tech trends
            trending_keywords = {
                'transformer': ['transformer', 'attention', 'bert', 'gpt'],
                'agents': ['ai agent', 'autonomous agent', 'multi-agent', 'agent framework'],
                'rag': ['rag', 'retrieval augmented', 'vector database', 'embedding'],
                'fine-tuning': ['fine-tuning', 'fine tune', 'training', 'custom model'],
                'code-generation': ['code generation', 'coding assistant', 'copilot', 'coder'],
                'multimodal': ['multimodal', 'vision-language', 'image-text', 'vlm']
            }
            
            for tag, keywords in trending_keywords.items():
                if any(keyword in title or keyword in content[:1000] for keyword in keywords):
                    tags.append(tag)
            
            # Ensure we have at least one meaningful tag
            if not tags:
                if 'blog' in domain or 'medium' in domain:
                    tags.append('article')
                elif any(ext in url for ext in ['.pdf', '.doc', '.paper']):
                    tags.append('document')
                else:
                    tags.append('general')
            
            # Remove duplicates and limit to most relevant tags
            unique_tags = list(set(tags))[:8]  # Limit to 8 most relevant tags
            
            return unique_tags
            
        except Exception as e:
            logger.error(f"Error generating tags: {str(e)}")
            return ['general']
    
    def _extract_domain(self, url):
        """Extract domain from URL"""
        try:
            from urllib.parse import urlparse
            return urlparse(url).netloc.lower()
        except:
            return 'unknown'
    
    def _create_content_preview(self, content, max_length=200):
        """Create a short preview of the content"""
        if not content:
            return ""
        
        # Clean and truncate content
        preview = content.strip()[:max_length]
        if len(content) > max_length:
            preview += "..."
        
        return preview
    
    def _save_as_csv(self, items, output_folder):
        """Save processed items as CSV"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M')
            csv_file = os.path.join(output_folder, f"AI_Links_Data_{timestamp}.csv")
            
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                if items:
                    writer = csv.DictWriter(f, fieldnames=items[0].keys())
                    writer.writeheader()
                    for item in items:
                        # Convert tags list to string for CSV
                        row = item.copy()
                        row['tags'] = ', '.join(row['tags']) if isinstance(row['tags'], list) else row['tags']
                        writer.writerow(row)
            
            logger.info(f"Saved CSV: {csv_file}")
            return csv_file
            
        except Exception as e:
            logger.error(f"Error saving CSV: {str(e)}")
            return None
    
    def _save_as_json(self, items, output_folder):
        """Save processed items as JSON"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M')
            json_file = os.path.join(output_folder, f"AI_Links_Raw_Data_{timestamp}.json")
            
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'scraped_at': datetime.now().isoformat(),
                    'total_items': len(items),
                    'items': items
                }, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved JSON: {json_file}")
            return json_file
            
        except Exception as e:
            logger.error(f"Error saving JSON: {str(e)}")
            return None
    
    def _save_as_html(self, items, output_folder):
        """Save processed items as HTML table"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M')
            html_file = os.path.join(output_folder, f"AI_Links_Preview_{timestamp}.html")
            
            html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Scraped Links - {datetime.now().strftime('%Y-%m-%d %H:%M')}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        .url {{ word-break: break-all; }}
        .tags {{ background-color: #e7f3ff; }}
        .preview {{ max-width: 300px; }}
    </style>
</head>
<body>
    <h1>Scraped Links Report</h1>
    <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    <p>Total Links: {len(items)}</p>
    
    <table>
        <tr>
            <th>Title</th>
            <th>URL</th>
            <th>Tags</th>
            <th>Domain</th>
            <th>Word Count</th>
            <th>Preview</th>
            <th>Slack User</th>
        </tr>
"""
            
            for item in items:
                tags_str = ', '.join(item['tags']) if isinstance(item['tags'], list) else item['tags']
                html_content += f"""
        <tr>
            <td>{item.get('title', 'No Title')}</td>
            <td class="url"><a href="{item['url']}" target="_blank">{item['url']}</a></td>
            <td class="tags">{tags_str}</td>
            <td>{item.get('domain', 'Unknown')}</td>
            <td>{item.get('word_count', 0)}</td>
            <td class="preview">{item.get('content_preview', '')}</td>
            <td>{item.get('slack_user', 'Unknown')}</td>
        </tr>
"""
            
            html_content += """
    </table>
</body>
</html>
"""
            
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"Saved HTML: {html_file}")
            return html_file
            
        except Exception as e:
            logger.error(f"Error saving HTML: {str(e)}")
            return None
    
    def _save_as_pdf(self, items, output_folder):
        """Save processed items as a beautifully formatted PDF"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M')
            pdf_file = os.path.join(output_folder, f"AI_Links_Report_{timestamp}.pdf")
            
            # Create PDF title
            title = f"AI Link Collection Report - {datetime.now().strftime('%Y-%m-%d')}"
            
            # Generate PDF report
            success = create_pdf_report(
                data=items,
                output_path=pdf_file,
                title=title,
                include_content=True
            )
            
            if success:
                logger.info(f"Saved PDF: {pdf_file}")
                return pdf_file
            else:
                logger.error("Failed to generate PDF report")
                return None
                
        except Exception as e:
            logger.error(f"Error saving PDF: {str(e)}")
            return None
        
    def _save_full_articles(self, items, output_folder):
        """Save full articles as individual text files"""
        try:
            for i, item in enumerate(items, 1):
                # Create a safe filename
                safe_title = "".join(c for c in item['title'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
                safe_title = safe_title[:50]  # Limit length
                filename = f"{i:03d}_{safe_title}.txt"
                file_path = os.path.join(output_folder, filename)
                
                # Create content with metadata
                content = f"""Title: {item['title']}
URL: {item['url']}
Domain: {item['domain']}
Category: {item['category']}
Tags: {', '.join(item['tags']) if isinstance(item['tags'], list) else item['tags']}
Word Count: {item['word_count']:,}
Shared by: {item['slack_user']}
Date: {item['slack_timestamp'][:10] if item['slack_timestamp'] else 'Unknown'}

{'-' * 80}

{item['formatted_content']}
"""
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            # Create an index file
            index_file = os.path.join(output_folder, "📋_INDEX.txt")
            with open(index_file, 'w', encoding='utf-8') as f:
                f.write("AI LINKS - FULL ARTICLES INDEX\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"Total Articles: {len(items)}\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                for i, item in enumerate(items, 1):
                    f.write(f"{i:03d}. {item['title']}\n")
                    f.write(f"     📊 {item['word_count']:,} words | 🏷️ {item['category']} | 👤 {item['slack_user']}\n")
                    f.write(f"     🔗 {item['url']}\n\n")
            
            logger.info(f"Saved {len(items)} full articles to: {output_folder}")
            return output_folder
            
        except Exception as e:
            logger.error(f"Error saving full articles: {str(e)}")
            return None
    
    def _create_readme(self, main_folder, total_items):
        """Create a README file explaining the folder structure"""
        try:
            readme_file = os.path.join(main_folder, "📖_README.md")
            
            readme_content = f"""# AI Links Export Report

Generated on: **{datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}**  
Total Links Processed: **{total_items}**

## 📁 Folder Structure

### 📊 CSV Data
- **Purpose**: Spreadsheet-compatible data with all metadata
- **Best for**: Data analysis, filtering, sorting
- **Contains**: Full article content in structured format

### 🔗 JSON Raw  
- **Purpose**: Complete structured data in JSON format
- **Best for**: Programming, API integration, data processing
- **Contains**: All scraped data with full content

### 🌐 HTML Preview
- **Purpose**: Web-viewable summary with links
- **Best for**: Quick browsing, sharing via web
- **Contains**: Formatted preview with clickable links

### 📄 PDF Report
- **Purpose**: Professional presentation format
- **Best for**: Reading, printing, formal sharing
- **Contains**: Complete articles with professional formatting

### 📝 Article Summaries
- **Purpose**: Individual full article text files
- **Best for**: Reading individual articles, text analysis
- **Contains**: One file per article with complete content

## 🚀 Usage Tips

1. **For Data Analysis**: Use the CSV files
2. **For Reading**: Use the PDF report or individual text files
3. **For Programming**: Use the JSON files
4. **For Quick Preview**: Open the HTML file in your browser

## 📋 Content Quality

- ✅ **Full Articles**: Complete content extracted (no summaries)
- ✅ **Clean Text**: Unicode artifacts and formatting issues removed
- ✅ **Well Spaced**: Proper paragraph breaks and readability
- ✅ **Metadata Rich**: Tags, categories, and source information included

---
*Generated by AI Link Scraper - Fully automated link processing with content extraction*
"""
            
            with open(readme_file, 'w', encoding='utf-8') as f:
                f.write(readme_content)
            
            logger.info(f"Created README: {readme_file}")
            return readme_file
            
        except Exception as e:
            logger.error(f"Error creating README: {str(e)}")
            return None
