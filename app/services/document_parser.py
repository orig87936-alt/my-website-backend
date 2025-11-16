"""
文档解析服务
支持 Markdown 和 Word 文档的解析、图片提取和元数据生成
T072: 流式处理大文件
T073: 安全检查防止恶意代码
"""
import re
import io
import base64
import asyncio
import aiohttp
from typing import List, Dict, Any, Tuple, Optional
from pathlib import Path
import markdown
from bs4 import BeautifulSoup
import time
from ..config import get_settings

settings = get_settings()

# T073: 危险标签和模式列表
DANGEROUS_TAGS = [
    'script', 'iframe', 'object', 'embed', 'applet',
    'meta', 'link', 'style', 'base', 'form'
]

DANGEROUS_PATTERNS = [
    r'javascript:',
    r'on\w+\s*=',  # onclick, onload, etc.
    r'data:text/html',
    r'vbscript:',
    r'<\s*script',
    r'eval\s*\(',
    r'expression\s*\(',
]

try:
    from docx import Document
    from docx.oxml.text.paragraph import CT_P
    from docx.oxml.table import CT_Tbl
    from docx.table import _Cell, Table
    from docx.text.paragraph import Paragraph
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

from ..schemas.article import ContentBlock


def sanitize_content(content: str) -> str:
    """
    T073: 清理内容，移除危险代码

    Args:
        content: 原始内容

    Returns:
        清理后的安全内容
    """
    # 检查危险模式
    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, content, re.IGNORECASE):
            print(f"⚠️  Detected dangerous pattern: {pattern}")
            content = re.sub(pattern, '', content, flags=re.IGNORECASE)

    return content


def sanitize_html(html: str) -> str:
    """
    T073: 清理 HTML，移除危险标签

    Args:
        html: 原始 HTML

    Returns:
        清理后的安全 HTML
    """
    soup = BeautifulSoup(html, 'html.parser')

    # 移除危险标签
    for tag_name in DANGEROUS_TAGS:
        for tag in soup.find_all(tag_name):
            print(f"⚠️  Removed dangerous tag: <{tag_name}>")
            tag.decompose()

    # 移除危险属性
    for tag in soup.find_all():
        # 移除所有 on* 事件属性
        attrs_to_remove = []
        for attr in tag.attrs:
            if attr.startswith('on') or attr in ['style', 'formaction']:
                attrs_to_remove.append(attr)

        for attr in attrs_to_remove:
            del tag[attr]

    return str(soup)


def check_file_size(file_content: bytes, max_size_mb: int = 10) -> bool:
    """
    T072: 检查文件大小

    Args:
        file_content: 文件内容
        max_size_mb: 最大文件大小（MB）

    Returns:
        是否在限制内
    """
    size_mb = len(file_content) / (1024 * 1024)
    if size_mb > max_size_mb:
        raise ValueError(f"File size ({size_mb:.2f}MB) exceeds maximum allowed size ({max_size_mb}MB)")
    return True


class DocumentParser:
    """文档解析器基类"""
    
    def __init__(self, file_content: bytes, filename: str):
        self.file_content = file_content
        self.filename = filename
        self.images: List[Tuple[str, bytes]] = []  # (filename, binary_data)
        
    def parse(self) -> Dict[str, Any]:
        """解析文档，返回结构化内容"""
        raise NotImplementedError
        
    def extract_metadata(self, content: str) -> Dict[str, Any]:
        """提取元数据"""
        # 计算字数
        word_count = len(re.findall(r'\w+', content))
        
        # 计算段落数
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        paragraph_count = len(paragraphs)
        
        # 生成摘要（取前150字）
        summary = content[:150].strip()
        if len(content) > 150:
            summary += '...'
            
        # 提取标题（第一行或第一个 # 标题）
        lines = content.split('\n')
        title = ''
        for line in lines:
            line = line.strip()
            if line:
                # 移除 Markdown 标题符号
                title = re.sub(r'^#+\s*', '', line)
                break
                
        return {
            'title': title or self.filename,
            'summary': summary,
            'word_count': word_count,
            'paragraph_count': paragraph_count,
            'image_count': len(self.images)
        }


