"""Test cases for reports module."""
from datetime import datetime, timedelta
from decimal import Decimal
import csv
from io import StringIO
import pytest
from flask import url_for
from flask_login import login_user

def test_reports_index_requires_login(app, client):
    """Test that reports index requires login."""
    with app.test_request_context():
        url = url_for('reports.index')
    response = client.get(url)
    assert response.status_code == 302
    assert 'login' in response.headers['Location']

def test_reports_index(app, client, auth, test_user, sample_data):
    """Test reports index page."""
    with app.app_context():
        auth.login()
        url = url_for('reports.index')
        response = client.get(url, follow_redirects=True)
        assert response.status_code == 200
        
        # Check that required sections are present
        html = response.get_data(as_text=True)
        assert 'Year-to-Date Spending by Category' in html
        assert 'Monthly Spending Trends' in html
        assert 'Category Trends' in html
        assert 'Budget vs Actual' in html

def test_export_expenses(app, client, auth, test_user, sample_data):
    """Test expense export functionality."""
    with app.app_context():
        auth.login()
        url = url_for('reports.export_expenses')
        response = client.get(url, follow_redirects=True)
        assert response.status_code == 200
        assert response.headers['Content-Type'] == 'text/csv'
        assert 'attachment' in response.headers['Content-Disposition']
    
    # Parse CSV and validate content
    csv_data = StringIO(response.get_data(as_text=True))
    reader = csv.reader(csv_data)
    rows = list(reader)
    
    # Check header
    assert rows[0] == [
        'Date', 'Category', 'Description', 'Amount',
        'Payment Method', 'Is Recurring', 'Recurrence Frequency',
        'Notes'
    ]
    
    # Check data rows
    assert len(rows) > 1  # Should have at least one expense
    for row in rows[1:]:
        assert len(row) == 8  # All columns should be present
        
        # Validate date format
        date_str = row[0]
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            pytest.fail(f"Invalid date format: {date_str}")
        
        # Amount should be numeric
        amount_str = row[3]
        try:
            float(amount_str)
        except ValueError:
            pytest.fail(f"Invalid amount format: {amount_str}")

def test_spending_history_api(app, client, auth, test_user, sample_data):
    """Test spending history API."""
    with app.app_context():
        auth.login()
        
        # Test without category filter
        url = url_for('reports.spending_history')
        response = client.get(url, follow_redirects=True)
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) == 12  # Default 12 months
    
    # Validate data structure
    for entry in data:
        assert 'year' in entry
        assert 'month' in entry
        assert 'total' in entry
        assert isinstance(entry['year'], int)
        assert isinstance(entry['month'], int)
        assert 1 <= entry['month'] <= 12
        assert isinstance(entry['total'], (int, float))
    
    # Test with category filter
    category = test_user.categories.first()
    response = client.get(url_for('reports.spending_history', 
                                 category_id=category.id))
    assert response.status_code == 200
    data = response.get_json()
    
    # Test custom month range
    response = client.get(url_for('reports.spending_history', months=6))
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 6

def test_category_trends(app, client, auth, test_user, sample_data):
    """Test category trends page."""
    with app.app_context():
        auth.login()
        
        # Test without category selection
        url = url_for('reports.category_trends')
        response = client.get(url, follow_redirects=True)
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert 'Category Spending Trends' in html
    
    # Test with specific category
    category = test_user.categories.first()
    response = client.get(url_for('reports.category_trends', 
                                 category_id=category.id))
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert category.name in html
    assert 'Average Monthly' in html
    assert 'Maximum' in html
    assert 'Minimum' in html