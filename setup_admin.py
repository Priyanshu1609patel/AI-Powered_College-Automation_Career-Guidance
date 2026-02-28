"""
One-time script to create the default admin and student user with proper password hashes.
Run: python setup_admin.py
"""
from werkzeug.security import generate_password
from database import execute_db, query_db


def setup():
    # Create admin user
    admin_email = 'admin@college.edu'
    existing = query_db("SELECT id FROM users WHERE email = %s", (admin_email,), one=True)
    if not existing:
        execute_db(
            """INSERT INTO users (name, email, password, role, branch)
               VALUES (%s, %s, %s, 'admin', 'CSE')""",
            ('Admin', admin_email, generate_password('admin123'))
        )
        print(f"Admin created: {admin_email} / admin123")
    else:
        print(f"Admin already exists: {admin_email}")

    # Create demo student
    student_email = 'student@college.edu'
    existing = query_db("SELECT id FROM users WHERE email = %s", (student_email,), one=True)
    if not existing:
        execute_db(
            """INSERT INTO users (name, email, password, role, enrollment_no, semester, branch)
               VALUES (%s, %s, %s, 'student', %s, %s, 'CSE')""",
            ('Priyanshu Kumar', student_email, generate_password('student123'), 'CSE2021001', 6)
        )
        print(f"Student created: {student_email} / student123")
    else:
        print(f"Student already exists: {student_email}")

    print("Setup complete!")


if __name__ == '__main__':
    setup()
