"""
Entry point: run both Flask applications on a single port.

Main app      → http://127.0.0.1:5000/
Career app    → http://127.0.0.1:5000/career/

Usage: python run.py
"""
import os
import sys
import importlib.util

from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple

from app import create_app

# ── Main app ────────────────────────────────────────────────
main_app = create_app()
main_app.config['SESSION_COOKIE_NAME'] = 'main_session'

# ── Career-guidance sub-app ──────────────────────────────────
# Load it via importlib so its `from config import *` and
# `from resume_parser.parser import ...` resolve against its
# own directory, not the main project's identically-named modules.

OLD_APP_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'Career_Guidance_SubProject')
)

_prev_cwd = os.getcwd()
_prev_path = sys.path[:]

# Temporarily adjust sys.path and cwd so the old app's internal
# imports (config, resume_parser, etc.) resolve correctly.
sys.path.insert(0, OLD_APP_DIR)
os.chdir(OLD_APP_DIR)

spec = importlib.util.spec_from_file_location(
    'career_old_app',
    os.path.join(OLD_APP_DIR, 'app.py'),
)
career_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(career_module)

# Restore original cwd and sys.path
os.chdir(_prev_cwd)
sys.path[:] = _prev_path

career_app = career_module.app
career_app.secret_key = main_app.secret_key          # share the same session
career_app.config['SESSION_COOKIE_NAME'] = 'main_session'
career_app.config['SESSION_COOKIE_PATH'] = '/'       # read cookie set at root
career_app.config['UPLOAD_FOLDER'] = os.path.join(OLD_APP_DIR, 'uploads')
career_app.config['APPLICATION_ROOT'] = '/Career_Guidance_SubProject'
career_app.config['TEMPLATES_AUTO_RELOAD'] = True    # reload templates on every request

# ── Combine with DispatcherMiddleware ───────────────────────
application = DispatcherMiddleware(main_app, {'/Career_Guidance_SubProject': career_app})

if __name__ == '__main__':
    run_simple(
        '0.0.0.0', 5000, application,
        use_reloader=True, use_debugger=True,
    )
