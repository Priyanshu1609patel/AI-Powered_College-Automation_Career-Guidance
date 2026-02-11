"""
Admin panel routes: manage subjects, rules, notices, materials, view analytics.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from database import query_db, execute_db
from routes.auth import admin_required

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/')
@admin_required
def dashboard():
    """Admin dashboard with summary stats."""
    stats = {
        'total_users': 0,
        'total_subjects': 0,
        'total_queries': 0,
        'unanswered_count': 0,
        'total_notices': 0,
        'total_materials': 0,
    }
    try:
        row = query_db("SELECT COUNT(*) as c FROM users WHERE role = 'student'", one=True)
        stats['total_users'] = row['c'] if row else 0

        row = query_db("SELECT COUNT(*) as c FROM subjects WHERE is_active = TRUE", one=True)
        stats['total_subjects'] = row['c'] if row else 0

        row = query_db("SELECT COUNT(*) as c FROM query_logs", one=True)
        stats['total_queries'] = row['c'] if row else 0

        row = query_db("SELECT COUNT(*) as c FROM unanswered_queries WHERE is_resolved = FALSE", one=True)
        stats['unanswered_count'] = row['c'] if row else 0

        row = query_db("SELECT COUNT(*) as c FROM notices WHERE is_active = TRUE", one=True)
        stats['total_notices'] = row['c'] if row else 0

        row = query_db("SELECT COUNT(*) as c FROM subject_materials", one=True)
        stats['total_materials'] = row['c'] if row else 0
    except Exception:
        pass

    # Recent queries
    recent_queries = query_db(
        """SELECT query_text, detected_intent, confidence, created_at
           FROM query_logs ORDER BY created_at DESC LIMIT 10"""
    )

    return render_template('admin/dashboard.html', stats=stats, recent_queries=recent_queries)


# ----------------------------------------------------------------
# Subject Management
# ----------------------------------------------------------------

@admin_bp.route('/subjects')
@admin_required
def subjects():
    """List all subjects grouped by semester."""
    all_subjects = query_db(
        """SELECT s.id, s.subject_code, s.subject_name, s.credits, s.subject_type,
                  s.is_active, sem.semester_number
           FROM subjects s
           JOIN semesters sem ON s.semester_id = sem.id
           ORDER BY sem.semester_number, s.subject_code"""
    )
    semesters = query_db("SELECT id, semester_number, semester_name FROM semesters ORDER BY semester_number")
    return render_template('admin/subjects.html', subjects=all_subjects, semesters=semesters)


@admin_bp.route('/subjects/add', methods=['POST'])
@admin_required
def add_subject():
    """Add a new subject."""
    semester_id = request.form.get('semester_id')
    code = request.form.get('subject_code', '').strip().upper()
    name = request.form.get('subject_name', '').strip()
    credits = request.form.get('credits', '3')
    stype = request.form.get('subject_type', 'theory')
    syllabus = request.form.get('syllabus_brief', '').strip()

    if not semester_id or not code or not name:
        flash('Semester, code, and name are required.', 'danger')
        return redirect(url_for('admin.subjects'))

    try:
        execute_db(
            """INSERT INTO subjects (semester_id, subject_code, subject_name, credits, subject_type, syllabus_brief)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (semester_id, code, name, int(credits), stype, syllabus or None)
        )
        flash(f'Subject {code} added successfully.', 'success')
    except Exception as e:
        flash(f'Error adding subject: {e}', 'danger')

    return redirect(url_for('admin.subjects'))


@admin_bp.route('/subjects/<subject_id>/edit', methods=['POST'])
@admin_required
def edit_subject(subject_id):
    """Edit an existing subject."""
    name = request.form.get('subject_name', '').strip()
    credits = request.form.get('credits', '3')
    stype = request.form.get('subject_type', 'theory')
    syllabus = request.form.get('syllabus_brief', '').strip()
    is_active = request.form.get('is_active') == 'on'

    execute_db(
        """UPDATE subjects SET subject_name = %s, credits = %s, subject_type = %s,
           syllabus_brief = %s, is_active = %s WHERE id = %s""",
        (name, int(credits), stype, syllabus or None, is_active, subject_id)
    )
    flash('Subject updated.', 'success')
    return redirect(url_for('admin.subjects'))


