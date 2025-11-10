"""Routes for budget management."""
from datetime import datetime
from decimal import Decimal
from flask import (
    Blueprint, render_template, redirect, url_for, flash, request, jsonify
)
from flask_login import login_required, current_user
from sqlalchemy.exc import SQLAlchemyError

from .. import db
from ..models import Category, Budget, BudgetAlert
from ..forms.budget import CategoryBudgetForm, UserBudgetForm

bp = Blueprint('budgets', __name__, url_prefix='/budgets')

@bp.route('/')
@login_required
def index():
    """Display budget management dashboard."""
    categories = current_user.categories.filter_by(is_active=True).all()
    now = datetime.now()
    
    # Get current month's budget data
    budgets = {
        b.category_id: b for b in Budget.query.filter(
            Budget.user_id == current_user.id,
            Budget.year == now.year,
            Budget.month == now.month
        ).all()
    }
    
    # Get alerts
    alerts = BudgetAlert.query.filter_by(
        user_id=current_user.id,
        is_read=False
    ).order_by(BudgetAlert.created_at.desc()).all()
    
    return render_template(
        'budgets/manage.html',
        categories=categories,
        budgets=budgets,
        alerts=alerts
    )

@bp.route('/category/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_category_budget(id):
    """Edit budget for a specific category."""
    category = Category.query.get_or_404(id)
    
    # Check if category belongs to current user
    if category.user_id != current_user.id:
        flash('You can only edit your own category budgets.', 'danger')
        return redirect(url_for('budgets.index'))
    
    form = CategoryBudgetForm(obj=category)
    
    if form.validate_on_submit():
        try:
            # Update category settings
            category.budget_amount = form.budget_amount.data
            category.alert_threshold = form.alert_threshold.data
            
            # Create or update budget record for current month
            now = datetime.now()
            budget = Budget.query.filter_by(
                user_id=current_user.id,
                category_id=category.id,
                year=now.year,
                month=now.month
            ).first()
            
            if budget:
                budget.amount = form.budget_amount.data
                budget.notes = form.notes.data
            else:
                budget = Budget(
                    user_id=current_user.id,
                    category_id=category.id,
                    amount=form.budget_amount.data,
                    year=now.year,
                    month=now.month,
                    notes=form.notes.data
                )
                db.session.add(budget)
            
            db.session.commit()
            flash('Budget updated successfully!', 'success')
            
            # Check if we need to create an alert
            if category.should_alert():
                alert = BudgetAlert(
                    user_id=current_user.id,
                    category_id=category.id,
                    alert_type='threshold',
                    message=f'Budget alert: {category.name} spending has reached '
                           f'{category.budget_progress}% of budget'
                )
                db.session.add(alert)
                db.session.commit()
            
            return redirect(url_for('budgets.index'))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash('Error updating budget. Please try again.', 'danger')
            print(f"Database error: {str(e)}")  # Log the error
    
    return render_template(
        'budgets/category_form.html',
        form=form,
        category=category
    )

@bp.route('/settings', methods=['GET', 'POST'])
@login_required
def budget_settings():
    """Edit user's overall budget settings."""
    form = UserBudgetForm(obj=current_user)
    
    if form.validate_on_submit():
        try:
            current_user.monthly_income = form.monthly_income.data
            current_user.total_budget = form.total_budget.data
            db.session.commit()
            flash('Budget settings updated successfully!', 'success')
            return redirect(url_for('budgets.index'))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash('Error updating settings. Please try again.', 'danger')
            print(f"Database error: {str(e)}")  # Log the error
    
    return render_template('budgets/settings.html', form=form)

@bp.route('/alerts/mark-read', methods=['POST'])
@login_required
def mark_alerts_read():
    """Mark all unread alerts as read."""
    try:
        BudgetAlert.query.filter_by(
            user_id=current_user.id,
            is_read=False
        ).update({'is_read': True})
        db.session.commit()
        return jsonify({'status': 'success'})
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'Error updating alerts'
        }), 500

@bp.route('/category/<int:id>/history')
@login_required
def category_history(id):
    """View budget history for a category."""
    category = Category.query.get_or_404(id)
    
    # Check if category belongs to current user
    if category.user_id != current_user.id:
        flash('You can only view your own category budgets.', 'danger')
        return redirect(url_for('budgets.index'))
    
    # Get last 12 months of budget history
    now = datetime.now()
    history = Budget.query.filter(
        Budget.category_id == category.id
    ).order_by(
        Budget.year.desc(),
        Budget.month.desc()
    ).limit(12).all()
    
    return render_template(
        'budgets/history.html',
        category=category,
        history=history
    )