"""Initialize development database with realistic test data."""
from datetime import datetime, timedelta
from decimal import Decimal
import random

from app import create_app, db
from app.models import User, Category, Expense, Budget, BudgetAlert

def init_dev_db():
    """Initialize development database with realistic data."""
    app = create_app('development')
    with app.app_context():
        # Create test user
        user = User(
            username='testuser',
            email='test@example.com',
            theme_preference='light',
            currency_symbol='₦',
            monthly_income=Decimal('5000.00'),
            total_budget=Decimal('4000.00')
        )
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()

        # Create categories with realistic names and budgets
        categories = [
            ('Groceries', 'fa-shopping-basket', '#10b981', Decimal('600.00'), 80),
            ('Dining Out', 'fa-utensils', '#f59e0b', Decimal('300.00'), 75),
            ('Transport', 'fa-car', '#3b82f6', Decimal('200.00'), 80),
            ('Entertainment', 'fa-film', '#8b5cf6', Decimal('150.00'), 70),
            ('Bills & Utilities', 'fa-file-invoice-dollar', '#ef4444', Decimal('800.00'), 90),
            ('Shopping', 'fa-shopping-bag', '#ec4899', Decimal('200.00'), 75),
            ('Healthcare', 'fa-hospital', '#06b6d4', Decimal('150.00'), 85),
            ('Home', 'fa-home', '#f97316', Decimal('1000.00'), 80),
        ]

        for name, icon, color, budget_amount, alert_threshold in categories:
            category = Category(
                user_id=user.id,
                name=name,
                icon=icon,
                color=color,
                budget_amount=budget_amount,
                alert_threshold=alert_threshold,
                is_active=True
            )
            db.session.add(category)
        db.session.commit()

        # Create realistic expenses for the last 3 months
        categories = Category.query.all()
        payment_methods = ['cash', 'credit_card', 'debit_card', 'bank_transfer']
        today = datetime.now().date()

        # Common expense descriptions per category
        descriptions = {
            'Groceries': [
                'Weekly groceries', 'Fruits and vegetables', 'Pantry restocking',
                'Snacks and drinks', 'Meat and dairy'
            ],
            'Dining Out': [
                'Lunch with colleagues', 'Pizza night', 'Coffee and pastries',
                'Restaurant dinner', 'Fast food'
            ],
            'Transport': [
                'Gas refill', 'Bus pass', 'Uber ride', 'Train ticket',
                'Car maintenance'
            ],
            'Entertainment': [
                'Movie tickets', 'Netflix subscription', 'Concert tickets',
                'Game purchase', 'Streaming service'
            ],
            'Bills & Utilities': [
                'Electricity bill', 'Water bill', 'Internet service',
                'Phone bill', 'Gas bill'
            ],
            'Shopping': [
                'New clothes', 'Electronics', 'Home supplies',
                'Books', 'Office supplies'
            ],
            'Healthcare': [
                'Pharmacy', 'Doctor visit', 'Medicine',
                'Health insurance', 'Dental checkup'
            ],
            'Home': [
                'Rent payment', 'Home insurance', 'Furniture',
                'Home repairs', 'Cleaning supplies'
            ]
        }

        # Generate expenses for last 3 months
        for days_ago in range(90, -1, -1):
            date = today - timedelta(days=days_ago)
            
            # Create 2-4 expenses per day
            for _ in range(random.randint(2, 4)):
                category = random.choice(categories)
                amount = Decimal(str(round(random.uniform(5, 200), 2)))
                
                # Use category-specific descriptions
                description = random.choice(descriptions.get(
                    category.name,
                    ['Miscellaneous expense']
                ))

                expense = Expense(
                    user_id=user.id,
                    category_id=category.id,
                    amount=amount,
                    description=description,
                    date=date,
                    payment_method=random.choice(payment_methods),
                    is_recurring=random.random() < 0.2,  # 20% chance of recurring
                    recurrence_frequency='monthly' if random.random() < 0.8 else 'weekly'
                )
                db.session.add(expense)

                # Create budget records for current month categories
                if date.year == today.year and date.month == today.month:
                    budget = Budget.query.filter_by(
                        user_id=user.id,
                        category_id=category.id,
                        year=date.year,
                        month=date.month
                    ).first()

                    if not budget:
                        budget = Budget(
                            user_id=user.id,
                            category_id=category.id,
                            amount=category.budget_amount,
                            year=date.year,
                            month=date.month
                        )
                        db.session.add(budget)

        # Create some budget alerts
        for category in categories:
            if category.should_alert():
                alert = BudgetAlert(
                    user_id=user.id,
                    category_id=category.id,
                    alert_type='threshold',
                    message=f'Budget alert: {category.name} spending has reached '
                           f'{category.budget_progress}% of budget'
                )
                db.session.add(alert)

        db.session.commit()
        print("Development database initialized with realistic test data!")
        print("\nLogin credentials:")
        print("Username: testuser")
        print("Password: password123")

if __name__ == '__main__':
    init_dev_db()