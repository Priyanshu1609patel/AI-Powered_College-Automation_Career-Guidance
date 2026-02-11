"""
Static / template responses for the chatbot.
"""

GREETING_RESPONSES = [
    "Hello! I'm your College AI Assistant. I can help you with:\n"
    "- **Attendance** calculation & eligibility\n"
    "- **Subjects** & study materials\n"
    "- **CGPA/SGPA** calculation\n"
    "- **Exam patterns** & academic rules\n"
    "- **Notices** & announcements\n\n"
    "Just type your question naturally!",
]

FAREWELL_RESPONSES = [
    "Goodbye! All the best with your studies. Feel free to come back anytime.",
]

HELP_RESPONSE = (
    "**Here's what I can help you with:**\n\n"
    "**1. Attendance**\n"
    "   - 'My attendance is 45/60'\n"
    "   - 'Am I eligible for exams?'\n"
    "   - 'What is the minimum attendance?'\n\n"
    "**2. Subjects & Materials**\n"
    "   - 'What subjects are in semester 5?'\n"
    "   - 'Give me notes for Data Structures'\n"
    "   - 'Syllabus of Machine Learning'\n\n"
    "**3. CGPA / SGPA**\n"
    "   - 'How to calculate SGPA?'\n"
    "   - 'Convert 8.5 CGPA to percentage'\n"
    "   - 'What is CGPA formula?'\n\n"
    "**4. Exams & Rules**\n"
    "   - 'What is the exam pattern?'\n"
    "   - 'Back paper rules'\n"
    "   - 'Branch change policy'\n\n"
    "**5. Notices**\n"
    "   - 'Any new notices?'\n"
    "   - 'Latest announcements'\n\n"
    "Just type your question in plain English!"
)

UNKNOWN_RESPONSE = (
    "I'm not sure I understand that question. Could you try rephrasing it?\n\n"
    "You can ask me about **attendance, subjects, CGPA, exam patterns, "
    "study materials, or academic rules**.\n\n"
    "Type **help** to see all the things I can do."
)

PLACEMENT_RESPONSE = (
    "For placement-related queries, here's what I can tell you:\n\n"
    "- **Eligibility:** Minimum CGPA 6.0, no active backlogs\n"
    "- **Process:** Pre-placement talk → Online test → Technical interview → HR interview\n"
    "- **Top Recruiters:** TCS, Infosys, Wipro, Cognizant, Accenture, and more\n"
    "- **Average Package:** 4-6 LPA | **Highest:** 12+ LPA\n\n"
    "Check the **Notices** section for upcoming placement drives, or visit the placement cell."
)
