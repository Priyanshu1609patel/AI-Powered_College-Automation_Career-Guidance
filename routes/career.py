"""
Career Guidance integration route.
Renders the career guidance page using the main app's session auth.
No separate login - uses the main project's authentication.
"""
from flask import Blueprint, render_template, session
from routes.auth import login_required

career_bp = Blueprint('career', __name__, url_prefix='/career')


@career_bp.route('/')
@login_required
def career_guidance():
    """
    Career guidance page integrated into the main application.
    Uses the authenticated session from the main project.
    """
    return render_template('career_guidance.html')
