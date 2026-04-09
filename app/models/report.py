"""Admin report models."""
from app.db import get_db


class Report:
    """Admin report model."""
    
    @staticmethod
    def most_forked_recipes():
        """Get recipes ordered by fork count."""
        db = get_db()
        return db.execute(
            'SELECT r.id, r.title, u.username as author_name, '
            'COUNT(forks.id) as fork_count '
            'FROM recipes r '
            'JOIN users u ON r.author_id = u.id '
            'LEFT JOIN recipes forks ON forks.parent_recipe_id = r.id '
            'WHERE r.parent_recipe_id IS NULL '
            'GROUP BY r.id '
            'HAVING fork_count > 0 '
            'ORDER BY fork_count DESC'
        ).fetchall()
    
    @staticmethod
    def recipes_with_allergen(allergen_id):
        """Get recipes containing a specific allergen."""
        db = get_db()
        return db.execute(
            'SELECT DISTINCT r.id, r.title, u.username as author_name, '
            'a.name as allergen_name '
            'FROM recipes r '
            'JOIN users u ON r.author_id = u.id '
            'JOIN ingredients i ON r.id = i.recipe_id '
            'JOIN allergens a ON i.allergen_id = a.id '
            'WHERE a.id = ? '
            'ORDER BY r.title',
            (allergen_id,)
        ).fetchall()
