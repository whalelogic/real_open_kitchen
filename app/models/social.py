"""Social interaction models."""
from app.db import get_db


class Review:
    """Review model."""
    
    @staticmethod
    def get_by_recipe(recipe_id):
        """Get all reviews for a recipe."""
        db = get_db()
        return db.execute(
            'SELECT r.*, u.username FROM reviews r '
            'JOIN users u ON r.user_id = u.id '
            'WHERE r.recipe_id = ? ORDER BY r.created_at DESC',
            (recipe_id,)
        ).fetchall()


class Comment:
    """Comment model."""
    
    @staticmethod
    def get_by_recipe(recipe_id):
        """Get all comments for a recipe."""
        db = get_db()
        return db.execute(
            'SELECT c.*, u.username FROM comments c '
            'JOIN users u ON c.user_id = u.id '
            'WHERE c.recipe_id = ? ORDER BY c.created_at DESC',
            (recipe_id,)
        ).fetchall()


class SavedRecipe:
    """Saved recipe model."""
    
    @staticmethod
    def get_by_user(user_id):
        """Get all saved recipes for a user."""
        db = get_db()
        return db.execute(
            'SELECT r.*, u.username as author_name, sr.saved_at '
            'FROM saved_recipes sr '
            'JOIN recipes r ON sr.recipe_id = r.id '
            'JOIN users u ON r.author_id = u.id '
            'WHERE sr.user_id = ? '
            'ORDER BY sr.saved_at DESC',
            (user_id,)
        ).fetchall()
    
    @staticmethod
    def is_saved(user_id, recipe_id):
        """Check if a recipe is saved by a user."""
        db = get_db()
        result = db.execute(
            'SELECT 1 FROM saved_recipes WHERE user_id = ? AND recipe_id = ?',
            (user_id, recipe_id)
        ).fetchone()
        return result is not None
    
    @staticmethod
    def save(user_id, recipe_id):
        """Save a recipe for a user."""
        db = get_db()
        db.execute(
            'INSERT INTO saved_recipes (user_id, recipe_id) VALUES (?, ?)',
            (user_id, recipe_id)
        )
        db.commit()
    
    @staticmethod
    def unsave(user_id, recipe_id):
        """Unsave a recipe for a user."""
        db = get_db()
        db.execute(
            'DELETE FROM saved_recipes WHERE user_id = ? AND recipe_id = ?',
            (user_id, recipe_id)
        )
        db.commit()
