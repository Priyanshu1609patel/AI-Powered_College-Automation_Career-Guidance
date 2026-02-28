"""
Main chatbot engine.

Response strategy (per message):
  1. For math intents (attendance calc, CGPA convert) → always use pattern engine
     (AI is not needed; exact calculation is better)
  2. For all other intents → try AI fallback chain first (5 providers)
  3. If ALL AI providers are unavailable → fall back to pattern-match handlers

This gives the best of both worlds:
  - AI for natural language, multilingual, context-aware answers
  - Pattern engine as a reliable offline fallback
"""
import re
import time
import logging
from .intents import recognize_intent
from .attendance import (
    parse_attendance_from_text, calculate_attendance, format_attendance_response,
    parse_future_attendance_from_text, calculate_future_attendance, format_future_attendance_response,
)
from .cgpa import format_sgpa_explanation, format_cgpa_explanation
from .json_loader import kb
from .ai_engine   import ai_respond
from .responses import (
    GREETING_RESPONSES, FAREWELL_RESPONSES, HELP_RESPONSE,
    UNKNOWN_RESPONSE,
)
from database import query_db, execute_db

log = logging.getLogger(__name__)

# Intents that must always use the pattern engine (math / calculation)
_ALWAYS_PATTERN = {
    'greeting', 'farewell', 'help',
    'attendance_calculate',      # needs arithmetic
    'attendance_future_plan',    # needs arithmetic
    'cgpa_to_percentage',        # needs arithmetic
    'grade_for_marks',           # needs arithmetic
    'passing_marks',             # needs arithmetic + subject lookup
    'cgpa_calculate',
    'sgpa_calculate',
    'notices',                   # reads live DB
    'study_material',            # needs exact drive-link pairing
}


