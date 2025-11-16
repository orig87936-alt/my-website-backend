import sys
sys.path.insert(0, '.')

from app.services.auth import auth_service

print('Testing authentication service...')
print(f'Admin username: {auth_service.admin_username}')
print(f'Visitor username: {auth_service.visitor_username}')

print('\n1. Testing admin login...')
try:
    token = auth_service.login('admin', 'admin123')
    if token:
        print(f'   Success! Token: {token.access_token[:50]}...')
    else:
        print('   Failed: Invalid credentials')
except Exception as e:
    print(f'   Error: {e}')
    import traceback
    traceback.print_exc()

print('\n2. Testing visitor login...')
try:
    token = auth_service.login('visitor', 'visitor123')
    if token:
        print(f'   Success! Token: {token.access_token[:50]}...')
    else:
        print('   Failed: Invalid credentials')
except Exception as e:
    print(f'   Error: {e}')
    import traceback
    traceback.print_exc()
