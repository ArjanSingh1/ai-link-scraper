#!/usr/bin/env python3
"""
Simple test script to verify the AI Link Scraper setup
"""

import sys
import os

# Add project root to path
sys.path.append('.')

def test_imports():
    """Test that all required modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        from config.settings import settings
        print("  ✅ settings")
        
        from src.utils import setup_logging, extract_urls_from_text
        print("  ✅ utils")
        
        from src.slack_client import SlackClient  
        print("  ✅ slack_client")
        
        from src.web_scraper import WebScraper
        print("  ✅ web_scraper")
        
        from src.summarizer import Summarizer
        print("  ✅ summarizer")
        
        return True
    except ImportError as e:
        print(f"  ❌ Import error: {e}")
        return False

def test_url_extraction():
    """Test URL extraction functionality"""
    print("\n🔗 Testing URL extraction...")
    
    try:
        from src.utils import extract_urls_from_text
        
        test_text = """
        Check out this article: https://example.com/article
        And this one too: https://github.com/user/repo
        Also see: http://blog.example.org/post/123
        """
        
        urls = extract_urls_from_text(test_text)
        print(f"  ✅ Extracted {len(urls)} URLs:")
        for url in urls:
            print(f"    - {url}")
        
        return len(urls) > 0
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_environment():
    """Test environment configuration"""
    print("\n⚙️  Testing environment...")
    
    env_file = '.env'
    if os.path.exists(env_file):
        print("  ✅ .env file exists")
        
        # Check if it has the required variables (even if empty)
        with open(env_file, 'r') as f:
            content = f.read()
            
        required_vars = ['SLACK_BOT_TOKEN', 'SLACK_CHANNEL_ID', 'OPENAI_API_KEY']
        for var in required_vars:
            if var in content:
                print(f"  ✅ {var} configured")
            else:
                print(f"  ⚠️  {var} not found in .env")
        
        return True
    else:
        print("  ❌ .env file not found")
        return False

def test_directories():
    """Test that required directories exist"""
    print("\n📁 Testing directories...")
    
    required_dirs = ['logs', 'summaries', 'src', 'config']
    all_exist = True
    
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"  ✅ {directory}/")
        else:
            print(f"  ❌ {directory}/ missing")
            all_exist = False
    
    return all_exist

def test_web_scraper():
    """Test web scraper with a simple example"""
    print("\n🌐 Testing web scraper...")
    
    try:
        from src.web_scraper import WebScraper
        
        scraper = WebScraper()
        # Test with httpbin which should always be available
        result = scraper.scrape_url("https://httpbin.org/html")
        
        if result and result.get('status') == 'success':
            print("  ✅ Web scraping test successful")
            print(f"    Title: {result.get('title', 'No title')[:50]}...")
            print(f"    Content length: {len(result.get('content', ''))} chars")
            return True
        else:
            print("  ⚠️  Web scraping test failed (may be network issue)")
            return False
    except Exception as e:
        print(f"  ❌ Web scraper error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 AI Link Scraper - Setup Test")
    print("=" * 40)
    
    tests = [
        test_imports,
        test_environment, 
        test_directories,
        test_url_extraction,
        test_web_scraper
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 40)
    print(f"🏁 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! Your setup looks good.")
        print("💡 Next step: Configure your .env file with API keys")
    else:
        print("⚠️  Some tests failed. Please check the setup.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
