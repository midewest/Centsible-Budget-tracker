"""Main routes for Centsible Budget Tracker."""
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy import extract, func
from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy.exc import SQLAlchemyError
from .. import db
from ..models import Expense, Category, BudgetAlert, Budget
from ..forms.quick import QuickExpenseForm

bp = Blueprint('main', __name__)

@bp.route('/dashboard')
@bp.route('/')
@login_required
def index():
    """Main dashboard view."""
    # Get current month spending
    now = datetime.now()
    monthly_spending = current_user.get_monthly_spending(now.year, now.month)
    
    # Calculate previous month spending change
    prev_month = now.month - 1 if now.month > 1 else 12
    prev_year = now.year if now.month > 1 else now.year - 1
    prev_spending = current_user.get_monthly_spending(prev_year, prev_month)
    
    if prev_spending > 0:
        monthly_spending_change = int(
            ((monthly_spending - prev_spending) / prev_spending) * 100
        )
    else:
        monthly_spending_change = None
    
    # Calculate budget remaining
    budget_remaining = (
        current_user.total_budget - monthly_spending 
        if current_user.total_budget else None
    )
    
    # Get top spending category
    top_category = None
    top_category_spent = Decimal('0')
    
    category_spending = (
        db.session.query(
            Category,
            func.sum(Expense.amount).label('total_spent')
        )
        .join(Expense)
        .filter(
            Expense.user_id == current_user.id,
            extract('year', Expense.date) == now.year,
            extract('month', Expense.date) == now.month
        )
        .group_by(Category)
        .order_by(func.sum(Expense.amount).desc())
        .first()
    )
    
    if category_spending:
        top_category = category_spending[0]
        top_category_spent = category_spending[1]
    
    # Get recent expenses
    recent_expenses = current_user.expenses.order_by(
        Expense.date.desc()
    ).limit(5).all()
    
    # Get unread alerts
    alerts = BudgetAlert.query.filter_by(
        user_id=current_user.id,
        is_read=False
    ).order_by(BudgetAlert.created_at.desc()).all()
    
    # Quick add expense form
    quick_form = QuickExpenseForm()
    quick_form.category_id.choices = [
        (c.id, c.name) for c in current_user.categories.all()
    ]
    
    # Prepare chart data
    categories = []
    amounts = []
    colors = []
    
    category_totals = (
        db.session.query(
            Category,
            func.sum(Expense.amount).label('total_spent')
        )
        .join(Expense)
        .filter(
            Expense.user_id == current_user.id,
            extract('year', Expense.date) == now.year,
            extract('month', Expense.date) == now.month
        )
        .group_by(Category)
        .order_by(func.sum(Expense.amount).desc())
        .all()
    )
    
    for category, total in category_totals:
        categories.append(category.name)
        amounts.append(float(total))  # Convert Decimal to float for JSON
        colors.append(category.color or '#10b981')  # Use default if no color
    
    chart_data = {
        'categories': categories,
        'amounts': amounts,
        'colors': colors
    }
    
    return render_template(
        'dashboard/index.html',
        monthly_spending=monthly_spending,
        monthly_spending_change=monthly_spending_change,
        budget_remaining=budget_remaining,
        top_category=top_category,
        top_category_spent=top_category_spent,
        recent_expenses=recent_expenses,
        alerts=alerts,
        quick_form=quick_form,
        chart_data=chart_data
    )