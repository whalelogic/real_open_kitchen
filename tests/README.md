# Open Kitchen Tests

   1. Test Isolation (setUp/tearDown)

     def setUp(self):
         self.db_fd, self.db_path = tempfile.mkstemp()  # Creates
   temporary database
         self.app = create_app({'DATABASE': self.db_path})

     - Each test gets a fresh, temporary SQLite database that's
   deleted after the test
     - No pollution between tests - they're completely independent
     - Uses Flask's create_app factory pattern to create isolated app
   instances

   2. Test Structure

   Each test follows the Arrange-Act-Assert pattern:

     - Arrange: Set up test data (create users, recipes)
     - Act: Call the method being tested (e.g., Recipe.fork())
     - Assert: Verify the results match expectations (e.g.,
   self.assertEqual())

   3. What We're Testing

   Business Logic Examples:

     - test_fork_recipe: When you fork a recipe, does it copy
   ingredients, instructions, and set the parent_recipe_id correctly?
   Does it add "(Fork)" to the title?
     - test_delete_recipe_preserves_forks: When you delete the
   original, the forked copies should remain but lose their parent
   reference (set to NULL).
     - test_get_all_public_with_search_filter: Does the search filter
   correctly find recipes with "chocolate" in the title or
   description?

## Running Tests

Run all tests:
```bash
python -m unittest discover tests
```

Run a specific test file:
```bash
python -m unittest tests.test_recipe_model -v
```

Run a specific test case:
```bash
python -m unittest tests.test_recipe_model.RecipeModelTestCase.test_fork_recipe -v
```

## Test Coverage

### test_recipe_model.py
Tests for the Recipe model logic:
- **test_create_recipe**: Validates recipe creation with all metadata
- **test_get_all_public_with_search_filter**: Tests search filtering by title/description
- **test_get_all_public_with_author_filter**: Tests filtering by author
- **test_fork_recipe**: Validates recipe forking copies all data correctly
- **test_fork_nonexistent_recipe_returns_none**: Edge case handling
- **test_delete_recipe_preserves_forks**: Ensures deleting originals keeps forks alive
- **test_get_forked_by_author**: Tests retrieving only forked recipes
- **test_get_by_author_excludes_forks**: Ensures original recipes query excludes forks
