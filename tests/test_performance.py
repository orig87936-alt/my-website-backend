"""
T077: Performance tests for translation and document upload
"""
import asyncio
import time
from typing import List
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.translation import TranslationService
from app.services.document_parser import parse_document
from app.database import AsyncSessionLocal


class TestTranslationPerformance:
    """Translation performance tests"""
    
    @pytest.mark.asyncio
    async def test_single_translation_performance(self):
        """Test single translation completes within 5 seconds"""
        async with AsyncSessionLocal() as db:
            service = TranslationService(db)
            
            test_text = "这是一个测试文本，用于验证翻译性能。" * 10  # ~300 characters
            
            start_time = time.time()
            result = await service.translate_text(
                text=test_text,
                source_lang='zh',
                target_lang='en'
            )
            elapsed_time = time.time() - start_time
            
            print(f"\n✅ Single translation time: {elapsed_time:.2f}s")
            assert elapsed_time < 5.0, f"Translation took {elapsed_time:.2f}s, expected < 5s"
            assert result['translated_text'], "Translation result should not be empty"
    
    @pytest.mark.asyncio
    async def test_batch_translation_performance(self):
        """Test batch translation with 4 fields completes within 10 seconds"""
        async with AsyncSessionLocal() as db:
            service = TranslationService(db)
            
            fields = [
                {'field_name': 'title', 'text': '新闻标题测试'},
                {'field_name': 'summary', 'text': '这是一个新闻摘要，包含了重要信息。'},
                {'field_name': 'lead', 'text': '导语部分提供了新闻的核心要点。'},
                {'field_name': 'content', 'text': '正文内容详细描述了事件的来龙去脉。' * 5}
            ]
            
            start_time = time.time()
            result = await service.batch_translate(
                fields=fields,
                source_lang='zh',
                target_lang='en'
            )
            elapsed_time = time.time() - start_time
            
            print(f"\n✅ Batch translation time: {elapsed_time:.2f}s")
            print(f"   - Fields: {result['total_fields']}")
            print(f"   - Cached: {result['cached_count']}")
            print(f"   - Cache hit rate: {result.get('cache_hit_rate', 0):.2f}%")
            
            assert elapsed_time < 10.0, f"Batch translation took {elapsed_time:.2f}s, expected < 10s"
            assert len(result['results']) == 4, "Should translate all 4 fields"
    
    @pytest.mark.asyncio
    async def test_concurrent_translation_speedup(self):
        """Test that concurrent translation is faster than sequential"""
        async with AsyncSessionLocal() as db:
            service = TranslationService(db)
            
            fields = [
                {'field_name': f'field_{i}', 'text': f'测试文本 {i}' * 20}
                for i in range(4)
            ]
            
            # Test with concurrent (max_concurrent=4)
            start_concurrent = time.time()
            result_concurrent = await service.batch_translate(
                fields=fields,
                source_lang='zh',
                target_lang='en',
                max_concurrent=4
            )
            time_concurrent = time.time() - start_concurrent
            
            # Test with sequential (max_concurrent=1)
            start_sequential = time.time()
            result_sequential = await service.batch_translate(
                fields=fields,
                source_lang='zh',
                target_lang='en',
                max_concurrent=1
            )
            time_sequential = time.time() - start_sequential
            
            print(f"\n✅ Concurrent vs Sequential:")
            print(f"   - Concurrent (4): {time_concurrent:.2f}s")
            print(f"   - Sequential (1): {time_sequential:.2f}s")
            print(f"   - Speedup: {time_sequential / time_concurrent:.2f}x")
            
            # Concurrent should be faster (or at least not slower)
            assert time_concurrent <= time_sequential * 1.1, "Concurrent should not be slower than sequential"


