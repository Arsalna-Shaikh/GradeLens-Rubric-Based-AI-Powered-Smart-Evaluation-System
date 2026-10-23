from app.services.auth_service import create_access_token


def test_header_fallbacks_and_user_in_login(client):
    client.post('/auth/register', json={'name':'A','email':'fallback@example.com','password':'password123','role':'student'})
    login = client.post('/auth/login', json={'email':'fallback@example.com','password':'password123'})
    body = login.json()
    assert body['user']['email'] == 'fallback@example.com'
    token = body['access_token']
    assert client.get('/auth/me', headers={'X-Access-Token': token}).status_code == 200
    assert client.get('/auth/me', params={'token': token}).status_code == 200


def test_missing_and_invalid_auth_are_distinct(client):
    assert client.get('/auth/me').json()['detail'] == 'Not authenticated'
    assert client.get('/auth/me', headers={'Authorization':'Bearer bad'}).json()['detail'] == 'Invalid token'
