import os
import csv
import json
import logging
from datetime import datetime
from src.web_scraper import WebScraper
from src.summarizer import Summarizer
from src.google_drive_client import GoogleDriveClient

logger = logging.getLogger(__name__)

class LinkProcessor:
    """Process links for Google Drive export without full summarization"""
    
    def __init__(self):
        self.scraper = WebScraper()
        self.summarizer = Summarizer()
        self.drive_client = GoogleDriveClient()
    
    def scrape_links_for_drive(self, links_data, output_folder='scraped_links'):
        """Scrape links and prepare data for Google Drive export"""
        try:
            # Create output folder
            os.makedirs(output_folder, exist_ok=True)
            
            # Extract unique URLs
            urls = list(set([link['url'] for link in links_data]))
            logger.info(f"Processing {len(urls)} unique URLs for Google Drive export")
            
            # Scrape content
            scraped_data = self.scraper.batch_scrape(urls)
            successful_scrapes = [data for data in scraped_data if data.get('status') == 'success']
            
            logger.info(f"Successfully scraped {len(successful_scrapes)} out of {len(urls)} URLs")
            
            # Process each scraped item
            processed_items = []
            
            for scraped in successful_scrapes:
                # Find corresponding Slack data
                slack_data = next(
                    (link for link in links_data if link['url'] == scraped['url']),
                    {}
                )
                
                # Generate lightweight tags (without full content analysis)
                tags = self._generate_lightweight_tags(scraped)
                
                # Create processed item
                item = {
                    'url': scraped['url'],
                    'title': scraped.get('title', 'No Title'),
                    'tags': tags,
                    'word_count': scraped.get('word_count', 0),
                    'scraped_at': datetime.now().isoformat(),
                    'domain': self._extract_domain(scraped['url']),
                    'slack_user': slack_data.get('user'),
                    'slack_timestamp': slack_data.get('timestamp').isoformat() if slack_data.get('timestamp') else None,
                    'slack_channel': slack_data.get('channel'),
                    'content_preview': self._create_content_preview(scraped.get('content', ''))
                }
                
                processed_items.append(item)
                logger.info(f"Processed: {item['title'][:50]}...")
            
            # Save to files
            csv_file = self._save_as_csv(processed_items, output_folder)
            json_file = self._save_as_json(processed_items, output_folder)
            html_file = self._save_as_html(processed_items, output_folder)
            
            return {
                'processed_items': processed_items,
                'csv_file': csv_file,
                'json_file': json_file,
                'html_file': html_file,
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
        """Generate simple tags without full AI analysis"""
        try:
            title = scraped_data.get('title', '').lower()
            content = scraped_data.get('content', '').lower()
            url = scraped_data.get('url', '').lower()
            
            tags = []
            
            # Simple keyword-based tagging
            tech_keywords = ['python', 'javascript', 'react', 'ai', 'machine learning', 'api', 'github', 'docker', 'kubernetes']
            business_keywords = ['startup', 'funding', 'business', 'strategy', 'market', 'finance', 'investment']
            news_keywords = ['news', 'update', 'release', 'announcement', 'breaking']
            
            for keyword in tech_keywords:
                if keyword in title or keyword in content[:500] or keyword in url:
                    tags.append('tech')
                    break
            
            for keyword in business_keywords:
                if keyword in title or keyword in content[:500] or keyword in url:
                    tags.append('business')
                    break
            
            for keyword in news_keywords:
                if keyword in title or keyword in content[:500] or keyword in url:
                    tags.append('news')
                    break
            
            # Add domain-based tags
            domain = self._extract_domain(scraped_data.get('url', ''))
            if 'github' in domain:
                tags.append('github')
            elif 'medium' in domain:
                tags.append('article')
            elif 'youtube' in domain:
                tags.append('video')
            elif 'twitter' in domain or 'x.com' in domain:
                tags.append('social')
            elif any(news_site in domain for news_site in ['cnn', 'bbc', 'reuters', 'techcrunch']):
                tags.append('news')
            
            # Add content length tag
            word_count = scraped_data.get('word_count', 0)
            if word_count > 2000:
                tags.append('long-read')
            elif word_count > 500:
                tags.append('article')
            else:
                tags.append('short')
            
            return list(set(tags)) if tags else ['general']
            
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
            csv_file = os.path.join(output_folder, f"scraped_links_{datetime.now().strftime('%Y%m%d_%H%M')}.csv")
            
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
            json_file = os.path.join(output_folder, f"scraped_links_{datetime.now().strftime('%Y%m%d_%H%M')}.json")
            
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
            html_file = os.path.join(output_folder, f"scraped_links_{datetime.now().strftime('%Y%m%d_%H%M')}.html")
            
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
