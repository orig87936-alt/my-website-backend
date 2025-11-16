"""
Test article API endpoints
"""
import requests
import json
from typing import Optional

BASE_URL = "http://localhost:8000"

# Global variable to store token and article ID
token: Optional[str] = None
article_id: Optional[str] = None


def login() -> str:
    """Login and get JWT token"""
    print("=" * 60)
    print("Logging in as admin...")
    print("=" * 60)
    
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        json={"username": "admin", "password": "admin123"}
    )
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        print(f"✅ Login successful! Token: {token[:50]}...")
        print()
        return token
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(response.text)
        return None


def test_create_article(token: str) -> Optional[str]:
    """Test creating an article"""
    print("=" * 60)
    print("Testing POST /api/v1/articles (Create Article)")
    print("=" * 60)
    
    article_data = {
        "category": "headline",
        "status": "published",
        "title_zh": "测试文章标题：FastAPI 后端开发最佳实践",
        "title_en": "Test Article: FastAPI Backend Development Best Practices",
        "summary_zh": "本文详细介绍了使用 FastAPI 框架开发高性能后端 API 的最佳实践、开发技巧和重要注意事项，帮助开发者快速上手。",
        "summary_en": "Best practices for developing high-performance backend APIs with FastAPI.",
        "lead_zh": "FastAPI 是一个现代、快速的 Python Web 框架，专为构建 API 而设计。",
        "lead_en": "FastAPI is a modern, fast Python web framework designed for building APIs.",
        "content_zh": [
            {
                "type": "heading",
                "content": "什么是 FastAPI？",
                "level": 2
            },
            {
                "type": "paragraph",
                "content": "FastAPI 是一个基于 Python 3.6+ 的现代 Web 框架，它利用了 Python 的类型提示功能来提供自动数据验证、序列化和文档生成。"
            },
            {
                "type": "heading",
                "content": "主要特性",
                "level": 2
            },
            {
                "type": "list",
                "content": "主要特性列表",
                "items": [
                    "高性能：与 NodeJS 和 Go 相当",
                    "快速开发：提高开发速度约 200-300%",
                    "减少错误：减少约 40% 的人为错误",
                    "直观：强大的编辑器支持",
                    "简单：易于学习和使用"
                ]
            }
        ],
        "content_en": [
            {
                "type": "heading",
                "content": "What is FastAPI?",
                "level": 2
            },
            {
                "type": "paragraph",
                "content": "FastAPI is a modern web framework for Python 3.6+ that leverages Python's type hints to provide automatic data validation, serialization, and documentation generation."
            },
            {
                "type": "heading",
                "content": "Key Features",
                "level": 2
            },
            {
                "type": "list",
                "content": "Key features list",
                "items": [
                    "High performance: On par with NodeJS and Go",
                    "Fast development: Increase development speed by 200-300%",
                    "Fewer bugs: Reduce about 40% of human errors",
                    "Intuitive: Great editor support",
                    "Easy: Simple to learn and use"
                ]
            }
        ],
        "image_url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png",
        "image_caption_zh": "FastAPI 官方标志",
        "image_caption_en": "FastAPI Official Logo",
        "author": "Admin"
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{BASE_URL}/api/v1/articles",
        json=article_data,
        headers=headers
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        data = response.json()
        article_id = data["id"]
        print(f"✅ Article created successfully!")
        print(f"Article ID: {article_id}")
        print(f"Title (ZH): {data['title_zh']}")
        print(f"Title (EN): {data['title_en']}")
        print()
        return article_id
    else:
        print(f"❌ Failed to create article")
        print(response.text)
        print()
        return None


def test_get_articles():
    """Test getting articles list"""
    print("=" * 60)
    print("Testing GET /api/v1/articles (Get Articles List)")
    print("=" * 60)
    
    response = requests.get(f"{BASE_URL}/api/v1/articles?page=1&page_size=10")
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Got {len(data['items'])} articles")
        print(f"Total: {data['total']}")
        print(f"Page: {data['page']}/{data['total_pages']}")
        if data['items']:
            print(f"\nFirst article:")
            print(f"  - ID: {data['items'][0]['id']}")
            print(f"  - Title (ZH): {data['items'][0]['title_zh']}")
            print(f"  - Category: {data['items'][0]['category']}")
        print()
    else:
        print(f"❌ Failed to get articles")
        print(response.text)
        print()


def test_get_article_by_id(article_id: str):
    """Test getting a single article"""
    print("=" * 60)
    print(f"Testing GET /api/v1/articles/{article_id} (Get Article by ID)")
    print("=" * 60)
    
    response = requests.get(f"{BASE_URL}/api/v1/articles/{article_id}")
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Got article successfully!")
        print(f"Title (ZH): {data['title_zh']}")
        print(f"Title (EN): {data['title_en']}")
        print(f"Content blocks (ZH): {len(data['content_zh'])}")
        print(f"Content blocks (EN): {len(data['content_en'])}")
        print()
    else:
        print(f"❌ Failed to get article")
        print(response.text)
        print()


def test_get_related_articles(article_id: str):
    """Test getting related articles"""
    print("=" * 60)
    print(f"Testing GET /api/v1/articles/{article_id}/related (Get Related Articles)")
    print("=" * 60)
    
    response = requests.get(f"{BASE_URL}/api/v1/articles/{article_id}/related?limit=6")
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Got {len(data['articles'])} related articles")
        print(f"Total in category: {data['total']}")
        print(f"Has more: {data['has_more']}")
        print()
    else:
        print(f"❌ Failed to get related articles")
        print(response.text)
        print()


def test_update_article(article_id: str, token: str):
    """Test updating an article"""
    print("=" * 60)
    print(f"Testing PUT /api/v1/articles/{article_id} (Update Article)")
    print("=" * 60)
    
    update_data = {
        "title_zh": "更新后的标题：FastAPI 后端开发完整指南",
        "status": "published"
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.put(
        f"{BASE_URL}/api/v1/articles/{article_id}",
        json=update_data,
        headers=headers
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Article updated successfully!")
        print(f"New title (ZH): {data['title_zh']}")
        print()
    else:
        print(f"❌ Failed to update article")
        print(response.text)
        print()


def test_delete_article(article_id: str, token: str):
    """Test deleting an article"""
    print("=" * 60)
    print(f"Testing DELETE /api/v1/articles/{article_id} (Delete Article)")
    print("=" * 60)
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.delete(
        f"{BASE_URL}/api/v1/articles/{article_id}",
        headers=headers
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 204:
        print(f"✅ Article deleted successfully!")
        print()
    else:
        print(f"❌ Failed to delete article")
        print(response.text)
        print()


if __name__ == "__main__":
    print("\n")
    print("🚀 Article API Tests")
    print("\n")
    
    # Login
    token = login()
    if not token:
        print("❌ Cannot proceed without authentication")
        exit(1)
    
    # Create article
    article_id = test_create_article(token)
    if not article_id:
        print("❌ Cannot proceed without article ID")
        exit(1)
    
    # Get articles list
    test_get_articles()
    
    # Get single article
    test_get_article_by_id(article_id)
    
    # Get related articles
    test_get_related_articles(article_id)
    
    # Update article
    test_update_article(article_id, token)
    
    # Delete article
    test_delete_article(article_id, token)
    
    print("=" * 60)
    print("✅ All tests completed!")
    print("=" * 60)