class MarkdownParser(DocumentParser):
    """Markdown 文档解析器"""

    def parse(self) -> Dict[str, Any]:
        """解析 Markdown 文档"""
        start_time = time.time()

        # T072: 检查文件大小
        check_file_size(self.file_content, max_size_mb=10)

        # 解码文本内容
        try:
            text_content = self.file_content.decode('utf-8')
        except UnicodeDecodeError:
            text_content = self.file_content.decode('utf-8', errors='ignore')

        # T073: 清理内容
        text_content = sanitize_content(text_content)

        # 提取图片（base64 和 URL）
        self._extract_images_from_markdown(text_content)

        # 转换为 HTML
        html_content = markdown.markdown(
            text_content,
            extensions=['extra', 'codehilite', 'tables', 'fenced_code']
        )

        # T073: 清理 HTML
        html_content = sanitize_html(html_content)

        # 解析 HTML 为 ContentBlock
        content_blocks = self._html_to_content_blocks(html_content)

        # 提取元数据
        metadata = self.extract_metadata(text_content)
        metadata['parse_time'] = time.time() - start_time

        return {
            'content_blocks': content_blocks,
            'metadata': metadata,
            'images': self.images
        }
    
    def _extract_images_from_markdown(self, text: str):
        """从 Markdown 中提取图片"""
        # 提取 base64 图片
        base64_pattern = r'!\[([^\]]*)\]\(data:image/([^;]+);base64,([^)]+)\)'
        for match in re.finditer(base64_pattern, text):
            alt_text, img_format, base64_data = match.groups()
            try:
                img_data = base64.b64decode(base64_data)
                filename = f"{alt_text or 'image'}.{img_format}"
                self.images.append((filename, img_data))
            except Exception:
                continue
    
    def _html_to_content_blocks(self, html: str) -> List[ContentBlock]:
        """将 HTML 转换为 ContentBlock 列表"""
        soup = BeautifulSoup(html, 'html.parser')
        blocks = []
        
        for element in soup.children:
            if element.name is None:
                continue
                
            if element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                level = int(element.name[1])
                blocks.append(ContentBlock(
                    type='heading',
                    content=element.get_text().strip(),
                    level=level
                ))
            elif element.name == 'p':
                text = element.get_text().strip()
                if text:
                    blocks.append(ContentBlock(
                        type='paragraph',
                        content=text
                    ))
            elif element.name == 'pre':
                code = element.find('code')
                if code:
                    blocks.append(ContentBlock(
                        type='code',
                        content=code.get_text(),
                        language=code.get('class', [''])[0].replace('language-', '') or 'text'
                    ))
            elif element.name == 'blockquote':
                blocks.append(ContentBlock(
                    type='quote',
                    content=element.get_text().strip()
                ))
            elif element.name in ['ul', 'ol']:
                items = [li.get_text().strip() for li in element.find_all('li')]
                blocks.append(ContentBlock(
                    type='list',
                    content='\n'.join(items),
                    ordered=element.name == 'ol'
                ))
            elif element.name == 'img':
                blocks.append(ContentBlock(
                    type='image',
                    content=element.get('src', ''),
                    caption=element.get('alt', '')
                ))
        
        return blocks