# ----------------------------------------------------------------
# Academic Rules
# ----------------------------------------------------------------

@admin_bp.route('/rules')
@admin_required
def rules():
    """Manage academic rules."""
    all_rules = query_db(
        "SELECT * FROM academic_rules ORDER BY rule_category, created_at DESC"
    )
    return render_template('admin/rules.html', rules=all_rules)


@admin_bp.route('/rules/add', methods=['POST'])
@admin_required
def add_rule():
    category = request.form.get('rule_category', '').strip()
    title = request.form.get('rule_title', '').strip()
    content = request.form.get('rule_content', '').strip()
    keywords = request.form.get('keywords', '').strip()

    if not category or not title or not content:
        flash('All fields are required.', 'danger')
        return redirect(url_for('admin.rules'))

    execute_db(
        "INSERT INTO academic_rules (rule_category, rule_title, rule_content, keywords) VALUES (%s, %s, %s, %s)",
        (category, title, content, keywords or None)
    )
    flash('Rule added successfully.', 'success')
    return redirect(url_for('admin.rules'))


@admin_bp.route('/rules/<rule_id>/edit', methods=['POST'])
@admin_required
def edit_rule(rule_id):
    category = request.form.get('rule_category', '').strip()
    title = request.form.get('rule_title', '').strip()
    content = request.form.get('rule_content', '').strip()
    keywords = request.form.get('keywords', '').strip()
    is_active = request.form.get('is_active') == 'on'

    execute_db(
        """UPDATE academic_rules SET rule_category = %s, rule_title = %s, rule_content = %s,
           keywords = %s, is_active = %s WHERE id = %s""",
        (category, title, content, keywords or None, is_active, rule_id)
    )
    flash('Rule updated.', 'success')
    return redirect(url_for('admin.rules'))


@admin_bp.route('/rules/<rule_id>/delete', methods=['POST'])
@admin_required
def delete_rule(rule_id):
    execute_db("DELETE FROM academic_rules WHERE id = %s", (rule_id,))
    flash('Rule deleted.', 'success')
    return redirect(url_for('admin.rules'))


# ----------------------------------------------------------------
# Study Materials
# ----------------------------------------------------------------

@admin_bp.route('/materials')
@admin_required
def materials():
    """Manage study materials / Google Drive links."""
    all_materials = query_db(
        """SELECT sm.id, sm.material_title, sm.material_type, sm.drive_link, sm.created_at,
                  s.subject_code, s.subject_name
           FROM subject_materials sm
           JOIN subjects s ON sm.subject_id = s.id
           ORDER BY s.subject_code, sm.material_type"""
    )
    subjects = query_db("SELECT id, subject_code, subject_name FROM subjects WHERE is_active = TRUE ORDER BY subject_code")
    return render_template('admin/materials.html', materials=all_materials, subjects=subjects)


@admin_bp.route('/materials/add', methods=['POST'])
@admin_required
def add_material():
    subject_id = request.form.get('subject_id')
    title = request.form.get('material_title', '').strip()
    mtype = request.form.get('material_type', 'notes')
    link = request.form.get('drive_link', '').strip()

    if not subject_id or not title or not link:
        flash('All fields are required.', 'danger')
        return redirect(url_for('admin.materials'))

    execute_db(
        """INSERT INTO subject_materials (subject_id, material_title, material_type, drive_link, uploaded_by)
           VALUES (%s, %s, %s, %s, %s)""",
        (subject_id, title, mtype, link, session.get('user_id'))
    )
    flash('Material added successfully.', 'success')
    return redirect(url_for('admin.materials'))


@admin_bp.route('/materials/<material_id>/delete', methods=['POST'])
@admin_required
def delete_material(material_id):
    execute_db("DELETE FROM subject_materials WHERE id = %s", (material_id,))
    flash('Material deleted.', 'success')
    return redirect(url_for('admin.materials'))


