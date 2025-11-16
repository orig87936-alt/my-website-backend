"""
为所有6个新闻模块创建测试文章
确保每个模块都有文章，以便测试相关文章功能
"""

import asyncio
import sys
from datetime import datetime, timedelta

sys.path.insert(0, '.')

from app.database import AsyncSessionLocal
from app.models.article import Article
from sqlalchemy import select


async def create_articles_for_all_categories():
    """为所有6个类别创建测试文章"""
    
    async with AsyncSessionLocal() as session:
        print("🚀 为所有6个新闻模块创建测试文章...")
        
        # 6个模块的文章数据
        articles_data = [
            # HEADLINE - 头条新闻
            {
                "category": "headline",
                "title_zh": "特朗普和习近平同意一年贸易休战——但关键细节仍不明确",
                "title_en": "Trump and Xi agree to a one-year trade truce",
                "summary_zh": "北京承诺购买大豆、延迟稀土出口管制并遏制芬太尼，但美国让步的问题仍然存在。",
                "summary_en": "Beijing pledges to buy soybeans and curb fentanyl exports.",
                "author": "FOCUS POINT",
                "image_url": "https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?w=1200",
            },
            {
                "category": "headline",
                "title_zh": "全球经济复苏迹象明显，各国央行调整货币政策",
                "title_en": "Global Economic Recovery Shows Clear Signs",
                "summary_zh": "随着通胀压力缓解，主要经济体开始调整货币政策，为经济增长创造更有利的环境。",
                "summary_en": "Major economies adjust monetary policies for favorable growth.",
                "author": "Economic Insights",
                "image_url": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=1200",
            },
            
            # REGULATORY BILLS - 监管法规
            {
                "category": "regulatory",
                "title_zh": "新数据保护法规即将生效，企业需加强合规措施",
                "title_en": "New Data Protection Regulations Take Effect",
                "summary_zh": "政府发布最新数据保护法规，要求企业在数据收集、存储和使用方面采取更严格的措施。",
                "summary_en": "Government issues new data protection regulations for businesses.",
                "author": "Legal Affairs",
                "image_url": "https://images.unsplash.com/photo-1589829545856-d10d557cf95f?w=1200",
            },
            {
                "category": "regulatory",
                "title_zh": "金融监管机构发布反洗钱新规，加强跨境交易监控",
                "title_en": "Financial Regulators Issue New AML Rules",
                "summary_zh": "为打击洗钱和恐怖融资活动，监管机构要求金融机构加强客户尽职调查和交易监控。",
                "summary_en": "Regulators require enhanced customer due diligence and monitoring.",
                "author": "Regulatory Watch",
                "image_url": "https://images.unsplash.com/photo-1450101499163-c8848c66ca85?w=1200",
            },
            
            # ANALYSIS REPORTS - 分析报告
            {
                "category": "analysis",
                "title_zh": "人工智能的未来发展趋势与行业应用分析",
                "title_en": "Future Trends in Artificial Intelligence",
                "summary_zh": "探讨人工智能技术的最新发展和未来趋势，包括机器学习、深度学习和自然语言处理等领域。",
                "summary_en": "Exploring latest AI developments and future trends in ML and DL.",
                "author": "Tech Analysis",
                "image_url": "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=1200",
            },
            {
                "category": "analysis",
                "title_zh": "2025年全球供应链重构趋势分析",
                "title_en": "Global Supply Chain Restructuring Trends 2025",
                "summary_zh": "受地缘政治和技术变革影响，全球供应链正在经历深刻重构和转型。",
                "summary_en": "Global supply chains undergoing profound restructuring.",
                "author": "Supply Chain Insights",
                "image_url": "https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?w=1200",
            },
            
            # BUSINESS CHANGE - 商业动态
            {
                "category": "business",
                "title_zh": "科技巨头加速布局人工智能领域，投资规模创新高",
                "title_en": "Tech Giants Accelerate AI Investments",
                "summary_zh": "主要科技公司大幅增加人工智能研发投入，推出多款创新产品和服务。",
                "summary_en": "Major tech companies significantly increase AI R&D investments.",
                "author": "Business News",
                "image_url": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=1200",
            },
            {
                "category": "business",
                "title_zh": "新能源汽车市场持续扩张，传统车企加速转型",
                "title_en": "EV Market Continues Expansion",
                "summary_zh": "电动汽车销量持续增长，传统汽车制造商纷纷推出新能源车型。",
                "summary_en": "EV sales continue to grow as automakers launch new models.",
                "author": "Auto Industry",
                "image_url": "https://images.unsplash.com/photo-1593941707882-a5bba14938c7?w=1200",
            },
            
            # CORE ENTERPRISE - 核心企业
            {
                "category": "enterprise",
                "title_zh": "华为发布新一代5G解决方案，助力数字化转型",
                "title_en": "Huawei Launches Next-Gen 5G Solutions",
                "summary_zh": "华为推出最新5G技术和解决方案，为企业数字化转型提供强大支持。",
                "summary_en": "Huawei introduces latest 5G technology and solutions.",
                "author": "Enterprise Tech",
                "image_url": "https://images.unsplash.com/photo-1519389950473-47ba0277781c?w=1200",
            },
            {
                "category": "enterprise",
                "title_zh": "阿里巴巴云计算业务持续增长，国际市场份额扩大",
                "title_en": "Alibaba Cloud Business Continues Growth",
                "summary_zh": "阿里云在国内外市场均实现强劲增长，推出多项创新服务。",
                "summary_en": "Alibaba Cloud achieves strong growth in domestic markets.",
                "author": "Cloud Computing",
                "image_url": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=1200",
            },
            
            # FUTURE OUTLOOK - 未来展望
            {
                "category": "outlook",
                "title_zh": "2030年科技发展趋势预测：量子计算与生物技术融合",
                "title_en": "Tech Trends 2030: Quantum and Biotech",
                "summary_zh": "展望未来五年，量子计算和生物技术的融合将带来革命性突破。",
                "summary_en": "Quantum computing and biotech convergence brings breakthroughs.",
                "author": "Future Insights",
                "image_url": "https://images.unsplash.com/photo-1635070041078-e363dbe005cb?w=1200",
            },
            {
                "category": "outlook",
                "title_zh": "可持续发展成为企业战略核心，绿色经济前景广阔",
                "title_en": "Sustainability Becomes Core Business Strategy",
                "summary_zh": "越来越多企业将可持续发展纳入核心战略，绿色技术和清洁能源投资持续增长。",
                "summary_en": "More companies integrate sustainability into core strategy.",
                "author": "Sustainability Report",
                "image_url": "https://images.unsplash.com/photo-1473341304170-971dccb5ac1e?w=1200",
            },
        ]
        
        # 创建文章
        created_count = 0
        base_date = datetime.utcnow()
        
        for i, data in enumerate(articles_data):
            # 创建内容块
            content_zh = [
                {"type": "paragraph", "text": f"这是关于{data['title_zh']}的详细分析报告。"},
                {"type": "heading", "text": "背景介绍", "level": 2},
                {"type": "paragraph", "text": "随着全球经济和技术环境的快速变化，这一领域正在经历深刻的转型。"},
                {"type": "heading", "text": "主要发现", "level": 2},
                {"type": "paragraph", "text": "我们的研究发现了几个关键趋势和发展方向。"},
                {"type": "paragraph", "text": "首先，技术创新正在加速推动行业变革。"},
                {"type": "paragraph", "text": "其次，监管环境的变化为市场带来了新的机遇和挑战。"},
                {"type": "heading", "text": "未来展望", "level": 2},
                {"type": "paragraph", "text": "展望未来，我们预计这一趋势将持续发展，为相关行业带来深远影响。"},
            ]
            
            content_en = [
                {"type": "paragraph", "text": f"This is a detailed analysis report on {data['title_en']}."},
                {"type": "heading", "text": "Background", "level": 2},
                {"type": "paragraph", "text": "With rapid changes in the global economic and technological environment, this field is undergoing profound transformation."},
                {"type": "heading", "text": "Key Findings", "level": 2},
                {"type": "paragraph", "text": "Our research has identified several key trends and developments."},
                {"type": "paragraph", "text": "First, technological innovation is accelerating industry transformation."},
                {"type": "paragraph", "text": "Second, changes in the regulatory environment bring new opportunities and challenges."},
                {"type": "heading", "text": "Future Outlook", "level": 2},
                {"type": "paragraph", "text": "Looking ahead, we expect this trend to continue, bringing far-reaching impacts to related industries."},
            ]
            
            article = Article(
                category=data["category"],
                status="published",
                title_zh=data["title_zh"],
                title_en=data["title_en"],
                summary_zh=data["summary_zh"],
                summary_en=data["summary_en"],
                content_zh=content_zh,
                content_en=content_en,
                author=data.get("author", "FOCUS POINT"),
                image_url=data.get("image_url"),
                published_at=base_date - timedelta(days=i),  # 每篇文章间隔一天
            )
            
            session.add(article)
            created_count += 1
            print(f"✅ 创建文章: [{data['category']}] {data['title_zh']}")
        
        await session.commit()
        print(f"\n🎉 成功创建 {created_count} 篇文章！")
        
        # 显示每个类别的文章数量
        print("\n📊 各模块文章数量：")
        categories = ['headline', 'regulatory', 'analysis', 'business', 'enterprise', 'outlook']
        for cat in categories:
            result = await session.execute(
                select(Article).where(Article.category == cat, Article.status == 'published')
            )
            count = len(result.scalars().all())
            print(f"   {cat}: {count} 篇")


if __name__ == "__main__":
    asyncio.run(create_articles_for_all_categories())

