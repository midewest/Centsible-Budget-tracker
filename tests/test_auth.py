"""Test authentication fixtures."""
import pytest

class AuthActions:
    def __init__(self, client):
        self._client = client

    def login(self, username='test_user', password='password123'):
        return self._client.post(
            '/auth/login',
            data={'username': username, 'password': password}
        )

    def logout(self):
        return self._client.get('/auth/logout')

@pytest.fixture
def auth(client):
    return AuthActions(client)