class ChatbotEngine:
    """
    Core chatbot processor.
    Uses AI providers (5 free APIs with auto-fallback) for natural language
    responses, and falls back to pattern-match handlers when AI is unavailable.
    """

    def process(self, user_message, user_id=None, chat_history=None):
        """
        Process a user message and return a response dict.
        chat_history: list of {"role": "user"|"assistant", "content": "..."}
        Returns: {'response', 'intent', 'confidence', 'response_time_ms', 'ai_provider'}
        """
        start = time.time()
        intent, confidence, extracted = recognize_intent(user_message)
        history   = chat_history or []
        ai_provider_used = 'pattern'

        # ── Step 1: always use pattern engine for calculation / meta intents ──
        if intent in _ALWAYS_PATTERN:
            response_text = self._pattern_handler(intent, user_message, extracted)

        else:
            # ── Step 2: try AI fallback chain ─────────────────────────────────
            extras = {
                'semester':    extracted.get('semester'),
                'keyword':     self._extract_subject_query(user_message),
                'raw_message': user_message,
            }
            ai_text, provider_name = ai_respond(
                user_message=user_message,
                intent=intent,
                history=history,
                extras=extras,
            )

            if ai_text:
                response_text    = ai_text
                ai_provider_used = provider_name
            else:
                # ── Step 3: all AI failed → use pattern engine ─────────────
                log.warning("[Engine] All AI providers unavailable — using pattern engine")
                response_text = self._pattern_handler(intent, user_message, extracted)

        elapsed_ms = int((time.time() - start) * 1000)

        self._log_query(user_id, user_message, intent, response_text, confidence, elapsed_ms)
        if intent == 'unknown':
            self._log_unanswered(user_id, user_message, intent)

        return {
            'response':         response_text,
            'intent':           intent,
            'confidence':       confidence,
            'response_time_ms': elapsed_ms,
            'ai_provider':      ai_provider_used,
        }

    # ----------------------------------------------------------------
    # Pattern handler dispatcher (used when AI is unavailable)
    # ----------------------------------------------------------------

    def _pattern_handler(self, intent, user_message, extracted):
        handler_map = {
            'greeting':               self._handle_greeting,
            'farewell':               self._handle_farewell,
            'help':                   self._handle_help,
            'fee_structure':          self._handle_fee_structure,
            'fee_payment_method':     self._handle_fee_payment,
            'attendance_calculate':   self._handle_attendance_calc,
            'attendance_future_plan': self._handle_attendance_future,
            'attendance_eligibility': self._handle_attendance_eligibility,
            'attendance_rule':        self._handle_attendance_rule,
            'mysy_scholarship':       self._handle_mysy,
            'academic_calendar':      self._handle_academic_calendar,
            'semester_subjects':      self._handle_semester_subjects,
            'subject_info':           self._handle_subject_info,
            'study_material':         self._handle_study_material,
            'exam_format':            self._handle_exam_format,
            'grading_system':         self._handle_grading_system,
            'grade_for_marks':        self._handle_grade_for_marks,
            'passing_marks':          self._handle_passing_marks,
            'cgpa_calculate':         self._handle_cgpa,
            'sgpa_calculate':         self._handle_sgpa,
            'cgpa_to_percentage':     self._handle_cgpa_to_percent,
            're_assessment':          self._handle_reassessment,
            'library_policy':         self._handle_library,
            'discipline_rules':       self._handle_discipline,
            'placement':              self._handle_placement,
            'back_paper':             self._handle_back_paper,
            'notices':                self._handle_notices,
            'academic_rule':          self._handle_academic_rule,
        }
        handler = handler_map.get(intent, self._handle_unknown)
        return handler(user_message, extracted)

    # ----------------------------------------------------------------
    # Meta Handlers
    # ----------------------------------------------------------------

    def _handle_greeting(self, msg, ext):
        return GREETING_RESPONSES[0]

    def _handle_farewell(self, msg, ext):
        return FAREWELL_RESPONSES[0]

    def _handle_help(self, msg, ext):
        return HELP_RESPONSE

    # ----------------------------------------------------------------
    # Fee Handlers
    # ----------------------------------------------------------------

    def _handle_fee_structure(self, msg, ext):
        fee = kb.get_fee_structure()
        if not fee:
            return "Fee information is currently unavailable. Please contact the accounts office."

        sb = fee.get('semester_breakdown', {})
        s16 = sb.get('semesters_1_to_6', {})
        s78 = sb.get('semesters_7_to_8', {})
        yearly = fee.get('yearly_estimates', {})
        total = fee.get('total_course_fee_readable', '')

        lines = [
            "**B.Tech CSE Fee Structure — Indus University (2025-26)**\n",
            "**Semesters 1 to 6 (per semester):**",
            f"- Tuition Fee: ₹{s16.get('tuition_fee', 48000):,}",
            f"- Library Fee: ₹{s16.get('library_fee', 3000):,}",
            f"- Miscellaneous Fee: ₹{s16.get('miscellaneous_fee', 4300):,}",
            f"- **Total: ₹{s16.get('total_per_semester', 55300):,}**\n",
            "**Semesters 7 & 8 (per semester):**",
            f"- Tuition Fee: ₹{s78.get('tuition_fee', 50400):,}",
            f"- Library Fee: ₹{s78.get('library_fee', 3000):,}",
            f"- Miscellaneous Fee: ₹{s78.get('miscellaneous_fee', 4300):,}",
            f"- **Total: ₹{s78.get('total_per_semester', 57700):,}**\n",
            "**Yearly Estimates:**",
            f"- Year 1 to 3: {yearly.get('year_1_to_3_readable', '₹1.11 Lakhs per year')}",
            f"- Year 4: {yearly.get('year_4_readable', '₹1.15 Lakhs')}",
            f"- **Total 4-Year Course Fee: {total}**\n",
            "Type **'payment methods'** to learn how to pay, or **'installment'** for EMI options.",
        ]
        return '\n'.join(lines)

    def _handle_fee_payment(self, msg, ext):
        pay = kb.get_fee_payment()
        if not pay:
            return "Payment information is currently unavailable. Please contact the accounts office."

        methods = pay.get('payment_methods', [])
        inst = pay.get('installment_policy', {})
        std = inst.get('standard_installments', {})
        emi = inst.get('emi_option', {})

        lines = [
            "**Fee Payment Methods — Indus University**\n",
            "**Accepted Modes:**",
        ]
        for m in methods:
            lines.append(f"- {m}")
        lines += [
            "\n**Installment Options:**",
            f"- Pay in up to **{std.get('max_parts', 3)} parts** (A / B / C suffix on Enrollment Number)",
            f"- Select installment option via IU Portal / ERP during payment window",
            f"\n**0% EMI Option:**",
            f"- Provider: **{emi.get('provider', 'GrayQuest')}**",
            f"- {emi.get('interest', '0% interest EMI')} — third-party plan",
        ]
        return '\n'.join(lines)

    # ----------------------------------------------------------------
    # Attendance Handlers
    # ----------------------------------------------------------------

    def _handle_attendance_calc(self, msg, ext):
        attended, total = parse_attendance_from_text(msg)
        if attended is None:
            nums = ext.get('numbers', [])
            if len(nums) >= 2:
                attended, total = int(nums[0]), int(nums[1])
        if attended is None:
            return (
                "I can calculate your attendance! Please provide it like:\n"
                "- 'My attendance is **45/60**'\n"
                "- 'Attended 50 out of 70 classes'"
            )
        result = calculate_attendance(attended, total)
        return format_attendance_response(result)

    def _handle_attendance_future(self, msg, ext):
        """Future attendance planner: how many of N remaining lectures to attend/skip."""
        attended, total, remaining, target_pct = parse_future_attendance_from_text(msg)

        # If we got the current fraction from extracted numbers as fallback
        if attended is None:
            nums = [int(n) for n in ext.get('numbers', []) if float(n) == int(n)]
            if len(nums) >= 2:
                attended, total = nums[0], nums[1]

        if attended is None or remaining is None:
            # Build a helpful partial-info message
            hints = []
            if attended is not None and total is not None:
                hints.append(f"✓ Current: **{attended}/{total}**")
            if remaining is not None:
                hints.append(f"✓ Upcoming lectures: **{remaining}**")
            missing = "your attendance (e.g. **12/15**)" if attended is None else "the upcoming lecture count (e.g. **next 20 lectures**)"
            return (
                "I can plan your future attendance! Please also tell me " + missing + ".\n\n"
                + ('\n'.join(hints) + '\n\n' if hints else '')
                + "**Example:** _'I attended 12 out of 15 and 20 lectures are remaining — target 80%'_\n\n"
                "Default target is **80%** (exam eligibility). You can ask for any percentage, e.g. '75%' or '85%'."
            )

        result = calculate_future_attendance(attended, total, remaining, target_pct)
        return format_future_attendance_response(result)

    def _handle_attendance_eligibility(self, msg, ext):
        attended, total = parse_attendance_from_text(msg)
        if attended is None:
            nums = ext.get('numbers', [])
            if len(nums) >= 2:
                attended, total = int(nums[0]), int(nums[1])
        if attended is not None:
            result = calculate_attendance(attended, total)
            return format_attendance_response(result)

        return (
            "To check your exam eligibility, please tell me your attendance.\n"
            "For example: 'I attended **40 out of 55** classes'\n\n"
            "**Indus University Attendance Rules:**\n"
            "- **80%+** → Eligible for Semester Examinations\n"
            "- **Below 80%** → NOT eligible (debarred from exams)\n"
            "- **75%+** → Eligible for MYSY Scholarship renewal\n"
            "- **5 minutes late** → No attendance for that period"
        )

    def _handle_attendance_rule(self, msg, ext):
        policy = kb.get_attendance_policy()
        if policy:
            return (
                "**Attendance Policy — Indus University (2025-26)**\n\n"
                f"- Minimum for Exam Eligibility: **{policy.get('minimum_for_exam_eligibility', '80%')}**\n"
                f"- Minimum for Scholarship (MYSY): **75%** | General: **90%**\n"
                f"- Punctuality Rule: **{policy.get('punctuality_rule', 'More than 5 minutes late = No attendance')}**\n\n"
                "**Consequences:**\n"
                "- Less than 80% → **Cannot appear in Semester Examinations**\n"
                "- 3+ consecutive days absent without leave → **Name removed from rolls**\n\n"
                "You can type your attendance (e.g., '45/60') and I'll calculate your percentage."
            )
        return (
            "**Attendance Requirements:**\n"
            "- Minimum **80%** attendance for exam eligibility\n"
            "- Below 80% → Debarred from examinations\n"
            "- 5 minutes late = no attendance for that period\n"
            "- MYSY Scholarship renewal needs 75% attendance"
        )

    # ----------------------------------------------------------------
    # MYSY Scholarship
    # ----------------------------------------------------------------

    def _handle_mysy(self, msg, ext):
        mysy = kb.get_mysy_scholarship()
        if not mysy:
            return "MYSY Scholarship information is currently unavailable. Visit: **mysy.guj.nic.in**"

        elig = mysy.get('eligibility', {})
        ben = mysy.get('benefits', {})
        proc = mysy.get('application_process', {})
        steps = proc.get('steps', [])

        lines = [
            f"**{mysy.get('full_name', 'MYSY Scholarship')}**\n",
            "**Eligibility Criteria:**",
            f"- {elig.get('residency', 'Gujarat State Domicile required')}",
            f"- Academic: {elig.get('academic_criteria', 'Minimum 80th percentile in Class 12')}",
            f"- Income: {elig.get('income_limit', 'Annual family income ≤ ₹6,00,000')}",
            f"- Attendance for Renewal: {elig.get('attendance_for_renewal', 'Minimum 75% annually')}\n",
            "**Benefits:**",
            f"- Tuition Grant: {ben.get('tuition_fee_grant', '50% or ₹50,000/year (whichever is less)')}",
            f"- Book & Equipment: {ben.get('book_and_equipment_allowance', '₹5,000 one-time (1st year)')}",
            f"- Hostel Grant: {ben.get('hostel_grant', '₹1,200/month × 10 months (outside native Taluka)')}\n",
            f"**Application Portal:** {proc.get('portal', 'mysy.guj.nic.in')}\n",
            "**Application Steps:**",
        ]
        for step in steps:
            lines.append(f"  {step}")

        return '\n'.join(lines)

    # ----------------------------------------------------------------
    # Academic Calendar
    # ----------------------------------------------------------------

    def _handle_academic_calendar(self, msg, ext):
        msg_lower = msg.lower()
        key_dates = kb.get_key_dates()

        # Try to get the pre-built key dates summary first
        if key_dates:
            odd = key_dates.get('odd_semester_2025', {})
            even = key_dates.get('even_semester_2026', {})

            # Route based on keyword in message
            if any(w in msg_lower for w in ('mid', 'midsem')):
                return (
                    "**Mid-Semester Exam Dates — 2025-26**\n\n"
                    "**Odd Semester (2025):**\n"
                    f"- Mid-Sem Exams: **{odd.get('mid_sem_exams', '08 Sep – 23 Sep 2025')}**\n"
                    f"- Mid-Sem Jury (Sem III, V, IX): **{odd.get('mid_sem_jury_sem3_5_9', '15 Sep – 19 Sep 2025')}**\n\n"
                    "**Even Semester (2026):**\n"
                    f"- Mid-Sem Exams: **{even.get('mid_sem_exams', '23 Mar – 11 Apr 2026')}**\n"
                    f"- Mid-Sem Jury (Sem IV, VI, VIII): **{even.get('mid_sem_jury_sem4_6_8', '23 Mar – 26 Mar 2026')}**\n"
                    f"- Mid-Sem Jury (Sem II): **{even.get('mid_sem_jury_sem2', '30 Mar 2026')}**\n\n"
                    "Which semester are you currently in?"
                )

            if any(w in msg_lower for w in ('ese', 'end sem', 'end-sem', 'theory', 'practical', 'ese-thy', 'ese-pr')):
                return (
                    "**End-Semester Exam Dates — 2025-26**\n\n"
                    "**Odd Semester (2025):**\n"
                    f"- ESE Practical: **{odd.get('ese_practical', '27 Oct – 08 Nov 2025')}**\n"
                    f"- ESE Theory: **{odd.get('ese_theory', '10 Nov – 29 Nov 2025')}**\n\n"
                    "**Even Semester (2026):**\n"
                    f"- ESE Practical: **{even.get('ese_practical', '01 May – 09 May 2026')}**\n"
                    f"- ESE Theory: **{even.get('ese_theory', '11 May – 30 May 2026')}**"
                )

            if any(w in msg_lower for w in ('holiday', 'vacation', 'winter', 'summer', 'break')):
                vac = kb.get_vacation_periods()
                winter = vac.get('winter_vacation', {})
                summer = vac.get('summer_vacation', {})
                return (
                    "**Vacation Periods — 2025-26**\n\n"
                    f"**Winter Vacation:** {winter.get('start_date', '01 Dec 2025')} to {winter.get('end_date', '31 Dec 2025')}\n"
                    f"  _{winter.get('description', 'Full vacation month between odd and even semesters')}_\n\n"
                    f"**Summer Vacation:** {summer.get('start_date', '01 Jun 2026')} to {summer.get('end_date', '30 Jun 2026')}\n"
                    f"  _{summer.get('description', 'Full vacation month after even semester ends')}_"
                )

            if any(w in msg_lower for w in ('term start', 'term end', 'semester start', 'begin', 'when does')):
                sem_struct = kb.get_semester_structure()
                odd_s = sem_struct.get('odd_semesters', {})
                even_s = sem_struct.get('even_semesters', {})
                return (
                    "**Semester Schedule — 2025-26**\n\n"
                    f"**Odd Semesters (I, III, V, VII):**\n"
                    f"- Months: {odd_s.get('months', 'July 2025 to November 2025')}\n"
                    f"- Term Start: **{odd_s.get('term_start', '01 July 2025')}**\n\n"
                    f"**Even Semesters (II, IV, VI, VIII):**\n"
                    f"- Months: {even_s.get('months', 'January 2026 to May 2026')}\n"
                    f"- Term Start: **{even_s.get('term_start', '01 January 2026')}**"
                )

            # Generic calendar response
            return (
                "**Academic Calendar — Indus University 2025-26**\n\n"
                "**Odd Semester (July – Nov 2025):**\n"
                f"- Term Start: {odd.get('odd_sem_term_start', '01 July 2025')}\n"
                f"- Mid-Sem Exams: {odd.get('mid_sem_exams', '08 Sep – 23 Sep 2025')}\n"
                f"- ESE Practical: {odd.get('ese_practical', '27 Oct – 08 Nov 2025')}\n"
                f"- ESE Theory: {odd.get('ese_theory', '10 Nov – 29 Nov 2025')}\n\n"
                "**Even Semester (Jan – May 2026):**\n"
                f"- Term Start: {even.get('even_sem_term_start', '01 January 2026')}\n"
                f"- Mid-Sem Exams: {even.get('mid_sem_exams', '23 Mar – 11 Apr 2026')}\n"
                f"- ESE Practical: {even.get('ese_practical', '01 May – 09 May 2026')}\n"
                f"- ESE Theory: {even.get('ese_theory', '11 May – 30 May 2026')}\n\n"
                "Ask me specifically about **mid-sem dates**, **ESE dates**, **holidays**, or **term start/end**."
            )

        # Fallback using hardcoded data from training prompt
        return (
            "**Academic Calendar 2025-26 (Key Dates):**\n\n"
            "**Odd Semester:**\n"
            "- Mid-Sem Exams: 08 Sep – 23 Sep 2025\n"
            "- ESE Practical: 27 Oct – 08 Nov 2025\n"
            "- ESE Theory: 10 Nov – 29 Nov 2025\n\n"
            "**Even Semester:**\n"
            "- Mid-Sem Exams: 23 Mar – 11 Apr 2026\n"
            "- ESE Practical: 01 May – 09 May 2026\n"
            "- ESE Theory: 11 May – 30 May 2026"
        )

    # ----------------------------------------------------------------
    # Semester Subjects
    # ----------------------------------------------------------------

    def _handle_semester_subjects(self, msg, ext):
        sem = ext.get('semester')
        if not sem:
            nums = ext.get('numbers', [])
            for n in nums:
                if 1 <= n <= 8:
                    sem = int(n)
                    break
        if not sem:
            return "Which semester? Please specify like: 'Semester 5 subjects' or '3rd sem subjects'"

        subjects = kb.get_semester_subjects(sem)
        if not subjects:
            # Fallback to DB
            subjects_db = query_db(
                """SELECT s.subject_code, s.subject_name, s.credits, s.subject_type
                   FROM subjects s
                   JOIN semesters sem ON s.semester_id = sem.id
                   WHERE sem.semester_number = %s AND s.is_active = TRUE
                   ORDER BY s.subject_code""",
                (sem,)
            )
            if subjects_db:
                lines = [f"**Semester {sem} Subjects (CSE):**\n",
                         "| Code | Subject | Credits |",
                         "|------|---------|---------|"]
                for s in subjects_db:
                    lines.append(f"| {s['subject_code']} | {s['subject_name']} | {s['credits']} |")
                return '\n'.join(lines)
            return f"No subjects found for Semester {sem}."

        lines = [f"**Semester {sem} Subjects — B.Tech CSE (Indus University)**\n",
                 "| # | Code | Subject | Credits | Practical |",
                 "|---|------|---------|---------|-----------|"]
        total_credits = 0
        for s in subjects:
            has_prac = "Yes" if s.get('teaching_scheme', {}).get('practical_hours', 0) > 0 else "No"
            credits = s.get('credits', 0)
            total_credits += credits
            lines.append(
                f"| {s.get('sr_no', '')} | {s.get('subject_code', '')} "
                f"| {s.get('subject_name', '')} | {credits} | {has_prac} |"
            )
        lines.append(f"\n**Total Credits: {total_credits}**")

        # Add drive link
        link = kb.get_semester_drive_link(sem)
        if link:
            lines.append(f"\n**Study Materials:** [Semester {sem} Drive]({link})")

        return '\n'.join(lines)

    # ----------------------------------------------------------------
    # Subject Info / Course Content
    # ----------------------------------------------------------------

    def _handle_subject_info(self, msg, ext):
        keyword = self._extract_subject_query(msg)
        if not keyword:
            return "Which subject? Please mention the subject name or code (e.g., 'DBMS', 'Data Structures', 'CE0317')."

        # 1. Course content (syllabus / units)
        content = kb.get_course_content(keyword)
        if content:
            units  = content.get('course_units', [])
            s_code = content.get('subject_code', '')
            s_name = content.get('subject_name', '')
            sem    = content.get('semester', '')

            lines = [
                f"**{s_name}** ({s_code})\n",
                f"- **Semester:** {sem}",
                f"- **Total Marks:** {content.get('total_marks', 'N/A')}",
            ]

            # Practical info from subjects_list
            subj_info, sem_num = kb.find_subject_in_list(s_code or keyword)
            if subj_info:
                scheme = subj_info.get('teaching_scheme', {})
                prac_hrs = scheme.get('practical_hours', 0)
                credits  = subj_info.get('credits', 'N/A')
                lines.append(f"- **Credits:** {credits}")
                lines.append(f"- **Has Practical:** {'Yes (%g hrs/week)' % prac_hrs if prac_hrs else 'No'}")

            lines.append("\n**Course Units:**")
            for u in units:
                lines.append(f"\n**{u.get('unit_number', '')} — {u.get('title', '')}** ({u.get('hours', '')} hrs)")
                content_text = u.get('content', '')
                if content_text:
                    preview = content_text[:200] + ('...' if len(content_text) > 200 else '')
                    lines.append(preview)

            # Drive link
            link = kb.get_semester_drive_link(sem_num or sem)
            if link:
                lines.append(f"\n**Study Materials:** [Semester {sem_num or sem} Drive]({link})")
            return '\n'.join(lines)

        # 2. study_materials search (gives drive link)
        matches = kb.find_subjects_by_keyword(keyword)
        if matches:
            m       = matches[0]
            sem     = m.get('semester')
            link    = kb.get_semester_drive_link(sem)
            # Extra detail from subjects_list
            subj_info, sem_num = kb.find_subject_in_list(keyword)
            scheme   = (subj_info or {}).get('teaching_scheme', {})
            prac_hrs = scheme.get('practical_hours', 0)
            credits  = (subj_info or {}).get('credits', m.get('credits', 'N/A'))

            lines = [
                f"**{m.get('name')}** ({m.get('code')})\n",
                f"- **Semester:** {sem}",
                f"- **Credits:** {credits}",
                f"- **Has Practical:** {'Yes (%g hrs/week)' % prac_hrs if prac_hrs else 'No'}",
            ]
            if link:
                lines.append(f"\n**Study Materials:** [Semester {sem} Drive]({link})")
            return '\n'.join(lines)

        # 3. subjects_list direct lookup (code-only query)
        subj_info, sem_num = kb.find_subject_in_list(keyword)
        if subj_info:
            scheme   = subj_info.get('teaching_scheme', {})
            prac_hrs = scheme.get('practical_hours', 0)
            link     = kb.get_semester_drive_link(sem_num)
            lines = [
                f"**{subj_info.get('subject_name')}** ({subj_info.get('subject_code', '')})\n",
                f"- **Semester:** {sem_num}",
                f"- **Credits:** {subj_info.get('credits', 'N/A')}",
                f"- **Has Practical:** {'Yes (%g hrs/week)' % prac_hrs if prac_hrs else 'No'}",
            ]
            if link:
                lines.append(f"\n**Study Materials:** [Semester {sem_num} Drive]({link})")
            return '\n'.join(lines)

        return f"I couldn't find information for '{keyword}'. Try the subject name or code (e.g., 'DBMS', 'CE0317')."

    # ----------------------------------------------------------------
    # Study Materials
    # ----------------------------------------------------------------

    def _handle_study_material(self, msg, ext):
        # Check if a specific semester is requested
        sem = ext.get('semester')
        if not sem:
            nums = ext.get('numbers', [])
            for n in nums:
                if 1 <= n <= 8:
                    sem = int(n)
                    break

        if sem:
            link = kb.get_semester_drive_link(sem)
            if link:
                return (
                    f"**Semester {sem} Study Materials — Indus University CSE**\n\n"
                    f"All notes, PDFs, practicals, and resources for Semester {sem}:\n"
                    f"**[Open Semester {sem} Drive Folder]({link})**\n\n"
                    "_Includes notes, previous year papers, lab manuals and more._"
                )
            return f"Drive link for Semester {sem} is not available yet. Please check with your faculty."

        # Try subject-specific search
        keyword = self._extract_subject_query(msg)
        if keyword:
            matches = kb.find_subjects_by_keyword(keyword)
            if not matches:
                # Fallback: find in subjects_list to get the semester → drive link
                subj_info, sem_num = kb.find_subject_in_list(keyword)
                if subj_info and sem_num:
                    link = kb.get_semester_drive_link(sem_num)
                    s_name = subj_info.get('subject_name', keyword)
                    s_code = subj_info.get('subject_code', '')
                    if link:
                        return (
                            f"Study Materials for {s_name}" + (f" ({s_code})" if s_code else "") + "\n\n"
                            f"You can access the study materials for {s_name}" + (f" ({s_code})" if s_code else "") + " on the following Google Drive link:\n\n"
                            f"{link}\n\n"
                            f"This link contains all the necessary study materials, including lecture notes, assignments, and other relevant documents, for the {s_name} course.\n\n"
                            f"If you have any issues accessing the link or need further assistance, please don't hesitate to ask.\n\n"
                            f"Subject Code: {s_code}\n"
                            f"Subject Name: {s_name}\n"
                            f"Semester: {sem_num}"
                        )
            if matches:
                m    = matches[0]
                sem  = m.get('semester')
                name = m.get('name', keyword)
                code = m.get('code', '')
                link = kb.get_semester_drive_link(sem)
                # Get subject code from subjects_list if not in study_materials
                if not code:
                    subj_info2, _ = kb.find_subject_in_list(keyword)
                    code = (subj_info2 or {}).get('subject_code', '')
                if link:
                    return (
                        f"Study Materials for {name}" + (f" ({code})" if code else "") + "\n\n"
                        f"You can access the study materials for {name}" + (f" ({code})" if code else "") + " on the following Google Drive link:\n\n"
                        f"{link}\n\n"
                        f"This link contains all the necessary study materials, including lecture notes, assignments, and other relevant documents, for the {name} course.\n\n"
                        f"If you have any issues accessing the link or need further assistance, please don't hesitate to ask.\n\n"
                        f"Subject Code: {code}\n"
                        f"Subject Name: {name}\n"
                        f"Semester: {sem}"
                    )

            # Return all drive links
            all_links = kb.study_materials.get('drive_links', {})
            if all_links:
                lines = ["**CSE Study Materials — All Semesters:**\n"]
                for i in range(1, 8):
                    key = f'semester_{i}'
                    link = all_links.get(key)
                    if link:
                        lines.append(f"- [Semester {i} Materials]({link})")
                return '\n'.join(lines)

        return (
            "**CSE Study Material Drive Links:**\n\n"
            "Please specify the semester number or subject name.\n"
            "Example: 'Semester 4 study material' or 'DBMS notes'"
        )

    # ----------------------------------------------------------------
    # Exam Format
    # ----------------------------------------------------------------

    def _handle_exam_format(self, msg, ext):
        return (
            "**Examination System — Indus University CSE**\n\n"
            "**Theory Subjects (100 marks):**\n"
            "- CIE (Internal Assessment): 60 marks\n"
            "- ESE (End Semester Exam): 40 marks\n\n"
            "**Subjects with Practical (200 marks):**\n"
            "- Theory CIE: 60 + Theory ESE: 40 = 100 marks\n"
            "- Practical CIE: 60 + Practical ESE: 40 = 100 marks\n\n"
            "**Key Terms:**\n"
            "- CIE = Continuous Internal Evaluation (internal)\n"
            "- ESE = End Semester Examination (external)\n"
            "- MID = Mid-Semester Exam (part of CIE)\n\n"
            "Type **'grading system'** to see grades, or **'exam dates'** for the schedule."
        )

    # ----------------------------------------------------------------
    # Grading System
    # ----------------------------------------------------------------

    def _handle_grading_system(self, msg, ext):
        gs = kb.get_grading_system()
        ug = gs.get('ug_programs', {})
        scale = ug.get('grade_scale', [])
        degree = kb.get_degree_classes()
        ug_degree = degree.get('ug_programmes', [])

        lines = ["**Grading System — Indus University (UG Programs)**\n",
                 "**Grade Scale (out of 100 marks):**",
                 "| Marks | Grade | Grade Points |",
                 "|-------|-------|-------------|"]

        for g in scale:
            lines.append(f"| {g.get('marks_range')} | **{g.get('letter_grade')}** | {g.get('grade_points')} |")

        lines += [
            "\n**Special Indicators:**",
            "- **AB** = Absent (backlog) | **F** = Fail (backlog)",
            "- **\\*** = Carry-forwarded marks | **+** = Passed with grace marks",
            "\n**Degree Classification (based on FGPA):**",
        ]
        for d in ug_degree:
            lines.append(f"- {d.get('class')}: {d.get('fgpa_range')}")

        lines.append("\n**CGPA → Percentage Formula:** `Percentage = (CGPA − 0.5) × 10`")
        return '\n'.join(lines)

    # ----------------------------------------------------------------
    # Grade for Marks
    # ----------------------------------------------------------------

    def _handle_grade_for_marks(self, msg, ext):
        nums = ext.get('numbers', [])
        marks = None
        for n in nums:
            if 0 <= n <= 200:
                marks = int(n)
                break
        if marks is None:
            return "Please tell me the marks. Example: 'What grade for 75 marks?' or 'I scored 145 out of 200'"

        # Try subject lookup to auto-detect correct total marks
        total = None
        subject_name = None
        keyword = self._extract_subject_query(msg)
        if keyword:
            subj_info, _ = kb.find_subject_in_list(keyword)
            if subj_info:
                total = subj_info.get('evaluation_scheme', {}).get('total_marks')
                subject_name = subj_info.get('subject_name', keyword)

        if total is None:
            total = 200 if marks > 100 else 100

        grade, points = kb.get_grade_for_marks(marks, total)
        percentage = round((marks / total) * 100, 1)
        status = "PASS" if grade not in ('F', 'AB') else "FAIL/BACKLOG"

        header = f"**Grade for {marks}/{total} marks"
        if subject_name:
            header += f" in {subject_name}"
        header += ":**\n"

        return (
            f"{header}\n"
            f"- Percentage: **{percentage}%**\n"
            f"- Letter Grade: **{grade}**\n"
            f"- Grade Points: **{points}**\n"
            f"- Status: **{status}**"
        )

    # ----------------------------------------------------------------
    # Passing / Minimum Marks
    # ----------------------------------------------------------------

    def _handle_passing_marks(self, msg, ext):
        """Answer 'what are the passing marks for [subject]?' and similar questions."""
        # Check if a specific total is explicitly mentioned (100 or 200)
        explicit_total = None
        for n in ext.get('numbers', []):
            if n in (100, 200):
                explicit_total = int(n)
                break

        # Try to find a subject name in the message
        keyword = self._extract_subject_query(msg)
        subj_info, sem_num = (None, None)
        if keyword:
            subj_info, sem_num = kb.find_subject_in_list(keyword)

        if subj_info:
            # Subject-specific response
            name    = subj_info.get('subject_name', keyword)
            code    = subj_info.get('subject_code', '')
            scheme  = subj_info.get('evaluation_scheme', {})
            theory  = scheme.get('theory', {})
            prac    = scheme.get('practical', {})
            total   = scheme.get('total_marks', 100)
            has_prac = (prac.get('CIE', 0) + prac.get('ESE', 0)) > 0

            pass_total = int(total * 0.40)
            grade, points = kb.get_grade_for_marks(pass_total, total)

            subj_label = f"**{name}**" + (f" ({code})" if code else "")
            lines = [
                f"**Passing Marks — {subj_label}**\n",
                f"- **Total Marks:** {total}",
                f"- **Minimum Marks to Pass:** {pass_total}/{total} (40%)",
                f"- **Passing Grade:** {grade} ({points} grade points)",
            ]
            if sem_num:
                lines.append(f"- **Semester:** {sem_num}")

            if has_prac:
                t_total = theory.get('CIE', 60) + theory.get('ESE', 40)
                p_total = prac.get('CIE', 60) + prac.get('ESE', 40)
                t_pass  = int(t_total * 0.40)
                p_pass  = int(p_total * 0.40)
                lines += [
                    "\n**Component Breakdown:**",
                    f"- Theory  (CIE {theory.get('CIE',60)} + ESE {theory.get('ESE',40)} = **{t_total}** marks) → min **{t_pass}** marks",
                    f"- Practical (CIE {prac.get('CIE',60)} + ESE {prac.get('ESE',40)} = **{p_total}** marks) → min **{p_pass}** marks",
                ]
            else:
                t_cie = theory.get('CIE', 60)
                t_ese = theory.get('ESE', 40)
                lines += [
                    "\n**Component Breakdown:**",
                    f"- CIE (Internal): {t_cie} marks",
                    f"- ESE (End Semester Exam): {t_ese} marks",
                ]

            lines.append(
                f"\nScoring below **{pass_total}** → **Grade F** (Fail / Backlog)"
            )
            return '\n'.join(lines)

        total = explicit_total

        if total:
            # Generic response for a known total (100 or 200)
            pass_marks = int(total * 0.40)
            grade, points = kb.get_grade_for_marks(pass_marks, total)
            return (
                f"**Passing Marks for a {total}-mark Subject:**\n\n"
                f"- **Minimum Marks to Pass:** {pass_marks}/{total} (40%)\n"
                f"- **Passing Grade:** {grade} ({points} grade points)\n\n"
                f"Scoring below **{pass_marks}** → **Grade F** (Fail / Backlog)\n\n"
                "**At Indus University:**\n"
                "- 100-mark subjects (theory only): minimum **40 marks**\n"
                "- 200-mark subjects (theory + practical): minimum **80 marks**"
            )

        # Generic overview of all passing thresholds
        return (
            "**Passing Marks — Indus University (UG Programs)**\n\n"
            "**Theory-only subjects (100 marks total):**\n"
            "- CIE (Internal): 60 marks + ESE (Exam): 40 marks = **100 total**\n"
            "- **Minimum to pass: 40 out of 100 (40%)**\n"
            "- Passing Grade: **P** (40–44 marks, 4 grade points)\n\n"
            "**Theory + Practical subjects (200 marks total):**\n"
            "- Theory: CIE 60 + ESE 40 = 100 marks\n"
            "- Practical: CIE 60 + ESE 40 = 100 marks\n"
            "- **Minimum to pass: 80 out of 200 (40%)**\n"
            "- Passing Grade: **P** (80–89 marks, 4 grade points)\n\n"
            "Scoring below the minimum → **Grade F** (Fail / Backlog)\n\n"
            "Ask about a specific subject, e.g. _'passing marks for AJT'_ or "
            "_'minimum marks for Operating System'_ for exact details."
        )

    # ----------------------------------------------------------------
    # CGPA / SGPA
    # ----------------------------------------------------------------

    def _handle_sgpa(self, msg, ext):
        return format_sgpa_explanation()

    def _handle_cgpa(self, msg, ext):
        return format_cgpa_explanation()

    def _handle_cgpa_to_percent(self, msg, ext):
        nums = ext.get('numbers', [])
        cgpa_val = None
        for n in nums:
            if 0 < n <= 10:
                cgpa_val = n
                break

        if cgpa_val is not None:
            percentage = kb.cgpa_to_percentage(cgpa_val)
            return (
                f"**CGPA to Percentage Conversion (Indus University):**\n\n"
                f"CGPA **{cgpa_val}** → **{percentage}%**\n\n"
                f"**Formula:** Percentage = (CGPA − 0.5) × 10\n"
                f"= ({cgpa_val} − 0.5) × 10 = **{percentage}%**"
            )

        return (
            "To convert CGPA to percentage, tell me your CGPA.\n"
            "Example: 'Convert **8.5** CGPA to percentage'\n\n"
            "**Indus University Formula:** Percentage = (CGPA − 0.5) × 10"
        )

    # ----------------------------------------------------------------
    # Re-Assessment & Re-Checking
    # ----------------------------------------------------------------

    def _handle_reassessment(self, msg, ext):
        fees = kb.get_reassessment_fees()
        elig = kb.get_reassessment_eligibility()
        proc = kb.get_reassessment_procedure()
        msg_lower = msg.lower()

        ra_fees = fees.get('re_assessment', {})
        rc_fees = fees.get('re_checking', {})

        lines = ["**Re-Assessment & Re-Checking — Indus University**\n"]

        if 'recheck' in msg_lower or 're-check' in msg_lower or 'checking' in msg_lower:
            rc = proc.get('re_checking', {})
            lines += [
                "**Re-Checking (Marks Verification):**",
                f"- Fee (without late fees): ₹{rc_fees.get('without_late_fees', {}).get('amount', 500):,} per course",
                f"- Fee (with late fees): ₹{rc_fees.get('with_late_fees', {}).get('amount', 1000):,} per course",
                f"- **Refund Policy:** {fees.get('refund_policy', 'Non-refundable')}",
                "\n**What gets checked:**",
            ]
            for step in rc.get('steps', []):
                lines.append(f"  - {step}")
        else:
            ra = proc.get('re_assessment', {})
            lines += [
                "**Re-Assessment (Full Re-Evaluation):**",
                f"- Fee (without late fees): ₹{ra_fees.get('without_late_fees', {}).get('amount', 1000):,} per course",
                f"- Fee (with late fees): ₹{ra_fees.get('with_late_fees', {}).get('amount', 2000):,} per course",
                f"- **Refund Policy:** {fees.get('refund_policy', 'Non-refundable')}",
                "\n**Re-Checking Fee (done first):**",
                f"- ₹{rc_fees.get('without_late_fees', {}).get('amount', 500):,} / ₹{rc_fees.get('with_late_fees', {}).get('amount', 1000):,} (with late fees)",
            ]

        lines += [
            "\n**Eligibility:**",
            f"- Allowed for: {', '.join(elig.get('allowed_for', ['End Semester Theory subjects only']))}",
            "- NOT allowed for: Mid Semester Exam, CIE, Term Work, Project, Practical",
        ]
        for rule in elig.get('special_rules', []):
            lines.append(f"- {rule}")

        return '\n'.join(lines)

    # ----------------------------------------------------------------
    # Library
    # ----------------------------------------------------------------

    def _handle_library(self, msg, ext):
        msg_lower = msg.lower()
        circ = kb.get_library_circulation()
        loans = kb.get_library_loan_periods()

        if 'fine' in msg_lower or 'overdue' in msg_lower or 'penalty' in msg_lower:
            return (
                "**Library Overdue Fine — Indus University**\n\n"
                "- Fine: **₹2/- per item per day** (applicable to all categories)\n"
                "- Lost/Damaged book: Replace the book **OR** pay **3× the cost** of the book\n"
                "- Max renewals: 2 consecutive renewals (if no demand from others)\n\n"
                "Return books on time to avoid fines!"
            )

        if any(w in msg_lower for w in ('hour', 'time', 'open', 'close', 'timing')):
            return (
                "**Library Hours — Indus University**\n\n"
                "- Open on all **working days: 9:00 AM to 5:00 PM**\n"
                "- Not accessible during lectures, practicals, or tutorials\n\n"
                "**Note:** ID card is mandatory for library access."
            )

        if any(w in msg_lower for w in ('borrow', 'issue', 'take', 'how many', 'limit')):
            lines = ["**Library Borrowing Limits — Indus University**\n"]
            if loans:
                lines.append("| Category | Max Books | Duration |")
                lines.append("|----------|-----------|----------|")
                for entry in loans:
                    cat = entry.get('category', '')
                    books = entry.get('max_books', '')
                    dur = entry.get('duration', '')
                    lines.append(f"| {cat} | {books} | {dur} |")
            else:
                lines += [
                    "| Category | Max Books | Duration |",
                    "|----------|-----------|----------|",
                    "| Students | 3 books | 15 days |",
                    "| Faculty | 7 books | Until Term End |",
                    "| Staff | 7 books | Until Term End |",
                    "| Visiting Faculty | 2 books | 15 days |",
                ]
            lines.append("\n**Reference books:** Maximum 24 hours only")
            lines.append("**Journals:** Cannot be taken outside (photocopies allowed)")
            return '\n'.join(lines)

        # General library rules
        return (
            "**Library Policy — Indus University**\n\n"
            "**Borrowing Limits:**\n"
            "- Students: 3 books / 15 days\n"
            "- Faculty & Staff: 7 books / until Term End\n"
            "- Visiting Faculty: 2 books / 15 days\n\n"
            "**Fines:** ₹2/- per item per day (overdue)\n\n"
            "**Important Rules:**\n"
            "- ID card is compulsory for library access\n"
            "- Bags, laptops, and personal belongings NOT allowed inside\n"
            "- Mobile phones must be on silent mode\n"
            "- Reference books: max 24 hours issue\n"
            "- Journals cannot be taken outside\n"
            "- Lost/damaged books: replace OR pay 3× cost\n"
            "- **No Due certificate** mandatory before receiving Hall Ticket for ESE\n\n"
            "**Library Hours:** 9:00 AM – 5:00 PM (all working days)\n\n"
            "Ask about **fines**, **borrowing limits**, or **library timings** for more detail."
        )

    # ----------------------------------------------------------------
    # Discipline Rules
    # ----------------------------------------------------------------

    def _handle_discipline(self, msg, ext):
        msg_lower = msg.lower()

        if any(w in msg_lower for w in ('dress', 'uniform', 'formal', 'clothes', 'attire')):
            dress = kb.get_dress_code_rules()
            rules_list = dress.get('key_rules', []) if dress else []
            if rules_list:
                lines = ["**Dress Code — Indus University**\n"]
                for r in rules_list[:8]:
                    lines.append(f"- {r}")
                return '\n'.join(lines)
            return (
                "**Dress Code Rules:**\n"
                "- Semi-formal dress code required at all times\n"
                "- T-shirts with objectionable content not allowed\n"
                "- Girls: Skirts/pants must be at least knee-length\n"
                "- Boys: Shorts or three-fourths NOT permitted\n"
                "- Closed shoes mandatory in labs and workshops\n"
                "- Formals required for oral exams, interviews, and placements\n"
                "- ID card must be worn at all times on campus"
            )

        if any(w in msg_lower for w in ('ragging', 'rag')):
            return (
                "**Ragging — Indus University Policy**\n\n"
                "- Ragging is **STRICTLY PROHIBITED** in all forms\n"
                "- Applies inside class, campus, bus, and outside campus\n"
                "- **Consequences:** May result in expulsion; noted in migration certificate\n"
                "- Anti-Ragging undertaking is mandatory at admission\n"
                "- Report any ragging incident to the HOD or Director immediately\n\n"
                "Every student and parent/guardian must sign the Anti-Ragging Undertaking at admission."
            )

        if any(w in msg_lower for w in ('mobile', 'phone', 'cell')):
            return (
                "**Mobile Phone Policy — Indus University**\n\n"
                "- Mobile phones are **STRICTLY PROHIBITED** in:\n"
                "  - Classrooms\n"
                "  - Library\n"
                "  - Labs and Workshops\n"
                "  - Examination Halls\n"
                "  - Corridors during class hours\n\n"
                "- Misuse of internet/intranet/mobile is also prohibited\n"
                "- Violation leads to disciplinary action"
            )

        if any(w in msg_lower for w in ('hostel', 'dorm', 'room')):
            hostel = kb.get_hostel_rules()
            key_rules = hostel.get('key_rules', []) if hostel else []
            if key_rules:
                lines = ["**Hostel Rules — Indus University**\n"]
                for r in key_rules[:8]:
                    lines.append(f"- {r}")
                return '\n'.join(lines)
            return (
                "**Hostel Rules:**\n"
                "- Students must return to hostel by designated curfew time\n"
                "- Boys and girls may interact ONLY in designated common areas\n"
                "- Entry into each other's rooms is STRICTLY prohibited\n"
                "- Overnight stay outside requires written permission\n"
                "- Gambling, alcohol, and narcotics strictly prohibited\n"
                "- Guests cannot stay overnight\n"
                "- Helmet compulsory for two-wheeler riders (penalty: ₹500 or restricted entry)"
            )

        if any(w in msg_lower for w in ('penalty', 'punishment', 'fine', 'suspension', 'rustication')):
            penalties = kb.get_penalties()
            major = penalties.get('major_penalties', []) if penalties else []
            minor = penalties.get('minor_penalties', []) if penalties else []
            lines = ["**Disciplinary Penalties — Indus University**\n", "**Major Penalties:**"]
            for p in (major or [
                "Police action for criminal acts",
                "Prohibition from appearing in exams",
                "Detention for semester(s)",
                "Rustication (temporary or permanent)",
                "Collective punishment if individual offenders not identified",
            ]):
                lines.append(f"- {p}")
            lines.append("\n**Minor Penalties:**")
            for p in (minor or [
                "Warning / Fine", "Special assignments",
                "Conduct probation", "Suspension from classes (up to 1 week)",
                "Prohibition from Mid-Semester exams",
            ]):
                lines.append(f"- {p}")
            return '\n'.join(lines)

        # General discipline overview
        conduct_rules = kb.get_conduct_rules()
        lines = ["**Student Discipline Rules — Indus University**\n",
                 "**Key Rules (Summary):**"]
        selected = [r for r in (conduct_rules or []) if len(r) < 120][:6]
        if selected:
            for r in selected:
                lines.append(f"- {r}")
        else:
            lines += [
                "- ID card must be worn at all times on campus",
                "- Semi-formal dress code required",
                "- Mobile phones prohibited in class, library, labs, exam halls",
                "- Ragging strictly prohibited (expulsion possible)",
                "- Smoking, alcohol, drugs strictly prohibited (rustication)",
                "- Politics on campus is prohibited",
            ]

        lines.append("\nAsk about **dress code**, **ragging**, **mobile policy**, **hostel rules**, or **penalties**.")
        return '\n'.join(lines)

    # ----------------------------------------------------------------
    # Placement
    # ----------------------------------------------------------------

    def _handle_placement(self, msg, ext):
        stats = kb.get_placement_stats()
        training = kb.get_training_programs()
        recruiters = kb.get_top_recruiters()
        contact = kb.placement.get('contact', {})
        msg_lower = msg.lower()

        if any(w in msg_lower for w in ('training', 'prepare', 'skill', 'mock')):
            lines = ["**Placement Training Programs — Indus University T&P Dept.**\n",
                     "**Programs Offered:**"]
            for p in (training or [
                "CV Writing", "Communication Skills (Written/Spoken)",
                "Employability Skill Tests", "Domain-Specific Technical Training",
                "Aptitude, Technical & Psychometric Test Practice",
                "Group Discussion (GD) Sessions", "Mock Interviews by Industry Experts",
                "Finishing School Training before Campus Drives",
            ]):
                lines.append(f"- {p}")
            return '\n'.join(lines)

        if any(w in msg_lower for w in ('company', 'compan', 'recruit', 'who', 'which')):
            lines = ["**Top Recruiting Companies — Indus University**\n"]
            if recruiters:
                lines.append(', '.join(str(r) for r in recruiters))
            else:
                lines.append("Amazon, Capgemini, Oracle, Samsung, Siemens, Tata Motors, Godrej, "
                             "Adani, BYJU's, Bajaj Allianz, IDFC First Bank, IndusInd Bank, "
                             "Odoo, Decathlon, JSW Paints, KIA and many more")
            return '\n'.join(lines)

        high = stats.get('highest_package', {})
        avg = stats.get('average_package', 'Rs. 6.8 LPA')
        tpo_num = contact.get('training_and_placement_officer', '+91 9879611169')

        return (
            "**Training & Placement — Indus University**\n\n"
            f"- **Highest Package:** {high.get('amount', 'Rs. 30 LPA')} ({high.get('company', 'LUMMO, Jakarta')})\n"
            f"- **Average Package:** {avg}\n\n"
            "**Services:**\n"
            "- On-Campus & Off-Campus recruitment drives\n"
            "- CV writing, mock interviews, GD sessions\n"
            "- Internships and live projects\n"
            "- Guest lectures & industrial visits\n\n"
            f"**T&P Office Contact:** {tpo_num}\n\n"
            "Ask about **training programs**, **recruiting companies**, or **internships**."
        )

    # ----------------------------------------------------------------
    # Legacy Handlers
    # ----------------------------------------------------------------

    def _handle_back_paper(self, msg, ext):
        # Route to re-assessment handler as it covers this topic
        return self._handle_reassessment(msg, ext)

    def _handle_notices(self, msg, ext):
        notices = query_db(
            """SELECT title, content, notice_type, created_at FROM notices
               WHERE is_active = TRUE AND (expires_at IS NULL OR expires_at > NOW())
               ORDER BY created_at DESC LIMIT 5"""
        )
        if not notices:
            return "No active notices at the moment. Check back later or visit the Indus University website."

        lines = ["**Latest Notices:**\n"]
        for n in notices:
            date_str = n['created_at'].strftime('%d %b %Y') if n['created_at'] else ''
            lines.append(f"**[{n['notice_type'].upper()}]** {n['title']}")
            lines.append(f"_{date_str}_")
            preview = n['content'][:150] + ('...' if len(n['content']) > 150 else '')
            lines.append(f"{preview}\n")
        return '\n'.join(lines)

    def _handle_academic_rule(self, msg, ext):
        rules = query_db(
            "SELECT rule_title, rule_content, keywords FROM academic_rules WHERE is_active = TRUE"
        )
        if not rules:
            return "Please contact the CSE Department office for academic rule queries."
        msg_lower = msg.lower()
        best_rule, best_score = None, 0
        for r in rules:
            score = sum(1 for kw in (r.get('keywords') or '').lower().split(',')
                        if kw.strip() and kw.strip() in msg_lower)
            if score > best_score:
                best_score = score
                best_rule = r
        if best_rule and best_score > 0:
            return f"**{best_rule['rule_title']}**\n\n{best_rule['rule_content']}"
        return (
            "I have academic rule information. Please be more specific.\n"
            "Examples: 'Attendance rule', 'Branch change policy', 'Examination rules'"
        )

    def _handle_unknown(self, msg, ext):
        """
        Smart fallback when AI is unavailable and intent is unknown.
        Tries keyword matching against all knowledge-base topics before
        giving up with the generic response.
        """
        msg_lower = msg.lower()

        # Fee related
        if any(w in msg_lower for w in ('fee', 'tuition', 'cost', 'pay', 'installment', 'emi')):
            return self._handle_fee_structure(msg, ext)

        # Attendance related
        if any(w in msg_lower for w in ('attendance', 'present', 'absent', 'lecture', 'bunk', 'eligible')):
            return self._handle_attendance_rule(msg, ext)

        # MYSY scholarship
        if any(w in msg_lower for w in ('mysy', 'scholarship', 'grant')):
            return self._handle_mysy(msg, ext)

        # Academic calendar / dates
        if any(w in msg_lower for w in ('exam', 'date', 'schedule', 'calendar', 'holiday', 'vacation', 'term', 'when')):
            return self._handle_academic_calendar(msg, ext)

        # Grading / CGPA
        if any(w in msg_lower for w in ('grade', 'cgpa', 'sgpa', 'gpa', 'percentage', 'distinction', 'first class')):
            return self._handle_grading_system(msg, ext)

        # Passing marks
        if any(w in msg_lower for w in ('pass', 'passing', 'minimum mark', 'fail', 'backlog', 'clear')):
            return self._handle_passing_marks(msg, ext)

        # Subjects / syllabus
        if any(w in msg_lower for w in ('subject', 'syllabus', 'course', 'topic', 'unit', 'credit')):
            # Try to find a specific subject first
            keyword = self._extract_subject_query(msg)
            if keyword:
                return self._handle_subject_info(msg, ext)
            sem = ext.get('semester')
            if sem:
                return self._handle_semester_subjects(msg, ext)
            return self._handle_semester_subjects(msg, ext)

        # Study materials
        if any(w in msg_lower for w in ('note', 'material', 'drive', 'link', 'pdf', 'pyq', 'study material')):
            return self._handle_study_material(msg, ext)

        # Exam format
        if any(w in msg_lower for w in ('cie', 'ese', 'internal', 'external', 'exam pattern', 'marking', 'format')):
            return self._handle_exam_format(msg, ext)

        # Library
        if any(w in msg_lower for w in ('library', 'book', 'borrow', 'fine', 'overdue')):
            return self._handle_library(msg, ext)

        # Placement
        if any(w in msg_lower for w in ('placement', 'job', 'company', 'package', 'salary', 'recruit', 'internship')):
            return self._handle_placement(msg, ext)

        # Discipline
        if any(w in msg_lower for w in ('discipline', 'dress', 'mobile', 'hostel', 'ragging', 'penalty', 'rule')):
            return self._handle_discipline(msg, ext)

        # Re-assessment
        if any(w in msg_lower for w in ('reassess', 'recheck', 'back paper', 'supplementary', 'supply', 'reappear')):
            return self._handle_reassessment(msg, ext)

        # Subject keyword lookup as last resort
        keyword = self._extract_subject_query(msg)
        if keyword:
            result = self._handle_subject_info(msg, ext)
            if 'couldn\'t find' not in result.lower():
                return result

        return UNKNOWN_RESPONSE

    # ----------------------------------------------------------------
    # Helpers
    # ----------------------------------------------------------------

    def _extract_subject_query(self, msg):
        """Extract a likely subject name or code from the message.

        Recognises subject codes (CE0317), known abbreviations (AJT, OS, DBMS),
        and plain keywords.  Abbreviations are expanded to their full subject name
        so downstream searches work correctly.
        """
        msg_lower = msg.lower()
        stop_words = {
            'give', 'me', 'the', 'of', 'for', 'about', 'tell', 'what', 'is',
            'are', 'notes', 'material', 'study', 'resource', 'book', 'pdf', 'pyq',
            'previous', 'year', 'papers', 'syllabus', 'topics', 'content', 'subject',
            'course', 'please', 'can', 'you', 'i', 'want', 'need', 'get', 'share',
            'send', 'provide', 'info', 'information', 'on', 'in', 'a', 'an', 'to',
            'my', 'explain', 'details', 'detail', 'drive', 'link', 'google',
            # passing / grading query words
            'passing', 'minimum', 'marks', 'mark', 'pass', 'fail', 'score',
            'how', 'many', 'required', 'needed', 'clear', 'min', 'max',
            'maximum', 'total', 'out', 'grade', 'grading', 'minimum',
            'criteria', 'will', 'if', 'with', 'below', 'above', 'under',
            'least', 'least', 'than', 'more', 'less', 'and', 'or', 'not',
        }
        # 1. Subject code (e.g., CE0317)
        code_match = re.search(r'\b([A-Za-z]{2}\d{3,4}[A-Za-z]?)\b', msg)
        if code_match:
            return code_match.group(1).upper()

        # 2. Extract meaningful words; allow short words that are known abbreviations
        abbr_map = getattr(kb, '_abbr_map', {})
        words = re.findall(r'[a-zA-Z]+', msg_lower)
        meaningful = [
            w for w in words
            if w not in stop_words and (len(w) > 2 or w.upper() in abbr_map)
        ]
        if not meaningful:
            return None

        keyword = ' '.join(meaningful)

        # 3. Expand any abbreviations found (e.g., 'ajt' → 'Advanced Java Technology')
        expanded = kb.expand_abbreviation(keyword)
        return expanded if expanded else keyword

    def _log_query(self, user_id, query_text, intent, response, confidence, elapsed_ms):
        try:
            execute_db(
                """INSERT INTO query_logs
                   (user_id, query_text, detected_intent, response_text, confidence, response_time_ms)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (user_id, query_text, intent, response[:500], confidence, elapsed_ms)
            )
        except Exception:
            pass

    def _log_unanswered(self, user_id, query_text, intent):
        try:
            existing = query_db(
                "SELECT id FROM unanswered_queries WHERE LOWER(query_text) = LOWER(%s) AND is_resolved = FALSE",
                (query_text,), one=True
            )
            if existing:
                execute_db("UPDATE unanswered_queries SET times_asked = times_asked + 1 WHERE id = %s",
                           (existing['id'],))
            else:
                execute_db(
                    "INSERT INTO unanswered_queries (user_id, query_text, detected_intent) VALUES (%s, %s, %s)",
                    (user_id, query_text, intent)
                )
        except Exception:
            pass
