"""
Main chatbot engine.
Processes user messages, detects intent, queries DB, and generates responses.
"""
import re
import time
from .intents import recognize_intent
from .attendance import parse_attendance_from_text, calculate_attendance, format_attendance_response
from .cgpa import (
    format_sgpa_explanation, format_cgpa_explanation, cgpa_to_percentage,
)
from .responses import (
    GREETING_RESPONSES, FAREWELL_RESPONSES, HELP_RESPONSE,
    UNKNOWN_RESPONSE, PLACEMENT_RESPONSE,
)
from database import query_db, execute_db


class ChatbotEngine:
    """Core chatbot processor."""

    def process(self, user_message, user_id=None):
        """
        Process a user message and return a response dict.
        Returns: {
            'response': str,
            'intent': str,
            'confidence': float,
            'response_time_ms': int
        }
        """
        start = time.time()
        intent, confidence, extracted = recognize_intent(user_message)

        # Route to handler
        handler_map = {
            'greeting':              self._handle_greeting,
            'farewell':              self._handle_farewell,
            'help':                  self._handle_help,
            'attendance_calculate':  self._handle_attendance_calc,
            'attendance_eligibility': self._handle_attendance_eligibility,
            'attendance_rule':       self._handle_attendance_rule,
            'semester_subjects':     self._handle_semester_subjects,
            'subject_info':          self._handle_subject_info,
            'study_material':        self._handle_study_material,
            'exam_pattern':          self._handle_exam_pattern,
            'back_paper':            self._handle_back_paper,
            'cgpa_calculate':        self._handle_cgpa,
            'sgpa_calculate':        self._handle_sgpa,
            'cgpa_to_percentage':    self._handle_cgpa_to_percent,
            'notices':               self._handle_notices,
            'academic_rule':         self._handle_academic_rule,
            'placement':             self._handle_placement,
        }

        handler = handler_map.get(intent, self._handle_unknown)
        response_text = handler(user_message, extracted)

        elapsed_ms = int((time.time() - start) * 1000)

        # Log query
        self._log_query(user_id, user_message, intent, response_text, confidence, elapsed_ms)

        # Log unanswered if unknown
        if intent == 'unknown':
            self._log_unanswered(user_id, user_message, intent)

        return {
            'response': response_text,
            'intent': intent,
            'confidence': confidence,
            'response_time_ms': elapsed_ms,
        }

    # ----------------------------------------------------------------
    # Intent Handlers
    # ----------------------------------------------------------------

    def _handle_greeting(self, msg, ext):
        return GREETING_RESPONSES[0]

    def _handle_farewell(self, msg, ext):
        return FAREWELL_RESPONSES[0]

    def _handle_help(self, msg, ext):
        return HELP_RESPONSE

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
            "**Quick rules:**\n"
            "- **75%+** → Eligible\n"
            "- **65-75%** → Eligible with fine (condonation)\n"
            "- **Below 65%** → Debarred from exams"
        )

    def _handle_attendance_rule(self, msg, ext):
        rules = query_db(
            "SELECT rule_content FROM academic_rules WHERE rule_category = 'attendance' AND is_active = TRUE"
        )
        if rules:
            parts = ["**Attendance Rules:**\n"]
            for i, r in enumerate(rules, 1):
                parts.append(f"{i}. {r['rule_content']}")
            return '\n\n'.join(parts)

        return (
            "**Attendance Policy:**\n"
            "- Minimum **75%** attendance required for exam eligibility\n"
            "- 65-75%: Allowed with condonation (fine)\n"
            "- Below 65%: **Debarred** from examinations\n"
            "- Medical cases reviewed individually by the Dean"
        )

    def _handle_semester_subjects(self, msg, ext):
        sem = ext.get('semester')
        if not sem:
            nums = ext.get('numbers', [])
            for n in nums:
                if 1 <= n <= 8:
                    sem = int(n)
                    break
        if not sem:
            return "Which semester? Please specify like: 'Semester 5 subjects' or 'subjects in 3rd sem'"

        subjects = query_db(
            """SELECT s.subject_code, s.subject_name, s.credits, s.subject_type
               FROM subjects s
               JOIN semesters sem ON s.semester_id = sem.id
               WHERE sem.semester_number = %s AND s.is_active = TRUE
               ORDER BY s.subject_code""",
            (sem,)
        )
        if not subjects:
            return f"No subjects found for Semester {sem}. The data might not be loaded yet."

        lines = [f"**Semester {sem} Subjects (CSE):**\n"]
        lines.append("| Code | Subject | Credits | Type |")
        lines.append("|------|---------|---------|------|")
        total_credits = 0
        for s in subjects:
            lines.append(f"| {s['subject_code']} | {s['subject_name']} | {s['credits']} | {s['subject_type'].title()} |")
            total_credits += s['credits']
        lines.append(f"\n**Total Credits: {total_credits}**")
        return '\n'.join(lines)

    def _handle_subject_info(self, msg, ext):
        # Try to find subject name in the message
        subject = self._extract_subject_query(msg)
        if not subject:
            return "Which subject would you like to know about? Please mention the subject name or code."

        row = query_db(
            """SELECT s.subject_code, s.subject_name, s.credits, s.subject_type,
                      s.syllabus_brief, sem.semester_number
               FROM subjects s
               JOIN semesters sem ON s.semester_id = sem.id
               WHERE LOWER(s.subject_name) LIKE %s OR LOWER(s.subject_code) LIKE %s
               LIMIT 1""",
            (f'%{subject}%', f'%{subject}%'),
            one=True
        )
        if not row:
            return f"I couldn't find a subject matching '{subject}'. Try the full name or code (e.g., CS201, Data Structures)."

        lines = [
            f"**{row['subject_name']}** ({row['subject_code']})\n",
            f"- **Semester:** {row['semester_number']}",
            f"- **Credits:** {row['credits']}",
            f"- **Type:** {row['subject_type'].title()}",
        ]
        if row['syllabus_brief']:
            lines.append(f"- **Syllabus:** {row['syllabus_brief']}")
        return '\n'.join(lines)

    def _handle_study_material(self, msg, ext):
        subject = self._extract_subject_query(msg)
        if not subject:
            return "Which subject do you need study material for? Please mention the name or code."

        materials = query_db(
            """SELECT sm.material_title, sm.material_type, sm.drive_link,
                      s.subject_name, s.subject_code
               FROM subject_materials sm
               JOIN subjects s ON sm.subject_id = s.id
               WHERE LOWER(s.subject_name) LIKE %s OR LOWER(s.subject_code) LIKE %s
               ORDER BY sm.material_type""",
            (f'%{subject}%', f'%{subject}%')
        )
        if not materials:
            return (
                f"No study materials found for '{subject}' yet.\n"
                "Materials are being added by admins. Check back later or ask your professor."
            )

        subj_name = materials[0]['subject_name']
        lines = [f"**Study Materials for {subj_name}:**\n"]
        for m in materials:
            emoji_map = {'notes': 'Notes', 'pyq': 'PYQ', 'book': 'Book', 'video': 'Video', 'syllabus': 'Syllabus', 'other': 'Other'}
            label = emoji_map.get(m['material_type'], 'Other')
            lines.append(f"- **[{label}]** [{m['material_title']}]({m['drive_link']})")

        return '\n'.join(lines)

    def _handle_exam_pattern(self, msg, ext):
        msg_lower = msg.lower()
        if 'practical' in msg_lower or 'lab' in msg_lower:
            category_match = 'practical'
        else:
            category_match = 'theory'

        rules = query_db(
            """SELECT rule_title, rule_content FROM academic_rules
               WHERE rule_category = 'examination'
                 AND LOWER(rule_title) LIKE %s
                 AND is_active = TRUE""",
            (f'%{category_match}%',)
        )
        if rules:
            lines = []
            for r in rules:
                lines.append(f"**{r['rule_title']}**\n{r['rule_content']}")
            return '\n\n'.join(lines)

        # Fallback: return all exam rules
        rules = query_db(
            "SELECT rule_title, rule_content FROM academic_rules WHERE rule_category = 'examination' AND is_active = TRUE"
        )
        if rules:
            lines = [f"**{r['rule_title']}**\n{r['rule_content']}" for r in rules]
            return '\n\n'.join(lines)

        return (
            "**Standard Exam Pattern (Theory):**\n"
            "- Internal Assessment: 30 marks (2 mid-terms)\n"
            "- End Semester: 70 marks (5 questions, attempt 3)\n"
            "- Passing: 40% overall, minimum 28 in end-sem"
        )

    def _handle_back_paper(self, msg, ext):
        rule = query_db(
            "SELECT rule_content FROM academic_rules WHERE LOWER(rule_title) LIKE '%supplementary%' AND is_active = TRUE",
            one=True
        )
        if rule:
            return f"**Back Paper / Supplementary Exam:**\n\n{rule['rule_content']}"

        return (
            "**Back Paper / Supplementary Exam:**\n"
            "- Available for students who fail end-semester exams\n"
            "- Conducted before next semester starts\n"
            "- Maximum 3 attempts per subject\n"
            "- Fee: Rs. 500 per subject per attempt\n"
            "- Results declared within 2 weeks"
        )

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
            result = cgpa_to_percentage(cgpa_val)
            if 'error' in result:
                return result['error']
            return (
                f"**CGPA to Percentage Conversion:**\n\n"
                f"CGPA **{result['cgpa']}** = **{result['percentage']}%**\n\n"
                f"Formula: CGPA x 10 = Percentage"
            )

        return (
            "To convert CGPA to percentage, just tell me your CGPA.\n"
            "For example: 'Convert **8.5** CGPA to percentage'\n\n"
            "**Formula:** CGPA x 10 = Percentage"
        )

    def _handle_notices(self, msg, ext):
        notices = query_db(
            """SELECT title, content, notice_type, created_at
               FROM notices
               WHERE is_active = TRUE
                 AND (expires_at IS NULL OR expires_at > NOW())
               ORDER BY created_at DESC
               LIMIT 5"""
        )
        if not notices:
            return "No active notices at the moment. Check back later!"

        lines = ["**Latest Notices:**\n"]
        for n in notices:
            date_str = n['created_at'].strftime('%d %b %Y') if n['created_at'] else ''
            type_label = n['notice_type'].upper()
            lines.append(f"**[{type_label}]** {n['title']}")
            lines.append(f"_{date_str}_")
            # Show first 150 chars of content
            content_preview = n['content'][:150]
            if len(n['content']) > 150:
                content_preview += '...'
            lines.append(f"{content_preview}\n")

        return '\n'.join(lines)

    def _handle_academic_rule(self, msg, ext):
        msg_lower = msg.lower()
        # Try to match specific rule keywords
        rules = query_db(
            "SELECT rule_title, rule_content, keywords FROM academic_rules WHERE is_active = TRUE"
        )
        if not rules:
            return "No academic rules found in the database. Please contact admin."

        # Score each rule based on keyword overlap
        best_rule = None
        best_score = 0
        for r in rules:
            score = 0
            kws = (r.get('keywords') or '').lower().split(',')
            for kw in kws:
                kw = kw.strip()
                if kw and kw in msg_lower:
                    score += 1
            if score > best_score:
                best_score = score
                best_rule = r

        if best_rule and best_score > 0:
            return f"**{best_rule['rule_title']}**\n\n{best_rule['rule_content']}"

        # Return summary of all categories
        categories = set(r.get('rule_category', '') for r in rules if r.get('rule_category'))
        return (
            "I have information about these academic rule categories:\n"
            + '\n'.join(f"- **{cat.title()}**" for cat in sorted(categories))
            + "\n\nPlease be more specific. For example: 'What is the attendance rule?' or 'Branch change policy'"
        )

    def _handle_placement(self, msg, ext):
        return PLACEMENT_RESPONSE

    def _handle_unknown(self, msg, ext):
        return UNKNOWN_RESPONSE

    # ----------------------------------------------------------------
    # Helpers
    # ----------------------------------------------------------------

    def _extract_subject_query(self, msg):
        """Extract a likely subject name or code from the message."""
        msg_lower = msg.lower()
        # Remove common filler words
        stop_words = {
            'give', 'me', 'the', 'of', 'for', 'about', 'tell', 'what', 'is',
            'are', 'notes', 'material', 'study', 'resource', 'book', 'pdf', 'pyq',
            'previous', 'year', 'papers', 'syllabus', 'topics', 'content', 'subject',
            'course', 'please', 'can', 'you', 'i', 'want', 'need', 'get', 'share',
            'send', 'provide', 'info', 'information', 'on', 'in', 'a', 'an', 'to',
            'my', 'explain', 'details', 'detail',
        }

        # Check for subject code pattern first (e.g., CS201, MA101)
        code_match = re.search(r'\b([A-Za-z]{2}\d{3}[A-Za-z]?)\b', msg)
        if code_match:
            return code_match.group(1).upper()

        # Extract meaningful words
        words = re.findall(r'[a-zA-Z]+', msg_lower)
        meaningful = [w for w in words if w not in stop_words and len(w) > 2]

        if meaningful:
            return ' '.join(meaningful)
        return None

    def _log_query(self, user_id, query_text, intent, response, confidence, elapsed_ms):
        """Log query to analytics table."""
        try:
            execute_db(
                """INSERT INTO query_logs (user_id, query_text, detected_intent, response_text, confidence, response_time_ms)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (user_id, query_text, intent, response[:500], confidence, elapsed_ms)
            )
        except Exception:
            pass  # Don't break chat if logging fails

    def _log_unanswered(self, user_id, query_text, intent):
        """Log unanswered query for admin review."""
        try:
            # Check if similar query exists
            existing = query_db(
                "SELECT id, times_asked FROM unanswered_queries WHERE LOWER(query_text) = LOWER(%s) AND is_resolved = FALSE",
                (query_text,),
                one=True
            )
            if existing:
                execute_db(
                    "UPDATE unanswered_queries SET times_asked = times_asked + 1 WHERE id = %s",
                    (existing['id'],)
                )
            else:
                execute_db(
                    """INSERT INTO unanswered_queries (user_id, query_text, detected_intent)
                       VALUES (%s, %s, %s)""",
                    (user_id, query_text, intent)
                )
        except Exception:
            pass
