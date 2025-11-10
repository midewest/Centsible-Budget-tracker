"""Routes for expense management."""
from datetime import datetime
from flask import (
    Blueprint, render_template, redirect, url_for, flash, request, jsonify
)
from flask_login import login_required, current_user
from sqlalchemy.exc import SQLAlchemyError

from .. import db
from ..models import Expense, Category, BudgetAlert
from ..forms.expense import ExpenseForm, CategoryForm
from ..forms.quick import QuickExpenseForm

# Create blueprint
bp = Blueprint('expenses', __name__)

@bp.route('/expenses')
@login_required
def index():
    """Display list of user's expenses."""
    page = request.args.get('page', 1, type=int)
    category_filter = request.args.get('category', type=int)
    date_from = request.args.get('from')
    date_to = request.args.get('to')
    
    # Base query
    query = current_user.expenses
    
    # Apply filters
    if category_filter:
        query = query.filter_by(category_id=category_filter)
    if date_from:
        try:
            from_date = datetime.strptime(date_from, '%Y-%m-%d').date()
            query = query.filter(Expense.date >= from_date)
        except ValueError:
            flash('Invalid date format for "From" date', 'warning')
    if date_to:
        try:
            to_date = datetime.strptime(date_to, '%Y-%m-%d').date()
            query = query.filter(Expense.date <= to_date)
        except ValueError:
            flash('Invalid date format for "To" date', 'warning')
    
    # Order by date descending
    expenses = query.order_by(Expense.date.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    # Get categories for filter dropdown
    categories = current_user.categories.all()
    
    return render_template(
        'expenses/list.html',
        expenses=expenses,
        categories=categories
    )

@bp.route('/expenses/quick-add', methods=['POST'])
@login_required
def quick_add():
    """Quickly add an expense from the dashboard."""
    form = QuickExpenseForm()
    form.category_id.choices = [
        (c.id, c.name) for c in current_user.categories.filter_by(is_active=True).all()
    ]
    
    if form.validate_on_submit():
        expense = Expense(
            user_id=current_user.id,
            category_id=form.category_id.data,
            amount=form.amount.data,
            description=form.description.data,
            date=form.date.data or datetime.now().date(),
            payment_method=form.payment_method.data if form.payment_method.data else None,
            is_recurring=form.is_recurring.data
        )
        
        try:
            # Add expense
            db.session.add(expense)
            
            # Check budget threshold
            category = Category.query.get(form.category_id.data)
            if category and category.should_alert():
                alert = BudgetAlert(
                    user_id=current_user.id,
                    category_id=category.id,
                    alert_type='threshold',
                    message=f'Budget alert: {category.name} spending has reached '
                           f'{category.budget_progress}% of budget'
                )
                db.session.add(alert)
            
            db.session.commit()
            flash('Expense added successfully!', 'success')
        except SQLAlchemyError as e:
            db.session.rollback()
            flash('Error adding expense. Please try again.', 'danger')
            print(f"Database error: {str(e)}")  # Log the error
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{getattr(form, field).label.text}: {error}", 'danger')
    
    return redirect(url_for('main.dashboard'))

@bp.route('/expenses/add', methods=['GET', 'POST'])
@login_required
def add_expense():
    """Add a new expense."""
    form = ExpenseForm()
    
    # Populate category choices
    form.category_id.choices = [
        (c.id, c.name) for c in current_user.categories.all()
    ]
    
    if form.validate_on_submit():
        expense = Expense(
            user_id=current_user.id,
            category_id=form.category_id.data,
            amount=form.amount.data,
            description=form.description.data,
            date=form.date.data,
            payment_method=form.payment_method.data,
            is_recurring=form.is_recurring.data,
            recurrence_frequency=form.recurrence_frequency.data,
            receipt_note=form.receipt_note.data
        )
        
        try:
            db.session.add(expense)
            db.session.commit()
            flash('Expense added successfully!', 'success')
            return redirect(url_for('expenses.index'))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash('Error adding expense. Please try again.', 'danger')
            print(f"Database error: {str(e)}")  # Log the error
    
    return render_template('expenses/form.html', form=form, title='Add Expense')

@bp.route('/expenses/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_expense(id):
    """Edit an existing expense."""
    expense = Expense.query.get_or_404(id)
    
    # Check if the expense belongs to the current user
    if expense.user_id != current_user.id:
        flash('You can only edit your own expenses.', 'danger')
        return redirect(url_for('expenses.index'))

    form = ExpenseForm(obj=expense)
    form.category_id.choices = [
        (c.id, c.name) for c in current_user.categories.all()
    ]
    
    if form.validate_on_submit():
        try:
            form.populate_obj(expense)
            db.session.commit()
            flash('Expense updated successfully!', 'success')
            return redirect(url_for('expenses.index'))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash('Error updating expense. Please try again.', 'danger')
            print(f"Database error: {str(e)}")  # Log the error
    
    return render_template(
        'expenses/form.html',
        form=form,
        expense=expense,
        title='Edit Expense'
    )

@bp.route('/expenses/<int:id>/delete', methods=['POST'])
@login_required
def delete_expense(id):
    """Delete an expense."""
    expense = Expense.query.get_or_404(id)
    
    # Check if the expense belongs to the current user
    if expense.user_id != current_user.id:
        flash('You can only delete your own expenses.', 'danger')
        return redirect(url_for('expenses.index'))
    
    try:
        db.session.delete(expense)
        db.session.commit()
        flash('Expense deleted successfully!', 'success')
    except SQLAlchemyError as e:
        db.session.rollback()
        flash('Error deleting expense. Please try again.', 'danger')
        print(f"Database error: {str(e)}")  # Log the error
    
    return redirect(url_for('expenses.index'))

# Category management routes
@bp.route('/categories')
@login_required
def list_categories():
    """Display list of user's expense categories."""
    categories = current_user.categories.order_by(Category.name).all()
    return render_template('expenses/categories.html', categories=categories)

@bp.route('/categories/add', methods=['GET', 'POST'])
@login_required
def add_category():
    """Add a new expense category."""
    form = CategoryForm()
    
    if form.validate_on_submit():
        category = Category(
            user_id=current_user.id,
            name=form.name.data,
            icon=form.icon.data,
            color=form.color.data,
            budget_amount=form.budget_amount.data
        )
        
        try:
            db.session.add(category)
            db.session.commit()
            flash('Category added successfully!', 'success')
            return redirect(url_for('expenses.list_categories'))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash('Error adding category. Please try again.', 'danger')
            print(f"Database error: {str(e)}")  # Log the error
    
    return render_template(
        'expenses/category_form.html',
        form=form,
        title='Add Category'
    )

@bp.route('/categories/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_category(id):
    """Edit an existing category."""
    category = Category.query.get_or_404(id)
    
    # Check if the category belongs to the current user
    if category.user_id != current_user.id:
        flash('You can only edit your own categories.', 'danger')
        return redirect(url_for('expenses.list_categories'))
    
    form = CategoryForm(obj=category)
    
    if form.validate_on_submit():
        try:
            form.populate_obj(category)
            db.session.commit()
            flash('Category updated successfully!', 'success')
            return redirect(url_for('expenses.list_categories'))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash('Error updating category. Please try again.', 'danger')
            print(f"Database error: {str(e)}")  # Log the error
    
    return render_template(
        'expenses/category_form.html',
        form=form,
        category=category,
        title='Edit Category'
    )

@bp.route('/categories/<int:id>/delete', methods=['POST'])
@login_required
def delete_category(id):
    """Delete a category."""
    category = Category.query.get_or_404(id)
    
    # Check if the category belongs to the current user
    if category.user_id != current_user.id:
        flash('You can only delete your own categories.', 'danger')
        return redirect(url_for('expenses.list_categories'))
    
    # Check if category has associated expenses
    if category.expenses.count() > 0:
        flash('Cannot delete category with existing expenses.', 'warning')
        return redirect(url_for('expenses.list_categories'))
    
    try:
        db.session.delete(category)
        db.session.commit()
        flash('Category deleted successfully!', 'success')
    except SQLAlchemyError as e:
        db.session.rollback()
        flash('Error deleting category. Please try again.', 'danger')
        print(f"Database error: {str(e)}")  # Log the error
    
    return redirect(url_for('expenses.list_categories'))