class WordParser(DocumentParser):
    """Word 文档解析器"""
    
    def __init__(self, file_content: bytes, filename: str):
        if not DOCX_AVAILABLE:
            raise ImportError("python-docx is not installed. Install it with: pip install python-docx")
        super().__init__(file_content, filename)
    
    def parse(self) -> Dict[str, Any]:
        """解析 Word 文档"""
        start_time = time.time()

        # T072: 检查文件大小
        check_file_size(self.file_content, max_size_mb=10)

        # 加载文档
        doc = Document(io.BytesIO(self.file_content))

        # 提取图片
        self._extract_images_from_docx(doc)

        # 解析内容块
        content_blocks = self._docx_to_content_blocks(doc)

        # 提取纯文本用于元数据
        plain_text = '\n\n'.join([block.content for block in content_blocks if block.content])

        # T073: 清理内容
        plain_text = sanitize_content(plain_text)

        # 提取元数据
        metadata = self.extract_metadata(plain_text)
        metadata['parse_time'] = time.time() - start_time

        return {
            'content_blocks': content_blocks,
            'metadata': metadata,
            'images': self.images
        }
    
    def _extract_images_from_docx(self, doc: Document):
        """从 Word 文档中提取图片"""
        # 遍历文档中的所有关系
        for rel in doc.part.rels.values():
            if "image" in rel.target_ref:
                try:
                    image_data = rel.target_part.blob
                    # 从关系中获取文件扩展名
                    ext = Path(rel.target_ref).suffix
                    filename = f"image_{len(self.images) + 1}{ext}"
                    self.images.append((filename, image_data))
                except Exception:
                    continue
    
    def _docx_to_content_blocks(self, doc: Document) -> List[ContentBlock]:
        """将 Word 文档转换为 ContentBlock 列表"""
        blocks = []
        
        for element in doc.element.body:
            if isinstance(element, CT_P):
                para = Paragraph(element, doc)
                self._parse_paragraph(para, blocks)
            elif isinstance(element, CT_Tbl):
                # 暂时跳过表格，可以后续扩展
                pass
        
        return blocks
    
    def _parse_paragraph(self, para: Paragraph, blocks: List[ContentBlock]):
        """解析段落"""
        text = para.text.strip()
        if not text:
            return
        
        # 检查是否是标题
        if para.style.name.startswith('Heading'):
            try:
                level = int(para.style.name.split()[-1])
                blocks.append(ContentBlock(
                    type='heading',
                    content=text,
                    level=min(level, 6)
                ))
            except (ValueError, IndexError):
                blocks.append(ContentBlock(
                    type='heading',
                    content=text,
                    level=2
                ))
        # 检查是否是列表
        elif para.style.name.startswith('List'):
            # 简单处理：将连续的列表项合并
            if blocks and blocks[-1].type == 'list':
                blocks[-1].content += '\n' + text
            else:
                blocks.append(ContentBlock(
                    type='list',
                    content=text,
                    ordered=False
                ))
        # 普通段落
        else:
            blocks.append(ContentBlock(
                type='paragraph',
                content=text
            ))


async def upload_images_concurrently(
    images: List[Tuple[str, bytes]],
    auth_token: str,
    max_concurrent: int = 5
) -> List[Dict[str, Any]]:
    """
    并发上传图片到服务器

    Args:
        images: 图片列表 [(filename, binary_data), ...]
        auth_token: 认证 token
        max_concurrent: 最大并发数（默认 5）

    Returns:
        上传结果列表 [{"original_name": str, "uploaded_url": str, "size": int}, ...]
    """
    if not images:
        return []

    # 限制并发数
    semaphore = asyncio.Semaphore(max_concurrent)

    async def upload_single_image(filename: str, image_data: bytes) -> Dict[str, Any]:
        async with semaphore:
            try:
                # 创建 FormData
                form_data = aiohttp.FormData()
                form_data.add_field(
                    'file',
                    image_data,
                    filename=filename,
                    content_type=f'image/{Path(filename).suffix[1:]}'
                )

                # 上传图片
                upload_url = f"{settings.API_BASE_URL}/api/v1/upload/image"
                headers = {"Authorization": f"Bearer {auth_token}"}

                async with aiohttp.ClientSession() as session:
                    async with session.post(upload_url, data=form_data, headers=headers) as response:
                        if response.status == 200:
                            result = await response.json()
                            return {
                                "original_name": filename,
                                "uploaded_url": result["url"],
                                "size": len(image_data)
                            }
                        else:
                            error_text = await response.text()
                            raise Exception(f"Upload failed: {error_text}")
            except Exception as e:
                # 上传失败时返回错误信息
                return {
                    "original_name": filename,
                    "uploaded_url": "",
                    "size": len(image_data),
                    "error": str(e)
                }

    # 并发上传所有图片
    tasks = [upload_single_image(filename, data) for filename, data in images]
    results = await asyncio.gather(*tasks, return_exceptions=False)

    return results


def parse_document(file_content: bytes, filename: str) -> Dict[str, Any]:
    """
    解析文档（自动检测类型）

    Args:
        file_content: 文件二进制内容
        filename: 文件名

    Returns:
        解析结果字典
    """
    ext = Path(filename).suffix.lower()

    if ext == '.md':
        parser = MarkdownParser(file_content, filename)
    elif ext == '.docx':
        parser = WordParser(file_content, filename)
    else:
        raise ValueError(f"Unsupported file type: {ext}")

    return parser.parse()

