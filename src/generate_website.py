import os
import json
import time
from glob import glob

def generate_website_from_summaries(summaries_dir='summaries', output_html='website/index.html'):
    os.makedirs(os.path.dirname(output_html), exist_ok=True)
    summary_files = sorted(glob(os.path.join(summaries_dir, '*.json')))
    articles = []
    for file in summary_files:
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            articles.append(data)

    # Build HTML using the old UI (from B2Bscraper.py)
    html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>B2B Vault Analysis Dashboard</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; padding: 0; }
        .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); text-align: center; color: white; margin-bottom: 40px; padding: 40px 20px; }
        .header h1 { font-size: 3rem; margin-bottom: 10px; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
        .header p { font-size: 1.2rem; opacity: 0.9; }
        .stats { display: flex; justify-content: center; gap: 30px; margin: 30px 0; flex-wrap: wrap; }
        .stat-card { background: rgba(255,255,255,0.1); padding: 20px; border-radius: 10px; text-align: center; color: white; backdrop-filter: blur(10px); }
        .stat-number { font-size: 2rem; font-weight: bold; display: block; }
        .search-box { margin: 30px 0; text-align: center; }
        .search-input { padding: 12px 20px; font-size: 16px; border: none; border-radius: 25px; width: 300px; max-width: 90%; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .articles-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(450px, 1fr)); gap: 30px; margin-top: 30px; }
        .article-card { background: white; border-radius: 15px; padding: 25px; box-shadow: 0 8px 25px rgba(0,0,0,0.1); transition: transform 0.3s ease, box-shadow 0.3s ease; border-left: 5px solid #667eea; }
        .article-card:hover { transform: translateY(-5px); box-shadow: 0 15px 35px rgba(0,0,0,0.15); }
        .article-title { color: #2c3e50; margin-bottom: 15px; font-size: 1.3rem; line-height: 1.4; }
        .article-meta { display: flex; gap: 10px; margin-bottom: 15px; flex-wrap: wrap; }
        .tab-badge { background: #667eea; color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: bold; }
        .date, .word-count, .publisher { color: #666; font-size: 0.9rem; padding: 4px 8px; background: #f8f9fa; border-radius: 15px; }
        .article-preview p { margin-bottom: 15px; color: #555; line-height: 1.6; }
        .expand-btn, .source-link { background: #667eea; color: white; border: none; padding: 10px 20px; border-radius: 25px; cursor: pointer; text-decoration: none; display: inline-block; transition: background 0.3s ease; font-size: 0.9rem; margin: 5px; }
        .expand-btn:hover, .source-link:hover { background: #5a6fd8; }
        .article-full { margin-top: 20px; padding-top: 20px; border-top: 1px solid #eee; }
        .summary-content { margin-bottom: 20px; line-height: 1.7; color: #444; }
        .article-link { text-align: center; }
        .footer { text-align: center; color: white; margin-top: 50px; padding: 20px; opacity: 0.8; }
        @media (max-width: 768px) { .articles-grid { grid-template-columns: 1fr; } .header h1 { font-size: 2rem; } .stats { gap: 15px; } }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>B2B Vault Analysis Dashboard</h1>
            <p>AI-powered B2B article summaries</p>
            <div class="stats">
                <div class="stat-card"><span class="stat-number">{}</span><span>Articles Analyzed</span></div>
                <div class="stat-card"><span class="stat-number">{:,}</span><span>Total Words</span></div>
                <div class="stat-card"><span class="stat-number">{}</span><span>Categories</span></div>
            </div>
            <div class="search-box"><input type="text" class="search-input" placeholder="Search articles..." onkeyup="searchArticles()"></div>
        </div>
        <div class="articles-grid" id="articles-grid">
'''.format(
        len(articles),
        sum(a.get('word_count', 0) for a in articles),
        len(set(a.get('tags', ['General'])[0] if a.get('tags') else 'General' for a in articles))
    )
    for i, art in enumerate(articles):
        summary_preview = art.get('summary', '')[:200] + ("..." if len(art.get('summary', '')) > 200 else "")
        word_count = art.get('word_count', 0)
        tags = art.get('tags', [])
        processed_date = art.get('processed_date', '')
        processed_time = art.get('processed_time', '')
        html += f'''<div class="article-card" id="article-{i}">
            <div class="article-header">
                <h2 class="article-title">{art.get('title','No Title')}</h2>
                <div class="article-meta">
                    <span class="date">{processed_date} {processed_time}</span>
                    <span class="word-count">{word_count} words</span>
                </div>
            </div>
            <div class="article-preview">
                <p>{summary_preview}</p>
                <button class="expand-btn" onclick="toggleArticle({i})">Read Full Summary</button>
            </div>
            <div class="article-full" id="full-{i}" style="display: none;">
                <div class="summary-content">{art.get('summary','').replace(chr(10), '<br>')}</div>
                <div class="article-link"><a href="{art.get('url','')}" target="_blank" class="source-link">View Original Article</a></div>
            </div>
        </div>\n'''
    html += '''        </div>
        <div class="footer">
            <p>Generated on {} | Powered by AI Link Scraper</p>
        </div>
    </div>
    <script>
        function toggleArticle(index) {{
            const fullDiv = document.getElementById('full-' + index);
            const btn = event.target;
            if (fullDiv.style.display === 'none') {{
                fullDiv.style.display = 'block';
                btn.textContent = 'Show Less';
            }} else {{
                fullDiv.style.display = 'none';
                btn.textContent = 'Read Full Summary';
            }}
        }}
        function searchArticles() {{
            const searchTerm = document.querySelector('.search-input').value.toLowerCase();
            const articles = document.querySelectorAll('.article-card');
            articles.forEach(article => {{
                const title = article.querySelector('.article-title').textContent.toLowerCase();
                const content = article.textContent.toLowerCase();
                if (title.includes(searchTerm) || content.includes(searchTerm)) {{
                    article.style.display = 'block';
                }} else {{
                    article.style.display = 'none';
                }}
            }});
        }}
    </script>
</body>
</html>'''.format(time.strftime('%Y-%m-%d %H:%M:%S'))
    with open(output_html, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"✅ Website updated: {output_html}")
