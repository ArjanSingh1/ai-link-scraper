import os
import json
from glob import glob

def generate_website_from_summaries(summaries_dir='summaries', output_html='website/index.html'):
    os.makedirs(os.path.dirname(output_html), exist_ok=True)
    summary_files = sorted(glob(os.path.join(summaries_dir, '*.json')))
    articles = []
    for file in summary_files:
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            articles.append(data)
    
    # Build HTML
    html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Links Dashboard</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f4f6fa; margin: 0; }
        .container { max-width: 900px; margin: 40px auto; padding: 20px; background: #fff; border-radius: 12px; box-shadow: 0 4px 24px rgba(0,0,0,0.07); }
        h1 { color: #667eea; text-align: center; }
        .article { border-bottom: 1px solid #eee; padding: 24px 0; }
        .article:last-child { border-bottom: none; }
        .title { font-size: 1.2rem; color: #222; margin-bottom: 8px; }
        .url { font-size: 0.95rem; color: #3498db; word-break: break-all; }
        .summary { margin: 12px 0; color: #444; }
        .meta { color: #888; font-size: 0.9rem; }
        .tags { margin-top: 8px; }
        .tag { display: inline-block; background: #eaf0fb; color: #667eea; border-radius: 8px; padding: 2px 10px; margin-right: 6px; font-size: 0.85rem; }
    </style>
</head>
<body>
    <div class="container">
        <h1>AI Links Dashboard</h1>
        <p style="text-align:center;color:#888;">Latest links and summaries from the AI-Links Slack channel.</p>
'''
    for art in articles:
        html += f'''<div class="article">
            <div class="title">{art.get('title','No Title')}</div>
            <div class="url"><a href="{art.get('url','')}" target="_blank">{art.get('url','')}</a></div>
            <div class="summary">{art.get('summary','')}</div>
            <div class="meta">Words: {art.get('word_count',0)} | Date: {art.get('processed_date','')} {art.get('processed_time','')}</div>
            <div class="tags">{''.join(f'<span class="tag">{tag}</span>' for tag in art.get('tags',[]))}</div>
        </div>\n'''
    html += '''    </div>\n</body>\n</html>'''
    with open(output_html, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"✅ Website updated: {output_html}")
