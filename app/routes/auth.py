"""Authentication routes for Centsible Budget Tracker."""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from urllib.parse import urlparse
from .. import db
from ..models import User
from ..forms.auth import LoginForm, RegistrationForm

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration endpoint with CSRF protection."""
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        
        try:
            db.session.add(user)
            db.session.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash('Registration failed. Please try again.', 'danger')
            return redirect(url_for('auth.register'))
    
    return render_template('auth/register.html', form=form)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login endpoint with CSRF protection."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password.', 'danger')
            return redirect(url_for('auth.login'))
        
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc:
            next_page = url_for('main.index')
        return redirect(next_page)
    
    return render_template('auth/login.html', form=form)

@bp.route('/logout')
@login_required
def logout():
    """User logout endpoint."""
    logout_user()
    return redirect(url_for('auth.login'))