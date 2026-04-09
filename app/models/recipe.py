"""Recipe models for recipe management."""
from app.db import get_db
from datetime import datetime


class Recipe:
    """Recipe model."""
    
    @staticmethod
    def create(title, description, template_type, author_id, 
               base_servings=None, prep_time=None, cook_time=None):
        """Create a new recipe."""
        db = get_db()
        cursor = db.execute(
            'INSERT INTO recipes (title, description, template_type, author_id, '
            'base_servings, prep_time_minutes, cook_time_minutes) '
            'VALUES (?, ?, ?, ?, ?, ?, ?)',
            (title, description, template_type, author_id, 
             base_servings, prep_time, cook_time)
        )
        db.commit()
        return cursor.lastrowid
    
    @staticmethod
    def get_by_id(recipe_id):
        """Get recipe by ID with author info."""
        db = get_db()
        return db.execute(
            'SELECT r.*, u.username as author_name '
            'FROM recipes r JOIN users u ON r.author_id = u.id '
            'WHERE r.id = ?',
            (recipe_id,)
        ).fetchone()
    
    @staticmethod
    def get_all_public(filters=None):
        """Get all public recipes with optional filters."""
        db = get_db()
        
        query = '''
            SELECT DISTINCT r.*, u.username as author_name,
                   AVG(rv.rating) as avg_rating,
                   COUNT(DISTINCT rv.id) as review_count
            FROM recipes r
            JOIN users u ON r.author_id = u.id
            LEFT JOIN reviews rv ON r.id = rv.recipe_id
            WHERE r.is_public = 1
        '''
        params = []
        
        if filters:
            if filters.get('category'):
                query += ' AND r.id IN (SELECT recipe_id FROM recipe_categories WHERE category_id = ?)'
                params.append(filters['category'])
            
            if filters.get('tag'):
                query += ' AND r.id IN (SELECT recipe_id FROM recipe_tags WHERE tag_id = ?)'
                params.append(filters['tag'])
            
            if filters.get('author'):
                query += ' AND r.author_id = ?'
                params.append(filters['author'])
            
            if filters.get('search'):
                query += ' AND (r.title LIKE ? OR r.description LIKE ?)'
                params.extend([f'%{filters["search"]}%', f'%{filters["search"]}%'])
        
        query += ' GROUP BY r.id ORDER BY r.created_at DESC'
        
        return db.execute(query, params).fetchall()
    
    @staticmethod
    def get_by_author(author_id):
        """Get all recipes by an author."""
        db = get_db()
        return db.execute(
            'SELECT r.*, COUNT(DISTINCT rv.id) as review_count, '
            'AVG(rv.rating) as avg_rating '
            'FROM recipes r '
            'LEFT JOIN reviews rv ON r.id = rv.recipe_id '
            'WHERE r.author_id = ? '
            'GROUP BY r.id ORDER BY r.created_at DESC',
            (author_id,)
        ).fetchall()
    
    @staticmethod
    def get_forked_by_author(author_id):
        """Get recipes forked by an author."""
        db = get_db()
        return db.execute(
            'SELECT r.*, orig.title as parent_title '
            'FROM recipes r '
            'LEFT JOIN recipes orig ON r.parent_recipe_id = orig.id '
            'WHERE r.author_id = ? AND r.parent_recipe_id IS NOT NULL '
            'ORDER BY r.created_at DESC',
            (author_id,)
        ).fetchall()
    
    @staticmethod
    def fork(recipe_id, author_id, username):
        """Fork an existing recipe."""
        db = get_db()
        
        original = Recipe.get_by_id(recipe_id)
        if not original:
            return None
        
        # Create forked recipe
        cursor = db.execute(
            'INSERT INTO recipes (title, description, template_type, author_id, '
            'base_servings, prep_time_minutes, cook_time_minutes, parent_recipe_id) '
            'VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
            (f"{original['title']} (Fork)", original['description'], 
             original['template_type'], author_id, original['base_servings'],
             original['prep_time_minutes'], original['cook_time_minutes'], recipe_id)
        )
        new_recipe_id = cursor.lastrowid
        
        # Copy ingredients
        Ingredient.copy_for_recipe(recipe_id, new_recipe_id)
        
        # Copy instructions
        Instruction.copy_for_recipe(recipe_id, new_recipe_id)
        
        # Copy categories and tags
        db.execute(
            'INSERT INTO recipe_categories (recipe_id, category_id) '
            'SELECT ?, category_id FROM recipe_categories WHERE recipe_id = ?',
            (new_recipe_id, recipe_id)
        )
        db.execute(
            'INSERT INTO recipe_tags (recipe_id, tag_id) '
            'SELECT ?, tag_id FROM recipe_tags WHERE recipe_id = ?',
            (new_recipe_id, recipe_id)
        )
        
        # Log activity
        from app.models.system import ActivityLog
        ActivityLog.log(author_id, 'forked', 'recipe', new_recipe_id)
        
        # Notify original author
        if original['author_id'] != author_id:
            from app.models.system import Notification
            Notification.create(
                original['author_id'], 
                'fork_created', 
                new_recipe_id,
                f"{username} forked your recipe '{original['title']}'"
            )
        
        db.commit()
        return new_recipe_id
    
    @staticmethod
    def get_recent(limit=6):
        """Get recent public recipes."""
        db = get_db()
        return db.execute(
            'SELECT r.*, u.username as author_name, '
            'AVG(rv.rating) as avg_rating, '
            'COUNT(DISTINCT rv.id) as review_count '
            'FROM recipes r '
            'JOIN users u ON r.author_id = u.id '
            'LEFT JOIN reviews rv ON r.id = rv.recipe_id '
            'WHERE r.is_public = 1 '
            'GROUP BY r.id '
            'ORDER BY r.created_at DESC LIMIT ?',
            (limit,)
        ).fetchall()
    
    @staticmethod
    def get_stats():
        """Get recipe statistics."""
        db = get_db()
        return {
            'total_recipes': db.execute('SELECT COUNT(*) FROM recipes WHERE is_public = 1').fetchone()[0],
        }


