"""
T077: Simple performance test runner
Run this script to verify translation and document upload performance
"""
import asyncio
import time
from app.database import AsyncSessionLocal
from app.services.translation import TranslationService
from app.services.document_parser import parse_document, check_file_size


async def test_translation_performance():
    """Test translation performance"""
    print("\n" + "="*60)
    print("🧪 Testing Translation Performance")
    print("="*60)
    
    async with AsyncSessionLocal() as db:
        service = TranslationService(db)
        
        # Test 1: Single translation
        print("\n1️⃣  Single Translation Test")
        test_text = "这是一个测试文本，用于验证翻译性能。人工智能技术正在改变世界。" * 5
        
        start_time = time.time()
        result = await service.translate_text(
            text=test_text,
            source_lang='zh',
            target_lang='en'
        )
        elapsed_time = time.time() - start_time
        
        print(f"   ⏱️  Time: {elapsed_time:.2f}s")
        print(f"   📝 Cached: {result['cached']}")
        print(f"   ✅ Status: {'PASS' if elapsed_time < 5.0 else 'FAIL'} (< 5s)")
        
        # Test 2: Batch translation
        print("\n2️⃣  Batch Translation Test (4 fields)")
        fields = [
            {'field_name': 'title', 'text': '人工智能的未来发展趋势'},
            {'field_name': 'summary', 'text': '本文探讨了人工智能技术在未来十年的发展方向和应用前景。'},
            {'field_name': 'lead', 'text': '随着技术的不断进步，人工智能正在各个领域发挥越来越重要的作用。'},
            {'field_name': 'content', 'text': '人工智能技术的发展将深刻改变我们的生活方式和工作模式。' * 10}
        ]
        
        start_time = time.time()
        result = await service.batch_translate(
            fields=fields,
            source_lang='zh',
            target_lang='en',
            max_concurrent=4
        )
        elapsed_time = time.time() - start_time
        
        print(f"   ⏱️  Time: {elapsed_time:.2f}s")
        print(f"   📊 Fields: {result['total_fields']}")
        print(f"   💾 Cached: {result['cached_count']}")
        print(f"   📈 Cache hit rate: {result.get('cache_hit_rate', 0):.2f}%")
        print(f"   ✅ Status: {'PASS' if elapsed_time < 10.0 else 'FAIL'} (< 10s)")
        
        # Test 3: Cache statistics
        print("\n3️⃣  Cache Statistics Test")
        start_time = time.time()
        stats = await service.get_cache_statistics()
        elapsed_time = time.time() - start_time
        
        print(f"   ⏱️  Time: {elapsed_time:.3f}s")
        print(f"   📦 Total cache entries: {stats['total_cache_entries']}")
        print(f"   🆕 Recent entries (24h): {stats['recent_cache_entries_24h']}")
        print(f"   📝 Total translations: {stats['total_translations']}")
        print(f"   📈 Cache hit rate: {stats['cache_hit_rate']:.2f}%")
        print(f"   ✅ Status: {'PASS' if elapsed_time < 1.0 else 'FAIL'} (< 1s)")


def test_document_parsing_performance():
    """Test document parsing performance"""
    print("\n" + "="*60)
    print("📄 Testing Document Parsing Performance")
    print("="*60)
    
    # Test 1: Markdown parsing
    print("\n1️⃣  Markdown Parsing Test")
    markdown_content = """
# Test Document

## Introduction

This is a performance test document.

""" + "\n\n".join([f"### Section {i}\n\nContent for section {i}." for i in range(30)])
    
    markdown_content += """

## Code Example

```python
def test_function():
    return "Hello, World!"
```

## List

- Item 1
- Item 2
- Item 3

> Quote example

"""
    
    file_content = markdown_content.encode('utf-8')
    
    start_time = time.time()
    result = parse_document(file_content, 'test.md')
    elapsed_time = time.time() - start_time
    
    print(f"   ⏱️  Time: {elapsed_time:.2f}s")
    print(f"   📝 Content blocks: {len(result['content_blocks'])}")
    print(f"   🖼️  Images: {len(result['images'])}")
    print(f"   ✅ Status: {'PASS' if elapsed_time < 2.0 else 'FAIL'} (< 2s)")
    
    # Test 2: File size validation
    print("\n2️⃣  File Size Validation Test")
    
    # Small file (should pass)
    small_file = b'x' * (5 * 1024 * 1024)  # 5MB
    try:
        check_file_size(small_file, max_size_mb=10)
        print(f"   ✅ 5MB file: PASS (accepted)")
    except ValueError:
        print(f"   ❌ 5MB file: FAIL (should be accepted)")
    
    # Large file (should fail)
    large_file = b'x' * (11 * 1024 * 1024)  # 11MB
    try:
        check_file_size(large_file, max_size_mb=10)
        print(f"   ❌ 11MB file: FAIL (should be rejected)")
    except ValueError as e:
        print(f"   ✅ 11MB file: PASS (correctly rejected)")


async def main():
    """Run all performance tests"""
    print("\n" + "🚀 " + "="*58)
    print("🚀  Phase 5 - Performance Tests (T077)")
    print("🚀 " + "="*58)
    
    try:
        # Translation tests
        await test_translation_performance()
        
        # Document parsing tests
        test_document_parsing_performance()
        
        print("\n" + "="*60)
        print("✅ All performance tests completed!")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error during performance tests: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

