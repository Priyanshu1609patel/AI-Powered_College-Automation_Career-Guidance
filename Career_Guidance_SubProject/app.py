from flask import Flask, render_template, request, redirect, session, send_file, flash, url_for, g, send_from_directory, abort, jsonify, Blueprint
import os
from config import *
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from resume_parser.parser import extract_text, extract_resume_data
from reportlab.pdfgen import canvas
from io import BytesIO
from apscheduler.schedulers.background import BackgroundScheduler
import smtplib
from email.mime.text import MIMEText
import json
import re
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
from flask import send_file
from functools import wraps
from collections import defaultdict
import secrets
from datetime import datetime, timedelta
import requests
import uuid

app = Flask(__name__, template_folder='career_guidance_ai/templates')
app.secret_key = SECRET_KEY
app.config['APPLICATION_ROOT'] = '/Career_Guidance_SubProject'
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

import psycopg2
import psycopg2.extras

ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
def allowed_image(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS

def get_db():
    return psycopg2.connect(
        DATABASE_URL,
        sslmode='require',
        cursor_factory=psycopg2.extras.RealDictCursor
    )

def add_notification(user_id, message):
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute('INSERT INTO notifications (user_id, message) VALUES (%s, %s)', (user_id, message))
        conn.commit()
    finally:
        conn.close()

@app.before_request
def load_unread_notifications():
    g.unread_notifications = 0
    if 'user_id' in session:
        conn = get_db()
        try:
            with conn.cursor() as cursor:
                cursor.execute('SELECT COUNT(*) as count FROM notifications WHERE user_id = %s AND is_read = FALSE', (session['user_id'],))
                row = cursor.fetchone()
                g.unread_notifications = row['count'] if row else 0
        finally:
            conn.close()

def get_course_links_for_skills(skills):
    # skills: list of skill names (strings)
    links = []
    for skill in skills:
        q = skill.replace(' ', '+')
        links.append({
            'skill': skill.title(),
            'google': f'https://www.google.com/search?q={q}+course',
            'coursera': f'https://www.coursera.org/search?query={q}',
            'udemy': f'https://www.udemy.com/courses/search/?q={q}',
            'edx': f'https://www.edx.org/search?q={q}',
            'linkedin': f'https://www.linkedin.com/learning/search?keywords={q}',
            'khan': f'https://www.khanacademy.org/search?page_search_query={q}'
        })
    return links

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        hashed = generate_password_hash(password)
        conn = get_db()
        try:
            with conn.cursor() as cursor:
                cursor.execute('INSERT INTO users (name, email, password, plain_password) VALUES (%s, %s, %s, %s)', (name, email, hashed, password))
            conn.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except:
            flash('Email already exists.', 'danger')
        finally:
            conn.close()
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = get_db()
        try:
            with conn.cursor() as cursor:
                cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
                user = cursor.fetchone()
        finally:
            conn.close()
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        flash('Invalid credentials.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        user_id = session['user_id']
        conn = get_db()
        try:
            with conn.cursor() as cursor:
                # User info
                cursor.execute('SELECT name, profile_pic FROM users WHERE id = %s', (user_id,))
                user = cursor.fetchone()
                # Notifications
                cursor.execute('SELECT * FROM notifications WHERE user_id = %s AND is_read = FALSE', (user_id,))
                notifications = cursor.fetchall()
                # Feedback count
                cursor.execute('SELECT COUNT(*) as count FROM feedback WHERE user_id = %s', (user_id,))
                feedback_row = cursor.fetchone()
                feedback_count = feedback_row['count'] if feedback_row and 'count' in feedback_row else 0
                # Last completed milestone
                cursor.execute("SELECT cp.milestone, c.title, cp.status, cp.id FROM career_progress cp JOIN careers c ON cp.career_id = c.id WHERE cp.user_id = %s AND cp.status = 'Completed' ORDER BY cp.id DESC LIMIT 1", (user_id,))
                last_milestone = cursor.fetchone()
                # Last resume upload
                cursor.execute('SELECT id, skills, education, experience FROM resumes WHERE user_id = %s ORDER BY id DESC LIMIT 1', (user_id,))
                last_resume = cursor.fetchone()
                # Progress summary for each active career plan
                cursor.execute('SELECT DISTINCT cp.career_id, c.title FROM career_progress cp JOIN careers c ON cp.career_id = c.id WHERE cp.user_id = %s', (user_id,))
                plans = cursor.fetchall()
                progress_summaries = []
                for plan in plans:
                    cursor.execute('SELECT COUNT(*) as total FROM career_progress WHERE user_id = %s AND career_id = %s', (user_id, plan['career_id']))
                    total_row = cursor.fetchone()
                    total = total_row['total'] if total_row and 'total' in total_row else 0
                    cursor.execute("SELECT COUNT(*) as completed FROM career_progress WHERE user_id = %s AND career_id = %s AND status = 'Completed'", (user_id, plan['career_id']))
                    completed_row = cursor.fetchone()
                    completed = completed_row['completed'] if completed_row and 'completed' in completed_row else 0
                    percent = round((completed / total * 100), 1) if total > 0 else 0
                    progress_summaries.append({
                        'career_title': plan['title'],
                        'percent': percent,
                        'completed': completed,
                        'total': total
                    })
        finally:
            conn.close()
        raw_pic = user['profile_pic'] if user else None
        print(f"[DEBUG dashboard] user={user}, raw_pic={raw_pic!r}")
        if raw_pic:
            profile_pic_url = f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/{raw_pic}"
        else:
            profile_pic_url = None
        return render_template('dashboard.html',
            name=session['user_name'],
            profile_pic_url=profile_pic_url,
            notifications=notifications,
            feedback_count=feedback_count,
            last_milestone=last_milestone,
            last_resume=last_resume,
            progress_summaries=progress_summaries
        )
    return redirect('/login')

@app.route('/upload_resume', methods=['GET', 'POST'])
def upload_resume():
    if 'user_id' not in session:
        return redirect('/login')
    user_id = session['user_id']
    analysis = None
    score = None
    # Always initialize these so they are defined for both GET and POST
    analysis_categories = {
        'Skills': {'issues': [], 'solutions': [], 'positive': []},
        'Education': {'issues': [], 'solutions': [], 'positive': []},
        'Experience': {'issues': [], 'solutions': [], 'positive': []},
        'General': {'issues': [], 'solutions': [], 'positive': []}
    }
    why_not_100_categorized = []
    zipped_issues = []
    if request.method == 'POST':
        file = request.files.get('resume')
        if file and file.filename:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            text = extract_text(filepath)
            parsed = extract_resume_data(text)
            feedback = []
            score = 100
            # Categorized feedback and solutions
            # analysis_categories = {
            #     'Skills': {'issues': [], 'solutions': [], 'positive': []},
            #     'Education': {'issues': [], 'solutions': [], 'positive': []},
            #     'Experience': {'issues': [], 'solutions': [], 'positive': []},
            #     'General': {'issues': [], 'solutions': [], 'positive': []}
            # }
            # why_not_100_categorized = []
            # Skills
            skills = parsed.get('skills', '')
            if not skills or len(skills.split(',')) < 3:
                analysis_categories['Skills']['issues'].append('Too few skills listed.')
                analysis_categories['Skills']['solutions'].append('List at least 5 technical and soft skills relevant to your target job.')
                score -= 15
            else:
                analysis_categories['Skills']['positive'].append('Good number of skills listed.')
            # Education
            education = parsed.get('education', '')
            if not education or len(education) < 5:
                analysis_categories['Education']['issues'].append('Education section is missing or too short.')
                analysis_categories['Education']['solutions'].append('Add a detailed education section with degree, institution, and years attended.')
                score -= 15
            else:
                analysis_categories['Education']['positive'].append('Education section present.')
            # Experience
            experience = parsed.get('experience', '')
            if not experience or len(experience) < 5:
                analysis_categories['Experience']['issues'].append('Experience section is missing or too short.')
                analysis_categories['Experience']['solutions'].append('Add at least one relevant work or project experience with details.')
                score -= 15
            else:
                analysis_categories['Experience']['positive'].append('Experience section present.')
            # Strong action verbs
            strong_verbs = ['developed', 'led', 'designed', 'managed', 'created', 'built', 'implemented', 'analyzed', 'improved', 'launched']
            experience_text = experience.lower()
            if not any(verb in experience_text for verb in strong_verbs):
                analysis_categories['Experience']['issues'].append('Weak or missing action verbs in experience.')
                analysis_categories['Experience']['solutions'].append('Start each experience bullet with a strong action verb (e.g., developed, led, designed).')
                score -= 10
            # Quantifiable achievements
            if not re.search(r'\b(\d+|percent|%|increase|decrease|growth|revenue|users|clients|projects)\b', experience_text):
                analysis_categories['Experience']['issues'].append('No quantifiable achievements in experience.')
                analysis_categories['Experience']['solutions'].append('Include numbers or measurable results (e.g., "Increased sales by 20%", "Managed 5 projects").')
                score -= 10
            # Certifications (General)
            if 'certification' not in education.lower() and 'certified' not in education.lower():
                analysis_categories['General']['issues'].append('No certifications listed.')
                analysis_categories['General']['solutions'].append('Add relevant certifications (e.g., AWS Certified, PMP, Google Analytics).')
                score -= 5
            # Project links (General)
            if 'github' not in experience_text and 'portfolio' not in experience_text and 'linkedin' not in experience_text:
                analysis_categories['General']['issues'].append('No links to projects or portfolio.')
                analysis_categories['General']['solutions'].append('Include links to your GitHub, portfolio, or LinkedIn for recruiters to view your work.')
                score -= 5
            # Positive general
            if score >= 90:
                analysis_categories['General']['positive'].append('Resume is strong overall!')
            if score < 0:
                score = 0
            analysis = {
                'skills': skills,
                'education': education,
                'experience': experience,
                'feedback': feedback,
            }
            # Prepare why_not_100_categorized for table
            for cat, vals in analysis_categories.items():
                for i, issue in enumerate(vals['issues']):
                    solution = vals['solutions'][i] if i < len(vals['solutions']) else ''
                    why_not_100_categorized.append({'category': cat, 'issue': issue, 'solution': solution})
            # Save to DB
            conn = get_db()
            try:
                with conn.cursor() as cursor:
                    cursor.execute('''
                        INSERT INTO resumes (user_id, skills, education, experience)
                        VALUES (%s, %s, %s, %s)
                    ''', (
                        user_id,
                        skills,
                        education,
                        experience
                    ))
                    conn.commit()
            finally:
                conn.close()
            add_notification(user_id, "Your resume was uploaded and parsed successfully.")
            flash('Resume uploaded and parsed successfully!', 'success')
            # Fetch updated resumes list
            conn = get_db()
            try:
                with conn.cursor() as cursor:
                    cursor.execute('SELECT * FROM resumes WHERE user_id = %s ORDER BY id DESC', (user_id,))
                    resumes = cursor.fetchall()
            finally:
                conn.close()
            selected_resume_id = session.get('selected_resume_id')
            zipped_issues = [(item['issue'], item['solution'], item['category']) for item in why_not_100_categorized]
            return render_template('upload_resume.html', resumes=resumes, selected_resume_id=selected_resume_id, analysis=analysis, score=score, analysis_categories=analysis_categories, why_not_100_categorized=why_not_100_categorized, zipped_issues=zipped_issues, success=True)
        selected_resume_id = request.form.get('selected_resume')
        if selected_resume_id:
            session['selected_resume_id'] = int(selected_resume_id)
            flash('Resume selected for recommendations.', 'success')
            return redirect(url_for('interest_quiz'))
    # Show all resumes for this user
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute('SELECT * FROM resumes WHERE user_id = %s ORDER BY id DESC', (user_id,))
            resumes = cursor.fetchall()
    finally:
        conn.close()
    selected_resume_id = session.get('selected_resume_id')
    zipped_issues = [(item['issue'], item['solution'], item['category']) for item in why_not_100_categorized]
    return render_template('upload_resume.html', resumes=resumes, selected_resume_id=selected_resume_id, analysis=analysis, score=score, analysis_categories=analysis_categories, why_not_100_categorized=why_not_100_categorized, zipped_issues=zipped_issues)

@app.route('/delete_resume/<int:resume_id>', methods=['POST'])
def delete_resume(resume_id):
    if 'user_id' not in session:
        return redirect('/login')
    user_id = session['user_id']
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute('DELETE FROM resumes WHERE id = %s AND user_id = %s', (resume_id, user_id))
        conn.commit()
    finally:
        conn.close()
    flash('Resume deleted successfully.', 'success')
    return redirect(url_for('upload_resume'))

@app.route('/interest_quiz', methods=['GET', 'POST'])
def interest_quiz():
    if 'user_id' not in session:
        return redirect('/login')
    selected_resume_id = session.get('selected_resume_id')
    if not selected_resume_id:
        flash('Please select a resume first.', 'warning')
        return redirect(url_for('upload_resume'))
    previous_answers = {}
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute('SELECT quiz_answers FROM interests WHERE user_id = %s AND resume_id = %s ORDER BY id DESC LIMIT 1', (session['user_id'], selected_resume_id))
            row = cursor.fetchone()
            if row and row['quiz_answers']:
                try:
                    previous_answers = json.loads(row['quiz_answers'])
                except Exception:
                    previous_answers = {}
    finally:
        conn.close()
    if request.method == 'POST':
        responses = {f'q{i}': request.form.get(f'q{i}') for i in range(1, 11)}
        scores = {}
        for ans in responses.values():
            if ans:
                scores[ans] = scores.get(ans, 0) + 1
        if not scores:
            flash('Please answer all questions.', 'danger')
            return render_template('interest_quiz.html', previous_answers=responses)
        max_score = max(scores.values())
        top_areas = [area for area, score in scores.items() if score == max_score]
        interest_area = top_areas[0]
        conn = get_db()
        try:
            with conn.cursor() as cursor:
                cursor.execute('INSERT INTO interests (user_id, resume_id, interest_area, quiz_answers) VALUES (%s, %s, %s, %s)',
                    (session['user_id'], selected_resume_id, interest_area, json.dumps(responses)))
            conn.commit()
        finally:
            conn.close()
        flash(f'Your dominant interest area is {interest_area}.', 'success')
        return redirect(url_for('dashboard'))
    return render_template('interest_quiz.html', previous_answers=previous_answers)

@app.route('/recommendations')
def recommendations():
    if 'user_id' not in session:
        return redirect('/login')
    user_id = session['user_id']
    selected_resume_id = session.get('selected_resume_id')
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            if selected_resume_id:
                cursor.execute('SELECT * FROM resumes WHERE id = %s AND user_id = %s', (selected_resume_id, user_id))
                resume = cursor.fetchone()
            else:
                cursor.execute('SELECT * FROM resumes WHERE user_id = %s ORDER BY id DESC LIMIT 1', (user_id,))
                resume = cursor.fetchone()
            cursor.execute('SELECT * FROM interests WHERE user_id = %s AND resume_id = %s ORDER BY id DESC LIMIT 1', (user_id, selected_resume_id))
            interest = cursor.fetchone()
            if not resume or not interest:
                flash('Please upload your resume and complete the interest quiz first.', 'warning')
                return redirect(url_for('dashboard'))
            cursor.execute('SELECT * FROM careers WHERE category = %s', (interest['interest_area'],))
            careers = cursor.fetchall()
    finally:
        conn.close()
    user_skills = [skill.strip().lower() for skill in resume['skills'].split(',')] if resume['skills'] else []
    user_education = resume['education'].lower() if resume['education'] else ''
    user_experience = resume['experience'].lower() if resume['experience'] else ''
    interest_area = interest['interest_area']
    # Expanded project ideas with step-by-step guides
    project_ideas_dict = {
        'Software Developer': [
            {'title': 'Build a Personal Portfolio Website', 'steps': [
                'Choose a tech stack (HTML/CSS/JS, Flask, Django, etc.)',
                'Design the layout and sections (About, Projects, Contact)',
                'Implement navigation and responsive design',
                'Deploy on GitHub Pages, Netlify, or Heroku'
            ]},
            {'title': 'Create a REST API with Flask', 'steps': [
                'Set up a Flask project',
                'Design API endpoints (CRUD)',
                'Connect to a database (SQLite/MySQL)',
                'Test with Postman and document the API'
            ]},
            {'title': 'Contribute to Open Source', 'steps': [
                'Find a beginner-friendly project on GitHub',
                'Read the contribution guidelines',
                'Fix a bug or add a feature',
                'Submit a pull request and get feedback'
            ]},
            {'title': 'Develop a To-Do List App', 'steps': [
                'Design the UI and data model',
                'Implement add/edit/delete functionality',
                'Add user authentication (optional)',
                'Deploy and share your app'
            ]}
        ],
        'Data Analyst': [
            {'title': 'Analyze a Public Dataset', 'steps': [
                'Find a dataset on Kaggle or data.gov',
                'Clean and preprocess the data',
                'Visualize insights with matplotlib or Tableau',
                'Write a summary report'
            ]},
            {'title': 'Build a Dashboard', 'steps': [
                'Choose a tool (Power BI, Tableau, Dash)',
                'Connect to a data source',
                'Create interactive charts and filters',
                'Publish or share your dashboard'
            ]},
            {'title': 'Predict Trends with Regression', 'steps': [
                'Select a dataset with time series data',
                'Apply linear regression in Python',
                'Visualize predictions vs. actuals',
                'Interpret and present your findings'
            ]}
        ],
        'UI/UX Designer': [
            {'title': 'Redesign a Popular App', 'steps': [
                'Choose an app and analyze its UI/UX',
                'Sketch wireframes for improvements',
                'Create a Figma prototype',
                'Present your redesign with rationale'
            ]},
            {'title': 'Design a Mobile App', 'steps': [
                'Pick an app idea (e.g., habit tracker)',
                'Design user flows and wireframes',
                'Create high-fidelity mockups',
                'Test with users and iterate'
            ]}
        ],
        'Project Manager': [
            {'title': 'Plan a Mock Project', 'steps': [
                'Define project scope and goals',
                'Create a timeline with milestones',
                'Assign roles and responsibilities',
                'Track progress using Trello or Jira'
            ]},
            {'title': 'Simulate a Risk Management Plan', 'steps': [
                'Identify potential project risks',
                'Assess likelihood and impact',
                'Develop mitigation strategies',
                'Document and review with team'
            ]}
        ],
        'Support Engineer': [
            {'title': 'Set Up a Virtual Helpdesk', 'steps': [
                'Choose a helpdesk tool (e.g., Freshdesk, Zendesk)',
                'Configure ticket categories and workflows',
                'Create sample tickets and resolve them',
                'Document common solutions in a knowledge base'
            ]}
        ],
        'Cloud Engineer': [
            {'title': 'Deploy a Web App to the Cloud', 'steps': [
                'Choose a cloud provider (AWS, Azure, GCP)',
                'Set up a virtual server or app service',
                'Deploy your app and configure DNS',
                'Set up monitoring and scaling'
            ]}
        ]
    }
    # For each career, calculate available/missing skills and course links
    enhanced_careers = []
    for career in careers:
        required_skills = [s.strip().lower() for s in career['required_skills'].split(',')] if career['required_skills'] else []
        available_skills = [s for s in required_skills if s in user_skills]
        missing_skills = [s for s in required_skills if s not in user_skills]
        course_links = get_course_links_for_skills(missing_skills)
        # Project ideas with steps
        ideas = project_ideas_dict.get(career['title'], [])
        # Advanced match explanation
        explanation = []
        if available_skills:
            explanation.append(f"Matched skills: {', '.join([s.title() for s in available_skills])}")
        if missing_skills:
            explanation.append(f"Missing skills: {', '.join([s.title() for s in missing_skills])}")
        if user_education and any(e.lower() in user_education for e in career['title'].split()):
            explanation.append("Your education matches this field.")
        if user_experience and any(e.lower() in user_experience for e in career['title'].split()):
            explanation.append("Your experience matches this field.")
        match_score = len(available_skills)
        # Salary insight
        avg_salary = get_average_salary(career['title'])
        enhanced_careers.append({
            **career,
            'available_skills': available_skills,
            'missing_skills': missing_skills,
            'course_links': course_links,
            'project_ideas': ideas,
            'match_explanation': explanation,
            'match_score': min(match_score, 5),
            'avg_salary': avg_salary
        })
    recommendations = sorted(enhanced_careers, key=lambda x: x['match_score'], reverse=True)[:5]
    return render_template('recommendations.html', careers=recommendations)

@app.route('/career_path/<int:career_id>')
def career_path(career_id):
    if 'user_id' not in session:
        return redirect('/login')
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute('SELECT * FROM careers WHERE id = %s', (career_id,))
            career = cursor.fetchone()
    finally:
        conn.close()
    if not career:
        flash('Career not found.', 'danger')
        return redirect(url_for('recommendations'))
    return render_template('career_path.html', career=career)

@app.route('/download_pdf')
def download_pdf():
    if 'user_id' not in session:
        return redirect('/login')
    user_id = session['user_id']
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
            user = cursor.fetchone()
            cursor.execute('SELECT * FROM resumes WHERE user_id = %s ORDER BY id DESC LIMIT 1', (user_id,))
            resume = cursor.fetchone()
            cursor.execute('SELECT * FROM interests WHERE user_id = %s ORDER BY id DESC LIMIT 1', (user_id,))
            interest = cursor.fetchone()
            if not user or not resume or not interest:
                flash('User, resume, or interest data missing. Please complete your profile, upload a resume, and take the quiz.', 'danger')
                return redirect(url_for('dashboard'))
            cursor.execute('SELECT * FROM careers WHERE category = %s', (interest['interest_area'],))
            careers = cursor.fetchall()
    finally:
        conn.close()
    buffer = BytesIO()
    p = canvas.Canvas(buffer)
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, 800, f"Career Recommendations for {user['name']}")
    p.setFont("Helvetica", 12)
    y = 770
    for i, career in enumerate(careers[:5], 1):
        p.drawString(80, y, f"{i}. {career['title']}")
        p.drawString(100, y - 15, f"Category: {career['category']}")
        p.drawString(100, y - 30, f"Skills: {career['required_skills']}")
        p.drawString(100, y - 45, f"Desc: {career['description'][:80]}...")
        y -= 70
    p.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="career_recommendations.pdf", mimetype='application/pdf')

