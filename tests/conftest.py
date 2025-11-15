"""Test configuration and fixtures."""
from datetime import datetime, timedelta
from decimal import Decimal
import pytest
from app import create_app, db
from app.models import User, Category, Expense
from tests.auth_fixture import AuthActions

@pytest.fixture
def app():
    """Create application for testing."""
    app = create_app('testing')
    
    # Configure testing
    app.config.update({
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SERVER_NAME': 'localhost',
        'APPLICATION_ROOT': '/',
        'PREFERRED_URL_SCHEME': 'http'
    })
    
    with app.app_context():
        # Initialize database
        db.create_all()
    
    return app

@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Create test CLI runner."""
    return app.test_cli_runner()

@pytest.fixture
def auth(client):
    """Authentication fixture."""
    return AuthActions(client)

@pytest.fixture
def test_user(app):
    """Create and return a test user."""
    with app.app_context():
        db.session.begin()
        try:
            user = User(
                username='test_user',
                email='test@example.com',
                theme_preference='light',
                currency_symbol='₦',
                monthly_income=5000.00,
                total_budget=4000.00
            )
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()
            
            # Refresh the user instance to ensure it's attached to the session
            db.session.refresh(user)
            return user
        except:
            db.session.rollback()
            raise

@pytest.fixture
def sample_data(app, test_user):
    """Create sample data for testing."""
    with app.app_context():
        db.session.begin()
        try:
            # Create categories
            categories = [
                Category(user_id=test_user.id, name='Food', icon='utensils', 
                        color='#FF0000', budget_amount=500),
                Category(user_id=test_user.id, name='Transport', icon='car', 
                        color='#00FF00', budget_amount=300),
                Category(user_id=test_user.id, name='Entertainment', icon='film', 
                        color='#0000FF', budget_amount=200)
            ]
            db.session.add_all(categories)
            db.session.flush()  # Get IDs without committing
            
            # Create expenses for the last 12 months
            now = datetime.now()
            for category in categories:
                for i in range(12):
                    month = ((now.month - i - 1) % 12) + 1
                    year = now.year - ((i + 12 - now.month) // 12)
                    date = datetime(year, month, 15)
                    
                    # Add 2-3 expenses per category per month
                    expenses = [
                        Expense(
                            user_id=test_user.id,
                            category_id=category.id,
                            date=date - timedelta(days=5),
                            amount=Decimal(str(50 + (i * 2))),
                            description=f'Test expense 1 - {category.name}',
                            payment_method='cash'
                        ),
                        Expense(
                            user_id=test_user.id,
                            category_id=category.id,
                            date=date,
                            amount=Decimal(str(75 + (i * 3))),
                            description=f'Test expense 2 - {category.name}',
                            payment_method='credit'
                        ),
                        Expense(
                            user_id=test_user.id,
                            category_id=category.id,
                            date=date + timedelta(days=5),
                            amount=Decimal(str(25 + i)),
                            description=f'Test expense 3 - {category.name}',
                            payment_method='debit'
                        )
                    ]
                    db.session.add_all(expenses)
            
            db.session.commit()
            
            # Refresh all objects to ensure they're properly attached
            for category in categories:
                db.session.refresh(category)
            
            return {'categories': categories}
        except:
            db.session.rollback()
            raise