import requests
import json

url = 'http://127.0.0.1:8000/api/auth/register/'
data = {
    'username': 'tester',
    'email': 'tester1@example.com',
    'password': 'Testpass123',
    'role': 'student'
}

try:
    r = requests.post(url, json=data, timeout=10)
    print('STATUS', r.status_code)
    try:
        print(json.dumps(r.json(), indent=2))
    except Exception:
        print(r.text)
except Exception as e:
    print('ERROR', e)
