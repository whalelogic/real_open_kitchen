"""Lookup table models."""
from app.db import get_db


# Category emoji mapping
CATEGORY_EMOJIS = {
    1: '🥟',   # Appetizer
    2: '🍖',   # Main Course
    3: '🍰',   # Dessert
    4: '🥞',   # Breakfast
    5: '🍱',   # Lunch
    6: '🍲',   # Dinner
    7: '🍿',   # Snack
    8: '🥤',   # Beverage
    9: '🥗',   # Salad
    10: '🍜',  # Soup
    11: '🍟',  # Side Dish
}


class Unit:
    """Unit model."""
    
    @staticmethod
    def get_all():
        """Get all units."""
        db = get_db()
        return db.execute('SELECT * FROM units ORDER BY name').fetchall()
    
    @staticmethod
    def create(name, abbreviation=None):
        """Create a new unit."""
        db = get_db()
        db.execute(
            'INSERT INTO units (name, abbreviation) VALUES (?, ?)',
            (name, abbreviation)
        )
        db.commit()


class Category:
    """Category model."""
    
    @staticmethod
    def get_all():
        """Get all categories."""
        db = get_db()
        return db.execute('SELECT * FROM categories ORDER BY name').fetchall()


class Tag:
    """Tag model."""
    
    @staticmethod
    def get_all():
        """Get all tags."""
        db = get_db()
        return db.execute('SELECT * FROM tags ORDER BY name').fetchall()


class Allergen:
    """Allergen model."""
    
    @staticmethod
    def get_all():
        """Get all allergens."""
        db = get_db()
        return db.execute('SELECT * FROM allergens ORDER BY name').fetchall()