@app.route('/saved_careers')
def saved_careers():
    if 'user_id' not in session:
        return redirect('/login')
    user_id = session['user_id']
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute('SELECT * FROM saved_careers WHERE user_id = %s', (user_id,))
            careers = cursor.fetchall()
    finally:
        conn.close()
    return render_template('saved_careers.html', careers=careers)

@app.route('/save_career/<int:career_id>', methods=['POST'])
def save_career(career_id):
    if 'user_id' not in session:
        return redirect('/login')
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute('SELECT * FROM careers WHERE id = %s', (career_id,))
            career = cursor.fetchone()
    finally:
        conn.close()
    if career:
        conn = get_db()
        try:
            with conn.cursor() as cursor2:
                cursor2.execute('''
                    INSERT INTO saved_careers (user_id, career_id, title, category, required_skills, description, path)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                ''', (
                    session['user_id'], career['id'], career['title'], career['category'],
                    career['required_skills'], career['description'], career['path']
                ))
            conn.commit()
        finally:
            conn.close()
    return redirect(url_for('saved_careers'))

@app.route('/remove_saved_career/<int:saved_id>', methods=['POST'])
def remove_saved_career(saved_id):
    if 'user_id' not in session:
        return redirect('/login')
    user_id = session['user_id']
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute('DELETE FROM saved_careers WHERE id = %s AND user_id = %s', (saved_id, user_id))
        conn.commit()
    finally:
        conn.close()
    return redirect(url_for('saved_careers'))

@app.route('/track_progress')
def track_progress():
    if 'user_id' not in session:
        return redirect('/login')
    user_id = session['user_id']
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute('''
                SELECT cp.*, c.title FROM career_progress cp
                JOIN careers c ON cp.career_id = c.id
                WHERE cp.user_id = %s
                ORDER BY c.title, cp.id
            ''', (user_id,))
            progress = cursor.fetchall()
    finally:
        conn.close()
    # For each milestone, if it matches a missing skill for the user's career, add course_links
    # First, build a map: (career_id) -> set of missing skills
    career_missing_skills = {}
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute('SELECT DISTINCT career_id FROM career_progress WHERE user_id = %s', (user_id,))
            career_ids = [row['career_id'] for row in cursor.fetchall()]
            for cid in career_ids:
                cursor.execute('SELECT required_skills FROM careers WHERE id = %s', (cid,))
                row = cursor.fetchone()
                required_skills = [s.strip().lower() for s in row['required_skills'].split(',')] if row and row['required_skills'] else []
                cursor.execute('SELECT skills FROM resumes WHERE user_id = %s ORDER BY id DESC LIMIT 1', (user_id,))
                rrow = cursor.fetchone()
                user_skills = [s.strip().lower() for s in rrow['skills'].split(',')] if rrow and rrow['skills'] else []
                missing_skills = [s for s in required_skills if s not in user_skills]
                career_missing_skills[cid] = set(missing_skills)
    finally:
        conn.close()
    # Attach course_links to each milestone if it matches a missing skill
    for item in progress:
        skill_match = None
        for skill in career_missing_skills.get(item['career_id'], []):
            if skill in item['milestone'].lower():
                skill_match = skill
                break
        if skill_match:
            item['course_links'] = get_course_links_for_skills([skill_match])
        else:
            item['course_links'] = []
    return render_template('track_progress.html', progress=progress)

