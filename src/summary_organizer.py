import json
import os
from datetime import datetime
from pathlib import Path

def create_shared_summary_folder(summaries_folder, output_file="shared_summaries.md"):
    """Create a consolidated markdown file with all summaries"""
    summaries_path = Path(summaries_folder)
    
    if not summaries_path.exists():
        return None
    
    # Collect all summary files
    summary_files = list(summaries_path.glob("*.json"))
    
    if not summary_files:
        return None
    
    # Sort by creation time (newest first)
    summary_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    
    # Create markdown content
    markdown_content = f"# AI Link Summaries\n\n"
    markdown_content += f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    markdown_content += f"Total Summaries: {len(summary_files)}\n\n"
    markdown_content += "---\n\n"
    
    for i, file_path in enumerate(summary_files, 1):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                summary_data = json.load(f)
            
            title = summary_data.get('title', 'Unknown Title')
            url = summary_data.get('url', '')
            summary = summary_data.get('summary', 'No summary available')
            tags = summary_data.get('tags', [])
            word_count = summary_data.get('word_count', 0)
            processed_date = summary_data.get('processed_date', 'Unknown')
            
            markdown_content += f"## {i}. {title}\n\n"
            markdown_content += f"Link: {url}\n\n"
            markdown_content += f"Summary: {summary}\n\n"
            
            if tags:
                markdown_content += f"Tags: {', '.join(tags)}\n\n"
            
            if word_count > 0:
                markdown_content += f"Length: {word_count:,} words\n\n"
            
            markdown_content += f"Processed: {processed_date}\n\n"
            markdown_content += "---\n\n"
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            continue
    
    # Write to output file
    output_path = summaries_path.parent / output_file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    return str(output_path)

def create_summary_digest(summaries_folder, max_summaries=10):
    """Create a short digest of recent summaries for Slack"""
    summaries_path = Path(summaries_folder)
    
    if not summaries_path.exists():
        return "No summaries found."
    
    summary_files = list(summaries_path.glob("*.json"))
    
    if not summary_files:
        return "No summaries found."
    
    # Sort by creation time (newest first) and limit
    summary_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    recent_files = summary_files[:max_summaries]
    
    digest = f"📋 **Summary Digest** ({len(recent_files)} recent items)\n\n"
    
    for i, file_path in enumerate(recent_files, 1):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                summary_data = json.load(f)
            
            title = summary_data.get('title', 'Unknown Title')[:50] + "..." if len(summary_data.get('title', '')) > 50 else summary_data.get('title', 'Unknown Title')
            summary = summary_data.get('summary', 'No summary available')[:100] + "..." if len(summary_data.get('summary', '')) > 100 else summary_data.get('summary', 'No summary available')
            
            digest += f"{i}. **{title}**\n   {summary}\n\n"
            
        except Exception as e:
            continue
    
    digest += f"\n_Total summaries available: {len(summary_files)}_"
    return digest

def create_weekly_document(summaries_folder, start_date=None):
    """Create a weekly summary document (PDF-ready HTML) with summaries from the past week"""
    from datetime import datetime, timedelta
    
    summaries_path = Path(summaries_folder)
    
    if not summaries_path.exists():
        return None
    
    # Set date range for the past week if not provided
    if start_date is None:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
    else:
        end_date = start_date + timedelta(days=7)
    
    # Collect summary files from the past week
    summary_files = []
    for file_path in summaries_path.glob("*.json"):
        try:
            file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
            if start_date <= file_mtime <= end_date:
                summary_files.append(file_path)
        except Exception:
            continue
    
    if not summary_files:
        return None
    
    # Sort by creation time (newest first)
    summary_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    
    # Create HTML content for PDF generation
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Weekly AI Link Summary</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
        h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #34495e; margin-top: 30px; }}
        .summary-item {{ margin-bottom: 30px; padding: 20px; border-left: 4px solid #3498db; background-color: #f8f9fa; }}
        .url {{ color: #3498db; word-break: break-all; }}
        .tags {{ color: #7f8c8d; font-style: italic; }}
        .meta {{ color: #95a5a6; font-size: 0.9em; }}
        .toc {{ background-color: #ecf0f1; padding: 20px; margin: 20px 0; }}
        .toc ul {{ list-style-type: none; padding-left: 0; }}
        .toc li {{ margin: 5px 0; }}
        .toc a {{ text-decoration: none; color: #2c3e50; }}
        .toc a:hover {{ color: #3498db; }}
    </style>
</head>
<body>
    <h1>📊 Weekly AI Link Summary</h1>
    <p><strong>Week of:</strong> {start_date.strftime('%B %d, %Y')} - {end_date.strftime('%B %d, %Y')}</p>
    <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    <p><strong>Total Links Processed:</strong> {len(summary_files)}</p>
    
    <div class="toc">
        <h2>📋 Table of Contents</h2>
        <ul>
"""
    
    # Add table of contents
    for i, file_path in enumerate(summary_files, 1):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                summary_data = json.load(f)
            title = summary_data.get('title', 'Unknown Title')
            html_content += f'            <li><a href="#item{i}">{i}. {title}</a></li>\n'
        except Exception:
            continue
    
    html_content += """        </ul>
    </div>
    
"""
    
    # Add detailed summaries
    for i, file_path in enumerate(summary_files, 1):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                summary_data = json.load(f)
            
            title = summary_data.get('title', 'Unknown Title')
            url = summary_data.get('url', '')
            summary = summary_data.get('summary', 'No summary available')
            tags = summary_data.get('tags', [])
            word_count = summary_data.get('word_count', 0)
            processed_date = summary_data.get('processed_date', 'Unknown')
            
            html_content += f"""
    <div class="summary-item" id="item{i}">
        <h2>{i}. {title}</h2>
        <p class="url"><strong>🔗 Link:</strong> <a href="{url}" target="_blank">{url}</a></p>
        <p><strong>📝 Summary:</strong></p>
        <p>{summary}</p>
"""
            
            if tags:
                html_content += f'        <p class="tags"><strong>🏷️ Tags:</strong> {", ".join(tags)}</p>\n'
            
            html_content += f"""        <p class="meta">
            <strong>📊 Length:</strong> {word_count:,} words | 
            <strong>⏰ Processed:</strong> {processed_date}
        </p>
    </div>
"""
            
        except Exception as e:
            continue
    
    html_content += """
    <footer style="margin-top: 50px; padding-top: 20px; border-top: 1px solid #bdc3c7; text-align: center; color: #7f8c8d;">
        <p>Generated by AI Link Scraper Bot 🤖</p>
    </footer>
</body>
</html>
"""
    
    # Write HTML file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_filename = f"weekly_summary_{start_date.strftime('%Y%m%d')}_{timestamp}.html"
    output_path = summaries_path.parent / output_filename
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return str(output_path)