class TestDocumentParsingPerformance:
    """Document parsing performance tests"""
    
    def test_markdown_parsing_performance(self):
        """Test Markdown parsing completes within 2 seconds"""
        # Create a large Markdown document
        markdown_content = """
# Test Document

## Introduction

This is a test document for performance testing.

""" + "\n\n".join([f"### Section {i}\n\nThis is section {i} with some content." for i in range(50)])
        
        markdown_content += """

## Code Example

```python
def hello_world():
    print("Hello, World!")
```

## List Example

- Item 1
- Item 2
- Item 3

> This is a quote

"""
        
        file_content = markdown_content.encode('utf-8')
        
        start_time = time.time()
        result = parse_document(file_content, 'test.md')
        elapsed_time = time.time() - start_time
        
        print(f"\n✅ Markdown parsing time: {elapsed_time:.2f}s")
        print(f"   - Content blocks: {len(result['content_blocks'])}")
        print(f"   - Parse time: {result['metadata'].get('parse_time', 0):.2f}s")
        
        assert elapsed_time < 2.0, f"Markdown parsing took {elapsed_time:.2f}s, expected < 2s"
        assert len(result['content_blocks']) > 0, "Should parse content blocks"
    
    def test_file_size_validation(self):
        """Test file size validation rejects files > 10MB"""
        from app.services.document_parser import check_file_size
        
        # Create a 5MB file (should pass)
        small_file = b'x' * (5 * 1024 * 1024)
        assert check_file_size(small_file, max_size_mb=10) == True
        
        # Create an 11MB file (should fail)
        large_file = b'x' * (11 * 1024 * 1024)
        with pytest.raises(ValueError, match="exceeds maximum allowed size"):
            check_file_size(large_file, max_size_mb=10)
        
        print("\n✅ File size validation working correctly")


class TestCachePerformance:
    """Cache performance tests"""
    
    @pytest.mark.asyncio
    async def test_cache_hit_performance(self):
        """Test that cached translations are significantly faster"""
        async with AsyncSessionLocal() as db:
            service = TranslationService(db)
            
            test_text = "这是一个缓存测试文本。"
            
            # First translation (cache miss)
            start_miss = time.time()
            result_miss = await service.translate_text(
                text=test_text,
                source_lang='zh',
                target_lang='en'
            )
            time_miss = time.time() - start_miss
            
            # Second translation (cache hit)
            start_hit = time.time()
            result_hit = await service.translate_text(
                text=test_text,
                source_lang='zh',
                target_lang='en'
            )
            time_hit = time.time() - start_hit
            
            print(f"\n✅ Cache performance:")
            print(f"   - Cache miss: {time_miss:.3f}s")
            print(f"   - Cache hit: {time_hit:.3f}s")
            print(f"   - Speedup: {time_miss / time_hit:.1f}x")
            
            assert result_hit['cached'] == True, "Second request should be cached"
            assert time_hit < time_miss * 0.5, "Cache hit should be at least 2x faster"
    
    @pytest.mark.asyncio
    async def test_cache_statistics(self):
        """Test cache statistics retrieval"""
        async with AsyncSessionLocal() as db:
            service = TranslationService(db)
            
            start_time = time.time()
            stats = await service.get_cache_statistics()
            elapsed_time = time.time() - start_time
            
            print(f"\n✅ Cache statistics retrieval: {elapsed_time:.3f}s")
            print(f"   - Total cache entries: {stats['total_cache_entries']}")
            print(f"   - Recent entries (24h): {stats['recent_cache_entries_24h']}")
            print(f"   - Total translations: {stats['total_translations']}")
            print(f"   - Cache hit rate: {stats['cache_hit_rate']:.2f}%")
            
            assert elapsed_time < 1.0, "Statistics retrieval should be fast"
            assert 'total_cache_entries' in stats
            assert 'cache_hit_rate' in stats


if __name__ == "__main__":
    print("🧪 Running performance tests...")
    print("=" * 60)
    
    # Run tests
    pytest.main([__file__, "-v", "-s"])

