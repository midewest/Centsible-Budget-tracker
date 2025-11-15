"""Test cases for dashboard functionality."""
from datetime import datetime, timedelta
from decimal import Decimal
import pytest
from app.models import Expense, Category, BudgetAlert

def test_dashboard_view(client, sample_data, auth):
    """Test dashboard page loads with correct data."""
    auth.login()
    response = client.get('/')
    assert response.status_code == 200
    
    # Test required template variables
    assert b'Monthly Spending Breakdown' in response.data
    assert b'Quick Add Expense' in response.data
    assert b'Recent Expenses' in response.data

def test_dashboard_stats(client, sample_data, auth):
    """Test dashboard statistics calculations."""
    auth.login()
    
    # Create test expenses
    now = datetime.now()
    last_month = now - timedelta(days=30)
    
    category = Category.query.first()
    expenses = [
        Expense(
            user_id=1,
            category_id=category.id,
            amount=Decimal('50.00'),
            description='Test expense 1',
            date=now.date()
        ),
        Expense(
            user_id=1,
            category_id=category.id,
            amount=Decimal('30.00'),
            description='Test expense 2',
            date=last_month.date()
        )
    ]
    
    db = init_database
    db.session.add_all(expenses)
    db.session.commit()
    
    response = client.get('/')
    assert response.status_code == 200
    
    # Verify monthly spending is shown
    assert '₦50.00' in response.get_data(as_text=True)
    
    # Verify spending change calculation
    assert b'67%' in response.data  # (50-30)/30 * 100

def test_quick_add_expense(client, sample_data, auth):
    """Test quick expense addition from dashboard."""
    auth.login()
    
    # Get first category for form
    category = Category.query.first()
    
    response = client.post('/expenses/quick-add', data={
        'amount': '42.50',
        'description': 'Quick test expense',
        'category_id': category.id
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Expense added successfully!' in response.data
    
    # Verify expense was added
    expense = Expense.query.filter_by(description='Quick test expense').first()
    assert expense is not None
    assert expense.amount == Decimal('42.50')
    assert expense.category_id == category.id

def test_alert_display(client, sample_data, auth):
    """Test budget alerts show on dashboard."""
    auth.login()
    
    # Create test alert
    category = Category.query.first()
    alert = BudgetAlert(
        user_id=1,
        category_id=category.id,
        alert_type='threshold',
        message='Test budget alert',
        is_read=False
    )
    
    db = init_database
    db.session.add(alert)
    db.session.commit()
    
    response = client.get('/')
    assert response.status_code == 200
    assert b'Test budget alert' in response.data

def test_chart_data(client, sample_data, auth):
    """Test spending chart data generation."""
    auth.login()
    
    # Create test expenses in different categories
    categories = Category.query.all()[:2]  # Get first two categories
    now = datetime.now()
    
    expenses = [
        Expense(
            user_id=1,
            category_id=categories[0].id,
            amount=Decimal('100.00'),
            description='Category 1 expense',
            date=now.date()
        ),
        Expense(
            user_id=1,
            category_id=categories[1].id,
            amount=Decimal('50.00'),
            description='Category 2 expense',
            date=now.date()
        )
    ]
    
    db = init_database
    db.session.add_all(expenses)
    db.session.commit()
    
    response = client.get('/')
    assert response.status_code == 200
    
    # Verify chart data is included
    assert categories[0].name.encode() in response.data
    assert categories[1].name.encode() in response.data
    assert b'100.0' in response.data  # Chart amounts as floats
    assert b'50.0' in response.data