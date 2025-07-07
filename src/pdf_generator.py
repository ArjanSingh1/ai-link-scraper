"""
PDF Generator for AI Link Scraper

Creates beautifully formatted PDF reports from scraped link data.
Supports both detailed summaries and simple link collections.
"""

import os
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import tempfile

logger = logging.getLogger(__name__)

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.colors import HexColor, black, white, grey
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, PageBreak, 
        Table, TableStyle, Frame, PageTemplate
    )
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
    from reportlab.platypus.tableofcontents import TableOfContents
    REPORTLAB_AVAILABLE = True
except ImportError:
    logger.warning("ReportLab not available. PDF generation will use HTML-to-PDF conversion.")
    REPORTLAB_AVAILABLE = False

try:
    import weasyprint
    WEASYPRINT_AVAILABLE = True
except ImportError:
    logger.warning("WeasyPrint not available. Some PDF features may be limited.")
    WEASYPRINT_AVAILABLE = False


class PDFGenerator:
    """Generate beautifully formatted PDF reports from link data"""
    
    def __init__(self):
        self.styles = self._create_styles()
    
    def _create_styles(self):
        """Create custom styles for the PDF"""
        if not REPORTLAB_AVAILABLE:
            return None
            
        styles = getSampleStyleSheet()
        
        # Custom styles with modern design
        styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=styles['Title'],
            fontSize=28,
            spaceAfter=30,
            textColor=HexColor('#1e293b'),
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        styles.add(ParagraphStyle(
            name='Subtitle',
            parent=styles['Normal'],
            fontSize=14,
            spaceAfter=20,
            textColor=HexColor('#64748b'),
            alignment=TA_CENTER,
            fontName='Helvetica'
        ))
        
        styles.add(ParagraphStyle(
            name='SectionTitle',
            parent=styles['Heading2'],
            fontSize=20,
            spaceBefore=25,
            spaceAfter=15,
            textColor=HexColor('#1e293b'),
            leftIndent=0,
            fontName='Helvetica-Bold'
        ))
        
        styles.add(ParagraphStyle(
            name='LinkTitle',
            parent=styles['Heading3'],
            fontSize=14,
            spaceBefore=20,
            spaceAfter=8,
            textColor=HexColor('#3b82f6'),
            leftIndent=0,
            fontName='Helvetica-Bold'
        ))
        
        styles.add(ParagraphStyle(
            name='LinkURL',
            parent=styles['Normal'],
            fontSize=9,
            spaceBefore=5,
            spaceAfter=8,
            textColor=HexColor('#3b82f6'),
            leftIndent=20,
            fontName='Courier'
        ))
        
        styles.add(ParagraphStyle(
            name='Summary',
            parent=styles['Normal'],
            fontSize=10,
            spaceBefore=8,
            spaceAfter=12,
            alignment=TA_JUSTIFY,
            leftIndent=20,
            rightIndent=20,
            textColor=HexColor('#475569')
        ))
        
        styles.add(ParagraphStyle(
            name='MetaInfo',
            parent=styles['Normal'],
            fontSize=9,
            spaceBefore=8,
            spaceAfter=15,
            textColor=HexColor('#64748b'),
            leftIndent=20
        ))
        
        styles.add(ParagraphStyle(
            name='TOCEntry',
            parent=styles['Normal'],
            fontSize=11,
            spaceBefore=4,
            spaceAfter=4,
            leftIndent=10,
            textColor=HexColor('#1e293b')
        ))
        
        styles.add(ParagraphStyle(
            name='TagStyle',
            parent=styles['Normal'],
            fontSize=8,
            spaceBefore=5,
            spaceAfter=5,
            textColor=HexColor('#3b82f6'),
            leftIndent=20
        ))
        
        return styles
    
    def generate_link_report_pdf(self, data: List[Dict[str, Any]], 
                                output_path: str, 
                                title: str = "AI Link Collection Report",
                                include_content: bool = True) -> bool:
        """Generate a comprehensive PDF report from link data"""
        
        if not REPORTLAB_AVAILABLE:
            return self._generate_html_to_pdf(data, output_path, title, include_content)
        
        try:
            # Create PDF document
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )
            
            # Build content
            story = []
            
            # Title page
            story.extend(self._create_title_page(title, len(data)))
            story.append(PageBreak())
            
            # Table of contents
            if len(data) > 5:
                story.extend(self._create_table_of_contents(data))
                story.append(PageBreak())
            
            # Main content
            story.extend(self._create_main_content(data, include_content))
            
            # Build PDF
            doc.build(story)
            logger.info(f"PDF report generated successfully: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error generating PDF: {e}")
            return False
    
    def _create_title_page(self, title: str, item_count: int) -> List:
        """Create the title page"""
        story = []
        
        # Main title
        story.append(Paragraph(title, self.styles['CustomTitle']))
        story.append(Spacer(1, 0.5*inch))
        
        # Subtitle with metadata
        subtitle = f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}"
        story.append(Paragraph(subtitle, self.styles['Subtitle']))
        
        count_text = f"Total Items: {item_count}"
        story.append(Paragraph(count_text, self.styles['Subtitle']))
        
        # Add some space and a decorative element
        story.append(Spacer(1, 1*inch))
        
        # Summary statistics
        stats_data = [
            ['Report Statistics', ''],
            ['Total Links Processed', str(item_count)],
            ['Generation Date', datetime.now().strftime('%Y-%m-%d')],
            ['Generation Time', datetime.now().strftime('%H:%M:%S')],
        ]
        
        stats_table = Table(stats_data, colWidths=[3*inch, 2*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), HexColor('#ecf0f1')),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#bdc3c7'))
        ]))
        
        story.append(stats_table)
        
        return story
    
    def _create_table_of_contents(self, data: List[Dict[str, Any]]) -> List:
        """Create table of contents"""
        story = []
        
        story.append(Paragraph("Table of Contents", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.3*inch))
        
        for i, item in enumerate(data, 1):
            title = item.get('title', 'Untitled')
            if len(title) > 60:
                title = title[:60] + "..."
            
            toc_entry = f"{i}. {title}"
            story.append(Paragraph(toc_entry, self.styles['TOCEntry']))
        
        return story
    
    def _create_main_content(self, data: List[Dict[str, Any]], include_content: bool = True) -> List:
        """Create the main content section"""
        story = []
        
        story.append(Paragraph("🔗 Link Collection Details", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.3*inch))
        
        for i, item in enumerate(data, 1):
            # Add some spacing between items
            if i > 1:
                story.append(Spacer(1, 0.15*inch))
            
            # Item number and title with modern styling
            title = item.get('title', 'Untitled')
            title_text = f"<b>{i}.</b> {title}"
            story.append(Paragraph(title_text, self.styles['LinkTitle']))
            
            # URL with better formatting
            url = item.get('url', '')
            if url:
                # Truncate very long URLs for better display
                display_url = url if len(url) <= 80 else url[:77] + "..."
                url_text = f"🔗 {display_url}"
                story.append(Paragraph(url_text, self.styles['LinkURL']))
            
            # Tags with visual styling
            if item.get('tags'):
                tags = item['tags'] if isinstance(item['tags'], list) else [item['tags']]
                tags_text = "🏷️ Tags: " + " • ".join([f"<b>#{tag}</b>" for tag in tags])
                story.append(Paragraph(tags_text, self.styles['TagStyle']))
            
            # Content/Summary with better presentation
            if include_content:
                content = item.get('content_preview', item.get('summary', ''))
                if content and len(content.strip()) > 0:
                    # Truncate content if too long
                    if len(content) > 500:
                        content = content[:497] + "..."
                    content_text = f"<b>📝 Content Preview:</b><br/><br/>{content}"
                    story.append(Paragraph(content_text, self.styles['Summary']))
            
            # Metadata with icons and better formatting
            meta_items = []
            
            if item.get('domain'):
                meta_items.append(f"🌐 <b>Domain:</b> {item['domain']}")
            
            if item.get('word_count'):
                meta_items.append(f"📊 <b>Length:</b> {item['word_count']:,} words")
            
            if item.get('slack_user'):
                meta_items.append(f"👤 <b>Shared by:</b> {item['slack_user']}")
            
            if item.get('scraped_at'):
                try:
                    # Format the date nicely
                    from datetime import datetime
                    scraped_date = datetime.fromisoformat(item['scraped_at'].replace('Z', '+00:00'))
                    formatted_date = scraped_date.strftime('%b %d, %Y at %I:%M %p')
                    meta_items.append(f"⏰ <b>Processed:</b> {formatted_date}")
                except:
                    meta_items.append(f"⏰ <b>Processed:</b> {item['scraped_at']}")
            
            if meta_items:
                # Join with line breaks for better readability
                meta_text = "<br/>".join(meta_items)
                story.append(Paragraph(meta_text, self.styles['MetaInfo']))
            
            # Add a subtle separator line between items
            if i < len(data):
                # Create a light gray line
                from reportlab.platypus import HRFlowable
                story.append(Spacer(1, 0.1*inch))
                story.append(HRFlowable(width="100%", thickness=0.5, color=HexColor('#e2e8f0')))
        
        return story
    
    def _generate_html_to_pdf(self, data: List[Dict[str, Any]], 
                             output_path: str, 
                             title: str,
                             include_content: bool = True) -> bool:
        """Fallback method using HTML-to-PDF conversion"""
        
        if not WEASYPRINT_AVAILABLE:
            logger.error("Neither ReportLab nor WeasyPrint available for PDF generation")
            return False
        
        try:
            html_content = self._create_html_for_pdf(data, title, include_content)
            
            # Generate PDF from HTML
            html_doc = weasyprint.HTML(string=html_content)
            html_doc.write_pdf(output_path)
            
            logger.info(f"PDF report generated using HTML conversion: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error generating PDF using HTML conversion: {e}")
            return False
    
    def _create_html_for_pdf(self, data: List[Dict[str, Any]], 
                            title: str, 
                            include_content: bool = True) -> str:
        """Create HTML content optimized for PDF conversion"""
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        @page {{
            size: A4;
            margin: 0.8in;
            @top-center {{
                content: "{title}";
                font-size: 9px;
                color: #94a3b8;
                font-family: 'Inter', sans-serif;
                margin-top: 0.3in;
            }}
            @bottom-right {{
                content: "Page " counter(page);
                font-size: 9px;
                color: #94a3b8;
                font-family: 'Inter', sans-serif;
                margin-bottom: 0.3in;
            }}
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            line-height: 1.6;
            color: #1e293b;
            font-size: 10px;
            font-weight: 400;
        }}
        
        .title-page {{
            text-align: center;
            page-break-after: always;
            padding-top: 2.5in;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
        }}
        
        .main-title {{
            font-size: 36px;
            font-weight: 700;
            margin-bottom: 0.5in;
            text-shadow: 0 2px 4px rgba(0,0,0,0.1);
            letter-spacing: -0.02em;
        }}
        
        .subtitle {{
            font-size: 16px;
            font-weight: 400;
            margin-bottom: 0.3in;
            opacity: 0.9;
        }}
        
        .stats-card {{
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            border-radius: 12px;
            padding: 2rem;
            margin-top: 1in;
            border: 1px solid rgba(255,255,255,0.2);
        }}
        
        .stats-table {{
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
            background: rgba(255,255,255,0.95);
            border-radius: 8px;
            overflow: hidden;
            color: #1e293b;
        }}
        
        .stats-table th {{
            background: linear-gradient(135deg, #3b82f6, #1d4ed8);
            color: white;
            padding: 12px 16px;
            text-align: left;
            font-weight: 600;
            font-size: 12px;
        }}
        
        .stats-table td {{
            padding: 10px 16px;
            border-bottom: 1px solid #e2e8f0;
            font-size: 11px;
        }}
        
        .stats-table tr:last-child td {{
            border-bottom: none;
        }}
        
        .stats-table tr:nth-child(even) {{
            background-color: #f8fafc;
        }}
        
        .toc {{
            page-break-after: always;
            padding: 2rem 0;
        }}
        
        .toc h1 {{
            color: #1e293b;
            text-align: center;
            margin-bottom: 2rem;
            font-size: 28px;
            font-weight: 700;
            position: relative;
        }}
        
        .toc h1::after {{
            content: '';
            position: absolute;
            bottom: -10px;
            left: 50%;
            transform: translateX(-50%);
            width: 60px;
            height: 3px;
            background: linear-gradient(135deg, #3b82f6, #1d4ed8);
            border-radius: 2px;
        }}
        
        .toc-entry {{
            margin: 12px 0;
            padding: 8px 12px;
            border-radius: 6px;
            transition: background-color 0.2s;
            border-left: 3px solid #e2e8f0;
        }}
        
        .toc-entry:hover {{
            background-color: #f1f5f9;
            border-left-color: #3b82f6;
        }}
        
        .section-break {{
            page-break-before: always;
            padding-top: 1rem;
        }}
        
        .section-title {{
            color: #1e293b;
            font-size: 28px;
            font-weight: 700;
            margin-bottom: 2rem;
            text-align: center;
            position: relative;
        }}
        
        .section-title::after {{
            content: '';
            position: absolute;
            bottom: -10px;
            left: 50%;
            transform: translateX(-50%);
            width: 80px;
            height: 3px;
            background: linear-gradient(135deg, #3b82f6, #1d4ed8);
            border-radius: 2px;
        }}
        
        .link-item {{
            margin-bottom: 2rem;
            background: white;
            border-radius: 12px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05), 0 1px 2px rgba(0,0,0,0.1);
            padding: 1.5rem;
            page-break-inside: avoid;
            border-left: 4px solid #3b82f6;
            position: relative;
        }}
        
        .link-item::before {{
            content: counter(item-counter);
            counter-increment: item-counter;
            position: absolute;
            top: -8px;
            left: -8px;
            background: linear-gradient(135deg, #3b82f6, #1d4ed8);
            color: white;
            width: 24px;
            height: 24px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 10px;
            font-weight: 600;
        }}
        
        .links-container {{
            counter-reset: item-counter;
        }}
        
        .link-title {{
            font-size: 16px;
            font-weight: 600;
            color: #1e293b;
            margin-bottom: 0.5rem;
            line-height: 1.4;
        }}
        
        .link-url {{
            color: #3b82f6;
            font-size: 9px;
            word-break: break-all;
            margin-bottom: 0.75rem;
            padding: 6px 10px;
            background: #eff6ff;
            border-radius: 6px;
            font-family: 'Monaco', 'Menlo', monospace;
        }}
        
        .link-content {{
            margin: 1rem 0;
            padding: 1rem;
            background: #f8fafc;
            border-radius: 8px;
            border-left: 3px solid #e2e8f0;
            font-size: 11px;
            line-height: 1.6;
            text-align: justify;
        }}
        
        .content-label {{
            font-weight: 600;
            color: #475569;
            margin-bottom: 0.5rem;
            display: block;
            font-size: 11px;
        }}
        
        .link-meta {{
            display: flex;
            flex-wrap: wrap;
            gap: 1rem;
            margin-top: 1rem;
            padding-top: 1rem;
            border-top: 1px solid #e2e8f0;
            font-size: 9px;
        }}
        
        .meta-item {{
            display: flex;
            align-items: center;
            color: #64748b;
            background: #f1f5f9;
            padding: 4px 8px;
            border-radius: 4px;
            font-weight: 500;
        }}
        
        .meta-icon {{
            margin-right: 4px;
            font-size: 10px;
        }}
        
        .tags {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin: 0.75rem 0;
        }}
        
        .tag {{
            background: linear-gradient(135deg, #3b82f6, #1d4ed8);
            color: white;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 9px;
            font-weight: 500;
        }}
        
        .footer {{
            margin-top: 3rem;
            text-align: center;
            color: #94a3b8;
            font-size: 10px;
            padding: 2rem;
            border-top: 1px solid #e2e8f0;
        }}
        
        .footer-logo {{
            font-weight: 600;
            color: #3b82f6;
        }}
    </style>
</head>
<body>
    <div class="title-page">
        <h1 class="main-title">{title}</h1>
        <p class="subtitle">Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
        <p class="subtitle">Total Items Processed: {len(data)}</p>
        
        <div class="stats-card">
            <table class="stats-table">
                <tr>
                    <th>Report Statistics</th>
                    <th>Value</th>
                </tr>
                <tr>
                    <td>Total Links Processed</td>
                    <td>{len(data)}</td>
                </tr>
                <tr>
                    <td>Generation Date</td>
                    <td>{datetime.now().strftime('%B %d, %Y')}</td>
                </tr>
                <tr>
                    <td>Generation Time</td>
                    <td>{datetime.now().strftime('%I:%M %p')}</td>
                </tr>
                <tr>
                    <td>Processing Status</td>
                    <td>Complete</td>
                </tr>
            </table>
        </div>
    </div>
"""
        
        # Table of contents
        if len(data) > 5:
            html += '''
    <div class="toc">
        <h1>📋 Table of Contents</h1>
        <div style="max-width: 600px; margin: 0 auto;">'''
            for i, item in enumerate(data, 1):
                title_text = item.get('title', 'Untitled')
                if len(title_text) > 70:
                    title_text = title_text[:70] + "..."
                domain = item.get('domain', 'Unknown')
                html += f'''
            <div class="toc-entry">
                <strong>{i}.</strong> {title_text}
                <div style="font-size: 8px; color: #94a3b8; margin-top: 2px;">🌐 {domain}</div>
            </div>'''
            html += '''
        </div>
    </div>'''
        
        # Main content
        html += '''
    <div class="section-break">
        <h1 class="section-title">🔗 Link Collection Details</h1>
        <div class="links-container">'''
        
        for i, item in enumerate(data, 1):
            title_text = item.get('title', 'Untitled')
            url = item.get('url', '')
            domain = item.get('domain', 'Unknown')
            
            html += f'''
        <div class="link-item">
            <div class="link-title">{title_text}</div>
            <div class="link-url">🔗 {url}</div>'''
            
            # Tags
            if item.get('tags'):
                tags = item['tags'] if isinstance(item['tags'], list) else [item['tags']]
                html += '<div class="tags">'
                for tag in tags:
                    html += f'<span class="tag">#{tag}</span>'
                html += '</div>'
            
            # Content
            if include_content:
                content = item.get('content_preview', item.get('summary', ''))
                if content and len(content.strip()) > 0:
                    html += f'''
            <div class="link-content">
                <span class="content-label">📝 Content Preview:</span>
                {content}
            </div>'''
            
            # Metadata
            meta_items = []
            if domain and domain != 'Unknown':
                meta_items.append(f'<div class="meta-item"><span class="meta-icon">🌐</span>Domain: {domain}</div>')
            if item.get('word_count'):
                meta_items.append(f'<div class="meta-item"><span class="meta-icon">📊</span>Length: {item["word_count"]:,} words</div>')
            if item.get('slack_user'):
                meta_items.append(f'<div class="meta-item"><span class="meta-icon">👤</span>Shared by: {item["slack_user"]}</div>')
            if item.get('scraped_at'):
                try:
                    from datetime import datetime
                    scraped_date = datetime.fromisoformat(item['scraped_at'].replace('Z', '+00:00'))
                    formatted_date = scraped_date.strftime('%b %d, %Y at %I:%M %p')
                    meta_items.append(f'<div class="meta-item"><span class="meta-icon">⏰</span>Processed: {formatted_date}</div>')
                except:
                    meta_items.append(f'<div class="meta-item"><span class="meta-icon">⏰</span>Processed: {item["scraped_at"]}</div>')
            
            if meta_items:
                html += f'''
            <div class="link-meta">
                {"".join(meta_items)}
            </div>'''
            
            html += '''
        </div>'''
        
        html += '''
        </div>
    </div>
    
    <div class="footer">
        <p><span class="footer-logo">🤖 AI Link Scraper Bot</span></p>
        <p>Automatically generated report • {datetime.now().strftime('%Y')}</p>
    </div>
</body>
</html>'''
        
        return html


def create_pdf_report(data: List[Dict[str, Any]], 
                     output_path: str,
                     title: str = "AI Link Collection Report",
                     include_content: bool = True) -> bool:
    """Convenience function to create a PDF report"""
    generator = PDFGenerator()
    return generator.generate_link_report_pdf(data, output_path, title, include_content)
