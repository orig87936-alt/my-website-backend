"""
Chat and FAQ API Tests
"""
import httpx
import asyncio
import json

BASE_URL = "http://localhost:8000"
TOKEN = None


async def login():
    """登录获取 token"""
    global TOKEN
    print("\n" + "="*60)
    print("Logging in as admin...")
    print("="*60)
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/api/v1/auth/login",
            json={"username": "admin", "password": "admin123"}
        )
        
        if response.status_code == 200:
            data = response.json()
            TOKEN = data["access_token"]
            print(f"✅ Login successful! Token: {TOKEN[:50]}...")
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(response.text)
            raise Exception("Login failed")


async def test_create_faq():
    """测试创建 FAQ"""
    print("\n" + "="*60)
    print("Testing POST /api/v1/faqs (Create FAQ)")
    print("="*60)
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/api/v1/faqs",
            headers={"Authorization": f"Bearer {TOKEN}"},
            json={
                "question": "如何预约咨询服务？",
                "answer": "您可以通过我们的预约页面选择合适的时间进行咨询服务预约。步骤如下：1. 访问预约页面 2. 选择日期和时间 3. 填写联系信息 4. 提交预约",
                "keywords": ["预约", "咨询", "服务", "时间"],
                "category": "预约相关",
                "priority": 90,
                "is_active": True
            }
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 201:
            data = response.json()
            print(f"✅ FAQ created successfully!")
            print(f"   ID: {data['id']}")
            print(f"   Question: {data['question']}")
            print(f"   Priority: {data['priority']}")
            return data['id']
        else:
            print(f"❌ Failed to create FAQ")
            print(response.text)
            return None


async def test_create_more_faqs():
    """创建更多 FAQ"""
    print("\n" + "="*60)
    print("Creating more FAQs...")
    print("="*60)
    
    faqs = [
        {
            "question": "预约需要多长时间？",
            "answer": "每个预约时间槽为 30 分钟。",
            "keywords": ["预约", "时间", "时长"],
            "category": "预约相关",
            "priority": 80
        },
        {
            "question": "如何取消预约？",
            "answer": "如需取消预约，请联系我们的客服团队，提供您的预约确认号。",
            "keywords": ["取消", "预约", "客服"],
            "category": "预约相关",
            "priority": 85
        },
        {
            "question": "你们提供哪些服务？",
            "answer": "我们提供咨询服务、技术支持、产品演示和培训服务。",
            "keywords": ["服务", "咨询", "技术", "培训"],
            "category": "服务介绍",
            "priority": 70
        }
    ]
    
    async with httpx.AsyncClient() as client:
        for faq in faqs:
            response = await client.post(
                f"{BASE_URL}/api/v1/faqs",
                headers={"Authorization": f"Bearer {TOKEN}"},
                json=faq
            )
            if response.status_code == 201:
                print(f"✅ Created: {faq['question']}")
            else:
                print(f"❌ Failed: {faq['question']}")


async def test_search_faqs():
    """测试搜索 FAQ"""
    print("\n" + "="*60)
    print("Testing GET /api/v1/faqs/search")
    print("="*60)
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/api/v1/faqs/search",
            params={"q": "预约", "limit": 5}
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Found {data['total']} FAQs")
            for i, result in enumerate(data['results'], 1):
                print(f"\n   {i}. {result['question']}")
                print(f"      Relevance: {result['relevance_score']:.2f}")
                print(f"      Category: {result.get('category', 'N/A')}")
        else:
            print(f"❌ Failed to search FAQs")
            print(response.text)


async def test_chat_quick_questions():
    """测试获取快捷问题"""
    print("\n" + "="*60)
    print("Testing GET /api/v1/chat/quick-questions")
    print("="*60)
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/api/v1/chat/quick-questions")
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Got {len(data['questions'])} quick questions")
            for q in data['questions']:
                print(f"   - {q['question']} ({q['category']})")
        else:
            print(f"❌ Failed to get quick questions")
            print(response.text)


async def test_chat_send_message():
    """测试发送聊天消息"""
    print("\n" + "="*60)
    print("Testing POST /api/v1/chat (Send Message)")
    print("="*60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{BASE_URL}/api/v1/chat",
            json={
                "message": "如何预约咨询服务？"
            }
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Got AI response!")
            print(f"   Session ID: {data['session_id']}")
            print(f"   Response time: {data['response_time']:.2f}s")
            print(f"   Sources: {len(data['sources'])}")
            print(f"\n   AI Response:")
            print(f"   {data['message'][:200]}...")
            
            if data['sources']:
                print(f"\n   Sources:")
                for source in data['sources']:
                    print(f"   - [{source['type']}] {source['title']}")
            
            return data['session_id']
        else:
            print(f"❌ Failed to send message")
            print(response.text)
            return None


async def test_chat_with_session(session_id):
    """测试多轮对话"""
    print("\n" + "="*60)
    print("Testing POST /api/v1/chat (Multi-turn)")
    print("="*60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{BASE_URL}/api/v1/chat",
            json={
                "message": "需要多长时间？",
                "session_id": session_id
            }
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Got AI response!")
            print(f"   Session ID: {data['session_id']}")
            print(f"   Response time: {data['response_time']:.2f}s")
            print(f"\n   AI Response:")
            print(f"   {data['message'][:200]}...")
        else:
            print(f"❌ Failed to send message")
            print(response.text)


async def test_chat_history(session_id):
    """测试获取聊天历史"""
    print("\n" + "="*60)
    print("Testing GET /api/v1/chat/history/{session_id}")
    print("="*60)
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/api/v1/chat/history/{session_id}"
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Got {data['total']} messages")
            for msg in data['messages']:
                print(f"\n   [{msg['role']}]: {msg['content'][:100]}...")
        else:
            print(f"❌ Failed to get chat history")
            print(response.text)


async def test_list_faqs():
    """测试获取 FAQ 列表"""
    print("\n" + "="*60)
    print("Testing GET /api/v1/faqs (List FAQs)")
    print("="*60)
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/api/v1/faqs",
            headers={"Authorization": f"Bearer {TOKEN}"},
            params={"page": 1, "page_size": 10}
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Got {data['total']} FAQs (Page {data['page']}/{data['total_pages']})")
            for item in data['items']:
                print(f"   - {item['question']} (Priority: {item['priority']})")
        else:
            print(f"❌ Failed to list FAQs")
            print(response.text)


async def main():
    """运行所有测试"""
    print("\n" + "="*60)
    print("🚀 Chat and FAQ API Tests")
    print("="*60)
    
    try:
        # 1. 登录
        await login()
        
        # 2. 创建 FAQ
        faq_id = await test_create_faq()
        
        # 3. 创建更多 FAQ
        await test_create_more_faqs()
        
        # 4. 搜索 FAQ
        await test_search_faqs()
        
        # 5. 获取 FAQ 列表
        await test_list_faqs()
        
        # 6. 获取快捷问题
        await test_chat_quick_questions()
        
        # 7. 发送聊天消息
        session_id = await test_chat_send_message()
        
        # 8. 多轮对话
        if session_id:
            await test_chat_with_session(session_id)
            
            # 9. 获取聊天历史
            await test_chat_history(session_id)
        
        print("\n" + "="*60)
        print("✅ All tests completed!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

