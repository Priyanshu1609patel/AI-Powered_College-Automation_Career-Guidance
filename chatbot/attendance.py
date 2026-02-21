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

    # Indus University thresholds (from JSON data):
    # 80%+ → Eligible for exams
    # 75-79% → MYSY scholarship eligible but NOT exam eligible
    # Below 75% → Debarred from exams, not eligible for MYSY renewal
    if percentage >= 80:
        result['status'] = 'Excellent — Exam Eligible'
        # Classes can be skipped while staying >= 80%
        can_skip = math.floor(attended / 0.80 - total)
        result['can_skip'] = max(can_skip, 0)
    elif percentage >= 75:
        result['status'] = 'Below Required — NOT Exam Eligible'
        result['eligible_for_exam'] = False
        result['warning'] = (
            'You have 75-79% attendance. At Indus University, '
            'minimum 80% is required to appear in Semester Examinations. '
            'You ARE eligible for MYSY Scholarship renewal (needs 75%), '
            'but you CANNOT write exams until you reach 80%.'
        )
    else:
        result['status'] = 'Critical — Debarred'
        result['eligible_for_exam'] = False
        result['warning'] = (
            'Below 75% attendance. You are NOT eligible for exams '
            'AND not eligible for MYSY Scholarship renewal. '
            'Contact your HOD immediately.'
        )

    # Lectures needed to reach 75% (MYSY threshold)
    if percentage < 75:
        needed = math.ceil((0.75 * total - attended) / 0.25)
        result['lectures_needed_for_75'] = max(needed, 0)

    # Lectures needed to reach 80% (exam eligibility threshold)
    if percentage < 80:
        needed = math.ceil((0.80 * total - attended) / 0.20)
        result['lectures_needed_for_80'] = max(needed, 0)

    return result


def parse_future_attendance_from_text(text):
    """
    Parse a future-planning query.  Returns (attended, total, remaining, target_percent).
    Any value that cannot be parsed is returned as None (target defaults to 80).

    Handles phrases like:
      "12 out of 15, next 20 lectures, for 80%"
      "attendance 30/50 and 15 remaining, target 75%"
      "12 out 15 and next 20 lectures remaining"
    """
    text_lower = text.lower()

    # --- current attendance ---
    attended, total = parse_attendance_from_text(text)
    if attended is None:
        # "out N" without "of"
        m = re.search(r'(\d+)\s*out\s+(\d+)', text_lower)
        if m:
            a, t = int(m.group(1)), int(m.group(2))
            if 0 < a <= t:
                attended, total = a, t

    # --- remaining / upcoming lectures ---
    remaining = None
    remaining_patterns = [
        r'(?:next|upcoming|future|more)\s+(\d+)\s+(?:lectures?|classes?|periods?)',
        r'(\d+)\s+(?:lectures?|classes?|periods?)\s+(?:remaining|left|more|upcoming|future|pending)',
        r'(\d+)\s+(?:more\s+)?(?:lectures?|classes?)\s+(?:are\s+)?(?:left|remaining|pending)',
        r'remaining\s+(?:lectures?|classes?)\s+(?:are\s+)?(\d+)',
    ]
    for pat in remaining_patterns:
        m = re.search(pat, text_lower, re.IGNORECASE)
        if m:
            remaining = int(m.group(1))
            break

    # --- target percentage (default 80) ---
    target_percent = 80
    target_patterns = [
        r'(?:for|to|reach|achieve|get|maintain|target|of)\s+(\d+)\s*%',
        r'(\d+)\s*%\s*(?:attendance|target|eligibility|chahiye|required)',
        r'(\d+)\s*percent(?:age)?',
    ]
    for pat in target_patterns:
        m = re.search(pat, text_lower)
        if m:
            val = int(m.group(1))
            if 40 <= val <= 100:
                target_percent = val
                break

    return attended, total, remaining, target_percent


def calculate_future_attendance(attended, total, remaining, target_percent=80):
    """
    Given current attendance (attended/total) and upcoming lecture count,
    calculate how many of the remaining lectures to attend (or can skip)
    to reach *target_percent*.

    Returns a result dict with all numbers pre-computed.
    """
    total_final   = total + remaining
    required_total = math.ceil(target_percent / 100 * total_final)
    more_needed   = max(0, required_total - attended)
    can_skip      = remaining - more_needed

    current_pct         = round(attended / total * 100, 1) if total > 0 else 0.0
    final_if_attend_all = round((attended + remaining) / total_final * 100, 1) if total_final > 0 else 0.0

    return {
        'attended':            attended,
        'total':               total,
        'remaining':           remaining,
        'target_percent':      target_percent,
        'current_percent':     current_pct,
        'total_final':         total_final,
        'required_total':      required_total,
        'more_needed':         more_needed,
        'can_skip':            max(0, can_skip),
        'achievable':          more_needed <= remaining,
        'already_achieved':    attended >= required_total,
        'final_if_attend_all': final_if_attend_all,
    }


def format_future_attendance_response(result):
    """Format the future attendance plan into a readable chatbot response."""
    a          = result['attended']
    t          = result['total']
    rem        = result['remaining']
    target     = result['target_percent']
    current    = result['current_percent']
    total_f    = result['total_final']
    req        = result['required_total']
    more       = result['more_needed']
    can_skip   = result['can_skip']
    max_final  = result['final_if_attend_all']

    lines = [
        f"**Attendance Planner — Target: {target}%**\n",
        "**Your Situation:**",
        f"- Current: **{a} / {t}** = **{current}%**",
        f"- Upcoming lectures: **{rem}**",
        f"- Total lectures after all: **{total_f}**",
        f"- Need **{req} / {total_f}** attended for {target}%\n",
    ]

    if result['already_achieved']:
        lines += [
            f"✅ **Already at {target}%! You can relax a little.**",
            f"- Can skip up to **{can_skip}** of the {rem} remaining lectures",
            f"- Minimum still to attend: **{more}** lectures",
        ]
    elif not result['achievable']:
        lines += [
            f"❌ **Cannot reach {target}% even attending all {rem} remaining lectures.**",
            f"- Maximum possible attendance: **{max_final}%**",
            f"- You are **{req - a - rem} lectures short** even in the best case",
        ]
    else:
        lines += [
            "📋 **What you need to do:**",
            f"- Must attend: **{more} out of {rem}** upcoming lectures",
            f"- Can skip: **{can_skip}** lectures",
        ]

    # Always show the key threshold comparison table
    lines.append(f"\n**Threshold Summary ({total_f} total lectures):**")
    for pct, label in [(80, "Exam Eligibility"), (75, "MYSY Scholarship"), (85, "Safe Zone")]:
        req_t  = math.ceil(pct / 100 * total_f)
        more_t = max(0, req_t - a)
        skip_t = rem - more_t
        if more_t <= rem:
            lines.append(f"- **{pct}% ({label}):** attend {more_t}, can skip {max(0, skip_t)}")
        else:
            lines.append(f"- **{pct}% ({label}):** ❌ not achievable (need {more_t}, only {rem} left)")

    return '\n'.join(lines)


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
        lines.append(f"\nYou need **{result['lectures_needed_for_75']} more consecutive classes** to reach 75% (MYSY threshold).")

    if result['lectures_needed_for_80'] > 0:
        lines.append(f"You need **{result['lectures_needed_for_80']} more consecutive classes** to reach 80% (exam eligibility).")

    if result['can_skip'] > 0:
        lines.append(f"\nYou can safely skip up to **{result['can_skip']} classes** while staying at or above 80%.")

    return '\n'.join(lines)
