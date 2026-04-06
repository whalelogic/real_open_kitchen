import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from app.models import User

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=('GET', 'POST'))
def register():
    """Register a new user."""
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        error = None

        if not username:
            error = 'Username is required.'
        elif not email:
            error = 'Email is required.'
        elif not password:
            error = 'Password is required.'

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
            error = 'Incorrect username.'
        elif not User.verify_password(user, password):
            error = 'Incorrect password.'

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
