"""Routes for expense reporting and analysis."""
from datetime import datetime
from decimal import Decimal
import csv
from io import StringIO
from sqlalchemy import extract, func
from flask import (
    Blueprint, render_template, send_file, make_response,
    jsonify, request, current_app
)
from flask_login import login_required, current_user
from .. import db
from ..models import Expense, Category, Budget

bp = Blueprint('reports', __name__, url_prefix='/reports')

@bp.route('/')
@login_required
def index():
    """Display reports dashboard."""
    now = datetime.now()
    
    # Get year-to-date spending by category
    ytd_spending = db.session.query(
        Category,
        func.sum(Expense.amount).label('total')
    ).join(Expense).filter(
        Expense.user_id == current_user.id,
        extract('year', Expense.date) == now.year
    ).group_by(Category).all()
    
    # Get monthly totals for the year
    monthly_totals = []
    for month in range(1, 13):
        total = db.session.query(
            func.sum(Expense.amount)
        ).filter(
            Expense.user_id == current_user.id,
            extract('year', Expense.date) == now.year,
            extract('month', Expense.date) == month
        ).scalar() or Decimal('0')
        
        monthly_totals.append({
            'month': month,
            'total': total
        })
    
    # Calculate spending trends
    trends = []
    for category, total in ytd_spending:
        # Get last 3 months of spending for trend
        last_3_months = []
        for i in range(3):
            month = now.month - i
            year = now.year
            if month < 1:
                month += 12
                year -= 1
            
            monthly_spent = db.session.query(
                func.sum(Expense.amount)
            ).filter(
                Expense.user_id == current_user.id,
                Expense.category_id == category.id,
                extract('year', Expense.date) == year,
                extract('month', Expense.date) == month
            ).scalar() or Decimal('0')
            
            last_3_months.append(monthly_spent)
        
        # Calculate trend (positive if increasing, negative if decreasing)
        if len(last_3_months) >= 2:
            trend = (last_3_months[0] - last_3_months[-1]) / last_3_months[-1] * 100
        else:
            trend = 0
        
        trends.append({
            'category': category,
            'total': total,
            'trend': round(trend, 1)
        })
    
    # Get budget vs actual for current month
    budget_vs_actual = []
    categories = current_user.categories.filter_by(is_active=True).all()
    for category in categories:
        budget_vs_actual.append({
            'category': category,
            'budget': category.budget_amount,
            'actual': category.current_month_spending,
            'variance': category.budget_amount - category.current_month_spending
            if category.budget_amount else None
        })
    
    return render_template(
        'reports/index.html',
        ytd_spending=ytd_spending,
        monthly_totals=monthly_totals,
        trends=trends,
        budget_vs_actual=budget_vs_actual
    )

@bp.route('/export/expenses')
@login_required
def export_expenses():
    """Export expenses as CSV."""
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'Date', 'Category', 'Description', 'Amount',
        'Payment Method', 'Is Recurring', 'Recurrence Frequency',
        'Notes'
    ])
    
    # Write expense data
    expenses = current_user.expenses.order_by(Expense.date.desc()).all()
    for expense in expenses:
        writer.writerow([
            expense.date.strftime('%Y-%m-%d'),
            expense.category.name,
            expense.description,
            float(expense.amount),
            expense.payment_method,
            'Yes' if expense.is_recurring else 'No',
            expense.recurrence_frequency or '',
            expense.receipt_note or ''
        ])
    
    # Create response
    output.seek(0)
    return send_file(
        StringIO(output.getvalue()),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'expenses_{datetime.now().strftime("%Y%m%d")}.csv'
    )

@bp.route('/api/spending-history')
@login_required
def spending_history():
    """Get historical spending data for charts."""
    category_id = request.args.get('category_id', type=int)
    months = request.args.get('months', 12, type=int)
    
    now = datetime.now()
    data = []
    
    for i in range(months - 1, -1, -1):
        month = ((now.month - i - 1) % 12) + 1
        year = now.year - ((i + 12 - now.month) // 12)
        
        query = db.session.query(func.sum(Expense.amount))
        query = query.filter(
            Expense.user_id == current_user.id,
            extract('year', Expense.date) == year,
            extract('month', Expense.date) == month
        )
        
        if category_id:
            query = query.filter(Expense.category_id == category_id)
        
        total = query.scalar() or Decimal('0')
        
        data.append({
            'year': year,
            'month': month,
            'total': float(total)
        })
    
    return jsonify(data)

@bp.route('/trends')
@login_required
def category_trends():
    """Display detailed category spending trends."""
    categories = current_user.categories.filter_by(is_active=True).all()
    selected_id = request.args.get('category_id', type=int)
    selected_category = next(
        (c for c in categories if c.id == selected_id),
        categories[0] if categories else None
    )
    
    if selected_category:
        # Get monthly spending for selected category
        now = datetime.now()
        monthly_data = []
        
        for i in range(12):
            month = ((now.month - i - 1) % 12) + 1
            year = now.year - ((i + 12 - now.month) // 12)
            
            total = db.session.query(
                func.sum(Expense.amount)
            ).filter(
                Expense.user_id == current_user.id,
                Expense.category_id == selected_category.id,
                extract('year', Expense.date) == year,
                extract('month', Expense.date) == month
            ).scalar() or Decimal('0')
            
            monthly_data.append({
                'year': year,
                'month': month,
                'total': total
            })
        
        # Calculate statistics
        totals = [d['total'] for d in monthly_data]
        avg_spending = sum(totals) / len(totals) if totals else Decimal('0')
        max_spending = max(totals) if totals else Decimal('0')
        min_spending = min(totals) if totals else Decimal('0')
        
        stats = {
            'average': avg_spending,
            'maximum': max_spending,
            'minimum': min_spending,
            'current': selected_category.current_month_spending,
            'budget': selected_category.budget_amount
        }
    else:
        monthly_data = []
        stats = None
    
    return render_template(
        'reports/trends.html',
        categories=categories,
        selected_category=selected_category,
        monthly_data=monthly_data,
        stats=stats
    )