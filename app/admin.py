from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import User, Unit, Allergen, ActivityLog, Report
from app.auth import curator_required

bp = Blueprint('admin', __name__, url_prefix='/admin')


@bp.route('/')
@curator_required
def index():
    """Admin dashboard."""
    return render_template('admin/index.html')


@bp.route('/users')
@curator_required
def users():
    """Manage users."""
    all_users = User.get_all()
    return render_template('admin/users.html', users=all_users)


@bp.route('/users/<int:id>/toggle-notifications', methods=('POST',))
@curator_required
def toggle_notifications(id):
    """Toggle user notification settings."""
    if User.toggle_notifications(id):
        flash("Notification settings updated.")
    else:
        flash("User not found.")
    
    return redirect(url_for('admin.users'))


@bp.route('/reports/most-forked')
@curator_required
def most_forked():
    """Report: Most forked recipes."""
    recipes = Report.most_forked_recipes()
    return render_template('admin/most_forked.html', recipes=recipes)


@bp.route('/reports/allergen-audit')
@curator_required
def allergen_audit():
    """Report: Recipes by allergen."""
    allergen_id = request.args.get('allergen_id', type=int)
    
    allergens = Allergen.get_all()
    recipes = []
    
    if allergen_id:
        recipes = Report.recipes_with_allergen(allergen_id)
    
    return render_template('admin/allergen_audit.html', 
                         allergens=allergens, 
                         recipes=recipes,
                         selected_allergen=allergen_id)


@bp.route('/reports/user-activity')
@curator_required
def user_activity():
    """Report: User activity in last 30 days."""
    activity = ActivityLog.get_user_activity_report(days=30)
    return render_template('admin/user_activity.html', activity=activity)


@bp.route('/units')
@curator_required
def units():
    """Manage units lookup table."""
    all_units = Unit.get_all()
    return render_template('admin/units.html', units=all_units)


@bp.route('/units/add', methods=('POST',))
@curator_required
def add_unit():
    """Add a new unit."""
    name = request.form['name']
    abbreviation = request.form.get('abbreviation')
    
    try:
        Unit.create(name, abbreviation)
        flash('Unit added successfully.')
    except Exception:
        flash('Unit already exists.')
    
    return redirect(url_for('admin.units'))
