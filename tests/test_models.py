"""Test cases for database models."""
import pytest
from app.models import User, Category, Expense
from app import db

def test_user_password_hashing():
    """Test password hashing and verification."""
    u = User(username='test', email='test@test.com')
    u.set_password('cat')
    assert not u.check_password('dog')
    assert u.check_password('cat')

def test_user_creation(init_database):
    """Test user creation and retrieval."""
    user = User.query.filter_by(username='test_user').first()
    assert user is not None
    assert user.email == 'test@example.com'
    assert user.check_password('password123')

def test_category_creation(init_database):
    """Test category creation and user relationship."""
    user = User.query.first()
    category = Category(
        user_id=user.id,
        name='Test Category',
        icon='test',
        color='#123456'
    )
    db.session.add(category)
    db.session.commit()
    
    assert category in user.categories
    assert category.user == user