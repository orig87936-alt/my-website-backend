"""
AI 元数据生成服务
使用 DeepSeek API 生成文章摘要、分类建议和标签
"""
from typing import List, Dict, Any, Optional
import json
from .deepseek import DeepSeekService


class MetadataGenerator:
    """AI 元数据生成器"""
    
    def __init__(self):
        self.deepseek = DeepSeekService()
    
    async def generate_summary(
        self,
        content: str,
        max_length: int = 150,
        language: str = 'zh'
    ) -> str:
        """
        生成文章摘要
        
        Args:
            content: 文章内容
            max_length: 最大长度（默认 150 字符）
            language: 语言（zh/en）
            
        Returns:
            生成的摘要
        """
        # 截取前 2000 字符用于生成摘要
        content_preview = content[:2000]
        
        prompt = f"""请为以下文章生成一个简洁的摘要，长度在 50-{max_length} 字符之间。
摘要应该准确概括文章的核心内容，语言为{'中文' if language == 'zh' else '英文'}。

文章内容：
{content_preview}

请直接返回摘要文本，不要包含任何其他说明。"""
        
        try:
            summary = await self.deepseek.generate_summary(content_preview, max_length)
            return summary.strip()
        except Exception as e:
            # 如果 AI 生成失败，返回简单截取
            fallback = content[:max_length].strip()
            if len(content) > max_length:
                fallback += '...'
            return fallback
    
    async def suggest_category(
        self,
        title: str,
        content: str,
        available_categories: Optional[List[str]] = None
    ) -> str:
        """
        建议文章分类
        
        Args:
            title: 文章标题
            content: 文章内容
            available_categories: 可用分类列表
            
        Returns:
            建议的分类
        """
        if available_categories is None:
            available_categories = [
                'headline',      # 头条
                'technology',    # 科技
                'business',      # 商业
                'finance',       # 金融
                'policy',        # 政策
                'industry'       # 行业
            ]
        
        # 截取前 1000 字符
        content_preview = content[:1000]
        
        prompt = f"""请根据以下文章的标题和内容，从给定的分类中选择最合适的一个。

可用分类：{', '.join(available_categories)}

文章标题：{title}

文章内容：
{content_preview}

请只返回分类名称，不要包含任何其他说明。"""
        
        try:
            category = await self.deepseek.suggest_category(title, content_preview, available_categories)
            # 验证返回的分类是否在可用列表中
            if category in available_categories:
                return category
            else:
                # 如果不在列表中，返回默认分类
                return available_categories[0]
        except Exception:
            # 如果 AI 生成失败，返回默认分类
            return available_categories[0]
    
    async def extract_tags(
        self,
        title: str,
        content: str,
        max_tags: int = 5
    ) -> List[str]:
        """
        提取文章标签
        
        Args:
            title: 文章标题
            content: 文章内容
            max_tags: 最大标签数（默认 5）
            
        Returns:
            标签列表
        """
        # 截取前 1500 字符
        content_preview = content[:1500]
        
        prompt = f"""请从以下文章中提取 {max_tags} 个关键标签。
标签应该是简短的词语或短语，能够准确描述文章的主题和关键概念。

文章标题：{title}

文章内容：
{content_preview}

请以 JSON 数组格式返回标签，例如：["标签1", "标签2", "标签3"]
只返回 JSON 数组，不要包含任何其他说明。"""
        
        try:
            tags = await self.deepseek.extract_tags(title, content_preview, max_tags)
            
            # 验证返回的是列表
            if isinstance(tags, list):
                # 限制标签数量
                return tags[:max_tags]
            else:
                return []
        except Exception:
            # 如果 AI 生成失败，返回空列表
            return []
    
    async def generate_all_metadata(
        self,
        title: str,
        content: str,
        language: str = 'zh'
    ) -> Dict[str, Any]:
        """
        一次性生成所有元数据
        
        Args:
            title: 文章标题
            content: 文章内容
            language: 语言（zh/en）
            
        Returns:
            包含所有元数据的字典
        """
        # 并发生成所有元数据
        import asyncio
        
        summary_task = self.generate_summary(content, language=language)
        category_task = self.suggest_category(title, content)
        tags_task = self.extract_tags(title, content)
        
        summary, category, tags = await asyncio.gather(
            summary_task,
            category_task,
            tags_task,
            return_exceptions=True
        )
        
        # 处理可能的异常
        if isinstance(summary, Exception):
            summary = content[:150].strip() + '...'
        if isinstance(category, Exception):
            category = 'headline'
        if isinstance(tags, Exception):
            tags = []
        
        return {
            'summary': summary,
            'category': category,
            'tags': tags
        }

