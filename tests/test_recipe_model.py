"""Unit tests for Recipe model logic."""
import unittest
import tempfile
import os
from app import create_app
from app.db import get_db, init_db
from app.models import Recipe, Ingredient, Instruction


class RecipeModelTestCase(unittest.TestCase):
    """Tests for Recipe model."""
    
    def setUp(self):
        """Set up test"""
        self.db_fd, self.db_path = tempfile.mkstemp()
        self.app = create_app({
            'TESTING': True,
            'DATABASE': self.db_path,
        })
        self.client = self.app.test_client()
        
        with self.app.app_context():
            init_db()
            db = get_db()
            
            # Create test users
            db.execute(
                'INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
                ('testuser', 'test@example.com', 'pbkdf2:sha256:test')
            )
            db.execute(
                'INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
                ('otheruser', 'other@example.com', 'pbkdf2:sha256:test')
            )
            db.commit()
    
    def tearDown(self):
        """Clean up test fixtures."""
        os.close(self.db_fd)
        os.unlink(self.db_path)
    
    def test_create_recipe(self):
        """Test creating a new recipe."""
        with self.app.app_context():
            recipe_id = Recipe.create(
                'Test Recipe',
                'A test description',
                'standard',
                1,
                base_servings=4,
                prep_time=15,
                cook_time=30
            )
            
            self.assertIsNotNone(recipe_id)
            recipe = Recipe.get_by_id(recipe_id)
            self.assertEqual(recipe['title'], 'Test Recipe')
            self.assertEqual(recipe['base_servings'], 4)
            self.assertEqual(recipe['prep_time_minutes'], 15)
            self.assertEqual(recipe['cook_time_minutes'], 30)
    
    def test_get_all_public_with_search_filter(self):
        """Test filtering public recipes by search term."""
        with self.app.app_context():
            db = get_db()
            
            # Create public recipes
            recipe1_id = Recipe.create('Chocolate Cake', 'Delicious dessert', 'standard', 1)
            recipe2_id = Recipe.create('Vanilla Cookies', 'Sweet treats', 'standard', 1)
            recipe3_id = Recipe.create('Chocolate Chip Cookies', 'Classic cookies', 'standard', 1)
            
            db.execute('UPDATE recipes SET is_public = 1 WHERE id IN (?, ?, ?)',
                      (recipe1_id, recipe2_id, recipe3_id))
            db.commit()
            
            # Search for "chocolate"
            results = Recipe.get_all_public({'search': 'chocolate'})
            self.assertEqual(len(results), 2)
            titles = [r['title'] for r in results]
            self.assertIn('Chocolate Cake', titles)
            self.assertIn('Chocolate Chip Cookies', titles)
            self.assertNotIn('Vanilla Cookies', titles)
    
    def test_get_all_public_with_author_filter(self):
        """Test filtering public recipes by author."""
        with self.app.app_context():
            db = get_db()
            
            # Create recipes by different authors
            recipe1_id = Recipe.create('Recipe by User 1', 'Description', 'standard', 1)
            recipe2_id = Recipe.create('Recipe by User 2', 'Description', 'standard', 2)
            recipe3_id = Recipe.create('Another by User 1', 'Description', 'standard', 1)
            
            db.execute('UPDATE recipes SET is_public = 1 WHERE id IN (?, ?, ?)',
                      (recipe1_id, recipe2_id, recipe3_id))
            db.commit()
            
            # Filter by author 1
            results = Recipe.get_all_public({'author': 1})
            self.assertEqual(len(results), 2)
            for recipe in results:
                self.assertEqual(recipe['author_id'], 1)
    
    def test_fork_recipe(self):
        """Test forking a recipe creates proper copy with (Fork) suffix."""
        with self.app.app_context():
            db = get_db()
            
            # Create original recipe
            original_id = Recipe.create('Original Recipe', 'Original description', 'standard', 1)
            
            # Add ingredient and instruction
            db.execute(
                'INSERT INTO ingredients (recipe_id, name, quantity, unit_id) VALUES (?, ?, ?, ?)',
                (original_id, 'Flour', 2.0, 1)
            )
            db.execute(
                'INSERT INTO instructions (recipe_id, step_number, content) VALUES (?, ?, ?)',
                (original_id, 1, 'Mix ingredients')
            )
            db.commit()
            
            # Fork the recipe
            forked_id = Recipe.fork(original_id, 2, 'otheruser')
            
            self.assertIsNotNone(forked_id)
            self.assertNotEqual(forked_id, original_id)
            
            # Check forked recipe
            forked = Recipe.get_by_id(forked_id)
            self.assertEqual(forked['title'], 'Original Recipe (Fork)')
            self.assertEqual(forked['description'], 'Original description')
            self.assertEqual(forked['parent_recipe_id'], original_id)
            self.assertEqual(forked['author_id'], 2)
            
            # Check ingredients were copied
            ingredients = Ingredient.get_by_recipe(forked_id)
            self.assertEqual(len(ingredients), 1)
            self.assertEqual(ingredients[0]['name'], 'Flour')
            
            # Check instructions were copied
            instructions = Instruction.get_by_recipe(forked_id)
            self.assertEqual(len(instructions), 1)
            self.assertEqual(instructions[0]['content'], 'Mix ingredients')
    
    def test_fork_nonexistent_recipe_returns_none(self):
        """Test forking a non-existent recipe returns None."""
        with self.app.app_context():
            result = Recipe.fork(99999, 1, 'testuser')
            self.assertIsNone(result)
    
    def test_delete_recipe_preserves_forks(self):
        """Test deleting original recipe doesn't delete forks."""
        with self.app.app_context():
            db = get_db()
            
            # Create and fork recipe
            original_id = Recipe.create('Original', 'Description', 'standard', 1)
            forked_id = Recipe.fork(original_id, 2, 'otheruser')
            
            # Delete original
            Recipe.delete(original_id)
            
            # Original should be gone
            original = Recipe.get_by_id(original_id)
            self.assertIsNone(original)
            
            # Fork should still exist but parent_recipe_id should be NULL
            forked = Recipe.get_by_id(forked_id)
            self.assertIsNotNone(forked)
            self.assertIsNone(forked['parent_recipe_id'])
    
    def test_get_forked_by_author(self):
        """Test retrieving only forked recipes by author."""
        with self.app.app_context():
            # Create original recipe by user 1
            original_id = Recipe.create('Original', 'Description', 'standard', 1)
            
            # User 2 creates an original and forks user 1's recipe
            user2_original = Recipe.create('User 2 Original', 'Description', 'standard', 2)
            user2_fork = Recipe.fork(original_id, 2, 'otheruser')
            
            # Get only forked recipes by user 2
            forks = Recipe.get_forked_by_author(2)
            self.assertEqual(len(forks), 1)
            self.assertEqual(forks[0]['id'], user2_fork)
            self.assertEqual(forks[0]['parent_title'], 'Original')
    
    def test_get_by_author_excludes_forks(self):
        """Test getting original recipes excludes forks."""
        with self.app.app_context():
            # User 1 creates original recipes
            original1 = Recipe.create('Original 1', 'Description', 'standard', 1)
            original2 = Recipe.create('Original 2', 'Description', 'standard', 1)
            
            # User 2 creates a recipe
            other_recipe = Recipe.create('Other Recipe', 'Description', 'standard', 2)
            
            # User 1 forks user 2's recipe
            user1_fork = Recipe.fork(other_recipe, 1, 'testuser')
            
            # Get only original recipes by user 1
            originals = Recipe.get_by_author(1)
            self.assertEqual(len(originals), 2)
            ids = [r['id'] for r in originals]
            self.assertIn(original1, ids)
            self.assertIn(original2, ids)
            self.assertNotIn(user1_fork, ids)


if __name__ == '__main__':
    unittest.main()
