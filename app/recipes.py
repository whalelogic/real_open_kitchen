from flask import Blueprint, render_template, request, redirect, url_for, flash, g
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
        category_ids = request.form.getlist('categories')
        tag_ids = request.form.getlist('tags')
        
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
                    'INSERT INTO recipe_categories (recipe_id, category_id) VALUES (?, ?)',
                    (recipe_id, cat_id)
                )
            
            for tag_id in tag_ids:
                db.execute(
                    'INSERT INTO recipe_tags (recipe_id, tag_id) VALUES (?, ?)',
                    (recipe_id, tag_id)
                )
            
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
