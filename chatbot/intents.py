"""
Intent recognition using keyword matching and regex patterns.
Each intent has: name, patterns (regex list), keywords (set), priority.
"""
import re

INTENTS = [
    # --- Greetings ---
    {
        'name': 'greeting',
        'patterns': [
            r'\b(hi|hello|hey|good\s*(morning|afternoon|evening)|howdy|sup)\b'
        ],
        'keywords': {'hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening'},
        'priority': 1,
    },
    {
        'name': 'farewell',
        'patterns': [r'\b(bye|goodbye|see\s*you|take\s*care|exit|quit)\b'],
        'keywords': {'bye', 'goodbye', 'see you', 'take care'},
        'priority': 1,
    },

    # --- Attendance ---
    {
        'name': 'attendance_calculate',
        'patterns': [
            r'(?:attended|present)\s*(\d+)\s*(?:out\s*of|\/)\s*(\d+)',
            r'(\d+)\s*(?:out\s*of|\/|from)\s*(\d+)\s*(?:class|lecture|period)',
            r'attendance.*?(\d+)\s*(?:out\s*of|\/)\s*(\d+)',
            r'(\d+)\s*\/\s*(\d+)\s*attendance',
        ],
        'keywords': {'attendance', 'present', 'attended', 'classes', 'lectures'},
        'priority': 10,
    },
    {
        'name': 'attendance_eligibility',
        'patterns': [
            r'(?:am\s*i|eligible|eligibility|can\s*i)\s*(?:for|to)\s*(?:exam|sit|appear)',
            r'attendance.*(?:enough|eligible|short|shortage)',
            r'(?:need|require).*(?:attendance|lectures?).*(?:exam|eligible)',
            r'how\s*many\s*(?:more\s*)?(?:class|lecture).*(?:need|require|attend)',
        ],
        'keywords': {'eligible', 'eligibility', 'exam', 'debarred', 'shortage'},
        'priority': 9,
    },
    {
        'name': 'attendance_rule',
        'patterns': [
            r'(?:what|how\s*much).*(?:minimum|required|compulsory).*attendance',
            r'attendance.*(?:rule|policy|requirement|criteria|percentage)',
            r'(?:minimum|required).*attendance',
        ],
        'keywords': {'attendance rule', 'minimum attendance', 'attendance policy'},
        'priority': 8,
    },

    # --- Subjects ---
    {
        'name': 'subject_info',
        'patterns': [
            r'(?:tell|about|what\s*is|explain|info).*(?:subject|course)\s+(\w+)',
            r'(?:syllabus|topics|content)\s*(?:of|for)\s+(.+)',
            r'(?:what|which).*subjects?\s*(?:in|for)\s*(?:sem(?:ester)?)\s*(\d+)',
        ],
        'keywords': {'subject', 'syllabus', 'course', 'topics', 'credits'},
        'priority': 7,
    },
    {
        'name': 'semester_subjects',
        'patterns': [
            r'(?:sem(?:ester)?)\s*(\d+)\s*subjects?',
            r'subjects?\s*(?:in|for|of)\s*(?:sem(?:ester)?)\s*(\d+)',
            r'(?:what|which|list).*subjects?.*(?:sem(?:ester)?)\s*(\d+)',
            r'(\d+)(?:st|nd|rd|th)\s*(?:sem(?:ester)?)\s*subjects?',
        ],
        'keywords': {'semester', 'sem', 'subjects list'},
        'priority': 8,
    },

    # --- Study Materials ---
    {
        'name': 'study_material',
        'patterns': [
            r'(?:notes|material|study|resource|book|pdf|pyq|previous\s*year)\s*(?:for|of|on)\s*(.+)',
            r'(?:give|share|send|provide|get).*(?:notes|material|resource|book|pdf|pyq)',
            r'(?:notes|material|resource)\s+(.+)',
        ],
        'keywords': {'notes', 'material', 'study', 'resource', 'book', 'pdf', 'pyq', 'previous year'},
        'priority': 8,
    },

    # --- Exams ---
    {
        'name': 'exam_pattern',
        'patterns': [
            r'(?:exam|test)\s*(?:pattern|format|structure|scheme|marking)',
            r'(?:how|what).*(?:exam|test).*(?:pattern|format|conduct|marks)',
            r'(?:internal|external|mid.?term|end.?sem).*(?:marks?|exam|pattern)',
            r'(?:marks?|marking)\s*(?:scheme|distribution|pattern)',
        ],
        'keywords': {'exam pattern', 'marking scheme', 'internal', 'external', 'mid-term', 'end semester'},
        'priority': 7,
    },
    {
        'name': 'back_paper',
        'patterns': [
            r'(?:back|supplementary|supply|reappear|re-exam)',
            r'(?:fail|failed).*(?:exam|subject|paper)',
            r'(?:how|what).*(?:back|supplementary|re-appear)',
        ],
        'keywords': {'back paper', 'supplementary', 'reappear', 'supply', 'failed'},
        'priority': 7,
    },

    # --- CGPA / SGPA ---
    {
        'name': 'cgpa_calculate',
        'patterns': [
            r'(?:calculate|compute|find|what).*(?:cgpa|cumulative)',
            r'cgpa.*(?:calculate|formula|how)',
            r'(?:my|overall)\s*cgpa',
        ],
        'keywords': {'cgpa', 'cumulative gpa', 'overall gpa'},
        'priority': 9,
    },
    {
        'name': 'sgpa_calculate',
        'patterns': [
            r'(?:calculate|compute|find|what).*(?:sgpa|semester\s*g)',
            r'sgpa.*(?:calculate|formula|how)',
            r'(?:my|this)\s*(?:sem(?:ester)?)\s*(?:sgpa|gpa|grade)',
        ],
        'keywords': {'sgpa', 'semester gpa', 'grade point'},
        'priority': 9,
    },
    {
        'name': 'cgpa_to_percentage',
        'patterns': [
            r'(?:cgpa|sgpa).*(?:to|into|in)\s*(?:percentage|percent|%)',
            r'(?:convert|change).*(?:cgpa|sgpa).*(?:percentage|percent)',
            r'(?:percentage|percent).*(?:from|of)\s*(?:cgpa|sgpa)',
            r'(\d+\.?\d*)\s*(?:cgpa|sgpa).*(?:percentage|percent|%)',
        ],
        'keywords': {'percentage', 'convert cgpa', 'cgpa to percent'},
        'priority': 9,
    },

    # --- Notices ---
    {
        'name': 'notices',
        'patterns': [
            r'(?:latest|recent|new|any)?\s*(?:notice|announcement|circular|update)',
            r'(?:what|any).*(?:notice|announcement|update|news)',
        ],
        'keywords': {'notice', 'announcement', 'circular', 'update', 'news'},
        'priority': 6,
    },

    # --- Academic Rules / Policies ---
    {
        'name': 'academic_rule',
        'patterns': [
            r'(?:rule|policy|regulation|guideline).*(?:about|for|on|regarding)',
            r'(?:what|explain|tell).*(?:rule|policy|regulation)',
            r'(?:branch\s*change|probation|credit|registration)',
        ],
        'keywords': {'rule', 'policy', 'regulation', 'branch change', 'probation', 'credit', 'registration'},
        'priority': 6,
    },

    # --- Placement ---
    {
        'name': 'placement',
        'patterns': [
            r'(?:placement|campus|recruit|job|company|package|ctc)',
            r'(?:which|when|how).*(?:placement|company|recruit)',
        ],
        'keywords': {'placement', 'campus', 'recruit', 'job', 'company', 'package'},
        'priority': 5,
    },

    # --- Help ---
    {
        'name': 'help',
        'patterns': [
            r'(?:help|what\s*can\s*you|capabilities|features|commands)',
            r'(?:how\s*to\s*use|guide|tutorial)',
        ],
        'keywords': {'help', 'features', 'what can you do', 'commands'},
        'priority': 2,
    },
]


