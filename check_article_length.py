"""
Check the length of all article fields in newsData.ts
"""
import json
import re

# Read the newsData.ts file
with open('../src/data/newsData.ts', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the article with id 'ai-hallucination'
pattern = r"'ai-hallucination':\s*\{([^}]+(?:\{[^}]*\}[^}]*)*)\}"
match = re.search(pattern, content, re.DOTALL)

if match:
    article_text = match.group(0)
    
    # Extract fields
    title_zh_match = re.search(r"titleZh:\s*'([^']*)'", article_text)
    title_en_match = re.search(r"titleEn:\s*'([^']*)'", article_text)
    lead_zh_match = re.search(r"leadZh:\s*'([^']*)'", article_text)
    lead_en_match = re.search(r"leadEn:\s*'([^']*)'", article_text)
    
    print("=== OpenAI 2025 Article Field Lengths ===\n")
    
    if title_zh_match:
        title_zh = title_zh_match.group(1)
        print(f"titleZh length: {len(title_zh)}")
        print(f"titleZh: {title_zh}\n")
    
    if title_en_match:
        title_en = title_en_match.group(1)
        print(f"titleEn length: {len(title_en)}")
        print(f"titleEn: {title_en}\n")
    
    if lead_zh_match:
        lead_zh = lead_zh_match.group(1)
        print(f"leadZh (summary_zh) length: {len(lead_zh)}")
        print(f"leadZh: {lead_zh}\n")
    
    if lead_en_match:
        lead_en = lead_en_match.group(1)
        print(f"leadEn (summary_en) length: {len(lead_en)}")
        print(f"leadEn: {lead_en}\n")
else:
    print("Article not found!")

