"""
Attendance calculation and eligibility prediction logic.
"""
import re
import math


def parse_attendance_from_text(text):
    """
    Extract attended and total classes from user text.
    Supports formats: "45/60", "45 out of 60", "attended 45 from 60"
    Returns (attended, total) or (None, None).
    """
    patterns = [
        r'(?:attended|present)\s*(\d+)\s*(?:out\s*of|\/|from)\s*(\d+)',
        r'(\d+)\s*(?:out\s*of|\/|from)\s*(\d+)\s*(?:class|lecture|period|total)',
        r'(\d+)\s*\/\s*(\d+)',
        r'attendance.*?(\d+)\s*(?:out\s*of|\/|from)\s*(\d+)',
    ]
    text_lower = text.lower()
    for pattern in patterns:
        match = re.search(pattern, text_lower)
        if match:
            attended = int(match.group(1))
            total = int(match.group(2))
            if 0 < attended <= total:
                return attended, total
    return None, None


def calculate_attendance(attended, total):
    """
    Calculate attendance percentage and return detailed analysis.
    """
    if total <= 0:
        return {'error': 'Total classes must be greater than 0.'}
    if attended > total:
        return {'error': 'Attended classes cannot exceed total classes.'}
    if attended < 0:
        return {'error': 'Attended classes cannot be negative.'}

    percentage = (attended / total) * 100

    result = {
        'attended': attended,
        'total': total,
        'percentage': round(percentage, 2),
        'status': '',
        'eligible_for_exam': True,
        'lectures_needed_for_75': 0,
        'lectures_needed_for_80': 0,
        'can_skip': 0,
        'warning': '',
    }

    # Eligibility thresholds
    if percentage >= 80:
        result['status'] = 'Excellent'
        # How many more can be skipped while staying >= 75%
        # (attended) / (total + x) >= 0.75 => x <= (attended/0.75) - total
        can_skip = math.floor(attended / 0.75 - total)
        result['can_skip'] = max(can_skip, 0)
    elif percentage >= 75:
        result['status'] = 'Safe'
        can_skip = math.floor(attended / 0.75 - total)
        result['can_skip'] = max(can_skip, 0)
    elif percentage >= 65:
        result['status'] = 'Warning Zone'
        result['eligible_for_exam'] = True
        result['warning'] = 'You are between 65-75%. You may need to pay a fine for condonation.'
    else:
        result['status'] = 'Critical - Debarred'
        result['eligible_for_exam'] = False
        result['warning'] = 'Below 65% attendance. You are likely debarred from exams.'

    # Lectures needed to reach 75%
    # (attended + x) / (total + x) >= 0.75
    # attended + x >= 0.75 * total + 0.75x
    # 0.25x >= 0.75*total - attended
    # x >= (0.75*total - attended) / 0.25
    if percentage < 75:
        needed = math.ceil((0.75 * total - attended) / 0.25)
        result['lectures_needed_for_75'] = max(needed, 0)

    # Lectures needed to reach 80%
    if percentage < 80:
        needed = math.ceil((0.80 * total - attended) / 0.20)
        result['lectures_needed_for_80'] = max(needed, 0)

    return result


def format_attendance_response(result):
    """Format attendance result into a readable chatbot response."""
    if 'error' in result:
        return f"Sorry, I couldn't calculate that. {result['error']}"

    lines = []
    lines.append(f"**Attendance Report**")
    lines.append(f"- Classes Attended: **{result['attended']} / {result['total']}**")
    lines.append(f"- Attendance Percentage: **{result['percentage']}%**")
    lines.append(f"- Status: **{result['status']}**")

    if result['eligible_for_exam']:
        lines.append(f"- Exam Eligibility: **Eligible**")
    else:
        lines.append(f"- Exam Eligibility: **NOT Eligible (Debarred)**")

    if result['warning']:
        lines.append(f"\n**Warning:** {result['warning']}")

    if result['lectures_needed_for_75'] > 0:
        lines.append(f"\nYou need to attend **{result['lectures_needed_for_75']} more consecutive classes** to reach 75%.")

    if result['lectures_needed_for_80'] > 0:
        lines.append(f"You need **{result['lectures_needed_for_80']} more consecutive classes** to reach 80%.")

    if result['can_skip'] > 0:
        lines.append(f"\nYou can safely skip up to **{result['can_skip']} classes** while staying at or above 75%.")

    return '\n'.join(lines)
