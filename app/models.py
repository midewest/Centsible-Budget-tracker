"""SQLAlchemy models for Centsible Budget Tracker."""
from datetime import datetime
from decimal import Decimal
from sqlalchemy import extract
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy.ext.hybrid import hybrid_property

from . import db, login_manager

class User(UserMixin, db.Model):
    """User model with secure password hashing."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True, nullable=False)
    email = db.Column(db.String(120), unique=True, index=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    theme_preference = db.Column(db.String(10), default='light')
    currency_symbol = db.Column(db.String(5), default='$')
    monthly_income = db.Column(db.Numeric(10, 2), default=0)
    total_budget = db.Column(db.Numeric(10, 2), default=0)
    
    # Relationships
    categories = db.relationship('Category', backref='user', lazy='dynamic')
    expenses = db.relationship('Expense', backref='user', lazy='dynamic')
    budgets = db.relationship('Budget', backref='user', lazy='dynamic')
    alerts = db.relationship('BudgetAlert', backref='user', lazy='dynamic')
    
    def set_password(self, password):
        """Hash password using Werkzeug security."""
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')
    
    def check_password(self, password):
        """Verify password hash."""
        return check_password_hash(self.password_hash, password)
    
    def get_monthly_spending(self, year=None, month=None):
        """Get total spending for a specific month."""
        if year is None or month is None:
            now = datetime.now()
            year = now.year
            month = now.month
            
        total = db.session.query(
            db.func.sum(Expense.amount)
        ).filter(
            Expense.user_id == self.id,
            extract('year', Expense.date) == year,
            extract('month', Expense.date) == month
        ).scalar()
        
        return total or Decimal('0')
    
    def get_category_spending(self, category_id, year=None, month=None):
        """Get total spending for a specific category in a month."""
        if year is None or month is None:
            now = datetime.now()
            year = now.year
            month = now.month
            
        total = db.session.query(
            db.func.sum(Expense.amount)
        ).filter(
            Expense.user_id == self.id,
            Expense.category_id == category_id,
            extract('year', Expense.date) == year,
            extract('month', Expense.date) == month
        ).scalar()
        
        return total or Decimal('0')

class Category(db.Model):
    """Expense category model."""
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(64), nullable=False)
    icon = db.Column(db.String(32))
    color = db.Column(db.String(7))  # Hex color code
    is_default = db.Column(db.Boolean, default=False)
    budget_amount = db.Column(db.Numeric(10, 2), default=0)
    alert_threshold = db.Column(db.Integer, default=80)  # Percentage
    is_active = db.Column(db.Boolean, default=True)
    
    # Create composite index for efficient user category lookups
    __table_args__ = (
        db.Index('idx_user_category', user_id, name),
    )
    
    # Relationships
    expenses = db.relationship('Expense', backref='category', lazy='dynamic')
    budgets = db.relationship('Budget', backref='category', lazy='dynamic')
    
    @hybrid_property
    def current_month_spending(self):
        """Get current month's spending for this category."""
        now = datetime.now()
        return self.user.get_category_spending(self.id, now.year, now.month)
    
    @hybrid_property
    def budget_progress(self):
        """Calculate budget progress as a percentage."""
        if not self.budget_amount or self.budget_amount == 0:
            return 0
        return min(100, int((self.current_month_spending / self.budget_amount) * 100))
    
    def should_alert(self):
        """Check if spending has crossed the alert threshold."""
        if not self.budget_amount or self.budget_amount == 0:
            return False
        return self.budget_progress >= self.alert_threshold

class Expense(db.Model):
    """Expense model."""
    __tablename__ = 'expenses'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    description = db.Column(db.String(128))
    date = db.Column(db.Date, nullable=False, index=True)
    payment_method = db.Column(db.String(32))
    is_recurring = db.Column(db.Boolean, default=False)
    recurrence_frequency = db.Column(db.String(32))
    receipt_note = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Create index for efficient date range queries
    __table_args__ = (
        db.Index('idx_user_expense_date', user_id, date),
    )

class Budget(db.Model):
    """Budget model for tracking category-specific budgets over time."""
    __tablename__ = 'budgets'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    month = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Create index for efficient lookups
    __table_args__ = (
        db.Index('idx_budget_period', user_id, category_id, year, month),
    )

class BudgetAlert(db.Model):
    """Budget alerts for tracking threshold violations."""
    __tablename__ = 'budget_alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    alert_type = db.Column(db.String(32), nullable=False)  # threshold, overspent
    message = db.Column(db.String(256), nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Create index for efficient alert retrieval
    __table_args__ = (
        db.Index('idx_user_alerts', user_id, is_read),
    )

@login_manager.user_loader
def load_user(user_id):
    """Flask-Login user loader callback."""
    return User.query.get(int(user_id))