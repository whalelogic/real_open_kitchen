import os
import uuid
import json
from google import genai
from google.genai import types
from flask import Blueprint, render_template, request, redirect, url_for, flash, g, jsonify
from app.models import Recipe, Ingredient, Instruction, Review, Comment, ActivityLog, Unit, Allergen, Category, Tag
from app.auth import login_required

bp = Blueprint('recipes', __name__, url_prefix='/recipes')


@bp.route('/')
def index():
    """List all public recipes with filtering."""
    filters = {
        'category': request.args.get('category'),
        'tag': request.args.get('tag'),
        'author': request.args.get('author'),
        'search': request.args.get('search'),
    }
    
    recipes = Recipe.get_all_public(filters)
    from app.db import get_db
    db = get_db()
    categories = Category.get_all()
    tags = Tag.get_all()
    authors = db.execute(
        'SELECT DISTINCT u.id, u.username '
        'FROM users u '
        'JOIN recipes r ON r.author_id = u.id '
        'WHERE r.is_public = 1 '
        'ORDER BY u.username'
    ).fetchall()
    return render_template(
        'recipes/index.html',
        recipes=recipes,
        categories=categories,
        tags=tags,
        authors=authors,
        filters=filters,
    )


@bp.route('/<int:id>')
def view(id):
    """View a single recipe with ingredients and instructions."""
    recipe = Recipe.get_by_id(id)
    
    if recipe is None:
        flash('Recipe not found.')
        return redirect(url_for('recipes.index'))
    
    ingredients = Ingredient.get_by_recipe(id)
    instructions = Instruction.get_by_recipe(id)
    reviews = Review.get_by_recipe(id)
    comments = Comment.get_by_recipe(id)
    
    # Get categories and tags
    from app.db import get_db
    from app.models.social import SavedRecipe
    db = get_db()
    categories = db.execute(
        'SELECT c.* FROM categories c '
        'JOIN recipe_categories rc ON c.id = rc.category_id '
        'WHERE rc.recipe_id = ?', (id,)
    ).fetchall()
    
    tags = db.execute(
        'SELECT t.* FROM tags t '
        'JOIN recipe_tags rt ON t.id = rt.tag_id '
        'WHERE rt.recipe_id = ?', (id,)
    ).fetchall()
    
    # Check if recipe is saved by current user
    is_saved = False
    if g.user:
        is_saved = SavedRecipe.is_saved(g.user['id'], id)
    
    return render_template('recipes/view.html', 
                         recipe=recipe, 
                         ingredients=ingredients,
                         instructions=instructions,
                         reviews=reviews,
                         comments=comments,
                         categories=categories,
                         tags=tags,
                         is_saved=is_saved)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    """Create a new recipe."""
    if request.method == 'POST':
        title = request.form['title']
        description = request.form.get('description')
        template_type = request.form['template_type']
        base_servings = request.form.get('base_servings', type=int)
        prep_time = request.form.get('prep_time_minutes', type=int)
        cook_time = request.form.get('cook_time_minutes', type=int)

        # Use set() to remove any duplicates sent by the browser
        category_ids = set(request.form.getlist('categories'))
        tag_ids = set(request.form.getlist('tags'))
        
        error = None
        if not title:
            error = 'Title is required.'
        elif template_type not in ['standard', 'quick_tip']:
            error = 'Invalid template type.'
        
        if error is None:
            recipe_id = Recipe.create(
                title, description, template_type, g.user['id'],
                base_servings, prep_time, cook_time
            )
            
            # Add categories and tags
            from app.db import get_db
            db = get_db()
            
            for cat_id in category_ids:
                db.execute(
                    'INSERT OR IGNORE INTO recipe_categories (recipe_id, category_id) VALUES (?, ?)',
                    (recipe_id, cat_id)
                )
            
            for tag_id in tag_ids:
                db.execute(
                    'INSERT OR IGNORE INTO recipe_tags (recipe_id, tag_id) VALUES (?, ?)',
                    (recipe_id, tag_id)
                )

            # --- NEW AI DATA PROCESSING ---
            import json
            ai_ingredients_raw = request.form.get('ai_ingredients')
            ai_instructions_raw = request.form.get('ai_instructions')

            # Process Ingredients
            if ai_ingredients_raw:
                try:
                    ingredients_data = json.loads(ai_ingredients_raw)
                    # Create a dictionary to easily look up unit IDs by name (e.g., 'cup': 5)
                    unit_rows = db.execute('SELECT id, name, abbreviation FROM units').fetchall()
                    unit_map = {u['name'].lower(): u['id'] for u in unit_rows}
                    
                    # Fallback to 'piece' (usually ID 10) or 'to taste' if the AI gives a weird unit
                    fallback_unit_id = unit_map.get('piece', 1) 

                    for ing in ingredients_data:
                        name = ing.get('name', 'Unknown Ingredient')
                        
                        # Ensure quantity is a float (AI sometimes returns strings)
                        try:
                            qty_raw = ing.get('qty')
                            qty = float(qty_raw) if qty_raw is not None else 1.0
                        except (ValueError, TypeError):
                            qty = 1.0
                            
                        unit_str = str(ing.get('unit', '')).lower()
                        unit_id = unit_map.get(unit_str, fallback_unit_id)

                        db.execute(
                            'INSERT INTO ingredients (recipe_id, name, quantity, unit_id) VALUES (?, ?, ?, ?)',
                            (recipe_id, name, qty, unit_id)
                        )
                except Exception as e:
                    print(f"Failed to parse AI ingredients: {e}")

            # Process Instructions
            if ai_instructions_raw:
                try:
                    instructions_data = json.loads(ai_instructions_raw)
                    for i, step_text in enumerate(instructions_data):
                        db.execute(
                            'INSERT INTO instructions (recipe_id, step_number, content) VALUES (?, ?, ?)',
                            (recipe_id, i + 1, step_text)
                        )
                except Exception as e:
                    print(f"Failed to parse AI instructions: {e}")
            # --- END AI DATA PROCESSING ---

            # --- START AI IMAGE GENERATION ---
            try:
                image_prompt = f"Professional food photography of {title}. {description}. Beautifully plated, modern kitchen table setting, shallow depth of field, warm cinematic lighting, 4k resolution."
                
                # Replace 'AIza...' with your actual new Tier 1 key!
                client = genai.Client()                
                # Back to the modern SDK syntax! Your Tier 1 key will let this pass.
                image_result = client.models.generate_content(
                    model='gemini-2.5-flash-image',
                    contents=image_prompt,
                    config=types.GenerateContentConfig(
                        response_modalities=["IMAGE"]
                    )
                )

                # Create a unique filename for the image
                filename = f"recipe_{recipe_id}_{uuid.uuid4().hex[:8]}.jpg"
                save_dir = os.path.join(os.getcwd(), 'app', 'static', 'images', 'recipes')
                filepath = os.path.join(save_dir, filename)

                os.makedirs(save_dir, exist_ok=True)

                # Save the image bytes to your static folder
                with open(filepath, "wb") as f:
                    f.write(image_result.parts[0].inline_data.data)

                # Update the database with the new image path
                image_url = f"/static/images/recipes/{filename}"
                db.execute('UPDATE recipes SET image_url = ? WHERE id = ?', (image_url, recipe_id))
                db.commit()
                print(f"Successfully generated and saved image: {filename}")

            except Exception as e:
                print(f"AI Image Generation failed: {e}")
            # --- END AI IMAGE GENERATION ---
            
            db.commit()
            ActivityLog.log(g.user['id'], 'created', 'recipe', recipe_id)
            return redirect(url_for('recipes.edit_ingredients', id=recipe_id))
        
        flash(error)
    
    categories = Category.get_all()
    tags = Tag.get_all()
    return render_template('recipes/create.html', categories=categories, tags=tags)


