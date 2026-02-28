"""
Career Guidance integration routes + Career Admin Panel routes.
Admin routes mirror the SubProject's admin panel, integrated into the main app.
"""
from flask import (Blueprint, render_template, request, redirect,
                   url_for, session, flash, current_app, send_from_directory)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from database import query_db, execute_db
from routes.auth import login_required
from functools import wraps
import os

career_bp = Blueprint('career', __name__, url_prefix='/career')

ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_image(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS


def career_admin_required(f):
    """Redirect to career admin login if not authenticated as career admin."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('admin_loggedin'):
            flash('Please log in as admin to access this page.', 'warning')
            return redirect(url_for('career.admin_login'))
        return f(*args, **kwargs)
    return decorated


# ── Career Guidance for Students ──────────────────────────────────────────────

@career_bp.route('/')
@login_required
def career_guidance():
    return render_template('career_guidance.html')


# ── Career Admin: Auth ─────────────────────────────────────────────────────────

@career_bp.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if session.get('admin_loggedin'):
        return redirect(url_for('career.admin_dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        admin = query_db('SELECT * FROM admin WHERE username = %s', (username,), one=True)
        if admin and check_password_hash(admin['password'], password):
            session['admin_loggedin'] = True
            session['admin_username'] = admin['username']
            flash('Admin login successful!', 'success')
            return redirect(url_for('career.admin_dashboard'))
        flash('Invalid admin credentials.', 'danger')

    return render_template('admin_login.html')


@career_bp.route('/admin_register', methods=['GET', 'POST'])
def admin_register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        hashed = generate_password_hash(password)
        try:
            execute_db(
                'INSERT INTO admin (username, password, plain_password) VALUES (%s, %s, %s)',
                (username, hashed, password)
            )
            flash('Admin registration successful! Please login.', 'success')
            return redirect(url_for('career.admin_login'))
        except Exception:
            flash('Username already exists.', 'danger')
    return render_template('admin_register.html')


@career_bp.route('/admin_logout')
def admin_logout():
    session.pop('admin_loggedin', None)
    session.pop('admin_username', None)
    flash('Logged out from admin.', 'info')
    return redirect(url_for('career.admin_login'))


@career_bp.route('/admin_forgot_password', methods=['GET', 'POST'])
def admin_forgot_password():
    password = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        row = query_db('SELECT plain_password FROM admin WHERE username = %s', (username,), one=True)
        if row:
            password = row['plain_password']
        else:
            flash('Admin not found or password not available.', 'danger')
    return render_template('admin_forgot_password.html', password=password)


# ── Career Admin: Dashboard ────────────────────────────────────────────────────

@career_bp.route('/admin_dashboard')
@career_admin_required
def admin_dashboard():
    admin = query_db(
        'SELECT * FROM admin WHERE username = %s',
        (session.get('admin_username', ''),),
        one=True
    )
    return render_template('admin_dashboard.html', admin=admin)


@career_bp.route('/admin_profile')
@career_admin_required
def admin_profile():
    admin = query_db(
        'SELECT * FROM admin WHERE username = %s',
        (session.get('admin_username', ''),),
        one=True
    )
    return render_template('admin_profile.html', admin=admin)


# ── Career Admin: Users ────────────────────────────────────────────────────────

@career_bp.route('/admin_users')
@career_admin_required
def admin_users():
    users = query_db('SELECT * FROM users ORDER BY id DESC')
    return render_template('admin_users.html', users=users)


@career_bp.route('/admin_delete_user/<int:user_id>', methods=['POST'])
@career_admin_required
def admin_delete_user(user_id):
    execute_db('DELETE FROM users WHERE id = %s', (user_id,))
    flash('User deleted.', 'info')
    return redirect(url_for('career.admin_users'))


@career_bp.route('/admin_reset_password/<int:user_id>', methods=['POST'])
@career_admin_required
def admin_reset_password(user_id):
    new_password = request.form.get('new_password', '')
    hashed = generate_password_hash(new_password)
    execute_db('UPDATE users SET password = %s WHERE id = %s', (hashed, user_id))
    flash('Password reset.', 'success')
    return redirect(url_for('career.admin_users'))


# ── Career Admin: Analytics ────────────────────────────────────────────────────

@career_bp.route('/admin_analytics')
@career_admin_required
def admin_analytics():
    try:
        total_users = (query_db('SELECT COUNT(*) as count FROM users', one=True) or {}).get('count', 0)
        total_resumes = (query_db("SELECT COUNT(*) as count FROM users WHERE resume_path IS NOT NULL", one=True) or {}).get('count', 0)
        total_career_plans = (query_db('SELECT COUNT(*) as count FROM career_plans', one=True) or {}).get('count', 0)
        total_feedback = (query_db('SELECT COUNT(*) as count FROM feedback', one=True) or {}).get('count', 0)
    except Exception:
        total_users = total_resumes = total_career_plans = total_feedback = 0
    return render_template(
        'admin_analytics.html',
        total_users=total_users,
        total_resumes=total_resumes,
        total_career_plans=total_career_plans,
        total_feedback=total_feedback
    )


# ── Career Admin: Feedback ─────────────────────────────────────────────────────

@career_bp.route('/admin_feedback')
@career_admin_required
def admin_feedback():
    try:
        feedbacks = query_db(
            'SELECT f.*, u.name FROM feedback f JOIN users u ON f.user_id = u.id ORDER BY f.created_at DESC'
        )
    except Exception:
        feedbacks = []
    return render_template('admin_feedback.html', feedbacks=feedbacks)


@career_bp.route('/admin_delete_feedback/<int:feedback_id>', methods=['POST'])
@career_admin_required
def admin_delete_feedback(feedback_id):
    execute_db('DELETE FROM feedback WHERE id = %s', (feedback_id,))
    flash('Feedback deleted.', 'info')
    return redirect(url_for('career.admin_feedback'))


# ── Career Admin: Careers ──────────────────────────────────────────────────────

@career_bp.route('/admin_careers')
@career_admin_required
def admin_careers():
    careers = query_db('SELECT * FROM careers ORDER BY id DESC')
    return render_template('admin_careers.html', careers=careers)


@career_bp.route('/admin_add_career', methods=['POST'])
@career_admin_required
def admin_add_career():
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    required_skills = request.form.get('required_skills', '').strip()
    category = request.form.get('category', '').strip()
    salary_range = request.form.get('salary_range', '').strip()
    courses = request.form.get('courses', '').strip()
    path = request.form.get('path', '').strip()
    try:
        execute_db(
            'INSERT INTO careers (title, description, required_skills, category, salary_range, courses, path) VALUES (%s, %s, %s, %s, %s, %s, %s)',
            (title, description, required_skills, category, salary_range, courses, path)
        )
        flash('Career added.', 'success')
    except Exception as e:
        flash(f'Error adding career: {e}', 'danger')
    return redirect(url_for('career.admin_careers'))


@career_bp.route('/admin_edit_career/<int:career_id>', methods=['POST'])
@career_admin_required
def admin_edit_career(career_id):
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    required_skills = request.form.get('required_skills', '').strip()
    category = request.form.get('category', '').strip()
    salary_range = request.form.get('salary_range', '').strip()
    courses = request.form.get('courses', '').strip()
    path = request.form.get('path', '').strip()
    execute_db(
        'UPDATE careers SET title=%s, description=%s, required_skills=%s, category=%s, salary_range=%s, courses=%s, path=%s WHERE id=%s',
        (title, description, required_skills, category, salary_range, courses, path, career_id)
    )
    flash('Career updated.', 'success')
    return redirect(url_for('career.admin_careers'))


@career_bp.route('/admin_delete_career/<int:career_id>', methods=['POST'])
@career_admin_required
def admin_delete_career(career_id):
    execute_db('DELETE FROM careers WHERE id = %s', (career_id,))
    flash('Career deleted.', 'info')
    return redirect(url_for('career.admin_careers'))


# ── Career Admin: Mentors ──────────────────────────────────────────────────────

@career_bp.route('/manage_mentors')
@career_admin_required
def manage_mentors():
    try:
        mentors = query_db('SELECT * FROM mentors ORDER BY id DESC')
    except Exception:
        mentors = []
    return render_template('manage_mentors.html', mentors=mentors)


@career_bp.route('/admin_add_mentor', methods=['POST'])
@career_admin_required
def admin_add_mentor():
    name = request.form.get('name', '').strip()
    expertise = request.form.get('expertise', '').strip()
    bio = request.form.get('bio', '').strip()
    contact = request.form.get('contact', '').strip()
    profile_pic = request.files.get('profile_pic')
    filename = None
    if profile_pic and profile_pic.filename and allowed_image(profile_pic.filename):
        filename = secure_filename(profile_pic.filename)
        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        profile_pic.save(os.path.join(upload_folder, filename))
    execute_db(
        'INSERT INTO mentors (name, expertise, bio, contact, profile_pic) VALUES (%s, %s, %s, %s, %s)',
        (name, expertise, bio, contact, filename)
    )
    flash('Mentor added successfully!', 'success')
    return redirect(url_for('career.manage_mentors'))


@career_bp.route('/admin_edit_mentor/<int:mentor_id>', methods=['POST'])
@career_admin_required
def admin_edit_mentor(mentor_id):
    name = request.form.get('name', '').strip()
    expertise = request.form.get('expertise', '').strip()
    bio = request.form.get('bio', '').strip()
    contact = request.form.get('contact', '').strip()
    profile_pic = request.files.get('profile_pic')
    existing = query_db('SELECT profile_pic FROM mentors WHERE id = %s', (mentor_id,), one=True)
    filename = existing['profile_pic'] if existing else None
    if profile_pic and profile_pic.filename and allowed_image(profile_pic.filename):
        filename = secure_filename(profile_pic.filename)
        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        profile_pic.save(os.path.join(upload_folder, filename))
    execute_db(
        'UPDATE mentors SET name=%s, expertise=%s, bio=%s, contact=%s, profile_pic=%s WHERE id=%s',
        (name, expertise, bio, contact, filename, mentor_id)
    )
    flash('Mentor updated successfully!', 'success')
    return redirect(url_for('career.manage_mentors'))


@career_bp.route('/admin_delete_mentor/<int:mentor_id>', methods=['POST'])
@career_admin_required
def admin_delete_mentor(mentor_id):
    execute_db('DELETE FROM mentors WHERE id = %s', (mentor_id,))
    flash('Mentor deleted successfully!', 'success')
    return redirect(url_for('career.manage_mentors'))


@career_bp.route('/uploads/<filename>')
def uploaded_file(filename):
    upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
    return send_from_directory(upload_folder, filename)


# ── Career Admin: Jobs ─────────────────────────────────────────────────────────

@career_bp.route('/admin_jobs', methods=['GET', 'POST'])
@career_admin_required
def admin_jobs():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        company = request.form.get('company', '').strip()
        location = request.form.get('location', '').strip()
        job_type = request.form.get('job_type', '').strip()
        salary = request.form.get('salary') or None
        job_url = request.form.get('url', '').strip()
        description = request.form.get('description', '').strip()
        requirements = request.form.get('requirements', '').strip()
        career_id = request.form.get('career_id') or None
        try:
            execute_db(
                'INSERT INTO jobs (title, company, location, job_type, salary, url, description, requirements, career_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)',
                (title, company, location, job_type, salary, job_url, description, requirements, career_id)
            )
            flash('Job added.', 'success')
        except Exception as e:
            flash(f'Error adding job: {e}', 'danger')
        return redirect(url_for('career.admin_jobs'))

    careers = query_db('SELECT id, title FROM careers ORDER BY title ASC')
    jobs = query_db(
        'SELECT j.*, c.title as career_title FROM jobs j LEFT JOIN careers c ON j.career_id = c.id ORDER BY j.id DESC'
    )
    return render_template('admin_jobs.html', jobs=jobs, careers=careers)


@career_bp.route('/admin_edit_job/<int:job_id>', methods=['POST'])
@career_admin_required
def admin_edit_job(job_id):
    title = request.form.get('title', '').strip()
    company = request.form.get('company', '').strip()
    location = request.form.get('location', '').strip()
    job_type = request.form.get('job_type', '').strip()
    salary = request.form.get('salary') or None
    job_url = request.form.get('url', '').strip()
    description = request.form.get('description', '').strip()
    requirements = request.form.get('requirements', '').strip()
    execute_db(
        'UPDATE jobs SET title=%s, company=%s, location=%s, job_type=%s, salary=%s, url=%s, description=%s, requirements=%s WHERE id=%s',
        (title, company, location, job_type, salary, job_url, description, requirements, job_id)
    )
    flash('Job updated.', 'success')
    return redirect(url_for('career.admin_jobs'))


@career_bp.route('/admin_delete_job/<int:job_id>', methods=['POST'])
@career_admin_required
def admin_delete_job(job_id):
    execute_db('DELETE FROM jobs WHERE id = %s', (job_id,))
    flash('Job deleted.', 'info')
    return redirect(url_for('career.admin_jobs'))