@app.route('/update_progress', methods=['POST'])
def update_progress():
    if 'user_id' not in session:
        return redirect('/login')
    progress_id = request.form['progress_id']
    new_status = request.form['status']
    note = request.form.get('note', None)
    if new_status not in ['Not Started', 'In Progress', 'Completed']:
        flash('Invalid status.', 'danger')
        return redirect(url_for('track_progress'))
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute('UPDATE career_progress SET status = %s, note = %s WHERE id = %s', (new_status, note, progress_id))
        conn.commit()
    finally:
        conn.close()
    if new_status == 'Completed':
        # Get milestone and career title for the notification
        conn2 = get_db()
        try:
            with conn2.cursor() as cursor2:
                cursor2.execute('SELECT cp.milestone, c.title FROM career_progress cp JOIN careers c ON cp.career_id = c.id WHERE cp.id = %s', (progress_id,))
                row = cursor2.fetchone()
                if row:
                    add_notification(session['user_id'], f"Congratulations! You completed the milestone: {row['milestone']} in {row['title']}.")
        finally:
            conn2.close()
    flash('Progress updated!', 'success')
    return redirect(url_for('track_progress'))

@app.route('/start_plan/<int:career_id>')
def start_plan(career_id):
    if 'user_id' not in session:
        return redirect('/login')
    user_id = session['user_id']
    selected_resume_id = session.get('selected_resume_id')
    if not selected_resume_id:
        flash('Please select a resume first.', 'warning')
        return redirect(url_for('upload_resume'))
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute('SELECT * FROM careers WHERE id = %s', (career_id,))
            career = cursor.fetchone()
            if not career:
                flash('Career not found.', 'danger')
                return redirect(url_for('recommendations'))
            # Fetch milestones from career_milestones table
            cursor.execute('SELECT milestone FROM career_milestones WHERE career_id = %s', (career_id,))
            milestone_rows = cursor.fetchall()
            if milestone_rows:
                milestones = [row['milestone'] for row in milestone_rows]
            else:
                # Fallback to default logic if no milestones in table
                title = career['title'].lower()
                if 'developer' in title:
                    milestones = [
                        'Learn Programming Language',
                        'Complete Git & GitHub Course',
                        'Build Portfolio Website',
                        'Contribute to Open Source',
                        'Do Internship',
                        'Apply for Developer Jobs'
                    ]
                elif 'data analyst' in title:
                    milestones = [
                        'Learn Excel & SQL',
                        'Master Data Visualization Tools',
                        'Do Case Study Projects',
                        'Internship in Analytics',
                        'Prepare Resume',
                        'Apply for Analyst Roles'
                    ]
                else:
                    milestones = [
                        'Research the Career Path',
                        'Take Online Courses',
                        'Build Projects',
                        'Get Mentorship',
                        'Internship or Freelancing',
                        'Apply for Jobs'
                    ]
            cursor.execute('SELECT milestone FROM career_progress WHERE user_id = %s AND career_id = %s AND resume_id = %s', (user_id, career_id, selected_resume_id))
            existing = set(row['milestone'] for row in cursor.fetchall())
    finally:
        conn.close()
    for m in milestones:
        if m not in existing:
            conn = get_db()
            try:
                with conn.cursor() as insert_cursor:
                    insert_cursor.execute(
                        'INSERT INTO career_progress (user_id, career_id, milestone, status, resume_id, note) VALUES (%s, %s, %s, %s, %s, %s)',
                        (user_id, career_id, m, 'Not Started', selected_resume_id, None)
                    )
                conn.commit()
            finally:
                conn.close()
    add_notification(user_id, f"You started the {career['title']} career plan. Good luck!")
    flash('Career plan started! Track your progress below.', 'success')
    return redirect(url_for('career_plan_started', career_id=career_id))

