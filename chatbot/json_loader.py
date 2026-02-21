"""
JSON Knowledge Base for Indus University CSE Chatbot.
Loads all 11 JSON data files at startup and exposes clean query helpers.
"""
import json
import os
import re

_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'JSON data')


def _load(filename):
    path = os.path.join(_DATA_DIR, filename)
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


class KnowledgeBase:
    """Singleton that holds all JSON data loaded at startup."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._loaded = False
        return cls._instance

    def load(self):
        if self._loaded:
            return
        self.academic_calendar = _load('indus_university_academic_calendar_2025_26_chatbot.json') or {}
        self.study_materials   = _load('cse-material-chatbot-data.json') or {}
        self.fee_data          = _load('fee-attendance-scholarship-chatbot-data.json') or {}
        self.subjects_list     = _load('subjects_list.json') or {}
        self.course_content    = _load('subjects_course_content.json') or []
        self.exam_format       = _load('indus_university_exam_format.json') or {}
        self.library_policy    = _load('indus_university_library_policy_chatbot.json') or {}
        self.discipline_rules  = _load('indus_university_student_discipline_rules_chatbot.json') or {}
        self.dbit_guidelines   = _load('dbit_student_guidelines_chatbot.json') or {}
        self.placement         = _load('indus_university_placement_chatbot.json') or {}
        self.reassessment      = _load('reassessment-chatbot-data.json') or {}
        self.attendance_planner = _load('attendance_planner_data.json') or {}
        self._loaded = True
        self._build_abbreviation_map()

    # ------------------------------------------------------------------
    # Fee & Attendance
    # ------------------------------------------------------------------

    def get_fee_structure(self):
        return self.fee_data.get('fee_structure', {})

    def get_fee_payment(self):
        return self.fee_data.get('fee_payment_details', {})

    def get_attendance_policy(self):
        return self.fee_data.get('attendance_policy', {})

    def get_mysy_scholarship(self):
        return self.fee_data.get('mysy_scholarship', {})

    def get_attendance_planner(self):
        return self.attendance_planner.get('attendance_planner', {})

    def get_planner_thresholds(self):
        return self.get_attendance_planner().get('key_thresholds', {})

    # ------------------------------------------------------------------
    # Academic Calendar
    # ------------------------------------------------------------------

    def get_key_dates(self):
        return self.academic_calendar.get('key_dates', {})

    def get_semester_structure(self):
        return self.academic_calendar.get('semester_structure', {})

    def get_vacation_periods(self):
        return self.academic_calendar.get('vacation_periods', {})

    # ------------------------------------------------------------------
    # Subjects
    # ------------------------------------------------------------------

    _ROMAN = {1:'I', 2:'II', 3:'III', 4:'IV', 5:'V', 6:'VI', 7:'VII', 8:'VIII'}

    # Words skipped when auto-generating abbreviations from subject names
    _ABBR_STOP = {
        'and', 'an', 'the', 'of', 'in', 'with', 'for', 'to', 'a', 'at', 'on',
    }

    # Hand-crafted abbreviations that auto-generation may not get right.
    # Any number of letters is supported — 2-letter (OS, CN), 3-letter (AJT, NLP),
    # 4-letter (DBMS, HVPE) and more all work the same way.
    _MANUAL_ABBR = {
        # Core CS subjects
        'DBMS': 'Database Management System',
        'DSA':  'Data Structure & Algorithms',
        'OS':   'Operating System',
        'COA':  'Computer Organization & Architecture',
        'CN':   'Computer Networks',
        'DAA':  'Design and Analysis of Algorithms',
        'TOC':  'Theory of Computation',
        'SE':   'Software Engineering with UML',
        'WT':   'Web Technology',
        'IOT':  'Internet of Things',
        'CD':   'Compiler Design',
        'DE':   'Digital Electronics',
        # Elective subjects (Sem VI–VIII)
        'AJT':  'Advanced Java Technology',
        'NLP':  'Natural Language Processing',
        'CC':   'Cloud Computing',
        'DWM':  'Data Warehouse & Mining',
        'HCI':  'Human Computer Interface',
        'CV':   'Computer Vision',
        'CNS':  'Cryptography & Network Security',
        'SC':   'Soft Computing',
        'ES':   'Embedded System',
        'BC':   'Block Chaining',
        # NEP / AICTE mandatory subjects
        'IKS':  'Indian Knowledge System',
        'IST':  'Indian Science Technology',
        'EVS':  'Environmental Science',
        'HVPE': 'Human Values and Professional Ethics',
        # Common CS acronyms (not necessarily in the specific curriculum)
        'ML':   'Machine Learning',
        'AI':   'Artificial Intelligence',
        'DS':   'Data Science',
        'OOP':  'Object Oriented Concepts with UML',
        'OOC':  'Object Oriented Concepts with UML',
        'ICT':  'ICT Tools',
        # Specific to Indus syllabi naming
        'PSC':  'Programming for Scientific Computing',
        'PSP':  'Programming for Problem Solving',
        'MPI':  'Microprocessing and Interfacing',
        'MAD':  'Mobile App Development',
        'NET':  'Advance .Net Framework',
        'JAVA': 'Core Java Programming',
    }

    @staticmethod
    def _make_abbr(name: str) -> str:
        """Return an auto-generated abbreviation from the first letters of
        significant words in *name* (skipping stop words and single chars)."""
        words = re.split(r'[\s\-/&]+', name)
        letters = [
            w[0].upper()
            for w in words
            if w and w.lower() not in KnowledgeBase._ABBR_STOP
        ]
        return ''.join(letters)

    def _build_abbreviation_map(self):
        """Build ``{ABBR: full_name}`` from manual overrides + every subject
        found in subjects_list.json and study_materials JSON."""
        abbr_map: dict[str, str] = {}

        # 1. Manual overrides (highest priority — never overwritten)
        abbr_map.update(self._MANUAL_ABBR)

        # 2. Auto-generate from subjects_list.json (handles elective "A / B / C" names)
        for sem in self.subjects_list.get('semesters', []):
            for subj in sem.get('subjects', []):
                raw_name = subj.get('subject_name', '')
                if not raw_name:
                    continue
                # Split elective options written as "Adv Java / .Net / Mobile App"
                options = re.split(r'\s*/\s*|\s+or\s+', raw_name, flags=re.IGNORECASE)
                for option in options:
                    option = option.strip()
                    if not option:
                        continue
                    auto = self._make_abbr(option)
                    if auto and auto not in abbr_map:
                        abbr_map[auto] = option

        # 3. Also auto-generate from study_materials semesters
        for sem_data in self.study_materials.get('semesters', []):
            for subj in sem_data.get('subjects', []):
                name = subj.get('name', '')
                if not name:
                    continue
                auto = self._make_abbr(name)
                if auto and auto not in abbr_map:
                    abbr_map[auto] = name

        self._abbr_map = abbr_map

    def expand_abbreviation(self, text: str) -> str:
        """Expand subject abbreviations found in *text*.

        Examples::

            kb.expand_abbreviation("AJT")           → "Advanced Java Technology"
            kb.expand_abbreviation("ajt notes")     → "Advanced Java Technology notes"
            kb.expand_abbreviation("os material")   → "Operating System material"
        """
        if not text or not hasattr(self, '_abbr_map'):
            return text

        # Fast path: entire text is a single abbreviation
        upper = text.strip().upper()
        if upper in self._abbr_map:
            return self._abbr_map[upper]

        # Word-by-word expansion
        words = text.split()
        expanded = []
        for word in words:
            clean = re.sub(r'[.,?!:;]$', '', word).upper()
            if clean in self._abbr_map:
                expanded.append(self._abbr_map[clean])
            else:
                expanded.append(word)
        return ' '.join(expanded)

    def get_semester_subjects(self, sem_num):
        """Return list of subjects for semester number 1-8."""
        roman = self._ROMAN.get(sem_num, str(sem_num))
        for s in self.subjects_list.get('semesters', []):
            if s.get('semester') in (roman, str(sem_num)):
                return s.get('subjects', [])
        return []

    def find_subjects_by_keyword(self, keyword):
        """Search study_materials semesters for subjects matching keyword.
        Automatically expands abbreviations before searching (e.g. 'AJT' → 'Advanced Java Technology').
        """
        expanded = self.expand_abbreviation(str(keyword))
        search_terms = list({expanded.lower(), str(keyword).lower()})  # deduplicated

        results = []
        seen = set()
        for kw in search_terms:
            for sem_data in self.study_materials.get('semesters', []):
                for subj in sem_data.get('subjects', []):
                    name = subj.get('name', '')
                    code = subj.get('code', '')
                    key = (name, code)
                    if key in seen:
                        continue
                    if (kw in name.lower()
                            or kw in code.lower()
                            or any(kw in k.lower() for k in subj.get('keywords', []))):
                        results.append({**subj, 'semester': sem_data.get('semester')})
                        seen.add(key)
        return results

    def get_course_content(self, keyword):
        """Return course content dict for a subject matching keyword.
        Automatically expands abbreviations (e.g. 'DBMS' → 'Database Management System').
        """
        expanded = self.expand_abbreviation(str(keyword))
        search_terms = list({expanded.lower(), str(keyword).lower()})

        for kw in search_terms:
            for subj in self.course_content:
                if (kw in subj.get('subject_name', '').lower()
                        or kw in subj.get('subject_code', '').lower()):
                    return subj
        return None

    def get_semester_drive_link(self, sem_num):
        key = f'semester_{sem_num}'
        return self.study_materials.get('drive_links', {}).get(key)

    def find_subject_in_list(self, keyword):
        """Search subjects_list.json by subject name or code (abbreviation-aware).

        Handles elective names like "Advanced Java Technology / Advance .Net Framework"
        by splitting on "/" and searching each option individually.

        Returns (subject_dict, semester_number_int) or (None, None).
        """
        expanded = self.expand_abbreviation(str(keyword))
        search_terms = list({expanded.lower(), str(keyword).lower()})
        roman_to_num = {v: k for k, v in self._ROMAN.items()}

        for kw in search_terms:
            for sem in self.subjects_list.get('semesters', []):
                for subj in sem.get('subjects', []):
                    raw_name = subj.get('subject_name', '')
                    code = subj.get('subject_code', '').lower()

                    # Exact code match
                    if kw == code:
                        sem_num = roman_to_num.get(sem.get('semester', ''), 0)
                        return subj, sem_num

                    # Name match — also check each elective option
                    options = re.split(r'\s*/\s*', raw_name)
                    for option in options:
                        if kw in option.lower():
                            sem_num = roman_to_num.get(sem.get('semester', ''), 0)
                            return subj, sem_num
        return None, None

    # ------------------------------------------------------------------
    # Exam Format & Grading
    # ------------------------------------------------------------------

    def get_grading_system(self):
        return self.exam_format.get('grading_system', {})

    def get_degree_classes(self):
        return self.exam_format.get('degree_class', {})

    def cgpa_to_percentage(self, cgpa):
        """Indus University formula: (CGPA - 0.5) * 10"""
        return round((cgpa - 0.5) * 10, 2)

    def get_grade_for_marks(self, marks, total=100):
        """Return letter grade and grade points for given marks."""
        gs = self.get_grading_system()
        if total == 200:
            scale_key = 'ug_200_marks'
        else:
            scale_key = 'ug_programs'
        scale = gs.get(scale_key, {}).get('grade_scale', [])
        for entry in scale:
            r = entry.get('marks_range', '')
            if r.startswith('<'):
                threshold = int(r[1:])
                if marks < threshold:
                    return entry['letter_grade'], entry['grade_points']
            elif '-' in r:
                lo, hi = r.split('-')
                if int(lo) <= marks <= int(hi):
                    return entry['letter_grade'], entry['grade_points']
        return 'F', 0

    # ------------------------------------------------------------------
    # Library
    # ------------------------------------------------------------------

    def get_library_circulation(self):
        return (self.library_policy
                .get('sections', {})
                .get('6_circulation_policy', {}))

    def get_library_loan_periods(self):
        circ = self.get_library_circulation()
        return circ.get('loan_periods_and_fines', [])

    def get_library_rules_summary(self):
        """Return key rules list from circulation policy."""
        circ = self.get_library_circulation()
        return circ.get('general_rules', [])

    # ------------------------------------------------------------------
    # Discipline
    # ------------------------------------------------------------------

    def get_conduct_rules(self):
        return (self.discipline_rules
                .get('regulation_2_conduct_and_discipline', {})
                .get('A_student_discipline', {})
                .get('key_rules', []))

    def get_dress_code_rules(self):
        reg = self.discipline_rules.get('regulation_2_conduct_and_discipline', {})
        return reg.get('B_dress_code', {})

    def get_penalties(self):
        reg = self.discipline_rules.get('regulation_2_conduct_and_discipline', {})
        return reg.get('E_penalties', {})

    def get_hostel_rules(self):
        return self.discipline_rules.get('regulation_3_hostel_rules', {})

    # ------------------------------------------------------------------
    # Placement
    # ------------------------------------------------------------------

    def get_placement_stats(self):
        return self.placement.get('placement_statistics', {})

    def get_training_programs(self):
        return (self.placement
                .get('activities', {})
                .get('training', {})
                .get('programs', []))

    def get_top_recruiters(self):
        return self.placement.get('top_recruiters', [])

    # ------------------------------------------------------------------
    # Re-assessment
    # ------------------------------------------------------------------

    def get_reassessment_fees(self):
        return self.reassessment.get('fees', {})

    def get_reassessment_eligibility(self):
        return self.reassessment.get('eligibility', {})

    def get_reassessment_procedure(self):
        return self.reassessment.get('procedure', {})


# Module-level singleton — load once at import time
kb = KnowledgeBase()
kb.load()
