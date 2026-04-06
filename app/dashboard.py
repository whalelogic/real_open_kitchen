from flask import Blueprint, render_template, g
from app.models import Recipe, SavedRecipe, Notification
from app.auth import login_required

bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')


@bp.route('/')
@login_required
def index():
    """User's personal dashboard - 'My Kitchen'."""
    user_id = g.user['id']
    
    authored = Recipe.get_by_author(user_id)
    forked = Recipe.get_forked_by_author(user_id)
    saved = SavedRecipe.get_by_user(user_id)
    notifications = Notification.get_by_user(user_id)
    
    return render_template('dashboard/index.html',
                         authored=authored,
                         forked=forked,
                         saved=saved,
                         notifications=notifications)
