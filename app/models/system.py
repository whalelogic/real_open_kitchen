"""System models for notifications and activity logging."""
from app.db import get_db


class Notification:
    """Notification model."""
    
    @staticmethod
    def create(user_id, notification_type, reference_id, message):
        """Create a notification."""
        db = get_db()
        db.execute(
            'INSERT INTO notifications (user_id, type, reference_id, message) '
            'VALUES (?, ?, ?, ?)',
            (user_id, notification_type, reference_id, message)
        )
        db.commit()
    
    @staticmethod
    def get_by_user(user_id, limit=10):
        """Get notifications for a user."""
        db = get_db()
        return db.execute(
            'SELECT * FROM notifications '
            'WHERE user_id = ? '
            'ORDER BY created_at DESC LIMIT ?',
            (user_id, limit)
        ).fetchall()


class ActivityLog:
    """Activity log model."""
    
    @staticmethod
    def log(user_id, action_type, entity_type, entity_id):
        """Log a user activity."""
        db = get_db()
        db.execute(
            'INSERT INTO activity_logs (user_id, action_type, entity_type, entity_id) '
            'VALUES (?, ?, ?, ?)',
            (user_id, action_type, entity_type, entity_id)
        )
        db.commit()
    
    @staticmethod
    def get_user_activity_report(days=30):
        """Get user activity report for the last N days."""
        from datetime import datetime, timedelta
        db = get_db()
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        return db.execute(
            'SELECT u.username, '
            'COUNT(CASE WHEN al.action_type = "created" AND al.entity_type = "recipe" THEN 1 END) as recipes_created, '
            'COUNT(CASE WHEN al.action_type = "forked" THEN 1 END) as recipes_forked '
            'FROM users u '
            'LEFT JOIN activity_logs al ON u.id = al.user_id AND al.created_at >= ? '
            'GROUP BY u.id '
            'HAVING recipes_created > 0 OR recipes_forked > 0 '
            'ORDER BY (recipes_created + recipes_forked) DESC',
            (cutoff_date,)
        ).fetchall()
