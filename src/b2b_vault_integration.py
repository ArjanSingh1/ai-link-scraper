"""
B2B Vault Integration Module
Provides a simplified interface to B2B Vault functionality
"""

import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class B2BVaultIntegration:
    """Simplified B2B Vault integration"""
    
    def __init__(self):
        self.base_url = "https://www.theb2bvault.com/"
        self.available_categories = [
            "All", "Content Marketing", "Demand Generation", "ABM & GTM", 
            "Paid Marketing", "Marketing Ops", "Event Marketing", "AI", 
            "Product Marketing", "Sales", "General", "Affiliate & Partnerships", 
            "Copy & Positioning"
        ]
    
    def get_demo_articles(self, category: str = "All", max_articles: int = 20) -> List[Dict]:
        """Generate demo B2B Vault articles for development"""
        demo_articles = [
            {
                "id": 1,
                "title": "The Future of B2B Sales: AI and Automation Revolution",
                "url": "https://theb2bvault.com/ai-sales-revolution",
                "publisher": "B2B Vault",
                "category": "Sales",
                "content": "Artificial intelligence is transforming B2B sales processes...",
                "summary": "AI and automation are revolutionizing B2B sales by enabling predictive analytics, intelligent lead scoring, and automated follow-up processes. Companies adopting AI-powered sales tools report 30% higher conversion rates and 25% faster deal closure times.",
                "word_count": 1850,
                "date_published": "2024-01-20",
                "date_scraped": datetime.now().isoformat()
            },
            {
                "id": 2,
                "title": "Account-Based Marketing: The Complete 2024 Playbook",
                "url": "https://theb2bvault.com/abm-playbook-2024",
                "publisher": "B2B Vault",
                "category": "ABM & GTM",
                "content": "Account-based marketing has evolved significantly...",
                "summary": "ABM success requires strategic alignment between sales and marketing teams, personalized content at scale, and sophisticated intent data analysis. This comprehensive playbook covers implementation strategies, technology stack recommendations, and measurement frameworks.",
                "word_count": 2100,
                "date_published": "2024-01-18",
                "date_scraped": datetime.now().isoformat()
            },
            {
                "id": 3,
                "title": "Content Marketing ROI: Measuring What Matters in B2B",
                "url": "https://theb2bvault.com/content-marketing-roi",
                "publisher": "B2B Vault",
                "category": "Content Marketing",
                "content": "Measuring content marketing ROI in B2B requires...",
                "summary": "B2B content marketing ROI measurement goes beyond vanity metrics to focus on pipeline influence, deal velocity, and customer lifetime value. Advanced attribution models and multi-touch analytics provide deeper insights into content performance.",
                "word_count": 1650,
                "date_published": "2024-01-15",
                "date_scraped": datetime.now().isoformat()
            },
            {
                "id": 4,
                "title": "Demand Generation in the Age of Privacy-First Marketing",
                "url": "https://theb2bvault.com/privacy-first-demand-gen",
                "publisher": "B2B Vault",
                "category": "Demand Generation",
                "content": "Privacy regulations are reshaping demand generation...",
                "summary": "Privacy-first demand generation requires new strategies including first-party data collection, consent management, and cookieless tracking alternatives. Successful B2B marketers are adapting by focusing on value exchange and transparent data practices.",
                "word_count": 1900,
                "date_published": "2024-01-12",
                "date_scraped": datetime.now().isoformat()
            },
            {
                "id": 5,
                "title": "AI-Powered Marketing Operations: Tools and Strategies",
                "url": "https://theb2bvault.com/ai-marketing-ops",
                "publisher": "B2B Vault",
                "category": "Marketing Ops",
                "content": "Marketing operations teams are leveraging AI...",
                "summary": "AI in marketing operations streamlines campaign management, automates data analysis, and enables predictive forecasting. Key applications include lead scoring automation, campaign optimization, and performance attribution modeling.",
                "word_count": 1750,
                "date_published": "2024-01-10",
                "date_scraped": datetime.now().isoformat()
            },
            {
                "id": 6,
                "title": "Event Marketing Renaissance: Hybrid Strategies That Work",
                "url": "https://theb2bvault.com/hybrid-event-marketing",
                "publisher": "B2B Vault",
                "category": "Event Marketing",
                "content": "Event marketing has transformed with hybrid approaches...",
                "summary": "Hybrid event marketing combines in-person and virtual experiences to maximize reach and engagement. Successful strategies include multi-channel promotion, interactive digital experiences, and comprehensive follow-up automation.",
                "word_count": 1550,
                "date_published": "2024-01-08",
                "date_scraped": datetime.now().isoformat()
            },
            {
                "id": 7,
                "title": "Product Marketing Alignment: Bridging Sales and Marketing",
                "url": "https://theb2bvault.com/product-marketing-alignment",
                "publisher": "B2B Vault",
                "category": "Product Marketing",
                "content": "Product marketing serves as the bridge between...",
                "summary": "Effective product marketing alignment requires clear communication channels, shared metrics, and collaborative content creation. Teams that prioritize alignment see 20% faster time-to-market and 15% higher win rates.",
                "word_count": 1800,
                "date_published": "2024-01-05",
                "date_scraped": datetime.now().isoformat()
            },
            {
                "id": 8,
                "title": "Partnership Marketing: Scaling Through Strategic Alliances",
                "url": "https://theb2bvault.com/partnership-marketing",
                "publisher": "B2B Vault",
                "category": "Affiliate & Partnerships",
                "content": "Partnership marketing creates win-win scenarios...",
                "summary": "Strategic partnership marketing leverages complementary strengths to expand market reach and accelerate growth. Key components include partner enablement, co-marketing campaigns, and shared value propositions.",
                "word_count": 1650,
                "date_published": "2024-01-03",
                "date_scraped": datetime.now().isoformat()
            },
            {
                "id": 9,
                "title": "Copy That Converts: B2B Messaging That Resonates",
                "url": "https://theb2bvault.com/b2b-copy-that-converts",
                "publisher": "B2B Vault",
                "category": "Copy & Positioning",
                "content": "B2B copywriting requires understanding of complex buyer journeys...",
                "summary": "High-converting B2B copy addresses specific pain points, demonstrates clear value propositions, and includes social proof. Effective messaging frameworks focus on outcomes rather than features and speak directly to decision-maker priorities.",
                "word_count": 1400,
                "date_published": "2024-01-01",
                "date_scraped": datetime.now().isoformat()
            },
            {
                "id": 10,
                "title": "Paid Marketing Attribution: Multi-Touch Models for B2B",
                "url": "https://theb2bvault.com/paid-marketing-attribution",
                "publisher": "B2B Vault",
                "category": "Paid Marketing",
                "content": "B2B paid marketing attribution requires sophisticated modeling...",
                "summary": "Multi-touch attribution models provide deeper insights into B2B customer journeys, enabling better budget allocation and campaign optimization. Advanced attribution helps identify the true impact of each touchpoint in complex B2B sales cycles.",
                "word_count": 1950,
                "date_published": "2023-12-28",
                "date_scraped": datetime.now().isoformat()
            }
        ]
        
        # Filter by category if specified
        if category != "All":
            demo_articles = [article for article in demo_articles if article["category"] == category]
        
        # Limit results
        return demo_articles[:max_articles]
    
    def get_statistics(self) -> Dict:
        """Get B2B Vault statistics"""
        articles = self.get_demo_articles()
        
        total_articles = len(articles)
        total_words = sum(article["word_count"] for article in articles)
        categories = len(set(article["category"] for article in articles))
        
        return {
            "total_articles": total_articles,
            "total_words": total_words,
            "categories": categories,
            "last_updated": datetime.now().isoformat()
        }
    
    def search_articles(self, query: str, category: str = "All") -> List[Dict]:
        """Search B2B Vault articles"""
        articles = self.get_demo_articles(category)
        
        if not query:
            return articles
        
        query_lower = query.lower()
        filtered_articles = []
        
        for article in articles:
            if (query_lower in article["title"].lower() or 
                query_lower in article["summary"].lower() or
                query_lower in article["category"].lower()):
                filtered_articles.append(article)
        
        return filtered_articles
    
    def simulate_scraping(self, categories: List[str], max_articles_per_category: int = 10) -> List[Dict]:
        """Simulate B2B Vault scraping process"""
        logger.info(f"Starting simulated B2B Vault scraping for categories: {categories}")
        
        all_articles = []
        
        for category in categories:
            if category == "All":
                continue
                
            category_articles = self.get_demo_articles(category, max_articles_per_category)
            all_articles.extend(category_articles)
            
            logger.info(f"Scraped {len(category_articles)} articles from {category}")
        
        logger.info(f"Total scraped articles: {len(all_articles)}")
        return all_articles
    
    def get_available_categories(self) -> List[str]:
        """Get available B2B Vault categories"""
        return self.available_categories.copy()
