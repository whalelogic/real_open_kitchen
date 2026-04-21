import functools
import random
import re
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from app.models import User
from datetime import datetime
from app.email import send_otp_email

bp = Blueprint('auth', __name__, url_prefix='/auth')


def is_password_strong(password):
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not re.search(r"[0-9]", password):
        return False, "Password must contain at least one number."
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Password must contain at least one special character."
    return True, ""

#comment
@bp.route('/register', methods=('GET', 'POST'))
def register():
    """Register a new user."""
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not email:
            error = 'Email is required.'
        elif not password:
            error = 'Password is required.'
        if password != confirm_password:
            error = "Passwords do not match."
        else:
            is_strong, msg = is_password_strong(password)
            if not is_strong:
                error = msg

        if error is None:
            try:
                User.create(username, email, password)
                return redirect(url_for("auth.login"))
            except Exception as e:
                error = f"User {username} or email {email} is already registered."

        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    """Log in a registered user."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None
        user = User.get_by_username(username)

        if user is None:
            error = 'Incorrect credentials.'
        elif not User.verify_password(user, password):
            error = 'Incorrect credentials.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


@bp.before_app_request
def load_logged_in_user():
    """Load user information before each request."""
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = User.get_by_id(user_id)


@bp.route('/logout')
def logout():
    """Clear the session and log out user."""
    session.clear()
    return redirect(url_for('index'))


def login_required(view):
    """Decorator to require login for views."""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view


def curator_required(view):
    """Decorator to require curator role for views."""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        if g.user['role_name'] != 'Curator':
            flash('Access denied. Curator role required.')
            return redirect(url_for('index'))
        return view(**kwargs)
    return wrapped_view

@bp.route('/forgot-password', methods=('GET','POST'))
def forgot_password():
    if request.method == 'POST':
        email =  request.form['email']
        user = User.get_by_email(email)

        if user:
            otp = str(random.randint(100000,999999))
            User.set_reset_code(user['id'], otp)
            send_otp_email(email, otp)

        flash('If an account with that email exists, a reset code has been sent.')
        return redirect(url_for('auth.reset_password', email=email))
        
    return render_template('auth/forgot_password.html')

@bp.route('/reset-password', methods=('GET', 'POST'))
def reset_password():
    email = request.args.get('email','')

    if request.method == 'POST':
        email = request.form['email']
        code = request.form['code']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        # --- NEW CHECK 1: Match ---
        if password != confirm_password:
            flash('Passwords do not match')
            return render_template('auth/reset_password.html', email=email)
            
        # --- NEW CHECK 2: Strength (Calling the helper) ---
        is_strong, message = is_password_strong(password)
        if not is_strong:
            flash(message)
            return render_template('auth/reset_password.html', email=email)

        user = User.get_by_email(email)

        if user is None or user['reset_code'] != code:
            flash('Invaild email or reset code.')
        else:
            expires = datetime.strptime(user['reset_code_expires'], '%Y-%m-%d %H:%M:%S')
            if datetime.utcnow() > expires:
                flash('The reset code has expired. Please request a new one.')
            else:
                User.reset_password(user['id'], password)
                flash('Your password has been reset successfully. You can now log in.')
                return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', email=email)


@bp.route('/account-settings', methods=('GET', 'POST'))
@login_required

# Allows users to update their email and/or password. 

def account_settings():

    error = None
    success = None
    
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'update_profile':
            username = request.form['username'].strip()
            email = request.form['email'].strip()
            if not username:
                error = 'Username cannot be empty.'
            elif not email:
                error = 'Email cannot be empty.'
            else:
                try:
                    User.update_profile(g.user['id'], username, email)
                    success = 'Profile updated successfully.'
                    g.user = User.get_by_id(g.user['id'])  # refresh
                except Exception:
                    error = 'That username or email is already taken.'

        elif action == 'change_password':
            current = request.form['current_password']
            new_pw = request.form['new_password']
            confirm = request.form['confirm_password']
            if not User.verify_password(g.user, current):
                error = 'Current password is incorrect.'
            elif new_pw != confirm:
                error = 'New passwords do not match.'
            elif len(new_pw) < 6:
                error = 'Password must be at least 6 characters.'
            else:
                User.reset_password(g.user['id'], new_pw)
                success = 'Password changed successfully.'

    if error:
        flash(error)
    if success:
        flash(success)

    return render_template('auth/account_settings.html')
