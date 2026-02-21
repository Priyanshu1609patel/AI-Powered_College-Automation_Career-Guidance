"""
CGPA / SGPA calculation and conversion utilities.
"""

# Grade-point mapping — Indus University UG scheme
# A+: 10 (80-100), A: 9 (70-79), B+: 8 (60-69), B: 7 (55-59)
# C: 6 (50-54), D: 5 (45-49), P: 4 (40-44), F: 0 (<40)
GRADE_MAP = {
    'A+': 10, 'a+': 10,
    'A':  9,  'a':  9,
    'B+': 8,  'b+': 8,
    'B':  7,  'b':  7,
    'C':  6,  'c':  6,
    'D':  5,  'd':  5,
    'P':  4,  'p':  4,
    'F':  0,  'f':  0,
    'AB': 0,  'ab': 0,
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
    # Indus University formula: Percentage = (CGPA - 0.5) * 10
    percentage = round((cgpa - 0.5) * 10, 1)

    # Indus University degree classification (FGPA based)
    classification = ''
    if cgpa >= 7.50:
        classification = 'First Class with Distinction'
    elif cgpa >= 6.50:
        classification = 'First Class'
    elif cgpa >= 5.50:
        classification = 'Second Class'
    elif cgpa >= 4.50:
        classification = 'Pass Class'
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

    # Indus University formula: Percentage = (CGPA - 0.5) * 10
    percentage = round((cgpa - 0.5) * 10, 1)
    return {
        'cgpa': cgpa,
        'percentage': percentage,
    }


def format_sgpa_explanation():
    """Return a readable explanation of SGPA calculation."""
    return (
        "**SGPA Calculation — Indus University**\n\n"
        "**Formula:** SGPA = Σ(Credit × Grade Points) / Σ Credits\n\n"
        "**Grade Point Scale (UG Programs):**\n"
        "| Marks | Grade | Points |\n|-------|-------|--------|\n"
        "| 80-100 | A+ | 10 |\n| 70-79 | A | 9 |\n| 60-69 | B+ | 8 |\n"
        "| 55-59 | B | 7 |\n| 50-54 | C | 6 |\n| 45-49 | D | 5 |\n"
        "| 40-44 | P | 4 |\n| <40 | F | 0 |\n\n"
        "**Example:** Subjects with credits 4, 3, 3 and grades A+, A, B+:\n"
        "SGPA = (4×10 + 3×9 + 3×8) / (4+3+3) = (40+27+24)/10 = **9.10**"
    )


def format_cgpa_explanation():
    """Return a readable explanation of CGPA calculation."""
    return (
        "**CGPA Calculation — Indus University**\n\n"
        "**Formula:** CGPA = Σ(SGPA × Semester Credits) / Σ Credits\n\n"
        "**CGPA → Percentage Formula:** `(CGPA − 0.5) × 10`\n\n"
        "**Degree Classification (FGPA):**\n"
        "- FGPA ≥ 7.50 → **First Class with Distinction**\n"
        "- 6.50 ≤ FGPA < 7.50 → **First Class**\n"
        "- 5.50 ≤ FGPA < 6.50 → **Second Class**\n"
        "- 4.50 ≤ FGPA < 5.50 → **Pass Class**\n\n"
        "**Example:** CGPA 8.5 → (8.5 − 0.5) × 10 = **80%** → First Class with Distinction"
    )
