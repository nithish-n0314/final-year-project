import requests
url = 'http://127.0.0.1:8000/api/auth/register/'
data = {
    'username':'tester',
    'email':'tester@example.com',
    'password':'Password123',
    'role':'professional'
}
resp = requests.post(url, json=data)
print('STATUS', resp.status_code)
print(resp.text)
