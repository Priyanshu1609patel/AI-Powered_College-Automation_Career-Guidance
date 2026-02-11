"""
Authentication routes: login, register, logout.
Single auth system for the entire application (including career guidance).
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from database import query_db, execute_db
from functools import wraps

auth_bp = Blueprint('auth', __name__)


# ----------------------------------------------------------------
# Decorators
# ----------------------------------------------------------------

def login_required(f):
    """Redirect to login if user is not authenticated."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    """Redirect if user is not an admin."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        if session.get('role') != 'admin':
            flash('Admin access required.', 'danger')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated


# ----------------------------------------------------------------
# Routes
# ----------------------------------------------------------------

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        login_type = request.form.get('login_type', 'student')

        if login_type == 'admin':
            # ── Admin login (career-guidance admin table) ──
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')

            if not username or not password:
                flash('Please enter both username and password.', 'danger')
                return render_template('login.html')

            admin = query_db(
                "SELECT * FROM admin WHERE username = %s",
                (username,),
                one=True
            )

            if admin and check_password_hash(admin['password'], password):
                session['admin_loggedin'] = True
                session['admin_username'] = username
                session.permanent = True
                flash('Admin login successful!', 'success')
                return redirect('/career/admin_dashboard')
            else:
                flash('Invalid admin credentials.', 'danger')
        else:
            # ── Student / user login ──
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '')

            if not email or not password:
                flash('Please enter both email and password.', 'danger')
                return render_template('login.html')

            user = query_db(
                "SELECT id, name, email, password, role, semester, branch FROM users WHERE LOWER(email) = %s AND is_active = TRUE",
                (email,),
                one=True
            )

            if user and check_password_hash(user['password'], password):
                session['user_id'] = user['id']
                session['user_name'] = user['name']
                session['user_email'] = user['email']
                session['role'] = user['role']
                session['semester'] = user['semester']
                session['branch'] = user['branch']
                session.permanent = True

                if user['role'] == 'admin':
                    return redirect(url_for('admin.dashboard'))
                return redirect(url_for('main.dashboard'))
            else:
                flash('Invalid email or password.', 'danger')

    return render_template('login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')
        enrollment = request.form.get('enrollment_no', '').strip()
        semester = request.form.get('semester', '')
        phone = request.form.get('phone', '').strip()

        # Validation
        if not name or not email or not password:
            flash('Name, email, and password are required.', 'danger')
            return render_template('register.html')

        if password != confirm:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
            return render_template('register.html')

        # Check if email already exists
        existing = query_db(
            "SELECT id FROM users WHERE LOWER(email) = %s",
            (email,),
            one=True
        )
        if existing:
            flash('An account with this email already exists.', 'danger')
            return render_template('register.html')

        # Create user
        password_hash = generate_password_hash(password)
        sem_val = int(semester) if semester and semester.isdigit() else None

        execute_db(
            """INSERT INTO users (name, email, password, role, enrollment_no, semester, phone, branch)
               VALUES (%s, %s, %s, 'student', %s, %s, %s, 'CSE')""",
            (name, email, generate_password_hash(password), enrollment or None, sem_val, phone or None)
        )

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