def recognize_intent(text):
    """
    Recognize intent from user text.
    Returns (intent_name, confidence, extracted_data).
    """
    text_lower = text.lower().strip()
    best_match = None
    best_score = 0.0

    for intent in INTENTS:
        score = 0.0

        # Pattern matching (higher weight)
        for pattern in intent['patterns']:
            match = re.search(pattern, text_lower)
            if match:
                # Base score from pattern match
                score = max(score, 0.7 + (intent['priority'] * 0.03))
                break

        # Keyword matching (additive)
        words_in_text = set(text_lower.split())
        keyword_matches = 0
        for kw in intent['keywords']:
            if kw in text_lower:
                keyword_matches += 1

        if keyword_matches > 0:
            kw_score = min(0.5 + keyword_matches * 0.15, 0.9)
            score = max(score, kw_score)

        if score > best_score:
            best_score = score
            best_match = intent['name']

    # Extract numbers from text (useful for attendance, CGPA calculations)
    numbers = re.findall(r'\d+\.?\d*', text_lower)
    extracted = {'numbers': [float(n) for n in numbers]}

    # Extract semester number specifically
    sem_match = re.search(r'(?:sem(?:ester)?)\s*(\d+)', text_lower)
    if not sem_match:
        sem_match = re.search(r'(\d+)(?:st|nd|rd|th)\s*sem', text_lower)
    if sem_match:
        extracted['semester'] = int(sem_match.group(1))

    if best_match is None:
        return 'unknown', 0.0, extracted

    return best_match, round(best_score, 2), extracted
