"""
Test script for Appointment API endpoints
"""
import asyncio
import httpx
from datetime import date, timedelta

BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"


async def test_appointments():
    """Test all appointment API endpoints"""
    
    print("\n" + "="*60)
    print("🚀 Appointment API Tests")
    print("="*60 + "\n")
    
    async with httpx.AsyncClient() as client:
        
        # ============================================================
        # 1. Login as admin
        # ============================================================
        print("="*60)
        print("Logging in as admin...")
        print("="*60)
        
        login_response = await client.post(
            f"{API_BASE}/auth/login",
            json={"username": "admin", "password": "admin123"}
        )
        
        if login_response.status_code == 200:
            token = login_response.json()["access_token"]
            print(f"✅ Login successful! Token: {token[:50]}...")
            headers = {"Authorization": f"Bearer {token}"}
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            print(login_response.text)
            return
        
        # ============================================================
        # 2. Get available slots for tomorrow
        # ============================================================
        print("\n" + "="*60)
        print("Testing GET /api/v1/appointments/available-slots")
        print("="*60)
        
        tomorrow = date.today() + timedelta(days=1)
        slots_response = await client.get(
            f"{API_BASE}/appointments/available-slots",
            params={"appointment_date": str(tomorrow)}
        )
        
        print(f"Status: {slots_response.status_code}")
        if slots_response.status_code == 200:
            slots_data = slots_response.json()
            print(f"✅ Got {len(slots_data['slots'])} time slots for {slots_data['date']}")
            available_slots = [s for s in slots_data['slots'] if s['available']]
            print(f"   Available slots: {len(available_slots)}")
            if available_slots:
                print(f"   First available: {available_slots[0]['time']}")
        else:
            print(f"❌ Failed to get available slots")
            print(slots_response.text)
            return
        
        # ============================================================
        # 3. Create appointment
        # ============================================================
        print("\n" + "="*60)
        print("Testing POST /api/v1/appointments (Create Appointment)")
        print("="*60)
        
        # Use first available slot
        first_slot = available_slots[0]['time'] if available_slots else "14:00"
        
        appointment_data = {
            "name": "张三",
            "email": "zhangsan@example.com",
            "phone": "13800138000",
            "appointment_date": str(tomorrow),
            "time_slot": first_slot,
            "service_type": "咨询服务",
            "notes": "希望了解产品详情"
        }
        
        create_response = await client.post(
            f"{API_BASE}/appointments",
            json=appointment_data
        )
        
        print(f"Status: {create_response.status_code}")
        if create_response.status_code == 201:
            result = create_response.json()
            print(f"✅ Appointment created successfully!")
            print(f"   Confirmation Number: {result['appointment']['confirmation_number']}")
            print(f"   Appointment ID: {result['appointment']['id']}")
            print(f"   Date: {result['appointment']['appointment_date']}")
            print(f"   Time: {result['appointment']['time_slot']}")
            print(f"   Status: {result['appointment']['status']}")
            print(f"   Message: {result['message']}")
            
            appointment_id = result['appointment']['id']
        else:
            print(f"❌ Failed to create appointment")
            print(create_response.text)
            return
        
        # ============================================================
        # 4. Try to create duplicate appointment (should fail)
        # ============================================================
        print("\n" + "="*60)
        print("Testing POST /api/v1/appointments (Duplicate - Should Fail)")
        print("="*60)
        
        duplicate_response = await client.post(
            f"{API_BASE}/appointments",
            json=appointment_data
        )
        
        print(f"Status: {duplicate_response.status_code}")
        if duplicate_response.status_code == 409:
            print(f"✅ Correctly rejected duplicate appointment")
            print(f"   Error: {duplicate_response.json()['detail']}")
        else:
            print(f"⚠️  Expected 409 Conflict, got {duplicate_response.status_code}")
        
        # ============================================================
        # 5. Get appointment by ID
        # ============================================================
        print("\n" + "="*60)
        print(f"Testing GET /api/v1/appointments/{appointment_id}")
        print("="*60)
        
        get_response = await client.get(
            f"{API_BASE}/appointments/{appointment_id}"
        )
        
        print(f"Status: {get_response.status_code}")
        if get_response.status_code == 200:
            apt = get_response.json()
            print(f"✅ Got appointment successfully!")
            print(f"   Name: {apt['name']}")
            print(f"   Email: {apt['email']}")
            print(f"   Date: {apt['appointment_date']} {apt['time_slot']}")
            print(f"   Status: {apt['status']}")
        else:
            print(f"❌ Failed to get appointment")
            print(get_response.text)
        
        # ============================================================
        # 6. Get all appointments (admin)
        # ============================================================
        print("\n" + "="*60)
        print("Testing GET /api/v1/appointments (List All - Admin)")
        print("="*60)
        
        list_response = await client.get(
            f"{API_BASE}/appointments",
            headers=headers,
            params={"page": 1, "page_size": 10}
        )
        
        print(f"Status: {list_response.status_code}")
        if list_response.status_code == 200:
            list_data = list_response.json()
            print(f"✅ Got {len(list_data['items'])} appointments")
            print(f"   Total: {list_data['total']}")
            print(f"   Page: {list_data['page']}/{list_data['total_pages']}")
            if list_data['items']:
                print(f"\n   First appointment:")
                apt = list_data['items'][0]
                print(f"   - ID: {apt['id']}")
                print(f"   - Name: {apt['name']}")
                print(f"   - Date: {apt['appointment_date']} {apt['time_slot']}")
                print(f"   - Status: {apt['status']}")
        else:
            print(f"❌ Failed to get appointments list")
            print(list_response.text)
        
        # ============================================================
        # 7. Update appointment status (admin)
        # ============================================================
        print("\n" + "="*60)
        print(f"Testing PUT /api/v1/appointments/{appointment_id} (Update Status)")
        print("="*60)
        
        update_response = await client.put(
            f"{API_BASE}/appointments/{appointment_id}",
            headers=headers,
            json={"status": "confirmed", "notes": "已确认预约"}
        )
        
        print(f"Status: {update_response.status_code}")
        if update_response.status_code == 200:
            updated = update_response.json()
            print(f"✅ Appointment updated successfully!")
            print(f"   New status: {updated['status']}")
            print(f"   New notes: {updated['notes']}")
        else:
            print(f"❌ Failed to update appointment")
            print(update_response.text)
        
        # ============================================================
        # 8. Check available slots again (should show one less)
        # ============================================================
        print("\n" + "="*60)
        print("Testing GET /api/v1/appointments/available-slots (After Booking)")
        print("="*60)
        
        slots_response2 = await client.get(
            f"{API_BASE}/appointments/available-slots",
            params={"appointment_date": str(tomorrow)}
        )
        
        if slots_response2.status_code == 200:
            slots_data2 = slots_response2.json()
            available_slots2 = [s for s in slots_data2['slots'] if s['available']]
            print(f"✅ Available slots now: {len(available_slots2)}")
            print(f"   (Was {len(available_slots)} before booking)")
            
            # Find the booked slot
            booked_slot = next((s for s in slots_data2['slots'] if s['time'] == first_slot), None)
            if booked_slot:
                print(f"   Slot {first_slot} is now: {'available' if booked_slot['available'] else 'booked'} ✅")
        
        # ============================================================
        # 9. Cancel appointment (admin)
        # ============================================================
        print("\n" + "="*60)
        print(f"Testing DELETE /api/v1/appointments/{appointment_id} (Cancel)")
        print("="*60)
        
        delete_response = await client.delete(
            f"{API_BASE}/appointments/{appointment_id}",
            headers=headers
        )
        
        print(f"Status: {delete_response.status_code}")
        if delete_response.status_code == 204:
            print(f"✅ Appointment cancelled successfully!")
        else:
            print(f"❌ Failed to cancel appointment")
            print(delete_response.text)
        
        # ============================================================
        # 10. Verify cancellation
        # ============================================================
        print("\n" + "="*60)
        print("Verifying cancellation...")
        print("="*60)
        
        verify_response = await client.get(
            f"{API_BASE}/appointments/{appointment_id}"
        )
        
        if verify_response.status_code == 200:
            apt = verify_response.json()
            if apt['status'] == 'cancelled':
                print(f"✅ Appointment status is now: {apt['status']}")
            else:
                print(f"⚠️  Expected status 'cancelled', got '{apt['status']}'")
        
        print("\n" + "="*60)
        print("✅ All tests completed!")
        print("="*60)


if __name__ == "__main__":
    asyncio.run(test_appointments())