@bp.route('/<int:id>/ingredients', methods=('GET', 'POST'))
@login_required
def edit_ingredients(id):
    """Add/edit ingredients for a recipe."""
    recipe = Recipe.get_by_id(id)
    
    if recipe is None or recipe['author_id'] != g.user['id']:
        flash('Recipe not found or access denied.')
        return redirect(url_for('recipes.index'))
    
    if request.method == 'POST':
        from app.db import get_db
        db = get_db()
        
        name = request.form['name']
        quantity = request.form.get('quantity', type=float)
        unit_id = request.form.get('unit_id', type=int)
        allergen_id = request.form.get('allergen_id', type=int) or None
        
        if name and quantity and unit_id:
            db.execute(
                'INSERT INTO ingredients (recipe_id, name, quantity, unit_id, allergen_id) '
                'VALUES (?, ?, ?, ?, ?)',
                (id, name, quantity, unit_id, allergen_id)
            )
            db.commit()
            flash('Ingredient added!')
        else:
            flash('Please fill all required fields.')
    
    ingredients = Ingredient.get_by_recipe(id)
    units = Unit.get_all()
    allergens = Allergen.get_all()
    
    return render_template('recipes/edit_ingredients.html',
                         recipe=recipe,
                         ingredients=ingredients,
                         units=units,
                         allergens=allergens)


