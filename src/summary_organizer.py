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
