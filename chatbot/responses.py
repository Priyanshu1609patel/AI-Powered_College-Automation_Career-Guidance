"""
Static / template responses for the Indus University CSE chatbot.
Dynamic responses are built in engine.py using JSON knowledge base data.
"""

GREETING_RESPONSES = [
    "Hello! I'm the **Indus University CSE Department AI Assistant**.\n\n"
    "I can help you with:\n"
    "- **Fees** — structure, payment, installments\n"
    "- **MYSY Scholarship** — eligibility & how to apply\n"
    "- **Attendance** — calculation, rules & eligibility\n"
    "- **Academic Calendar** — exam dates, term schedule\n"
    "- **Subjects & Syllabus** — all 8 semesters\n"
    "- **Study Materials** — Google Drive links\n"
    "- **Exam & Grading** — format, grades, CGPA/SGPA\n"
    "- **Re-Assessment / Re-Checking** — fees & process\n"
    "- **Library Policy** — borrowing, fines, hours\n"
    "- **Discipline Rules** — conduct, dress code, hostel\n"
    "- **Placement** — stats, companies, training\n\n"
    "Just type your question in English, Hindi, or Gujarati!"
]

FAREWELL_RESPONSES = [
    "Goodbye! Best of luck with your studies at Indus University. Feel free to come back anytime!"
]

HELP_RESPONSE = (
    "**Here's everything I can help you with:**\n\n"
    "**Fees & Payments**\n"
    "  - 'What is the semester fee?'\n"
    "  - 'How to pay fee in installments?'\n\n"
    "**MYSY Scholarship**\n"
    "  - 'How to apply for MYSY scholarship?'\n"
    "  - 'Am I eligible for MYSY?'\n\n"
    "**Attendance**\n"
    "  - 'My attendance is 45/60'\n"
    "  - 'What is minimum attendance?'\n\n"
    "**Academic Calendar**\n"
    "  - 'When is mid sem exam?'\n"
    "  - 'When does Semester 3 start?'\n\n"
    "**Subjects & Materials**\n"
    "  - 'Semester 5 subjects'\n"
    "  - 'DBMS course content'\n"
    "  - 'Sem 4 study material link'\n\n"
    "**Grading & CGPA**\n"
    "  - 'What grade for 75 marks?'\n"
    "  - 'Convert 8.2 CGPA to percentage'\n\n"
    "**Re-Assessment**\n"
    "  - 'Re-assessment fee?'\n"
    "  - 'How to apply for rechecking?'\n\n"
    "**Library**\n"
    "  - 'Library borrowing rules'\n"
    "  - 'What is the library fine?'\n\n"
    "**Discipline Rules**\n"
    "  - 'Dress code rules'\n"
    "  - 'Is mobile allowed on campus?'\n\n"
    "**Placement**\n"
    "  - 'Highest placement package?'\n"
    "  - 'Which companies visit for placement?'\n\n"
    "Just type your question naturally!"
)

UNKNOWN_RESPONSE = (
    "I'm not sure I understand that question. Could you please rephrase it?\n\n"
    "I can help with **fees, attendance, MYSY scholarship, exam dates, subjects, "
    "study materials, grading, re-assessment, library rules, discipline, and placement**.\n\n"
    "Type **help** to see everything I can do, or contact the CSE Department office for specific queries."
)