@bp.route('/<int:id>/instructions', methods=('GET', 'POST'))
@login_required
def edit_instructions(id):
    """Add/edit instructions for a recipe."""
    recipe = Recipe.get_by_id(id)
    
    if recipe is None or recipe['author_id'] != g.user['id']:
        flash('Recipe not found or access denied.')
        return redirect(url_for('recipes.index'))
    
    if request.method == 'POST':
        from app.db import get_db
        db = get_db()
        
        content = request.form['content']
        step_number = request.form.get('step_number', type=int)
        
        if content and step_number:
            db.execute(
                'INSERT INTO instructions (recipe_id, step_number, content) '
                'VALUES (?, ?, ?)',
                (id, step_number, content)
            )
            db.commit()
            flash('Instruction added!')
        else:
            flash('Please fill all required fields.')
    
    instructions = Instruction.get_by_recipe(id)
    
    return render_template('recipes/edit_instructions.html',
                         recipe=recipe,
                         instructions=instructions)


@bp.route('/ingredients/<int:id>/delete', methods=('POST',))
@login_required
def delete_ingredient(id):
    """Delete an ingredient."""
    from app.db import get_db
    db = get_db()
    
    ingredient = db.execute(
        'SELECT i.*, r.author_id FROM ingredients i '
        'JOIN recipes r ON i.recipe_id = r.id '
        'WHERE i.id = ?', (id,)
    ).fetchone()
    
    if ingredient is None or ingredient['author_id'] != g.user['id']:
        flash('Ingredient not found or access denied.')
        return redirect(url_for('recipes.index'))
    
    recipe_id = ingredient['recipe_id']
    db.execute('DELETE FROM ingredients WHERE id = ?', (id,))
    db.commit()
    flash('Ingredient deleted.')
    
    return redirect(url_for('recipes.edit_ingredients', id=recipe_id))


@bp.route('/instructions/<int:id>/delete', methods=('POST',))
@login_required
def delete_instruction(id):
    """Delete an instruction."""
    from app.db import get_db
    db = get_db()
    
    instruction = db.execute(
        'SELECT i.*, r.author_id FROM instructions i '
        'JOIN recipes r ON i.recipe_id = r.id '
        'WHERE i.id = ?', (id,)
    ).fetchone()
    
    if instruction is None or instruction['author_id'] != g.user['id']:
        flash('Instruction not found or access denied.')
        return redirect(url_for('recipes.index'))
    
    recipe_id = instruction['recipe_id']
    db.execute('DELETE FROM instructions WHERE id = ?', (id,))
    db.commit()
    flash('Instruction deleted.')
    
    return redirect(url_for('recipes.edit_instructions', id=recipe_id))


