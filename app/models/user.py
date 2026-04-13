"""User and Role models for authentication and authorization."""
from werkzeug.security import check_password_hash, generate_password_hash
from app import db
from app.db import get_db
from datetime import datetime


class User:
    """User model."""
    
    @staticmethod
    def create(username, email, password, role_id=1):
        """Create a new user."""
        db = get_db()
        db.execute(
            "INSERT INTO users (username, email, password_hash, role_id) VALUES (?, ?, ?, ?)",
            (username, email, generate_password_hash(password), role_id),
        )
        db.commit()
        return User.get_by_username(username)
    
    @staticmethod
    def get_by_id(user_id):
        """Get user by ID."""
        db = get_db()
        return db.execute(
            'SELECT u.*, r.name as role_name FROM users u '
            'JOIN roles r ON u.role_id = r.id '
            'WHERE u.id = ?', (user_id,)
        ).fetchone()
    
    @staticmethod
    def get_by_username(username):
        """Get user by username."""
        db = get_db()
        return db.execute(
            'SELECT u.*, r.name as role_name FROM users u '
            'JOIN roles r ON u.role_id = r.id '
            'WHERE u.username = ?', (username,)
        ).fetchone()
    
    @staticmethod
    def get_all():
        """Get all users."""
        db = get_db()
        return db.execute(
            'SELECT u.*, r.name as role_name FROM users u '
            'JOIN roles r ON u.role_id = r.id '
            'ORDER BY u.created_at DESC'
        ).fetchall()
    
    @staticmethod
    def verify_password(user, password):
        """Verify user password."""
        return check_password_hash(user['password_hash'], password)
    
    @staticmethod
    def toggle_notifications(user_id):
        """Toggle notification settings for a user."""
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        if user:
            new_value = 0 if user['notifications_enabled'] else 1
            db.execute(
                'UPDATE users SET notifications_enabled = ? WHERE id = ?',
                (new_value, user_id)
            )
            db.commit()
            return True
        return False

    @staticmethod
    def update_role(user_id, role_id):
        """Update a user's role."""
        db = get_db()
        db.execute(
            'UPDATE users SET role_id = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
            (role_id, user_id)
        )
        db.commit()

    @staticmethod
    def get_by_email(email):
        """Get user by email"""
        db = get_db()
        return db.execute('SELECT * FROM users WHERE email = ?',(email,)).fetchone()

    @staticmethod
    def set_reset_code(user_id, code, expires_in_minutes=10):
        """save 6-digit OTP and its expiration time to the user"""
        from datetime import timedelta
        db = get_db()
        expires = (datetime.utcnow() + timedelta(minutes=expires_in_minutes)).strftime('%Y-%m-%d %H:%M:%S')
        db.execute(
            'UPDATE users SET reset_code = ?, reset_code_expires = ? WHERE id = ?',
            (code, expires, user_id)
        )
        db.commit()

    @staticmethod
    def reset_password(user_id, new_password):
        """Hash the new password, save it, and clear the reset code."""
        db = get_db()
        db.execute(
            'UPDATE users SET password_hash = ?, reset_code = NULL, reset_code_expires = NULL WHERE id = ?',
            (generate_password_hash(new_password), user_id)
        )
        db.commit()

    @staticmethod
    def update_profile(user_id, username, email):
        db = get_db()
        db.execute(
        'UPDATE users SET username = ?, email = ? WHERE id = ?',
        (username, email, user_id)
    )
    db.commit()
        

class Role:
    """Role model."""
    
    @staticmethod
    def get_all():
        """Get all roles."""
        db = get_db()
        return db.execute('SELECT * FROM roles').fetchall()
    
    @staticmethod
    def get_by_name(name):
        """Get role by name."""
        db = get_db()
        return db.execute('SELECT * FROM roles WHERE name = ?', (name,)).fetchone()