@app.route('/career_plan_started/<int:career_id>')
def career_plan_started(career_id):
    if 'user_id' not in session:
        return redirect('/login')
    user_id = session['user_id']
    selected_resume_id = session.get('selected_resume_id')
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute('SELECT * FROM careers WHERE id = %s', (career_id,))
            career = cursor.fetchone()
            cursor.execute('SELECT * FROM career_progress WHERE user_id = %s AND career_id = %s AND resume_id = %s', (user_id, career_id, selected_resume_id))
            milestones = cursor.fetchall()
    finally:
        conn.close()
    return render_template('career_plan_started.html', career=career, milestones=milestones)

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if 'user_id' not in session:
        return redirect('/login')
    if request.method == 'POST':
        message = request.form['message']
        if not message:
            flash('Feedback cannot be empty.', 'danger')
            return render_template('feedback.html')
        conn = get_db()
        try:
            with conn.cursor() as cursor:
                cursor.execute('INSERT INTO feedback (user_id, message) VALUES (%s, %s)', (session['user_id'], message))
            conn.commit()
        finally:
            conn.close()
        flash('Thank you for your feedback!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('feedback.html')

@app.route('/notifications')
def notifications():
    if 'user_id' not in session:
        return redirect('/login')
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute('SELECT * FROM notifications WHERE user_id = %s ORDER BY created_at DESC', (session['user_id'],))
            notes = cursor.fetchall()
            cursor.execute('UPDATE notifications SET is_read = TRUE WHERE user_id = %s', (session['user_id'],))
        conn.commit()
    finally:
        conn.close()
    return render_template('notifications.html', notifications=notes)

def send_weekly_progress_emails():
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute('SELECT id, email, name FROM users')
            users = cursor.fetchall()
            for user in users:
                cursor.execute('SELECT * FROM career_progress WHERE user_id = %s', (user['id'],))
                progress = cursor.fetchall()
                # Compose email body
                body = f"Hello {user['name']},\n\nHere is your career progress:\n"
                for p in progress:
                    body += f"- {p['milestone']}: {p['status']}\n"
                # Send email
                msg = MIMEText(body)
                msg['Subject'] = 'Your Weekly Career Progress'
                msg['From'] = 'your_email@example.com'
                msg['To'] = user['email']
                with smtplib.SMTP('smtp.example.com', 587) as server:
                    server.starttls()
                    server.login('your_email@example.com', 'your_password')
                    server.send_message(msg)
    finally:
        conn.close()

scheduler = BackgroundScheduler()
scheduler.add_job(send_weekly_progress_emails, 'interval', weeks=1)
scheduler.start()

@app.route('/remove_progress/<int:progress_id>', methods=['POST'])
def remove_progress(progress_id):
    if 'user_id' not in session:
        return redirect('/login')
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute('DELETE FROM career_progress WHERE id = %s', (progress_id,))
        conn.commit()
    finally:
        conn.close()
    flash('Milestone removed.', 'success')
    return redirect(url_for('track_progress'))

@app.route('/delete_career_progress', methods=['POST'])
def delete_career_progress():
    if 'user_id' not in session:
        return redirect('/login')
    user_id = session['user_id']
    career_id = request.form.get('career_id')
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute('DELETE FROM career_progress WHERE user_id = %s AND career_id = %s', (user_id, career_id))
        conn.commit()
    finally:
        conn.close()
    flash('Career plan deleted.', 'success')
    return redirect(url_for('track_progress'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect('/login')
    user_id = session['user_id']
    if request.method == 'POST':
        name = request.form.get('name')
        bio = request.form.get('bio')
        linkedin = request.form.get('linkedin')
        file = request.files.get('profile_pic')
        profile_pic_filename = None
        
        if file and file.filename and allowed_image(file.filename):
            # Get old profile pic to delete
            conn = get_db()
            try:
                with conn.cursor() as cursor:
                    cursor.execute('SELECT profile_pic FROM users WHERE id = %s', (user_id,))
                    old_user = cursor.fetchone()
                    old_pic = old_user['profile_pic'] if old_user else None
            finally:
                conn.close()
            
            ext = file.filename.rsplit('.', 1)[1].lower()
            profile_pic_filename = f"{user_id}_{uuid.uuid4().hex}.{ext}"
            
            # Upload to Supabase Storage
            try:
                file_data = file.read()
                storage_url = f"{SUPABASE_URL}/storage/v1/object/{SUPABASE_BUCKET}/{profile_pic_filename}"
                
                headers = {
                    'Authorization': f'Bearer {SUPABASE_SERVICE_ROLE_KEY}',
                    'Content-Type': f'image/{ext}'
                }
                
                response = requests.post(storage_url, data=file_data, headers=headers)
                
                if response.status_code not in [200, 201]:
                    flash(f'Upload failed: {response.text}', 'danger')
                    return redirect(url_for('profile', edit=1))
                
                # Delete old image from Supabase if exists
                if old_pic:
                    delete_url = f"{SUPABASE_URL}/storage/v1/object/{SUPABASE_BUCKET}/{old_pic}"
                    requests.delete(delete_url, headers={'Authorization': f'Bearer {SUPABASE_SERVICE_ROLE_KEY}'})
                    
            except Exception as e:
                flash(f'Upload error: {str(e)}', 'danger')
                return redirect(url_for('profile', edit=1))
        
        conn = get_db()
        try:
            with conn.cursor() as cursor:
                if profile_pic_filename:
                    cursor.execute('UPDATE users SET name=%s, bio=%s, linkedin=%s, profile_pic=%s WHERE id=%s',
                        (name, bio, linkedin, profile_pic_filename, user_id))
                else:
                    cursor.execute('UPDATE users SET name=%s, bio=%s, linkedin=%s WHERE id=%s',
                        (name, bio, linkedin, user_id))
            conn.commit()
        finally:
            conn.close()
        
        # Update session name
        session['user_name'] = name
        
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))
    
    # GET: show profile
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
            user = cursor.fetchone()
    finally:
        conn.close()
    return render_template('profile.html', user=user)

@app.route('/toggle_dark_mode', methods=['GET', 'POST'])
def toggle_dark_mode():
    if 'dark_mode' in session:
        session['dark_mode'] = not session['dark_mode']
    else:
        session['dark_mode'] = True
    return redirect(request.referrer or url_for('dashboard'))

@app.route('/projects')
def projects():
    if 'user_id' not in session:
        return redirect('/login')
    user_id = session['user_id']
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute('SELECT * FROM projects WHERE user_id = %s ORDER BY created_at DESC', (user_id,))
            projects = cursor.fetchall()
    finally:
        conn.close()
    return render_template('projects.html', projects=projects)

@app.route('/add_project', methods=['POST'])
def add_project():
    if 'user_id' not in session:
        return redirect('/login')
    user_id = session['user_id']
    title = request.form['title']
    description = request.form.get('description', '')
    skills = request.form.get('skills', '')
    link = request.form.get('link', '')
    if not title:
        flash('Project title is required.', 'danger')
        return redirect(url_for('projects'))
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute('INSERT INTO projects (user_id, title, description, skills, link) VALUES (%s, %s, %s, %s, %s)',
                (user_id, title, description, skills, link))
        conn.commit()
    finally:
        conn.close()
    flash('Project added!', 'success')
    return redirect(url_for('projects'))

@app.route('/edit_project/<int:project_id>', methods=['POST'])
def edit_project(project_id):
    if 'user_id' not in session:
        return redirect('/login')
    user_id = session['user_id']
    title = request.form['title']
    description = request.form.get('description', '')
    skills = request.form.get('skills', '')
    link = request.form.get('link', '')
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute('UPDATE projects SET title = %s, description = %s, skills = %s, link = %s WHERE id = %s AND user_id = %s',
                (title, description, skills, link, project_id, user_id))
        conn.commit()
    finally:
        conn.close()
    flash('Project updated!', 'success')
    return redirect(url_for('projects'))

@app.route('/delete_project/<int:project_id>', methods=['POST'])
def delete_project(project_id):
    if 'user_id' not in session:
        return redirect('/login')
    user_id = session['user_id']
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute('DELETE FROM projects WHERE id = %s AND user_id = %s', (project_id, user_id))
        conn.commit()
    finally:
        conn.close()
    flash('Project deleted!', 'info')
    return redirect(url_for('projects'))

@app.route('/add_project_from_idea', methods=['POST'])
def add_project_from_idea():
    if 'user_id' not in session:
        return redirect('/login')
    user_id = session['user_id']
    title = request.form['title']
    description = request.form.get('description', '')
    skills = request.form.get('skills', '')
    link = request.form.get('link', '')
    if not title:
        flash('Project title is required.', 'danger')
        return redirect(url_for('recommendations'))
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute('INSERT INTO projects (user_id, title, description, skills, link) VALUES (%s, %s, %s, %s, %s)',
                (user_id, title, description, skills, link))
        conn.commit()
    finally:
        conn.close()
    flash('Project idea added to your portfolio!', 'success')
    return redirect(url_for('projects'))

@app.route('/mentors')
def mentors():
    if 'user_id' not in session:
        return redirect('/login')
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute('SELECT * FROM mentors ORDER BY name')
            mentors = cursor.fetchall()
    finally:
        conn.close()
    return render_template('mentors.html', mentors=mentors)

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db()
        try:
            with conn.cursor() as cursor:
                cursor.execute('SELECT * FROM admin WHERE username = %s', (username,))
                admin = cursor.fetchone()
        finally:
            conn.close()
        if admin and check_password_hash(admin['password'], password):
            session['admin_loggedin'] = True
            session['admin_username'] = admin['username']
            flash('Admin login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        flash('Invalid admin credentials.', 'danger')
    return render_template('admin_login.html')

@app.route('/admin_register', methods=['GET', 'POST'])
def admin_register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed = generate_password_hash(password)
        conn = get_db()
        try:
            with conn.cursor() as cursor:
                cursor.execute('INSERT INTO admin (username, password, plain_password) VALUES (%s, %s, %s)', (username, hashed, password))
            conn.commit()
            flash('Admin registration successful! Please login.', 'success')
            return redirect(url_for('admin_login'))
        except:
            flash('Username already exists.', 'danger')
        finally:
            conn.close()
    return render_template('admin_register.html')

@app.route('/admin_logout')
def admin_logout():
    session.pop('admin_loggedin', None)
    session.pop('admin_username', None)
    flash('Logged out from admin.', 'info')
    return redirect('/login')

@app.route('/admin_dashboard')
def admin_dashboard():
    if not session.get('admin_loggedin'):
        return redirect(url_for('admin_login'))
    # For now, just show the logged-in admin username
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute('SELECT * FROM admin WHERE username = %s', (session.get('admin_username', 'admin'),))
            admin = cursor.fetchone()
    finally:
        conn.close()
    return render_template('admin_dashboard.html', admin=admin)

@app.route('/admin_profile')
def admin_profile():
    if not session.get('admin_loggedin'):
        return redirect(url_for('admin_login'))
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute('SELECT * FROM admin WHERE username = %s', (session.get('admin_username', 'admin'),))
            admin = cursor.fetchone()
    finally:
        conn.close()
    return render_template('admin_profile.html', admin=admin)

@app.route('/admin_users')
def admin_users():
    if not session.get('admin_loggedin'):
        return redirect(url_for('admin_login'))
    conn = get_db()
    with conn.cursor() as cursor:
        cursor.execute('SELECT * FROM users ORDER BY id DESC')
        users = cursor.fetchall()
    conn.close()
    return render_template('admin_users.html', users=users)

@app.route('/admin_delete_user/<int:user_id>', methods=['POST'])
def admin_delete_user(user_id):
    if not session.get('admin_loggedin'):
        return redirect(url_for('admin_login'))
    conn = get_db()
    with conn.cursor() as cursor:
        cursor.execute('DELETE FROM users WHERE id = %s', (user_id,))
    conn.commit()
    conn.close()
    flash('User deleted.', 'info')
    return redirect(url_for('admin_users'))

@app.route('/admin_reset_password/<int:user_id>', methods=['POST'])
def admin_reset_password(user_id):
    if not session.get('admin_loggedin'):
        return redirect(url_for('admin_login'))
    new_password = request.form['new_password']
    hashed = generate_password_hash(new_password)
    conn = get_db()
    with conn.cursor() as cursor:
        cursor.execute('UPDATE users SET password = %s WHERE id = %s', (hashed, user_id))
    conn.commit()
    conn.close()
    flash('Password reset.', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin_analytics')
def admin_analytics():
    if not session.get('admin_loggedin'):
        return redirect(url_for('admin_login'))
    conn = get_db()
    with conn.cursor() as cursor:
        cursor.execute('SELECT COUNT(*) as count FROM users')
        total_users = cursor.fetchone()['count']
        cursor.execute('SELECT COUNT(*) as count FROM resumes')
        total_resumes = cursor.fetchone()['count']
        cursor.execute('SELECT COUNT(*) as count FROM career_progress')
        total_career_plans = cursor.fetchone()['count']
        cursor.execute('SELECT COUNT(*) as count FROM feedback')
        total_feedback = cursor.fetchone()['count']
    conn.close()
    return render_template('admin_analytics.html', total_users=total_users, total_resumes=total_resumes, total_career_plans=total_career_plans, total_feedback=total_feedback)

@app.route('/admin_feedback')
def admin_feedback():
    if not session.get('admin_loggedin'):
        return redirect(url_for('admin_login'))
    conn = get_db()
    with conn.cursor() as cursor:
        cursor.execute('SELECT f.*, u.name FROM feedback f JOIN users u ON f.user_id = u.id ORDER BY f.created_at DESC')
        feedbacks = cursor.fetchall()
    conn.close()
    return render_template('admin_feedback.html', feedbacks=feedbacks)

@app.route('/admin_delete_feedback/<int:feedback_id>', methods=['POST'])
def admin_delete_feedback(feedback_id):
    if not session.get('admin_loggedin'):
        return redirect(url_for('admin_login'))
    conn = get_db()
    with conn.cursor() as cursor:
        cursor.execute('DELETE FROM feedback WHERE id = %s', (feedback_id,))
    conn.commit()
    conn.close()
    flash('Feedback deleted.', 'info')
    return redirect(url_for('admin_feedback'))

@app.route('/admin_careers')
def admin_careers():
    if not session.get('admin_loggedin'):
        return redirect(url_for('admin_login'))
    conn = get_db()
    with conn.cursor() as cursor:
        cursor.execute('SELECT * FROM careers ORDER BY id DESC')
        careers = cursor.fetchall()
    conn.close()
    return render_template('admin_careers.html', careers=careers)

@app.route('/admin_add_career', methods=['POST'])
def admin_add_career():
    if not session.get('admin_loggedin'):
        return redirect(url_for('admin_login'))
    title = request.form['title']
    description = request.form.get('description', '')
    required_skills = request.form.get('required_skills', '')
    category = request.form.get('category', '')
    salary_range = request.form.get('salary_range', '')
    courses = request.form.get('courses', '')
    path = request.form.get('path', '')
    conn = get_db()
    with conn.cursor() as cursor:
        cursor.execute('INSERT INTO careers (title, description, required_skills, category, salary_range, courses, path) VALUES (%s, %s, %s, %s, %s, %s, %s)',
            (title, description, required_skills, category, salary_range, courses, path))
    conn.commit()
    conn.close()
    flash('Career added.', 'success')
    return redirect(url_for('admin_careers'))

@app.route('/admin_edit_career/<int:career_id>', methods=['POST'])
def admin_edit_career(career_id):
    if not session.get('admin_loggedin'):
        return redirect(url_for('admin_login'))
    title = request.form['title']
    description = request.form.get('description', '')
    required_skills = request.form.get('required_skills', '')
    category = request.form.get('category', '')
    salary_range = request.form.get('salary_range', '')
    courses = request.form.get('courses', '')
    path = request.form.get('path', '')
    conn = get_db()
    with conn.cursor() as cursor:
        cursor.execute('UPDATE careers SET title=%s, description=%s, required_skills=%s, category=%s, salary_range=%s, courses=%s, path=%s WHERE id=%s',
            (title, description, required_skills, category, salary_range, courses, path, career_id))
    conn.commit()
    conn.close()
    flash('Career updated.', 'success')
    return redirect(url_for('admin_careers'))

@app.route('/admin_delete_career/<int:career_id>', methods=['POST'])
def admin_delete_career(career_id):
    if not session.get('admin_loggedin'):
        return redirect(url_for('admin_login'))
    conn = get_db()
    with conn.cursor() as cursor:
        cursor.execute('DELETE FROM careers WHERE id = %s', (career_id,))
    conn.commit()
    conn.close()
    flash('Career deleted.', 'info')
    return redirect(url_for('admin_careers'))

def is_valid_email(email):
    return re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email)
def is_valid_url(url):
    return url.startswith('http://') or url.startswith('https://')

# Helper: Validate contact (email or URL)
def is_valid_contact(contact):
    email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    url_regex = r"^(https?://)?[\w.-]+(\.[\w\.-]+)+[/#?]?.*$"
    return re.match(email_regex, contact) or re.match(url_regex, contact)

@app.route('/manage_mentors')
def manage_mentors():
    if not session.get('admin_loggedin'):
        return redirect(url_for('admin_login'))
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute('SELECT * FROM mentors')
            mentors = cursor.fetchall()
    finally:
        conn.close()
    return render_template('manage_mentors.html', mentors=mentors)

@app.route('/admin_add_mentor', methods=['POST'])
def admin_add_mentor():
    if not session.get('admin_loggedin'):
        return redirect(url_for('admin_login'))
    name = request.form['name']
    expertise = request.form['expertise']
    bio = request.form['bio']
    contact = request.form['contact']
    profile_pic = request.files.get('profile_pic')
    if not is_valid_contact(contact):
        flash('Contact must be a valid email or URL.', 'danger')
        return redirect(url_for('manage_mentors'))
    filename = None
    if profile_pic and profile_pic.filename:
        filename = secure_filename(profile_pic.filename)
        profile_pic.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute('INSERT INTO mentors (name, expertise, bio, contact, profile_pic) VALUES (%s, %s, %s, %s, %s)',
                           (name, expertise, bio, contact, filename))
        conn.commit()
    finally:
        conn.close()
    flash('Mentor added successfully!', 'success')
    return redirect(url_for('manage_mentors'))

@app.route('/admin_edit_mentor/<int:mentor_id>', methods=['POST'])
def admin_edit_mentor(mentor_id):
    if not session.get('admin_loggedin'):
        return redirect(url_for('admin_login'))
    name = request.form['name']
    expertise = request.form['expertise']
    bio = request.form['bio']
    contact = request.form['contact']
    profile_pic = request.files.get('profile_pic')
    if not is_valid_contact(contact):
        flash('Contact must be a valid email or URL.', 'danger')
        return redirect(url_for('manage_mentors'))
    filename = None
    if profile_pic and profile_pic.filename:
        filename = secure_filename(profile_pic.filename)
        profile_pic.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            if filename:
                cursor.execute('UPDATE mentors SET name=%s, expertise=%s, bio=%s, contact=%s, profile_pic=%s WHERE id=%s',
                               (name, expertise, bio, contact, filename, mentor_id))
            else:
                cursor.execute('UPDATE mentors SET name=%s, expertise=%s, bio=%s, contact=%s WHERE id=%s',
                               (name, expertise, bio, contact, mentor_id))
        conn.commit()
    finally:
        conn.close()
    flash('Mentor updated successfully!', 'success')
    return redirect(url_for('manage_mentors'))

@app.route('/admin_delete_mentor/<int:mentor_id>', methods=['POST'])
def admin_delete_mentor(mentor_id):
    if not session.get('admin_loggedin'):
        return redirect(url_for('admin_login'))
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute('DELETE FROM mentors WHERE id=%s', (mentor_id,))
        conn.commit()
    finally:
        conn.close()
    flash('Mentor deleted successfully!', 'success')
    return redirect(url_for('manage_mentors'))

def award_badge(user_id, badge_name):
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute('SELECT id FROM badges WHERE name = %s', (badge_name,))
            badge = cursor.fetchone()
            if not badge:
                return
            badge_id = badge['id']
            cursor.execute('SELECT * FROM user_badges WHERE user_id = %s AND badge_id = %s', (user_id, badge_id))
            if not cursor.fetchone():
                cursor.execute('INSERT INTO user_badges (user_id, badge_id) VALUES (%s, %s)', (user_id, badge_id))
        conn.commit()
    finally:
        conn.close()

def add_points(user_id, points):
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute('UPDATE users SET points = points + %s WHERE id = %s', (points, user_id))
        conn.commit()
    finally:
        conn.close()

# Award on resume upload
# In upload_resume, after successful upload:
# add_points(user_id, 10); award_badge(user_id, 'First Resume Upload')
# Award on quiz completion
# In interest_quiz, after POST:
# add_points(session['user_id'], 5); award_badge(session['user_id'], 'Quiz Master')
# Award on milestone completion
# In update_progress, if new_status == 'Completed':
# add_points(session['user_id'], 10); award_badge(session['user_id'], 'First Milestone') (if first completed)
# Award on career plan completion (all milestones completed)
# In update_progress, after marking last milestone as completed:
# add_points(session['user_id'], 25); award_badge(session['user_id'], 'Career Plan Finisher')
# Award on feedback
# In feedback, after POST:
# add_points(session['user_id'], 5); award_badge(session['user_id'], 'Feedback Giver')
# Award on project add
# In add_project, after successful add:
# add_points(user_id, 10); award_badge(user_id, 'Project Builder')

@app.route('/leaderboard')
def leaderboard():
    conn = get_db()
    with conn.cursor() as cursor:
        cursor.execute('SELECT id, name, points FROM users ORDER BY points DESC, id ASC LIMIT 20')
        users = cursor.fetchall()
    conn.close()
    return render_template('leaderboard.html', users=users)

@app.route('/jobs')
def jobs():
    if 'user_id' not in session:
        return redirect('/login')
    search = request.args.get('search', '')
    user_id = session['user_id']
    # New filters
    company = request.args.get('company', '').strip()
    location = request.args.get('location', '').strip()
    job_type = request.args.get('job_type', '').strip()
    salary_min = request.args.get('salary_min', '').strip()
    salary_max = request.args.get('salary_max', '').strip()
    posted = request.args.get('posted', '').strip()
    sort = request.args.get('sort', '').strip()
    show_all = request.args.get('show_all')
    conn = get_db()
    with conn.cursor() as cursor:
        # Fetch filter options
        cursor.execute("SELECT DISTINCT company FROM jobs WHERE company IS NOT NULL AND company != '' ORDER BY company ASC")
        company_options = [row['company'] for row in cursor.fetchall()]
        cursor.execute("SELECT DISTINCT location FROM jobs WHERE location IS NOT NULL AND location != '' ORDER BY location ASC")
        location_options = [row['location'] for row in cursor.fetchall()]
        cursor.execute("SELECT DISTINCT job_type FROM jobs WHERE job_type IS NOT NULL AND job_type != '' ORDER BY job_type ASC")
        job_type_options = [row['job_type'] for row in cursor.fetchall()]
        # Get recommended career IDs based on user's interest area
        cursor.execute('SELECT id FROM resumes WHERE user_id = %s ORDER BY id DESC LIMIT 1', (user_id,))
        resume_row = cursor.fetchone()
        selected_resume_id = resume_row['id'] if resume_row else None
        interest_area = None
        if selected_resume_id:
            cursor.execute('SELECT interest_area FROM interests WHERE user_id = %s AND resume_id = %s ORDER BY id DESC LIMIT 1', (user_id, selected_resume_id))
            interest_row = cursor.fetchone()
            if interest_row:
                interest_area = interest_row['interest_area']
        recommended_career_ids = []
        if interest_area:
            cursor.execute('SELECT id FROM careers WHERE category = %s', (interest_area,))
            recommended_career_ids = [row['id'] for row in cursor.fetchall()]
        # DEBUG: Show interest_area and recommended_career_ids
        flash(f"Interest area: {interest_area}, Recommended career IDs: {recommended_career_ids}", "info")
        jobs = []
        saved = set()
        if recommended_career_ids and not show_all:
            # Build dynamic SQL with correct IN clause
            placeholders = ','.join(['%s'] * len(recommended_career_ids))
            sql = f'SELECT * FROM jobs WHERE career_id IN ({placeholders})'
            params = recommended_career_ids[:]
            if search:
                sql += ' AND (title LIKE %s OR company LIKE %s OR location LIKE %s)'
                params += [f'%{search}%', f'%{search}%', f'%{search}%']
            if company:
                sql += ' AND company LIKE %s'
                params.append(f'%{company}%')
            if location:
                sql += ' AND location LIKE %s'
                params.append(f'%{location}%')
            if job_type:
                sql += ' AND job_type = %s'
                params.append(job_type)
            if salary_min:
                sql += ' AND salary >= %s'
                params.append(salary_min)
            if salary_max:
                sql += ' AND salary <= %s'
                params.append(salary_max)
            if posted:
                sql += " AND posted_at >= NOW() - INTERVAL '1 day' * %s"
                params.append(posted)
            # Sorting
            if sort == 'newest':
                sql += ' ORDER BY posted_at DESC'
            elif sort == 'company':
                sql += ' ORDER BY company ASC'
            else:
                sql += ' ORDER BY posted_at DESC'
            cursor.execute(sql, tuple(params))
            jobs = cursor.fetchall()
            cursor.execute('SELECT job_id FROM saved_jobs WHERE user_id = %s', (user_id,))
            saved = {row['job_id'] for row in cursor.fetchall()}
        else:
            # Show all jobs if no recommended careers (fallback) or show_all is set
            sql = 'SELECT * FROM jobs WHERE 1=1'
            params = []
            if search:
                sql += ' AND (title LIKE %s OR company LIKE %s OR location LIKE %s)'
                params += [f'%{search}%', f'%{search}%', f'%{search}%']
            if company:
                sql += ' AND company LIKE %s'
                params.append(f'%{company}%')
            if location:
                sql += ' AND location LIKE %s'
                params.append(f'%{location}%')
            if job_type:
                sql += ' AND job_type = %s'
                params.append(job_type)
            if salary_min:
                sql += ' AND salary >= %s'
                params.append(salary_min)
            if salary_max:
                sql += ' AND salary <= %s'
                params.append(salary_max)
            if posted:
                sql += " AND posted_at >= NOW() - INTERVAL '1 day' * %s"
                params.append(posted)
            # Sorting
            if sort == 'newest':
                sql += ' ORDER BY posted_at DESC'
            elif sort == 'company':
                sql += ' ORDER BY company ASC'
            else:
                sql += ' ORDER BY posted_at DESC'
            cursor.execute(sql, tuple(params))
            jobs = cursor.fetchall()
            cursor.execute('SELECT job_id FROM saved_jobs WHERE user_id = %s', (user_id,))
            saved = {row['job_id'] for row in cursor.fetchall()}
    conn.close()
    return render_template('jobs.html', jobs=jobs, saved=saved, search=search, recommended=(len(jobs) > 0 and not show_all and bool(recommended_career_ids)),
                           company_options=company_options, location_options=location_options, job_type_options=job_type_options)

@app.route('/save_job/<int:job_id>', methods=['POST'])
def save_job(job_id):
    if 'user_id' not in session:
        return redirect('/login')
    conn = get_db()
    with conn.cursor() as cursor:
        cursor.execute('INSERT INTO saved_jobs (user_id, job_id) VALUES (%s, %s) ON CONFLICT DO NOTHING', (session['user_id'], job_id))
    conn.commit()
    conn.close()
    return redirect(request.referrer or url_for('jobs'))

@app.route('/unsave_job/<int:job_id>', methods=['POST'])
def unsave_job(job_id):
    if 'user_id' not in session:
        return redirect('/login')
    conn = get_db()
    with conn.cursor() as cursor:
        cursor.execute('DELETE FROM saved_jobs WHERE user_id = %s AND job_id = %s', (session['user_id'], job_id))
    conn.commit()
    conn.close()
    return redirect(request.referrer or url_for('jobs'))

@app.route('/my_jobs')
def my_jobs():
    if 'user_id' not in session:
        return redirect('/login')
    conn = get_db()
    with conn.cursor() as cursor:
        cursor.execute('''
            SELECT j.*, sj.id as saved_id, ja.status, ja.notes, ja.applied_at
            FROM saved_jobs sj
            JOIN jobs j ON sj.job_id = j.id
            LEFT JOIN job_applications ja ON ja.user_id = sj.user_id AND ja.job_id = sj.job_id
            WHERE sj.user_id = %s
            ORDER BY j.posted_at DESC
        ''', (session['user_id'],))
        jobs = cursor.fetchall()
    conn.close()
    return render_template('my_jobs.html', jobs=jobs)

@app.route('/apply_job/<int:job_id>', methods=['POST'])
def apply_job(job_id):
    if 'user_id' not in session:
        return redirect('/login')
    status = request.form.get('status', 'Applied')
    notes = request.form.get('notes', '')
    conn = get_db()
    with conn.cursor() as cursor:
        cursor.execute('SELECT * FROM job_applications WHERE user_id = %s AND job_id = %s', (session['user_id'], job_id))
        if cursor.fetchone():
            cursor.execute('UPDATE job_applications SET status = %s, notes = %s WHERE user_id = %s AND job_id = %s', (status, notes, session['user_id'], job_id))
        else:
            cursor.execute('INSERT INTO job_applications (user_id, job_id, status, notes) VALUES (%s, %s, %s, %s)', (session['user_id'], job_id, status, notes))
    conn.commit()
    conn.close()
    return redirect(url_for('my_jobs'))

from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

@app.route('/resume_builder', methods=['GET', 'POST'])
@login_required
def resume_builder():
    if request.method == 'POST':
        title = request.form['title']
        summary = request.form['summary']
        education = request.form['education']
        experience = request.form['experience']
        skills = request.form['skills']
        projects = request.form['projects']
        certifications = request.form['certifications']
        contact_info = request.form['contact_info']
        if not title or not summary or not education or not experience or not skills or not contact_info:
            flash('Please fill all required fields.', 'danger')
            return redirect(url_for('resume_builder'))
        conn = get_db()
        try:
            with conn.cursor() as cursor:
                cursor.execute('INSERT INTO resumes_builder (user_id, title, summary, education, experience, skills, projects, certifications, contact_info) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)',
                    (session['user_id'], title, summary, education, experience, skills, projects, certifications, contact_info))
            conn.commit()
        finally:
            conn.close()
        flash('Resume created successfully!', 'success')
        return redirect(url_for('my_resumes'))
    return render_template('resume_builder.html')

@app.route('/my_resumes')
def my_resumes():
    if 'id' not in session:
        return redirect('/login')
    user_id = session['user_id']
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM resumes_builder WHERE user_id=%s", (user_id,))
            resumes = cursor.fetchall()
    finally:
        conn.close()
    return render_template('my_resumes.html', resumes=resumes)

@app.route('/edit_resume_builder/<int:resume_id>', methods=['GET', 'POST'])
@login_required
def edit_resume_builder(resume_id):
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute('SELECT * FROM resumes_builder WHERE id=%s AND user_id=%s', (resume_id, session['user_id']))
            resume = cursor.fetchone()
            if not resume:
                flash('Resume not found.', 'danger')
                return redirect(url_for('my_resumes'))
            if request.method == 'POST':
                title = request.form['title']
                summary = request.form['summary']
                education = request.form['education']
                experience = request.form['experience']
                skills = request.form['skills']
                projects = request.form['projects']
                certifications = request.form['certifications']
                contact_info = request.form['contact_info']
                if not title or not summary or not education or not experience or not skills or not contact_info:
                    flash('Please fill all required fields.', 'danger')
                    return redirect(url_for('edit_resume_builder', resume_id=resume_id))
                cursor.execute('UPDATE resumes_builder SET title=%s, summary=%s, education=%s, experience=%s, skills=%s, projects=%s, certifications=%s, contact_info=%s WHERE id=%s AND user_id=%s',
                    (title, summary, education, experience, skills, projects, certifications, contact_info, resume_id, session['user_id']))
                conn.commit()
                flash('Resume updated successfully!', 'success')
                return redirect(url_for('my_resumes'))
    finally:
        conn.close()
    return render_template('resume_builder.html', resume=resume)

@app.route('/delete_resume_builder/<int:resume_id>', methods=['POST'])
@login_required
def delete_resume_builder(resume_id):
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute('DELETE FROM resumes_builder WHERE id=%s AND user_id=%s', (resume_id, session['user_id']))
        conn.commit()
    finally:
        conn.close()
    flash('Resume deleted.', 'info')
    return redirect(url_for('my_resumes'))

@app.route('/download_resume_builder/<int:resume_id>')
@login_required
def download_resume_builder(resume_id):
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute('SELECT * FROM resumes_builder WHERE id=%s AND user_id=%s', (resume_id, session['user_id']))
            resume = cursor.fetchone()
            if not resume:
                flash('Resume not found.', 'danger')
                return redirect(url_for('my_resumes'))
    finally:
        conn.close()
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    y = height - 50
    min_y = 60
    font_main = 11
    font_header = 13
    font_title = 18
    line_gap = 14
    section_gap = 8
    # Title
    p.setFont('Helvetica-Bold', font_title)
    p.drawString(50, y, resume['title'])
    y -= 30
    # Draw a line under the title
    p.setLineWidth(1)
    p.line(50, y, width - 50, y)
    y -= 20
    # Sections
    def draw_section(header, content):
        nonlocal y
        p.setFont('Helvetica-Bold', font_header)
        if y < min_y:
            p.showPage()
            y = height - 50
            p.setFont('Helvetica-Bold', font_header)
        p.drawString(50, y, header)
        y -= 18
        p.setFont('Helvetica', font_main)
        for line in (content or '').replace('\r', '').split('\n'):
            line = line.strip()
            if line:
                if y < min_y:
                    p.showPage()
                    y = height - 50
                    p.setFont('Helvetica', font_main)
                p.drawString(60, y, line)
                y -= line_gap
        y -= section_gap
        # Draw a line after each section
        if y > min_y:
            p.setLineWidth(0.5)
            p.line(50, y, width - 50, y)
            y -= 16
        else:
            p.showPage()
            y = height - 50
    draw_section("Summary:", resume['summary'])
    draw_section("Education:", resume['education'])
    draw_section("Experience:", resume['experience'])
    draw_section("Skills:", resume['skills'])
    draw_section("Projects:", resume['projects'])
    draw_section("Certifications:", resume['certifications'])
    draw_section("Contact Info:", resume['contact_info'])
    p.showPage()
    p.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=f"{resume['title']}.pdf", mimetype='application/pdf')

# ------------------- Peer Groups Backend -------------------
@app.route('/peer_groups')
def peer_groups():
    if 'user_id' not in session:
        return redirect('/login')
    user_id = session['user_id']
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute('SELECT * FROM peer_groups')
            groups = cursor.fetchall()
            cursor.execute('SELECT group_id FROM group_members WHERE user_id = %s', (user_id,))
            user_groups = [row['group_id'] for row in cursor.fetchall()]
    finally:
        conn.close()
    return render_template('peer_groups.html', groups=groups, user_groups=user_groups)

@app.route('/create_group', methods=['GET', 'POST'])
def create_group():
    if 'user_id' not in session:
        return redirect('/login')
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        image = None
        if 'image' in request.files and request.files['image'].filename:
            file = request.files['image']
            if allowed_image(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image = filename
        conn = get_db()
        try:
            with conn.cursor() as cursor:
                cursor.execute('INSERT INTO peer_groups (name, description, image, created_by) VALUES (%s, %s, %s, %s)', (name, description, image, session['user_id']))
                conn.commit()
            flash('Group created successfully!', 'success')
            return redirect(url_for('peer_groups'))
        finally:
            conn.close()
    return render_template('create_group.html')

@app.route('/join_group/<int:group_id>', methods=['POST'])
def join_group(group_id):
    if 'user_id' not in session:
        return redirect('/login')
    user_id = session['user_id']
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute('SELECT * FROM group_members WHERE group_id = %s AND user_id = %s', (group_id, user_id))
            if not cursor.fetchone():
                cursor.execute('INSERT INTO group_members (group_id, user_id) VALUES (%s, %s)', (group_id, user_id))
                conn.commit()
                flash('Joined group!', 'success')
            else:
                flash('Already a member of this group.', 'info')
    finally:
        conn.close()
    return redirect(url_for('peer_groups'))

@app.route('/leave_group/<int:group_id>', methods=['POST'])
def leave_group(group_id):
    if 'user_id' not in session:
        return redirect('/login')
    user_id = session['user_id']
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute('DELETE FROM group_members WHERE group_id = %s AND user_id = %s', (group_id, user_id))
            conn.commit()
            flash('Left group.', 'info')
    finally:
        conn.close()
    return redirect(url_for('peer_groups'))

@app.route('/group/<int:group_id>')
def group_detail(group_id):
    if 'user_id' not in session:
        return redirect('/login')
    user_id = session['user_id']
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute('SELECT * FROM peer_groups WHERE id = %s', (group_id,))
            group = cursor.fetchone()
            if not group:
                flash('Group not found.', 'danger')
                return redirect(url_for('peer_groups'))
            cursor.execute('SELECT u.id, u.name, u.profile_pic FROM group_members gm JOIN users u ON gm.user_id = u.id WHERE gm.group_id = %s', (group_id,))
            members = cursor.fetchall()
            cursor.execute('SELECT * FROM group_members WHERE group_id = %s AND user_id = %s', (group_id, user_id))
            is_member = cursor.fetchone() is not None
    finally:
        conn.close()
    return render_template('group_detail.html', group=group, members=members, is_member=is_member)
# ------------------- End Peer Groups Backend -------------------

@app.route('/job/<int:job_id>')
def job_detail(job_id):
    if 'user_id' not in session:
        return redirect('/login')
    user_id = session['user_id']
    conn = get_db()
    with conn.cursor() as cursor:
        cursor.execute('SELECT * FROM jobs WHERE id = %s', (job_id,))
        job = cursor.fetchone()
        if not job:
            flash('Job not found.', 'danger')
            return redirect(url_for('jobs'))
        cursor.execute('SELECT 1 FROM saved_jobs WHERE user_id = %s AND job_id = %s', (user_id, job_id))
        is_saved = cursor.fetchone() is not None
        cursor.execute('SELECT status, notes, applied_at FROM job_applications WHERE user_id = %s AND job_id = %s', (user_id, job_id))
        app_row = cursor.fetchone() or {}
        status = app_row.get('status')
        notes = app_row.get('notes')
        applied_at = app_row.get('applied_at')
    # Salary insight for this job title/location
    avg_salary = get_average_salary(job['title'], job['location'])
    conn.close()
    return render_template('job_detail.html', job=job, is_saved=is_saved, status=status, notes=notes, applied_at=applied_at, avg_salary=avg_salary)

@app.route('/job_alerts', methods=['GET', 'POST'])
def job_alerts():
    if 'user_id' not in session:
        return redirect('/login')
    user_id = session['user_id']
    conn = get_db()
    if request.method == 'POST':
        keyword = request.form.get('keyword', '').strip()
        company = request.form.get('company', '').strip()
        location = request.form.get('location', '').strip()
        if not keyword and not company and not location:
            flash('Please enter at least one field for the alert.', 'warning')
        else:
            with conn.cursor() as cursor:
                cursor.execute('INSERT INTO job_alerts (user_id, keyword, company, location) VALUES (%s, %s, %s, %s)', (user_id, keyword, company, location))
            conn.commit()
            flash('Job alert added!', 'success')
    with conn.cursor() as cursor:
        cursor.execute('SELECT * FROM job_alerts WHERE user_id = %s ORDER BY created_at DESC', (user_id,))
        alerts = cursor.fetchall()
        # Fetch suggested jobs for each alert
        suggested_jobs_by_alert = {}
        for alert in alerts:
            sql = 'SELECT * FROM jobs WHERE 1=1'
            params = []
            if alert['keyword']:
                sql += ' AND title LIKE %s'
                params.append(f'%{alert["keyword"]}%')
            if alert['company']:
                sql += ' AND company LIKE %s'
                params.append(f'%{alert["company"]}%')
            if alert['location']:
                sql += ' AND location LIKE %s'
                params.append(f'%{alert["location"]}%')
            sql += ' ORDER BY posted_at DESC LIMIT 5'
            cursor.execute(sql, tuple(params))
            jobs = cursor.fetchall()
            suggested_jobs_by_alert[alert['id']] = {'alert': alert, 'jobs': jobs}
    conn.close()
    return render_template('job_alerts.html', alerts=alerts, suggested_jobs_by_alert=suggested_jobs_by_alert)

@app.route('/delete_job_alert/<int:alert_id>', methods=['POST'])
def delete_job_alert(alert_id):
    if 'user_id' not in session:
        return redirect('/login')
    user_id = session['user_id']
    conn = get_db()
    with conn.cursor() as cursor:
        cursor.execute('DELETE FROM job_alerts WHERE id = %s AND user_id = %s', (alert_id, user_id))
    conn.commit()
    conn.close()
    flash('Job alert deleted.', 'info')
    return redirect(url_for('job_alerts'))

@app.route('/autocomplete_job_titles')
def autocomplete_job_titles():
    if 'user_id' not in session:
        return jsonify([])
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify([])
    conn = get_db()
    with conn.cursor() as cursor:
        cursor.execute('SELECT DISTINCT title FROM jobs WHERE title LIKE %s ORDER BY title LIMIT 10', (f'%{q}%',))
        titles = [row['title'] for row in cursor.fetchall()]
    conn.close()
    return jsonify(titles)

@app.route('/autocomplete_companies')
def autocomplete_companies():
    if 'user_id' not in session:
        return jsonify([])
    q = request.args.get('q', '').strip()
    conn = get_db()
    with conn.cursor() as cursor:
        if q:
            cursor.execute('SELECT DISTINCT company FROM jobs WHERE company LIKE %s ORDER BY company LIMIT 10', (f'%{q}%',))
        else:
            cursor.execute('SELECT DISTINCT company FROM jobs ORDER BY company LIMIT 10')
        companies = [row['company'] for row in cursor.fetchall()]
    conn.close()
    return jsonify(companies)

@app.route('/autocomplete_locations')
def autocomplete_locations():
    if 'user_id' not in session:
        return jsonify([])
    q = request.args.get('q', '').strip()
    conn = get_db()
    with conn.cursor() as cursor:
        if q:
            cursor.execute('SELECT DISTINCT location FROM jobs WHERE location LIKE %s ORDER BY location LIMIT 10', (f'%{q}%',))
        else:
            cursor.execute('SELECT DISTINCT location FROM jobs ORDER BY location LIMIT 10')
        locations = [row['location'] for row in cursor.fetchall()]
    conn.close()
    return jsonify(locations)

# Static interview questions and tips for demonstration
INTERVIEW_QUESTIONS = {
    'Software Developer': {
        'qa': [
            {'q': 'Explain the difference between object-oriented and functional programming.', 'a': 'Object-oriented programming (OOP) is based on objects and classes, focusing on encapsulation, inheritance, and polymorphism. Functional programming treats computation as the evaluation of mathematical functions and avoids changing state and mutable data.'},
            {'q': 'What is a REST API? How would you design one?', 'a': 'A REST API is an application programming interface that uses HTTP requests to access and use data. It is stateless and uses standard HTTP methods. To design one, define resources, use proper HTTP verbs, and ensure statelessness and proper error handling.'},
            {'q': 'Describe a challenging bug you fixed.', 'a': 'Describe a real example, the debugging process, tools used, and how you identified and fixed the root cause.'},
            {'q': 'How do you ensure code quality and maintainability?', 'a': 'By following coding standards, writing unit tests, conducting code reviews, and using static analysis tools.'},
            {'q': 'What are your favorite programming languages and why?', 'a': 'Mention languages you are comfortable with and explain their strengths and your experience.'},
            {'q': 'How do you approach debugging a complex issue?', 'a': 'Break down the problem, use logging, debuggers, and isolate the issue step by step.'},
            {'q': 'What is the difference between synchronous and asynchronous programming?', 'a': 'Synchronous programming executes tasks sequentially, while asynchronous programming allows tasks to run independently, improving efficiency.'},
            {'q': 'Explain SOLID principles.', 'a': 'SOLID stands for five design principles: Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, and Dependency Inversion.'},
            {'q': 'How do you manage version control in your projects?', 'a': 'By using Git, following branching strategies, and writing clear commit messages.'},
            {'q': 'Describe your experience with unit testing and test-driven development.', 'a': 'Explain your approach to writing tests before code, using frameworks like pytest or unittest, and the benefits of TDD.'},
            {'q': 'What is dependency injection?', 'a': 'A design pattern where dependencies are provided to a class rather than hardcoded, improving flexibility and testability.'},
            {'q': 'How do you optimize code for performance?', 'a': 'By profiling code, identifying bottlenecks, optimizing algorithms, and reducing resource usage.'},
            {'q': 'Describe a time you worked in a team to deliver a software project.', 'a': 'Share a specific example, your role, collaboration, and the outcome.'},
            {'q': 'What is continuous integration and continuous deployment (CI/CD)?', 'a': 'CI/CD automates code integration, testing, and deployment, ensuring faster and more reliable releases.'},
            {'q': 'How do you stay updated with new technologies?', 'a': 'By following tech blogs, attending conferences, and participating in online courses and communities.'}
        ],
        'tips': [
            'Practice coding problems on LeetCode, HackerRank, or CodeSignal.',
            'Be ready to discuss your past projects in detail, including challenges and solutions.',
            'Brush up on data structures, algorithms, and system design.',
            'Prepare to explain your design decisions clearly and concisely.',
            'Review version control workflows (e.g., Git branching strategies).',
            'Understand the basics of DevOps and CI/CD pipelines.',
            'Be familiar with common design patterns and their use cases.',
            'Practice whiteboard coding and verbalizing your thought process.',
            'Prepare questions to ask the interviewer about team practices and code reviews.',
            'Show enthusiasm for learning and adapting to new technologies.'
        ]
    },
    'Data Analyst': {
        'qa': [
            {'q': 'How do you handle missing data in a dataset?', 'a': 'Describe a real example, the process of identifying missing data, and how you handled it.'},
            {'q': 'Explain the difference between supervised and unsupervised learning.', 'a': 'Supervised learning involves predicting a target variable based on input features, while unsupervised learning involves finding patterns in data without explicit labels.'},
            {'q': 'What visualization tools have you used?', 'a': 'Mention tools you are familiar with, such as matplotlib, seaborn, Tableau, Power BI, or others.'},
            {'q': 'Describe a project where you derived insights from data.', 'a': 'Share a specific example, the dataset, the analysis process, key findings, and the impact of the insights.'},
            {'q': 'How do you validate your analysis results?', 'a': 'Explain your approach to data validation, including checks for data quality, consistency, and accuracy.'},
            {'q': 'What is the difference between a left join and an inner join?', 'a': 'A left join returns all rows from the left table, plus matching rows from the right table. An inner join returns only the matching rows from both tables.'},
            {'q': 'How do you deal with outliers in your data?', 'a': 'Describe a real example, the process of identifying outliers, and how you handled them.'},
            {'q': 'Explain the concept of p-value and statistical significance.', 'a': 'P-value is a measure of the probability of observing a test statistic as extreme as, or more extreme than, the one observed if the null hypothesis is true. Statistical significance is determined by comparing p-values to a threshold (e.g., 0.05).'},
            {'q': 'How do you automate data cleaning processes?', 'a': 'Explain your process for data cleaning, including steps like data profiling, data profiling, and data validation.'},
            {'q': 'Describe your experience with SQL and writing complex queries.', 'a': 'Share examples of complex queries you have written, the challenges you faced, and how you solved them.'},
            {'q': 'What is data normalization and why is it important?', 'a': 'Data normalization is the process of organizing data to reduce redundancy and improve consistency. It is important for data consistency, query performance, and ease of maintenance.'},
            {'q': 'How do you present your findings to non-technical stakeholders?', 'a': 'Explain your approach to presenting data analysis results to non-technical audiences, including visualizations, storytelling, and clear communication.'},
            {'q': 'What is the difference between correlation and causation?', 'a': 'Correlation is a statistical measure that shows the degree to which two variables are related. Causation implies a causal relationship between variables.'},
            {'q': 'How do you handle large datasets that do not fit in memory?', 'a': 'Describe a real example, the process of handling large datasets, and tools or techniques you used to manage them.'},
            {'q': 'Describe a time you used data to influence business decisions.', 'a': 'Share a specific example, the situation, the data analysis process, key findings, and the impact of the insights on business decisions.'}
        ],
        'tips': [
            'Review SQL, Excel, and data visualization basics.',
            'Practice explaining your analysis process and results clearly.',
            'Know how to use visualization libraries like matplotlib, seaborn, or Tableau.',
            'Be prepared to discuss data cleaning, feature engineering, and model evaluation.',
            'Understand basic statistics and hypothesis testing.',
            'Show your ability to communicate insights to both technical and non-technical audiences.',
            'Prepare to discuss real-world projects and the impact of your analysis.',
            'Be familiar with Python or R for data analysis.',
            'Demonstrate curiosity and a problem-solving mindset.'
        ]
    },
    'UI/UX Designer': {
        'qa': [
            {'q': 'How do you approach user research?', 'a': 'Explain your process for user research, including methods like surveys, interviews, usability testing, and competitive analysis.'},
            {'q': 'Describe your design process for a new product.', 'a': 'Explain your design process, including research, ideation, prototyping, testing, and iteration.'},
            {'q': 'What tools do you use for prototyping?', 'a': 'Mention tools you are familiar with, such as Figma, Sketch, Adobe XD, Axure RP, or others.'},
            {'q': 'How do you handle feedback and iteration?', 'a': 'Explain your process for incorporating user feedback, including steps like summarizing feedback, prioritizing changes, and iterating on designs.'},
            {'q': 'Show us a portfolio piece you are proud of.', 'a': 'Share a specific example, the project, your role, the design process, and the outcome.'},
            {'q': 'How do you ensure accessibility in your designs?', 'a': 'Explain your approach to designing for accessibility, including considerations like color contrast, keyboard navigation, and screen reader compatibility.'},
            {'q': 'Describe a time you worked with developers to implement a design.', 'a': 'Share a specific example, the project, your role, the design process, and the outcome.'},
            {'q': 'What is your process for creating user personas?', 'a': 'Explain your process for creating user personas, including research, empathy mapping, and scenario-based design.'},
            {'q': 'How do you conduct usability testing?', 'a': 'Explain your process for usability testing, including recruitment, setup, tasks, and analysis.'},
            {'q': 'What are the key differences between UI and UX?', 'a': 'UI focuses on the visual and interactive elements of a product, while UX focuses on the overall user experience.'},
            {'q': 'How do you stay updated with design trends?', 'a': 'Explain your approach to staying updated with design trends, including following design blogs, attending conferences, and experimenting with new tools and techniques.'},
            {'q': 'Describe a challenging design problem you solved.', 'a': 'Share a specific example, the problem, your approach, the solution, and the results.'},
            {'q': 'How do you balance user needs with business goals?', 'a': 'Explain your approach to balancing user needs and business goals, including understanding user pain points, prioritizing features, and aligning design with business objectives.'},
            {'q': 'What is your experience with design systems?', 'a': 'Explain your experience with design systems, including the tools and processes you use, and how they help maintain consistency across products.'},
            {'q': 'How do you prioritize features in a design project?', 'a': 'Explain your approach to prioritizing features, including considering user needs, business objectives, and technical constraints.'}
        ],
        'tips': [
            'Prepare a strong, visually appealing portfolio.',
            'Be ready to walk through your design thinking and process.',
            'Practice explaining your design choices and rationale.',
            'Show familiarity with accessibility standards (WCAG).',
            'Demonstrate collaboration with cross-functional teams.',
            'Be prepared to discuss feedback and how you iterate on designs.',
            'Stay updated with the latest design tools and trends.',
            'Show empathy for users and understanding of their needs.',
            'Be ready to present wireframes, prototypes, and user flows.'
        ]
    },
    'Project Manager': {
        'qa': [
            {'q': 'How do you prioritize tasks in a project?', 'a': 'Explain your approach to prioritizing tasks, including considering project goals, stakeholder needs, and resource availability.'},
            {'q': 'Describe a time you managed a difficult stakeholder.', 'a': 'Share a specific example, the situation, the stakeholder, and how you managed the conflict.'},
            {'q': 'What project management tools do you use?', 'a': 'Mention tools you are familiar with, such as Jira, Trello, Asana, or others.'},
            {'q': 'How do you handle project risks?', 'a': 'Explain your approach to risk management, including identifying potential risks, assessing likelihood and impact, and developing mitigation strategies.'},
            {'q': 'Explain your experience with Agile or Scrum.', 'a': 'Explain your experience with Agile or Scrum, including the roles you played, the team structure, and the benefits of the methodology.'},
            {'q': 'How do you manage project scope changes?', 'a': 'Explain your approach to managing scope changes, including steps like scope creep identification, stakeholder communication, and change management.'},
            {'q': 'Describe your process for resource allocation.', 'a': 'Explain your process for resource allocation, including steps like workload analysis, skill matching, and scheduling.'},
            {'q': 'How do you track project progress and milestones?', 'a': 'Explain your process for tracking project progress and milestones, including the tools and techniques you use, such as Gantt charts, Kanban boards, or project management software.'},
            {'q': 'What is your approach to conflict resolution within a team?', 'a': 'Explain your approach to conflict resolution, including steps like identifying the issue, gathering input, brainstorming solutions, and reaching a consensus.'},
            {'q': 'How do you ensure project deliverables meet quality standards?', 'a': 'Explain your approach to quality assurance, including steps like setting standards, conducting reviews, and implementing feedback mechanisms.'},
            {'q': 'Describe a project that failed and what you learned.', 'a': 'Share a specific example, the project, the failure, the lessons learned, and how you implemented changes.'},
            {'q': 'How do you communicate with remote or distributed teams?', 'a': 'Explain your approach to remote communication, including tools like Slack, Zoom, and project management software.'},
            {'q': 'What is your experience with budgeting and cost management?', 'a': 'Explain your experience with budgeting and cost management, including the tools and processes you use, such as project management software, spreadsheets, or budgeting frameworks.'},
            {'q': 'How do you motivate your team during challenging times?', 'a': 'Explain your approach to motivating your team during challenging times, including steps like recognizing achievements, providing support, and adjusting workload.'},
            {'q': 'What metrics do you use to measure project success?', 'a': 'Explain the key performance indicators (KPIs) you use to measure project success, including project completion rate, stakeholder satisfaction, and budget utilization.'}
        ],
        'tips': [
            'Review common project management methodologies (Agile, Waterfall, Scrum).',
            'Prepare examples of leadership, conflict resolution, and stakeholder management.',
            'Know how to use tools like Jira, Trello, or MS Project.',
            'Be ready to discuss risk management and mitigation strategies.',
            'Show your ability to adapt to changing project requirements.',
            'Demonstrate clear communication and team motivation skills.',
            'Prepare to discuss project failures and lessons learned.',
            'Understand budgeting, resource allocation, and project metrics.'
        ]
    },
    'Support Engineer': {
        'qa': [
            {'q': 'How do you handle a frustrated customer?', 'a': 'Explain your approach to handling frustrated customers, including steps like active listening, empathy, and problem-solving.'},
            {'q': 'Describe your troubleshooting process.', 'a': 'Explain your process for troubleshooting, including steps like isolating the issue, diagnosing the problem, and implementing a solution.'},
            {'q': 'What ticketing systems have you used?', 'a': 'Mention systems you are familiar with, such as Freshdesk, Zendesk, Jira, or others.'},
            {'q': 'How do you document solutions?', 'a': 'Explain your process for documenting solutions, including steps like summarizing the issue, providing a solution, and following up to ensure satisfaction.'},
            {'q': 'Give an example of a time you solved a difficult issue.', 'a': 'Share a specific example, the issue, the approach, and the outcome.'},
            {'q': 'How do you prioritize support tickets?', 'a': 'Explain your approach to prioritizing support tickets, including the tools and processes you use, such as ticket management software or spreadsheets.'},
            {'q': 'Describe a time you worked with engineering to resolve a bug.', 'a': 'Share a specific example, the bug, the approach, and the outcome.'},
            {'q': 'What is your experience with remote support?', 'a': 'Explain your experience with remote support, including tools like TeamViewer, Zoom, or remote access software.'},
            {'q': 'How do you stay updated with product changes?', 'a': 'Explain your process for staying updated with product changes, including subscribing to release notes, attending webinars, or using product update notifications.'},
            {'q': 'What is your process for onboarding new users?', 'a': 'Explain your process for onboarding new users, including steps like providing training, setting up access, and creating documentation.'},
            {'q': 'How do you measure customer satisfaction?', 'a': 'Explain your approach to measuring customer satisfaction, including the tools and processes you use, such as surveys, Net Promoter Score (NPS), or customer feedback software.'},
            {'q': 'Describe a time you went above and beyond for a customer.', 'a': 'Share a specific example, the situation, the action, and the outcome.'},
            {'q': 'How do you handle multiple high-priority issues at once?', 'a': 'Explain your approach to handling multiple high-priority issues, including prioritization, delegation, and time management.'},
            {'q': 'What is your experience with knowledge base management?', 'a': 'Explain your experience with knowledge base management, including the tools and processes you use, such as internal wikis, knowledge databases, or customer support software.'},
            {'q': 'How do you ensure clear communication with non-technical users?', 'a': 'Explain your approach to communicating with non-technical users, including using technical language, breaking down complex concepts, and providing clear instructions.'}
        ],
        'tips': [
            'Practice clear and empathetic communication.',
            'Be ready to discuss technical troubleshooting steps and tools.',
            'Show your ability to document and share solutions effectively.',
            'Demonstrate prioritization and time management skills.',
            'Prepare examples of customer satisfaction and positive feedback.',
            'Be familiar with common ticketing and remote support tools.',
            'Show your willingness to learn and adapt to new products.'
        ]
    },
    'Cloud Engineer': {
        'qa': [
            {'q': 'What cloud platforms have you worked with?', 'a': 'Mention platforms you are familiar with, such as AWS, Azure, Google Cloud Platform (GCP), or others.'},
            {'q': 'How do you ensure security in cloud deployments?', 'a': 'Explain your approach to cloud security, including the use of encryption, access controls, and monitoring tools.'},
            {'q': 'Describe a time you automated a deployment.', 'a': 'Share a specific example, the deployment process, the automation tool, and the outcome.'},
            {'q': 'What is IaC (Infrastructure as Code)?', 'a': 'Infrastructure as Code (IaC) is the practice of managing infrastructure through code, allowing for repeatable deployments and infrastructure as a service (IaaS).'},
            {'q': 'How do you monitor cloud resources?', 'a': 'Explain your process for monitoring cloud resources, including the tools and dashboards you use, such as AWS CloudWatch, Azure Monitor, or Google Cloud Monitoring.'},
            {'q': 'What is your experience with containerization (Docker, Kubernetes)?', 'a': 'Explain your experience with containerization, including the tools and processes you use, such as Docker, Kubernetes, and container orchestration platforms.'},
            {'q': 'How do you handle cloud cost optimization?', 'a': 'Explain your approach to cloud cost optimization, including the tools and techniques you use, such as cost management dashboards, auto-scaling policies, or reserved instances.'},
            {'q': 'Describe a time you migrated an application to the cloud.', 'a': 'Share a specific example, the application, the migration process, the cloud provider, and the outcome.'},
            {'q': 'What is your approach to disaster recovery and backups?', 'a': 'Explain your approach to disaster recovery and backups, including the tools and processes you use, such as multi-region deployments, automated backups, and disaster recovery plans.'},
            {'q': 'How do you manage secrets and credentials in the cloud?', 'a': 'Explain your approach to managing secrets and credentials in the cloud, including the use of secrets managers, environment variables, and least privilege access.'},
            {'q': 'What is your experience with serverless architectures?', 'a': 'Explain your experience with serverless architectures, including the tools and processes you use, such as AWS Lambda, Azure Functions, or Google Cloud Functions.'},
            {'q': 'How do you troubleshoot performance issues in the cloud?', 'a': 'Explain your approach to troubleshooting performance issues in the cloud, including the tools and techniques you use, such as performance monitoring dashboards, auto-scaling policies, or serverless monitoring tools.'},
            {'q': 'What is your process for scaling applications?', 'a': 'Explain your process for scaling applications, including the tools and techniques you use, such as auto-scaling groups, load balancers, or container orchestration platforms.'},
            {'q': 'How do you stay updated with cloud technology trends?', 'a': 'Explain your approach to staying updated with cloud technology trends, including following cloud blogs, attending conferences, and participating in online communities and forums.'},
            {'q': 'Describe a challenging cloud project you delivered.', 'a': 'Share a specific example, the project, the challenges, the solution, and the results.'}
        ],
        'tips': [
            'Review basics of AWS, Azure, or GCP and their core services.',
            'Be ready to discuss automation, scripting, and DevOps practices.',
            'Understand cloud security best practices and compliance.',
            'Show experience with containerization and orchestration tools.',
            'Prepare to discuss cost management and optimization strategies.',
            'Demonstrate troubleshooting and performance tuning skills.',
            'Stay updated with the latest cloud trends and certifications.'
        ]
    },
    'Junior Data Analyst': {
        'qa': [
            {'q': 'How do you handle missing data in a dataset?', 'a': 'I identify missing data patterns and choose appropriate methods like imputation or deletion based on the context.'},
            {'q': 'What is the difference between Excel and SQL?', 'a': 'Excel is great for small datasets and quick analysis, while SQL is better for large datasets and complex queries.'},
            {'q': 'Explain what a pivot table is.', 'a': 'A pivot table summarizes and reorganizes data from a larger dataset to quickly analyze trends and patterns.'},
            {'q': 'How would you explain findings to non-technical stakeholders?', 'a': 'I use simple language, visual charts, and focus on business impact rather than technical details.'},
            {'q': 'What steps ensure data quality?', 'a': 'I check for duplicates, validate data types, look for outliers, and document cleaning steps.'}
        ],
        'tips': [
            'Practice basic SQL queries and Excel functions.',
            'Learn to create clear visualizations.',
            'Understand basic statistics concepts.',
            'Practice explaining technical concepts simply.',
            'Show curiosity about data and business problems.'
        ]
    }
}

@app.route('/interview_prep/<career_title>')
def interview_prep(career_title):
    if 'user_id' not in session:
        return redirect('/login')
    # Normalize title
    title = career_title.replace('-', ' ').title()
    questions = INTERVIEW_QUESTIONS.get(title, {}).get('qa', [])
    tips = INTERVIEW_QUESTIONS.get(title, {}).get('tips', [])
    return render_template('interview_prep.html', career_title=title, questions=questions, tips=tips)

@app.route('/interview_prep/job/<int:job_id>')
def interview_prep_job(job_id):
    if 'user_id' not in session:
        return redirect('/login')
    conn = get_db()
    with conn.cursor() as cursor:
        cursor.execute('SELECT * FROM jobs WHERE id = %s', (job_id,))
        job = cursor.fetchone()
    conn.close()
    if not job:
        flash('Job not found.', 'danger')
        return redirect(url_for('jobs'))
    # Try to match job title to a career for questions
    title = job['title'].title()
    questions = INTERVIEW_QUESTIONS.get(title, {}).get('qa', [])
    tips = INTERVIEW_QUESTIONS.get(title, {}).get('tips', [])
    # If no exact match, provide generic questions
    if not questions:
        questions = [
            {'q': 'Tell me about yourself and your experience.', 'a': 'Provide a brief overview of your background, skills, and what makes you suitable for this role.'},
            {'q': 'Why are you interested in this position?', 'a': 'Show your knowledge of the company and role, and explain how it aligns with your career goals.'},
            {'q': 'What are your strengths and weaknesses?', 'a': 'Be honest about areas for improvement while highlighting your key strengths relevant to the job.'},
            {'q': 'Describe a challenging situation you faced and how you handled it.', 'a': 'Use the STAR method (Situation, Task, Action, Result) to structure your response.'},
            {'q': 'Where do you see yourself in 5 years?', 'a': 'Show ambition and alignment with the company\'s growth opportunities.'}
        ]
        tips = [
            'Research the company and role thoroughly.',
            'Prepare specific examples from your experience.',
            'Practice common interview questions.',
            'Prepare thoughtful questions to ask the interviewer.',
            'Show enthusiasm and genuine interest in the role.'
        ]
    return render_template('interview_prep.html', career_title=title, questions=questions, tips=tips, job=job)

# Helper for salary insights

def get_average_salary(title, location=None):
    conn = get_db()
    with conn.cursor() as cursor:
        if location:
            cursor.execute('SELECT AVG(salary) as avg_salary FROM jobs WHERE title = %s AND location = %s AND salary IS NOT NULL', (title, location))
            row = cursor.fetchone()
            if row and row['avg_salary']:
                conn.close()
                return int(row['avg_salary'])
        cursor.execute('SELECT AVG(salary) as avg_salary FROM jobs WHERE title = %s AND salary IS NOT NULL', (title,))
        row = cursor.fetchone()
    conn.close()
    if row and row['avg_salary']:
        return int(row['avg_salary'])
    return None

@app.route('/admin_jobs', methods=['GET', 'POST'])
def admin_jobs():
    if not session.get('admin_loggedin'):
        return redirect(url_for('admin_login'))
    conn = get_db()
    with conn.cursor() as cursor:
        cursor.execute('SELECT id, title FROM careers ORDER BY title ASC')
        careers = cursor.fetchall()
    if request.method == 'POST':
        # Add new job
        title = request.form.get('title')
        company = request.form.get('company')
        location = request.form.get('location')
        job_type = request.form.get('job_type')
        salary = request.form.get('salary')
        description = request.form.get('description')
        requirements = request.form.get('requirements')
        url = request.form.get('url')
        career_id = request.form.get('career_id')
        with conn.cursor() as cursor:
            cursor.execute('''
                INSERT INTO jobs (title, company, location, job_type, salary, description, requirements, url, career_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (title, company, location, job_type, salary, description, requirements, url, career_id))
        conn.commit()
    with conn.cursor() as cursor:
        cursor.execute('SELECT * FROM jobs ORDER BY posted_at DESC')
        jobs = cursor.fetchall()
    conn.close()
    return render_template('admin_jobs.html', jobs=jobs, careers=careers)

@app.route('/admin_edit_job/<int:job_id>', methods=['POST'])
def admin_edit_job(job_id):
    if not session.get('admin_loggedin'):
        return redirect(url_for('admin_login'))
    title = request.form.get('title')
    company = request.form.get('company')
    location = request.form.get('location')
    job_type = request.form.get('job_type')
    salary = request.form.get('salary')
    description = request.form.get('description')
    requirements = request.form.get('requirements')
    url = request.form.get('url')
    conn = get_db()
    with conn.cursor() as cursor:
        cursor.execute('''
            UPDATE jobs SET title=%s, company=%s, location=%s, job_type=%s, salary=%s, description=%s, requirements=%s, url=%s WHERE id=%s
        ''', (title, company, location, job_type, salary, description, requirements, url, job_id))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_jobs'))

@app.route('/admin_delete_job/<int:job_id>', methods=['POST'])
def admin_delete_job(job_id):
    if not session.get('admin_loggedin'):
        return redirect(url_for('admin_login'))
    conn = get_db()
    with conn.cursor() as cursor:
        cursor.execute('DELETE FROM jobs WHERE id = %s', (job_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_jobs'))

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    password = None
    if request.method == 'POST':
        email = request.form.get('email')
        conn = get_db()
        with conn.cursor() as cursor:
            cursor.execute('SELECT plain_password FROM users WHERE email = %s', (email,))
            row = cursor.fetchone()
        conn.close()
        if row and row['plain_password']:
            password = row['plain_password']
        else:
            flash('No account found with that email or password not available.', 'danger')
    return render_template('forgot_password.html', password=password)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    conn = get_db()
    with conn.cursor() as cursor:
        cursor.execute('SELECT user_id, expires_at FROM password_reset_tokens WHERE token = %s', (token,))
        row = cursor.fetchone()
    if not row or row['expires_at'] < datetime.now():
        flash('Invalid or expired token.', 'danger')
        return redirect('/login')
    if request.method == 'POST':
        new_password = request.form.get('password')
        hashed = generate_password_hash(new_password)
        with conn.cursor() as cursor:
            cursor.execute('UPDATE users SET password = %s WHERE id = %s', (hashed, row['user_id']))
            cursor.execute('DELETE FROM password_reset_tokens WHERE token = %s', (token,))
        conn.commit()
        conn.close()
        flash('Password reset successful. Please log in.', 'success')
        return redirect('/login')
    conn.close()
    return render_template('reset_password.html')

# Simple email sender (configure SMTP as needed)
def send_email(to, subject, body):
    smtp_host = 'smtp.example.com'  # Change to your SMTP server
    smtp_port = 587
    smtp_user = 'your@email.com'
    smtp_pass = 'yourpassword'
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = smtp_user
    msg['To'] = to
    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, [to], msg.as_string())
    except Exception as e:
        print('Email send failed:', e)

@app.route('/admin_forgot_password', methods=['GET', 'POST'])
def admin_forgot_password():
    password = None
    if request.method == 'POST':
        username = request.form.get('username')
        conn = get_db()
        with conn.cursor() as cursor:
            cursor.execute('SELECT plain_password FROM admin WHERE username = %s', (username,))
            row = cursor.fetchone()
        conn.close()
        if row and row['plain_password']:
            password = row['plain_password']
        else:
            flash('Admin not found or password not available.', 'danger')
    return render_template('admin_forgot_password.html', password=password)
    
if __name__ == '__main__':
    app.run(debug=True, port=5001)