@bp.route('/<int:id>/fork', methods=('POST',))
@login_required
def fork(id):
    """Fork an existing recipe."""
    new_recipe_id = Recipe.fork(id, g.user['id'], g.user['username'])
    
    if new_recipe_id is None:
        flash('Recipe not found.')
        return redirect(url_for('recipes.index'))
    
    flash('Recipe forked successfully!')
    return redirect(url_for('recipes.view', id=new_recipe_id))



@bp.route('/parse', methods=['POST'])
@login_required
def parse_recipe():
    """Takes raw text from the frontend and returns a structured JSON recipe."""
    data = request.get_json()
    raw_text = data.get('text', '')
    
    if not raw_text:
        return jsonify({'error': 'No text provided'}), 400

    
    prompt = f"""
        You are a culinary parser. Extract the recipe details from the following text.
        Return ONLY a valid JSON object. Do not include markdown formatting.
        Use exactly these keys:
        - "title" (string)
        - "description" (string)
        - "base_servings" (integer)
        - "prep_time_minutes" (integer)
        - "cook_time_minutes" (integer)
        - "ingredients" (array of objects with name, qty, unit)
        - "instructions" (array of strings)
        - "categories" (array of strings, ONLY pick from: Appetizer, Main Course, Dessert, Breakfast, Lunch, Dinner, Snack, Beverage, Salad, Soup, Side Dish)
        - "tags" (array of strings, ONLY pick from: Vegetarian, Vegan, Gluten-Free, Dairy-Free, Nut-Free, Keto, Paleo, Low-Carb, High-Protein, Quick, Easy)
    
        Text to parse:
        {raw_text}
        """

    # NEW CODE TO ADD
    try:
        # The client automatically detects GEMINI_API_KEY from your .flaskenv
        client = genai.Client() 
            
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            )
        )
        parsed_data = json.loads(response.text)
        return jsonify(parsed_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    


@bp.route('/<int:id>/save', methods=('POST',))
@login_required
def save(id):
    """Save a recipe to user's saved recipes."""
    from app.models.social import SavedRecipe
    
    recipe = Recipe.get_by_id(id)
    if recipe is None:
        flash('Recipe not found.')
        return redirect(url_for('recipes.index'))
    
    if SavedRecipe.is_saved(g.user['id'], id):
        SavedRecipe.unsave(g.user['id'], id)
        flash('Recipe removed from saved recipes.')
    else:
        SavedRecipe.save(g.user['id'], id)
        flash('Recipe saved successfully!')
    
    return redirect(url_for('recipes.view', id=id))

@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """Delete a recipe created or forked by the user."""
    from app.db import get_db
    db = get_db()
    
    # Fetch the recipe to verify ownership
    recipe = db.execute('SELECT * FROM recipes WHERE id = ?', (id,)).fetchone()
    
    if recipe is None:
        flash('Recipe not found.', 'error')
        return redirect(url_for('dashboard.index'))
        
    # Security check: Make sure the current user is the author
    if recipe['author_id'] != g.user['id']:
        flash('You do not have permission to delete this recipe.', 'error')
        return redirect(url_for('dashboard.index'))
        
    # Delete the recipe (SQLite will handle related rows if ON DELETE CASCADE is set up,
    # otherwise we manually delete related data first to keep the database clean)
    db.execute('DELETE FROM ingredients WHERE recipe_id = ?', (id,))
    db.execute('DELETE FROM instructions WHERE recipe_id = ?', (id,))
    db.execute('DELETE FROM recipe_tags WHERE recipe_id = ?', (id,))
    db.execute('DELETE FROM recipe_categories WHERE recipe_id = ?', (id,))
    db.execute('DELETE FROM saved_recipes WHERE recipe_id = ?', (id,))
    db.execute('DELETE FROM recipes WHERE id = ?', (id,))
    db.commit()
    
    flash(f'"{recipe["title"]}" was successfully deleted.', 'success')
    return redirect(url_for('dashboard.index'))
