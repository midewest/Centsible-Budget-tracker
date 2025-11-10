"""Authentication fixture for testing."""
import functools
from flask import session

class AuthActions:
    """Authentication test helper."""
    
    def __init__(self, client):
        self._client = client
    
    def login(self, username='test_user', password='password123'):
        """Log in as test user."""
        print("\nAttempting login...")
        response = self._client.post(
            '/auth/login',
            data={
                'username': username,
                'password': password,
                'remember_me': False
            },
            follow_redirects=True
        )
        print(f"Login response status: {response.status_code}")
        print(f"Response data: {response.get_data(as_text=True)[:200]}...")
        assert response.status_code == 200, "Login failed"
        return response
    
    def logout(self):
        """Log out test user."""
        return self._client.get('/auth/logout')