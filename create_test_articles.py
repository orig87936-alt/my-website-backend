"""
Create test articles for Phase 4 frontend testing

This script creates sample articles in the database for testing the
RelatedArticles component and article navigation functionality.
"""

import asyncio
import sys
import uuid
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

# Add parent directory to path
sys.path.insert(0, '.')

from app.database import AsyncSessionLocal
from app.models.article import Article


async def create_test_articles():
    """Create test articles in the database"""
    
    async with AsyncSessionLocal() as session:
        print("🚀 Creating test articles...")
        
        # Check if articles already exist
        from sqlalchemy import select
        result = await session.execute(select(Article))
        existing = result.scalars().all()
        
        if len(existing) > 0:
            print(f"⚠️  Found {len(existing)} existing articles")
            response = input("Do you want to delete them and create new ones? (y/N): ")
            if response.lower() != 'y':
                print("❌ Cancelled")
                return
            
            # Delete existing articles
            for article in existing:
                await session.delete(article)
            await session.commit()
            print("✅ Deleted existing articles")
        
        # Analysis articles (for testing related articles)
        # Valid categories: 'headline', 'regulatory', 'analysis', 'business', 'enterprise', 'outlook'
        # Note: IDs will be generated as UUIDs
        analysis_articles = [
            {
                "title_zh": "人工智能的未来发展趋势",
                "title_en": "Future Trends in Artificial Intelligence",
                "summary_zh": "探讨人工智能技术的最新发展和未来趋势，包括机器学习、深度学习和自然语言处理等领域的突破。",
                "summary_en": "Exploring latest AI developments and future trends in ML, DL, and NLP.",
                "category": "analysis",
            },
            {
                "title_zh": "量子计算：下一代计算革命",
                "title_en": "Quantum Computing: The Next Revolution",
                "summary_zh": "量子计算机正在改变我们处理复杂问题的方式，从药物发现到密码学。",
                "summary_en": "Quantum computers changing how we solve complex problems.",
                "category": "analysis",
            },
            {
                "title_zh": "5G网络如何改变我们的生活",
                "title_en": "How 5G Networks Are Changing Lives",
                "summary_zh": "5G技术不仅提供更快的网速，还将推动物联网、自动驾驶和智慧城市的发展。",
                "summary_en": "5G drives IoT, autonomous driving, and smart cities development.",
                "category": "analysis",
            },
            {
                "title_zh": "区块链技术的实际应用",
                "title_en": "Practical Blockchain Applications",
                "summary_zh": "从加密货币到供应链管理，区块链技术正在各个行业中找到实际应用场景。",
                "summary_en": "Blockchain finding applications from crypto to supply chain.",
                "category": "analysis",
            },
            {
                "title_zh": "2025年网络安全趋势",
                "title_en": "Cybersecurity Trends in 2025",
                "summary_zh": "随着网络威胁的不断演变，企业需要采用最新的安全技术和策略来保护数据。",
                "summary_en": "Businesses need latest security tech to protect data and systems.",
                "category": "analysis",
            },
            {
                "title_zh": "云计算的未来发展方向",
                "title_en": "Future of Cloud Computing",
                "summary_zh": "云计算正在从基础设施即服务向更高级的平台和软件服务演进。",
                "summary_en": "Cloud evolving from IaaS to advanced platform and software services.",
                "category": "analysis",
            },
            {
                "title_zh": "物联网与智能家居的融合",
                "title_en": "IoT and Smart Home Integration",
                "summary_zh": "物联网技术正在让我们的家变得更智能、更高效、更安全。",
                "summary_en": "IoT making homes smarter, more efficient, and safer.",
                "category": "analysis",
            },
            {
                "title_zh": "AR/VR与元宇宙的未来",
                "title_en": "Future of AR/VR and Metaverse",
                "summary_zh": "增强现实和虚拟现实技术正在构建下一代互联网体验。",
                "summary_en": "AR/VR building next-gen internet experiences.",
                "category": "analysis",
            },
        ]

        # Business articles (different category)
        business_articles = [
            {
                "title_zh": "2025年全球经济展望",
                "title_en": "Global Economic Outlook 2025",
                "summary_zh": "分析全球经济趋势、贸易政策变化和主要市场的发展机遇与挑战。",
                "summary_en": "Analyzing global economic trends and market opportunities.",
                "category": "business",
            },
            {
                "title_zh": "创业公司融资策略指南",
                "title_en": "Startup Funding Strategy Guide",
                "summary_zh": "从种子轮到IPO，了解创业公司在不同阶段的融资策略和最佳实践。",
                "summary_en": "Funding strategies from seed rounds to IPO for startups.",
                "category": "business",
            },
        ]
        
        # Create content blocks
        def create_content():
            return [
                {
                    "type": "paragraph",
                    "text": "这是文章的第一段内容。本文将深入探讨相关主题，为读者提供全面的分析和见解。"
                },
                {
                    "type": "heading",
                    "text": "主要观点"
                },
                {
                    "type": "paragraph",
                    "text": "在这一部分，我们将详细讨论主要观点和核心概念。通过实际案例和数据分析，帮助读者更好地理解这个话题。"
                },
                {
                    "type": "list",
                    "items": [
                        "第一个要点：详细说明",
                        "第二个要点：深入分析",
                        "第三个要点：实践建议"
                    ]
                },
                {
                    "type": "heading",
                    "text": "未来展望"
                },
                {
                    "type": "paragraph",
                    "text": "展望未来，这个领域将继续快速发展。我们需要保持关注，及时了解最新动态和趋势变化。"
                }
            ]
        
        def create_content_en():
            return [
                {
                    "type": "paragraph",
                    "text": "This is the first paragraph of the article. This article will explore the topic in depth, providing readers with comprehensive analysis and insights."
                },
                {
                    "type": "heading",
                    "text": "Key Points"
                },
                {
                    "type": "paragraph",
                    "text": "In this section, we will discuss the main points and core concepts in detail. Through real-world examples and data analysis, we help readers better understand this topic."
                },
                {
                    "type": "list",
                    "items": [
                        "First point: Detailed explanation",
                        "Second point: In-depth analysis",
                        "Third point: Practical advice"
                    ]
                },
                {
                    "type": "heading",
                    "text": "Future Outlook"
                },
                {
                    "type": "paragraph",
                    "text": "Looking ahead, this field will continue to develop rapidly. We need to stay informed and keep up with the latest developments and trends."
                }
            ]
        
        # Create all articles
        all_articles = analysis_articles + business_articles
        base_date = datetime.now()

        for i, article_data in enumerate(all_articles):
            article = Article(
                # id will be auto-generated as UUID
                title_zh=article_data["title_zh"],
                title_en=article_data["title_en"],
                summary_zh=article_data["summary_zh"],
                summary_en=article_data["summary_en"],
                content_zh=create_content(),
                content_en=create_content_en(),
                category=article_data["category"],
                author="Test Author",
                image_url="https://images.unsplash.com/photo-1677442136019-21780ecad995?w=1200",
                status="published",
                published_at=base_date - timedelta(days=i),
            )
            session.add(article)
            print(f"  ✅ Created: {article.title_en}")

        await session.commit()

        print(f"\n🎉 Successfully created {len(all_articles)} test articles!")
        print(f"   - {len(analysis_articles)} Analysis articles")
        print(f"   - {len(business_articles)} Business articles")
        print("\n📝 You can now test the RelatedArticles component:")
        print("   1. Start the backend: uvicorn app.main:app --reload")
        print("   2. Start the frontend: npm run dev")
        print("   3. Navigate to any Analysis article")
        print("   4. Scroll to the bottom to see related articles")
        print("   5. Click 'Load More' to load additional articles")


if __name__ == "__main__":
    asyncio.run(create_test_articles())