class Ingredient:
    """Ingredient model."""
    
    @staticmethod
    def get_by_recipe(recipe_id):
        """Get all ingredients for a recipe."""
        db = get_db()
        return db.execute(
            'SELECT i.*, u.name as unit_name, u.abbreviation, a.name as allergen_name '
            'FROM ingredients i '
            'JOIN units u ON i.unit_id = u.id '
            'LEFT JOIN allergens a ON i.allergen_id = a.id '
            'WHERE i.recipe_id = ?',
            (recipe_id,)
        ).fetchall()
    
    @staticmethod
    def copy_for_recipe(source_recipe_id, target_recipe_id):
        """Copy ingredients from one recipe to another."""
        db = get_db()
        ingredients = db.execute(
            'SELECT * FROM ingredients WHERE recipe_id = ?', 
            (source_recipe_id,)
        ).fetchall()
        
        for ing in ingredients:
            db.execute(
                'INSERT INTO ingredients (recipe_id, name, quantity, unit_id, allergen_id) '
                'VALUES (?, ?, ?, ?, ?)',
                (target_recipe_id, ing['name'], ing['quantity'], 
                 ing['unit_id'], ing['allergen_id'])
            )


class Instruction:
    """Instruction model."""
    
    @staticmethod
    def get_by_recipe(recipe_id):
        """Get all instructions for a recipe."""
        db = get_db()
        return db.execute(
            'SELECT * FROM instructions WHERE recipe_id = ? ORDER BY step_number',
            (recipe_id,)
        ).fetchall()
    
    @staticmethod
    def copy_for_recipe(source_recipe_id, target_recipe_id):
        """Copy instructions from one recipe to another."""
        db = get_db()
        instructions = db.execute(
            'SELECT * FROM instructions WHERE recipe_id = ?', 
            (source_recipe_id,)
        ).fetchall()
        
        for inst in instructions:
            db.execute(
                'INSERT INTO instructions (recipe_id, step_number, content) '
                'VALUES (?, ?, ?)',
                (target_recipe_id, inst['step_number'], inst['content'])
            )