# ----------------------------------------------------------------
# Notices
# ----------------------------------------------------------------

@admin_bp.route('/notices')
@admin_required
def notices():
    all_notices = query_db("SELECT * FROM notices ORDER BY created_at DESC")
    return render_template('admin/notices.html', notices=all_notices)


@admin_bp.route('/notices/add', methods=['POST'])
@admin_required
def add_notice():
    title = request.form.get('title', '').strip()
    content = request.form.get('content', '').strip()
    ntype = request.form.get('notice_type', 'general')

    if not title or not content:
        flash('Title and content are required.', 'danger')
        return redirect(url_for('admin.notices'))

    execute_db(
        "INSERT INTO notices (title, content, notice_type, posted_by) VALUES (%s, %s, %s, %s)",
        (title, content, ntype, session.get('user_id'))
    )
    flash('Notice posted successfully.', 'success')
    return redirect(url_for('admin.notices'))


@admin_bp.route('/notices/<notice_id>/toggle', methods=['POST'])
@admin_required
def toggle_notice(notice_id):
    execute_db("UPDATE notices SET is_active = NOT is_active WHERE id = %s", (notice_id,))
    flash('Notice status updated.', 'success')
    return redirect(url_for('admin.notices'))


@admin_bp.route('/notices/<notice_id>/delete', methods=['POST'])
@admin_required
def delete_notice(notice_id):
    execute_db("DELETE FROM notices WHERE id = %s", (notice_id,))
    flash('Notice deleted.', 'success')
    return redirect(url_for('admin.notices'))


# ----------------------------------------------------------------
# Unanswered Queries
# ----------------------------------------------------------------

@admin_bp.route('/unanswered')
@admin_required
def unanswered():
    queries = query_db(
        """SELECT uq.*, au.name as user_name
           FROM unanswered_queries uq
           LEFT JOIN users au ON uq.user_id = au.id
           ORDER BY uq.is_resolved ASC, uq.times_asked DESC, uq.created_at DESC"""
    )
    return render_template('admin/unanswered.html', queries=queries)


@admin_bp.route('/unanswered/<query_id>/resolve', methods=['POST'])
@admin_required
def resolve_query(query_id):
    response = request.form.get('admin_response', '').strip()
    execute_db(
        "UPDATE unanswered_queries SET is_resolved = TRUE, admin_response = %s, resolved_at = NOW() WHERE id = %s",
        (response or None, query_id)
    )
    flash('Query marked as resolved.', 'success')
    return redirect(url_for('admin.unanswered'))


# ----------------------------------------------------------------
# Analytics
# ----------------------------------------------------------------

@admin_bp.route('/analytics')
@admin_required
def analytics():
    # Top intents
    top_intents = query_db(
        """SELECT detected_intent, COUNT(*) as cnt
           FROM query_logs
           WHERE detected_intent IS NOT NULL
           GROUP BY detected_intent
           ORDER BY cnt DESC LIMIT 10"""
    )

    # Queries per day (last 7 days)
    daily_stats = query_db(
        """SELECT DATE(created_at) as day, COUNT(*) as cnt
           FROM query_logs
           WHERE created_at >= NOW() - INTERVAL '7 days'
           GROUP BY DATE(created_at)
           ORDER BY day"""
    )

    # Average confidence
    avg_conf = query_db(
        "SELECT ROUND(AVG(confidence)::numeric, 2) as avg_conf FROM query_logs WHERE confidence > 0",
        one=True
    )

    # Total unique users
    unique_users = query_db(
        "SELECT COUNT(DISTINCT user_id) as cnt FROM query_logs",
        one=True
    )

    return render_template(
        'admin/analytics.html',
        top_intents=top_intents,
        daily_stats=daily_stats,
        avg_confidence=avg_conf['avg_conf'] if avg_conf else 0,
        unique_users=unique_users['cnt'] if unique_users else 0,
    )
