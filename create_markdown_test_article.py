"""
Create a test article with various Markdown elements to test auto-formatting
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models.article import Article
from datetime import datetime
import os

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/sl_news")


async def create_markdown_test_article():
    """Create a test article with various Markdown elements"""

    # Create async engine
    engine = create_async_engine(DATABASE_URL, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Test article with various content blocks
        article = Article(
            category="analysis",
            status="published",
            title_zh="Markdown 自动排版测试文章",
            title_en="Markdown Auto-formatting Test Article",
            summary_zh="这是一篇测试文章，包含各种 Markdown 元素，用于测试自动排版功能的完整性和正确性。",
            summary_en="This is a test article containing various Markdown elements to test the completeness and correctness of auto-formatting.",
            lead_zh="本文展示了 Markdown 渲染器支持的所有内容类型，包括标题、段落、列表、代码块、引用、图片等。通过这篇文章，您可以全面了解我们的文章排版系统的强大功能。",
            lead_en="This article demonstrates all content types supported by the Markdown renderer, including headings, paragraphs, lists, code blocks, quotes, images, and more. Through this article, you can fully understand the powerful features of our article formatting system.",
            image_url="https://images.unsplash.com/photo-1516116216624-53e697fedbea?w=1200&h=600&fit=crop",
            image_caption_zh="Markdown 编辑器示意图",
            image_caption_en="Markdown Editor Illustration",
            author="测试作者 / Test Author",
            published_at=datetime.utcnow(),
            content_zh=[
                {
                    "type": "heading",
                    "text": "一、什么是 Markdown？",
                    "level": 2
                },
                {
                    "type": "paragraph",
                    "text": "Markdown 是一种轻量级标记语言，它允许人们使用易读易写的纯文本格式编写文档，然后转换成有效的 HTML 文档。Markdown 由 John Gruber 在 2004 年创建，现在已经成为世界上最流行的标记语言之一。"
                },
                {
                    "type": "heading",
                    "text": "二、Markdown 的优势",
                    "level": 2
                },
                {
                    "type": "list",
                    "items": [
                        "简单易学：语法简洁，几分钟即可上手",
                        "纯文本格式：可以使用任何文本编辑器编辑",
                        "跨平台兼容：在任何操作系统上都能正常工作",
                        "版本控制友好：纯文本格式便于使用 Git 等工具进行版本管理",
                        "专注内容：让作者专注于内容创作，而不是格式调整"
                    ]
                },
                {
                    "type": "heading",
                    "text": "三、代码示例",
                    "level": 2
                },
                {
                    "type": "paragraph",
                    "text": "Markdown 支持代码块，可以指定编程语言以获得语法高亮。以下是一个 JavaScript 示例："
                },
                {
                    "type": "code",
                    "text": "// 计算斐波那契数列\nfunction fibonacci(n) {\n  if (n <= 1) return n;\n  return fibonacci(n - 1) + fibonacci(n - 2);\n}\n\n// 使用示例\nconst result = fibonacci(10);\nconsole.log(`第 10 个斐波那契数是: ${result}`);\n\n// 输出: 第 10 个斐波那契数是: 55",
                    "language": "javascript"
                },
                {
                    "type": "paragraph",
                    "text": "这是一个 Python 示例："
                },
                {
                    "type": "code",
                    "text": "# 快速排序算法\ndef quick_sort(arr):\n    if len(arr) <= 1:\n        return arr\n    pivot = arr[len(arr) // 2]\n    left = [x for x in arr if x < pivot]\n    middle = [x for x in arr if x == pivot]\n    right = [x for x in arr if x > pivot]\n    return quick_sort(left) + middle + quick_sort(right)\n\n# 使用示例\nnumbers = [3, 6, 8, 10, 1, 2, 1]\nprint(quick_sort(numbers))\n# 输出: [1, 1, 2, 3, 6, 8, 10]",
                    "language": "python"
                },
                {
                    "type": "heading",
                    "text": "四、引用文本",
                    "level": 2
                },
                {
                    "type": "quote",
                    "text": "简洁是智慧的灵魂，冗长是肤浅的藻饰。—— 威廉·莎士比亚"
                },
                {
                    "type": "paragraph",
                    "text": "这句话完美地诠释了 Markdown 的设计哲学：用最简洁的语法表达最丰富的内容。"
                },
                {
                    "type": "heading",
                    "text": "五、图片展示",
                    "level": 2
                },
                {
                    "type": "paragraph",
                    "text": "Markdown 支持插入图片，并且我们的渲染器支持图片懒加载，提升页面性能。"
                },
                {
                    "type": "image",
                    "url": "https://images.unsplash.com/photo-1542831371-29b0f74f9713?w=800&h=400&fit=crop",
                    "caption": "编程代码示意图"
                },
                {
                    "type": "heading",
                    "text": "六、嵌套列表",
                    "level": 2
                },
                {
                    "type": "paragraph",
                    "text": "Markdown 支持多级列表，可以创建复杂的层级结构："
                },
                {
                    "type": "list",
                    "items": [
                        "前端技术栈",
                        "  - React / Vue / Angular",
                        "  - TypeScript / JavaScript",
                        "  - Tailwind CSS / Styled Components",
                        "后端技术栈",
                        "  - Node.js / Python / Go",
                        "  - PostgreSQL / MongoDB / Redis",
                        "  - Docker / Kubernetes"
                    ]
                },
                {
                    "type": "heading",
                    "text": "七、总结",
                    "level": 2
                },
                {
                    "type": "paragraph",
                    "text": "通过本文的展示，我们可以看到 Markdown 渲染器支持丰富的内容类型，包括："
                },
                {
                    "type": "list",
                    "items": [
                        "多级标题（H1-H6）",
                        "段落文本",
                        "有序和无序列表",
                        "代码块（支持语法高亮）",
                        "引用文本",
                        "图片（支持懒加载）",
                        "自动生成目录（TOC）"
                    ]
                },
                {
                    "type": "paragraph",
                    "text": "这些功能确保了文章的美观性和可读性，为读者提供了优质的阅读体验。"
                }
            ],
            content_en=[
                {
                    "type": "heading",
                    "text": "1. What is Markdown?",
                    "level": 2
                },
                {
                    "type": "paragraph",
                    "text": "Markdown is a lightweight markup language that allows people to write documents in an easy-to-read and easy-to-write plain text format, which can then be converted into valid HTML documents. Markdown was created by John Gruber in 2004 and has now become one of the most popular markup languages in the world."
                },
                {
                    "type": "heading",
                    "text": "2. Advantages of Markdown",
                    "level": 2
                },
                {
                    "type": "list",
                    "items": [
                        "Easy to learn: Simple syntax, can be mastered in minutes",
                        "Plain text format: Can be edited with any text editor",
                        "Cross-platform compatible: Works on any operating system",
                        "Version control friendly: Plain text format is easy to manage with tools like Git",
                        "Focus on content: Allows authors to focus on content creation rather than formatting"
                    ]
                },
                {
                    "type": "heading",
                    "text": "3. Code Examples",
                    "level": 2
                },
                {
                    "type": "paragraph",
                    "text": "Markdown supports code blocks with syntax highlighting. Here's a JavaScript example:"
                },
                {
                    "type": "code",
                    "text": "// Calculate Fibonacci sequence\nfunction fibonacci(n) {\n  if (n <= 1) return n;\n  return fibonacci(n - 1) + fibonacci(n - 2);\n}\n\n// Usage example\nconst result = fibonacci(10);\nconsole.log(`The 10th Fibonacci number is: ${result}`);\n\n// Output: The 10th Fibonacci number is: 55",
                    "language": "javascript"
                },
                {
                    "type": "paragraph",
                    "text": "Here's a Python example:"
                },
                {
                    "type": "code",
                    "text": "# Quick sort algorithm\ndef quick_sort(arr):\n    if len(arr) <= 1:\n        return arr\n    pivot = arr[len(arr) // 2]\n    left = [x for x in arr if x < pivot]\n    middle = [x for x in arr if x == pivot]\n    right = [x for x in arr if x > pivot]\n    return quick_sort(left) + middle + quick_sort(right)\n\n# Usage example\nnumbers = [3, 6, 8, 10, 1, 2, 1]\nprint(quick_sort(numbers))\n# Output: [1, 1, 2, 3, 6, 8, 10]",
                    "language": "python"
                },
                {
                    "type": "heading",
                    "text": "4. Blockquotes",
                    "level": 2
                },
                {
                    "type": "quote",
                    "text": "Brevity is the soul of wit. — William Shakespeare"
                },
                {
                    "type": "paragraph",
                    "text": "This quote perfectly illustrates the design philosophy of Markdown: express the richest content with the simplest syntax."
                },
                {
                    "type": "heading",
                    "text": "5. Images",
                    "level": 2
                },
                {
                    "type": "paragraph",
                    "text": "Markdown supports inserting images, and our renderer supports lazy loading to improve page performance."
                },
                {
                    "type": "image",
                    "url": "https://images.unsplash.com/photo-1542831371-29b0f74f9713?w=800&h=400&fit=crop",
                    "caption": "Programming code illustration"
                },
                {
                    "type": "heading",
                    "text": "6. Nested Lists",
                    "level": 2
                },
                {
                    "type": "paragraph",
                    "text": "Markdown supports multi-level lists for creating complex hierarchical structures:"
                },
                {
                    "type": "list",
                    "items": [
                        "Frontend Stack",
                        "  - React / Vue / Angular",
                        "  - TypeScript / JavaScript",
                        "  - Tailwind CSS / Styled Components",
                        "Backend Stack",
                        "  - Node.js / Python / Go",
                        "  - PostgreSQL / MongoDB / Redis",
                        "  - Docker / Kubernetes"
                    ]
                },
                {
                    "type": "heading",
                    "text": "7. Summary",
                    "level": 2
                },
                {
                    "type": "paragraph",
                    "text": "Through this article, we can see that the Markdown renderer supports rich content types, including:"
                },
                {
                    "type": "list",
                    "items": [
                        "Multi-level headings (H1-H6)",
                        "Paragraph text",
                        "Ordered and unordered lists",
                        "Code blocks (with syntax highlighting)",
                        "Blockquotes",
                        "Images (with lazy loading)",
                        "Automatic table of contents (TOC) generation"
                    ]
                },
                {
                    "type": "paragraph",
                    "text": "These features ensure the beauty and readability of articles, providing readers with a high-quality reading experience."
                }
            ]
        )
        
        session.add(article)
        await session.commit()
        await session.refresh(article)
        
        print(f"\n✅ Test article created successfully!")
        print(f"   ID: {article.id}")
        print(f"   Title (ZH): {article.title_zh}")
        print(f"   Title (EN): {article.title_en}")
        print(f"   Category: {article.category}")
        print(f"   Content blocks (ZH): {len(article.content_zh)}")
        print(f"   Content blocks (EN): {len(article.content_en)}")
        print(f"\n📝 Visit the article at: http://localhost:3000")
        print(f"   (Navigate to News > Analysis category)")


if __name__ == "__main__":
    asyncio.run(create_markdown_test_article())

