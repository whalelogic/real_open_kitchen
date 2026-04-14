from flask import Blueprint, render_template, g, redirect, url_for, flash
from app.models import Recipe, SavedRecipe, Notification, User
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


@bp.route('/notifications/<int:id>/read', methods=('POST',))
@login_required
def mark_notification_read(id):
    """Mark one notification as read."""
    Notification.mark_read(id, g.user['id'])
    flash('Notification marked as read.')
    return redirect(url_for('dashboard.index'))


@bp.route('/notifications/read-all', methods=('POST',))
@login_required
def mark_all_notifications_read():
    """Mark all notifications as read."""
    Notification.mark_all_read(g.user['id'])
    flash('All notifications marked as read.')
    return redirect(url_for('dashboard.index'))


@bp.route('/notifications/<int:id>/delete', methods=('POST',))
@login_required
def delete_notification(id):
    """Delete one notification."""
    Notification.delete(id, g.user['id'])
    flash('Notification removed.')
    return redirect(url_for('dashboard.index'))


@bp.route('/settings/toggle-notifications', methods=('POST',))
@login_required
def toggle_my_notifications():
    """Allow a signed-in user to manage their own notification setting."""
    User.toggle_notifications(g.user['id'])
    flash('Notification preference updated.')
    return redirect(url_for('dashboard.index'))
