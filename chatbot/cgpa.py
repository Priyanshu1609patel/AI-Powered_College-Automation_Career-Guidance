"""
CGPA / SGPA calculation and conversion utilities.
"""

# Grade-point mapping (standard 10-point scale)
GRADE_MAP = {
    'O':  10, 'o':  10,
    'A+': 9,  'a+': 9,
    'A':  8,  'a':  8,
    'B+': 7,  'b+': 7,
    'B':  6,  'b':  6,
    'C':  5,  'c':  5,
    'P':  4,  'p':  4,
    'F':  0,  'f':  0,
}


def calculate_sgpa(subjects):
    """
    Calculate SGPA from list of (credit, grade) tuples.
    subjects: [(credit_int, grade_str), ...]
    Returns dict with sgpa, total_credits, details.
    """
    if not subjects:
        return {'error': 'No subjects provided.'}

    total_weighted = 0
    total_credits = 0
    details = []

    for credit, grade in subjects:
        gp = GRADE_MAP.get(grade.strip())
        if gp is None:
            return {'error': f"Invalid grade '{grade}'. Valid grades: O, A+, A, B+, B, C, P, F"}
        total_weighted += credit * gp
        total_credits += credit
        details.append({'credit': credit, 'grade': grade.strip().upper(), 'gp': gp, 'weighted': credit * gp})

    if total_credits == 0:
        return {'error': 'Total credits cannot be zero.'}

    sgpa = round(total_weighted / total_credits, 2)
    return {
        'sgpa': sgpa,
        'total_credits': total_credits,
        'total_weighted': total_weighted,
        'details': details,
        'percentage': round(sgpa * 10, 1),
    }


def calculate_cgpa(semester_data):
    """
    Calculate CGPA from list of (sgpa, credits) for each semester.
    semester_data: [(sgpa_float, credits_int), ...]
    """
    if not semester_data:
        return {'error': 'No semester data provided.'}

    total_weighted = 0
    total_credits = 0

    for sgpa, credits in semester_data:
        total_weighted += sgpa * credits
        total_credits += credits

    if total_credits == 0:
        return {'error': 'Total credits cannot be zero.'}

    cgpa = round(total_weighted / total_credits, 2)
    percentage = round(cgpa * 10, 1)

    classification = ''
    if cgpa >= 8.0:
        classification = 'Distinction'
    elif cgpa >= 6.5:
        classification = 'First Class'
    elif cgpa >= 5.0:
        classification = 'Second Class'
    elif cgpa >= 4.0:
        classification = 'Pass'
    else:
        classification = 'Fail'

    return {
        'cgpa': cgpa,
        'percentage': percentage,
        'classification': classification,
        'total_credits': total_credits,
    }


def cgpa_to_percentage(cgpa_value):
    """Convert CGPA to approximate percentage."""
    try:
        cgpa = float(cgpa_value)
    except (ValueError, TypeError):
        return {'error': 'Please provide a valid number for CGPA.'}

    if cgpa < 0 or cgpa > 10:
        return {'error': 'CGPA must be between 0 and 10.'}

    percentage = round(cgpa * 10, 1)
    return {
        'cgpa': cgpa,
        'percentage': percentage,
    }


def format_sgpa_explanation():
    """Return a readable explanation of SGPA calculation."""
    return (
        "**SGPA Calculation Formula:**\n\n"
        "SGPA = Sum(Credit x Grade Point) / Total Credits\n\n"
        "**Grade Point Scale:**\n"
        "| Grade | Points |\n|-------|--------|\n"
        "| O | 10 |\n| A+ | 9 |\n| A | 8 |\n| B+ | 7 |\n"
        "| B | 6 |\n| C | 5 |\n| P | 4 |\n| F | 0 |\n\n"
        "**Example:** If you have 3 subjects with credits 4, 3, 3 and grades A+, A, B+:\n"
        "SGPA = (4x9 + 3x8 + 3x7) / (4+3+3) = (36+24+21)/10 = **8.10**"
    )


def format_cgpa_explanation():
    """Return a readable explanation of CGPA calculation."""
    return (
        "**CGPA Calculation Formula:**\n\n"
        "CGPA = Sum(SGPA x Semester Credits) / Total Credits\n\n"
        "**CGPA to Percentage:** CGPA x 10 = Percentage\n\n"
        "**Classification:**\n"
        "- CGPA >= 8.0 → Distinction\n"
        "- CGPA >= 6.5 → First Class\n"
        "- CGPA >= 5.0 → Second Class\n"
        "- CGPA >= 4.0 → Pass\n"
        "- CGPA < 4.0 → Fail\n\n"
        "**Example:** CGPA 8.5 → 85% → Distinction"
    )
