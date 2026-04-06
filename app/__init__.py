import os
from flask import Flask, render_template


def create_app(test_config=None):
    """Application factory for Open Kitchen."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'community_kitchen.db'),
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    # Ensure instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Initialize database
    from . import db
    db.init_app(app)

    # Register blueprints
    from . import auth, recipes, dashboard, admin
    app.register_blueprint(auth.bp)
    app.register_blueprint(recipes.bp)
    app.register_blueprint(dashboard.bp)
    app.register_blueprint(admin.bp)

    # Index route
    @app.route('/')
    def index():
        from app.models import Recipe, Category
        from app.db import get_db
        
        recent_recipes = Recipe.get_recent(limit=6)
        
        # Get stats
        db = get_db()
        stats = {
            'total_recipes': Recipe.get_stats()['total_recipes'],
            'total_users': db.execute('SELECT COUNT(*) FROM users').fetchone()[0],
            'total_reviews': db.execute('SELECT COUNT(*) FROM reviews').fetchone()[0],
        }
        
        categories = Category.get_all()[:6]
        
        return render_template('index.html', 
                             recipes=recent_recipes, 
                             stats=stats,
                             categories=categories)

    return app
