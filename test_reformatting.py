#!/usr/bin/env python3
"""
Test script for the new article reformatting
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.content_formatter import ContentFormatter

def test_reformatting():
    # Sample article content to test
    test_content = """
    Artificial intelligence has been transforming the technology landscape at an unprecedented pace. Machine learning algorithms are now being deployed across various industries, from healthcare to finance, enabling organizations to make data-driven decisions with greater accuracy and efficiency.

    The development of large language models has particularly captured attention in recent years. These sophisticated AI systems can understand and generate human-like text, opening up new possibilities for automation and human-computer interaction. Companies are investing billions of dollars in AI research and development.

    Key benefits of AI implementation include improved efficiency, reduced costs, enhanced decision-making capabilities, and the ability to process vast amounts of data quickly. However, there are also challenges such as data privacy concerns, the need for skilled personnel, and potential job displacement.

    Organizations looking to implement AI should consider several factors: data quality and availability, technical infrastructure requirements, regulatory compliance, and employee training needs. Successful AI adoption requires a strategic approach and careful planning.

    The future of AI looks promising with continued advancements in natural language processing, computer vision, and autonomous systems. As these technologies mature, we can expect to see even more innovative applications across different sectors.
    """
    
    title = "The Impact of Artificial Intelligence on Modern Business"
    url = "https://example.com/ai-article"
    
    formatter = ContentFormatter()
    result = formatter.format_for_pdf(test_content, title, url)
    
    print("=== ORIGINAL CONTENT ===")
    print(test_content)
    print("\n=== REFORMATTED CONTENT ===")
    print(result['formatted_content'])
    print(f"\n=== STATS ===")
    print(f"Original words: {result.get('word_count_original', 'N/A')}")
    print(f"Formatted words: {result.get('word_count_formatted', 'N/A')}")
    print(f"Formatting notes: {result.get('formatting_notes', 'N/A')}")

if __name__ == "__main__":
    test_reformatting()
