"""
Intent recognition using keyword matching and regex patterns.
Each intent has: name, patterns (regex list), keywords (set), priority.
"""
import re

INTENTS = [

    # ----------------------------------------------------------------
    # Greetings / Meta
    # ----------------------------------------------------------------
    {
        'name': 'greeting',
        'patterns': [r'\b(hi|hello|hey|good\s*(morning|afternoon|evening)|howdy|sup|namaste)\b'],
        'keywords': {'hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening', 'namaste'},
        'priority': 1,
    },
    {
        'name': 'farewell',
        'patterns': [r'\b(bye|goodbye|see\s*you|take\s*care|exit|quit|alvida)\b'],
        'keywords': {'bye', 'goodbye', 'see you', 'take care', 'alvida'},
        'priority': 1,
    },
    {
        'name': 'help',
        'patterns': [r'(?:help|what\s*can\s*you|capabilities|features|commands|how\s*to\s*use|guide)'],
        'keywords': {'help', 'features', 'what can you do', 'commands', 'guide'},
        'priority': 2,
    },

    # ----------------------------------------------------------------
    # Fee & Payment
    # ----------------------------------------------------------------
    {
        'name': 'fee_structure',
        'patterns': [
            r'(?:fee|fees|tuition|payment|charges?|cost).*(?:structure|detail|break|semester|total|year|annual)',
            r'(?:how\s*much|kitna|kya\s*hai).*(?:fee|fees|tuition)',
            r'(?:total|course|btech|cse|sem(?:ester)?)\s*(?:fee|fees)',
            r'(?:fee|fees).*(?:per|each)\s*(?:semester|year)',
        ],
        'keywords': {'fee', 'fees', 'tuition', 'charges', 'fee structure', 'semester fee',
                     'total fee', 'course fee', 'kitna lagega', 'payment'},
        'priority': 9,
    },
    {
        'name': 'fee_payment_method',
        'patterns': [
            r'(?:how|kaise).*(?:pay|bhare|bharu).*(?:fee|fees)',
            r'(?:payment|pay).*(?:method|mode|option|way)',
            r'(?:upi|neft|netbanking|card|cheque|dd|emi|installment|kisto)',
            r'(?:grayquest|icici|online\s*payment)',
        ],
        'keywords': {'payment method', 'how to pay', 'upi', 'installment', 'emi',
                     'grayquest', 'netbanking', 'kisto mein', 'part payment'},
        'priority': 8,
    },

    # ----------------------------------------------------------------
    # Attendance
    # ----------------------------------------------------------------
    {
        'name': 'attendance_future_plan',
        'patterns': [
            # "next/remaining/upcoming N lectures"
            r'(?:next|remaining|future|upcoming)\s+\d+\s+(?:lectures?|classes?|periods?)',
            # "N lectures remaining/left"
            r'\d+\s+(?:lectures?|classes?|periods?)\s+(?:remaining|left|more|upcoming|pending)',
            # "how many lectures can I attend/skip/bunk/miss"
            r'how\s*many\s*(?:lectures?|classes?)?\s*(?:can\s*i|should\s*i|do\s*i\s*(?:need|have)\s*to|must\s*i)\s*(?:attend|be\s*present)',
            r'how\s*many\s*(?:lectures?|classes?)?\s*(?:can\s*i|may\s*i)\s*(?:skip|bunk|miss|be\s*absent)',
            # "can I skip/bunk N lectures"
            r'(?:can\s*i|may\s*i)\s*(?:skip|bunk|miss)\s*(?:\d+\s*)?(?:more\s*)?(?:lectures?|classes?)',
            # "attendance plan / plan my attendance"
            r'(?:attendance\s*plan|plan\s*(?:my\s*)?attendance|future\s*attendance)',
            # combined: current + remaining in same message
            r'(?:\d+\s*(?:\/|out\s*of?)\s*\d+).*(?:remaining|next\s+\d+|lectures?\s+left)',
        ],
        'keywords': {
            'remaining lectures', 'lectures remaining', 'classes remaining',
            'lectures left', 'classes left', 'next lectures', 'upcoming lectures',
            'future attendance', 'attendance plan', 'plan attendance',
            'how many can i skip', 'how many can i bunk', 'can i skip', 'can i bunk',
            'how many to attend', 'how many must attend', 'how many lectures attend',
            'baaki lectures', 'kitni chhuti', 'aage kitna',
        },
        'priority': 11,   # higher than attendance_calculate (10) → wins when both match
    },
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
            r'attendance.*(?:rule|policy|requirement|criteria|percentage|kitna)',
            r'(?:minimum|required).*attendance',
            r'80.*(?:percent|%).*attendance',
        ],
        'keywords': {'attendance rule', 'minimum attendance', 'attendance policy',
                     '80 percent', 'late attendance', '5 minute'},
        'priority': 8,
    },

    # ----------------------------------------------------------------
    # MYSY Scholarship
    # ----------------------------------------------------------------
    {
        'name': 'mysy_scholarship',
        'patterns': [
            r'\bmysy\b',
            r'(?:scholarship|छात्रवृत्ति|scholarship).*(?:apply|how|kaise|eligib|benefit|mysy)',
            r'(?:mukhyamantri|yuva|swavalamban)',
            r'(?:scholarship|grant).*(?:government|gujarat|state)',
            r'(?:how\s*to|kaise).*(?:apply|get|claim).*scholarship',
        ],
        'keywords': {'mysy', 'scholarship', 'mukhyamantri', 'yuva swavalamban',
                     'scholarship apply', 'scholarship eligibility', 'scholarship benefit'},
        'priority': 9,
    },

    # ----------------------------------------------------------------
    # Academic Calendar / Exam Dates
    # ----------------------------------------------------------------
    {
        'name': 'academic_calendar',
        'patterns': [
            r'(?:when|date|schedule|kab).*(?:mid|ese|exam|practical|jury|start|end|term)',
            r'(?:mid\s*sem(?:ester)?|midsem).*(?:exam|date|when|schedule)',
            r'(?:end\s*sem(?:ester)?|ese|ese-thy|ese-pr).*(?:exam|date|when)',
            r'(?:academic|semester)\s*(?:calendar|schedule|dates?)',
            r'(?:term|semester)\s*(?:start|end|begin)',
            r'(?:exam|examination)\s*(?:date|schedule|timetable)',
            r'(?:holiday|vacation|winter|summer)\s*(?:break|vacation|holiday)',
        ],
        'keywords': {'academic calendar', 'mid sem exam', 'end sem exam', 'ese',
                     'exam date', 'exam schedule', 'term start', 'term end',
                     'holiday', 'vacation', 'mid semester', 'midsem'},
        'priority': 9,
    },

    # ----------------------------------------------------------------
    # Subjects
    # ----------------------------------------------------------------
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
    {
        'name': 'subject_info',
        'patterns': [
            r'(?:tell|about|what\s*is|explain|info).*(?:subject|course)\s+(\w+)',
            r'(?:syllabus|topics|content|units?)\s*(?:of|for)\s+(.+)',
            r'(?:what|which).*subjects?\s*(?:in|for)\s*(?:sem(?:ester)?)\s*(\d+)',
        ],
        'keywords': {'subject', 'syllabus', 'course content', 'topics', 'credits', 'units'},
        'priority': 7,
    },

    # ----------------------------------------------------------------
    # Study Materials & Drive Links
    # ----------------------------------------------------------------
    {
        'name': 'study_material',
        'patterns': [
            r'(?:notes?|material|study|resource|book|pdf|pyq|previous\s*year|drive\s*link)\s*(?:for|of|on)\s*(.+)',
            r'(?:give|share|send|provide|get|chahiye).*(?:notes?|material|resource|book|pdf|pyq|drive)',
            r'(?:notes?|material|resource)\s+(.+)',
            r'(?:drive|google\s*drive|link).*sem(?:ester)?\s*(\d+)',
            r'sem(?:ester)?\s*(\d+).*(?:drive|link|material|notes?)',
        ],
        'keywords': {'notes', 'material', 'study', 'resource', 'book', 'pdf', 'pyq',
                     'previous year', 'drive link', 'google drive'},
        'priority': 8,
    },

    # ----------------------------------------------------------------
    # Exam Format / Grading
    # ----------------------------------------------------------------
    {
        'name': 'exam_format',
        'patterns': [
            r'(?:exam|test)\s*(?:pattern|format|structure|scheme|marking)',
            r'(?:how|what).*(?:exam|test).*(?:pattern|format|conduct|marks)',
            r'(?:internal|external|mid.?term|end.?sem|cie|ese).*(?:marks?|exam|pattern)',
            r'(?:marks?|marking)\s*(?:scheme|distribution|pattern)',
            r'(?:cie|ese)\s*(?:marks?|weightage|format)',
        ],
        'keywords': {'exam pattern', 'marking scheme', 'internal', 'external',
                     'mid-term', 'end semester', 'cie', 'ese', 'exam format'},
        'priority': 7,
    },
    {
        'name': 'grading_system',
        'patterns': [
            r'(?:grade|grading|gpa|cgpa|sgpa|grade\s*point)',
            r'(?:what|how|which).*(?:grade|gpa|cgpa|sgpa)',
            r'(?:marks?|score).*(?:grade|letter)',
            r'(?:a\+|a|b\+|b|c|d|p|f)\s*grade',
            r'(?:degree|class|distinction|first\s*class|second\s*class)',
            r'(?:percentage|percent|%).*(?:cgpa|gpa)',
        ],
        'keywords': {'grade', 'grading', 'gpa', 'cgpa', 'sgpa', 'grade points',
                     'distinction', 'first class', 'second class', 'pass class',
                     'a+ grade', 'f grade', 'pass marks'},
        'priority': 8,
    },

    # ----------------------------------------------------------------
    # CGPA / SGPA Calculation
    # ----------------------------------------------------------------
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
    {
        'name': 'grade_for_marks',
        'patterns': [
            r'(?:if|i\s*(?:score|get|got|scored))\s*(\d+).*(?:grade|what\s*grade)',
            r'(?:what|which)\s*grade.*(?:for|if|with)\s*(\d+)',
            r'(\d+)\s*(?:marks?|out\s*of).*(?:grade|letter)',
        ],
        'keywords': {'what grade', 'grade for marks', 'score grade', 'if i score', 'i got'},
        'priority': 9,
    },

    # ----------------------------------------------------------------
    # Passing / Minimum Marks
    # ----------------------------------------------------------------
    {
        'name': 'passing_marks',
        'patterns': [
            r'(?:passing|minimum|pass|min)[\s\-]*marks?',
            r'(?:minimum|min|how\s*many|what)\s+marks?.*(?:pass|clear|need|requir)',
            r'marks?.*(?:need|requir|minimum|to\s*pass|to\s*clear)',
            r'(?:fail|below|under|less\s*than)\s+(?:\d+\s+)?marks?',
            r'how\s*many\s*marks?.*(?:pass|fail|need|clear)',
            r'marks?\s*(?:required|needed|minimum)\s*(?:to\s*pass|to\s*clear|for\s*pass)',
            r'(?:pass|clear)\s+(?:\w+\s+){0,4}(?:subject|paper|exam|course)',
            r'(?:minimum|min)\s+(?:marks?|score)\s+(?:for|in|of)',
            r'(?:i\s+(?:fail|passed)|will\s+i\s+(?:fail|pass))\s+(?:if|with)',
            r'(?:need|require).*(?:\d+).*(?:pass|clear)',
        ],
        'keywords': {
            'passing marks', 'minimum marks', 'pass marks', 'marks to pass',
            'minimum to pass', 'fail marks', 'marks required', 'marks needed',
            'how many marks', 'passing criteria', 'pass criteria',
            'minimum passing', 'will i fail', 'will i pass',
            'marks for pass', 'kya marks chahiye', 'pass hone ke liye',
        },
        'priority': 10,
    },

    # ----------------------------------------------------------------
    # Re-Assessment & Re-Checking
    # ----------------------------------------------------------------
    {
        'name': 're_assessment',
        'patterns': [
            r'(?:re.?assess(?:ment)?|reassess)',
            r'(?:re.?check(?:ing)?|recheck)',
            r'(?:apply|how).*(?:re.?assess|re.?check)',
            r'(?:rechecking|reassessment)\s*(?:fee|process|eligib|rule)',
            r'(?:result|marks?).*(?:check|verify|recheck|reassess)',
        ],
        'keywords': {'reassessment', 're-assessment', 'rechecking', 're-checking',
                     'recheck fee', 'reassess fee', 'marks verify'},
        'priority': 9,
    },

    # ----------------------------------------------------------------
    # Library
    # ----------------------------------------------------------------
    {
        'name': 'library_policy',
        'patterns': [
            r'(?:library|lib).*(?:rule|policy|hour|book|borrow|fine|due|limit)',
            r'(?:borrow|issue|take).*(?:book|library)',
            r'(?:how\s*many|kitni).*(?:book|books?).*(?:borrow|issue|take)',
            r'(?:library|lib)\s*(?:open|close|time|hour)',
            r'(?:fine|penalty).*(?:book|library|overdue)',
            r'(?:return|due\s*date).*(?:book|library)',
            r'(?:library\s*card|id.*library|library.*id)',
        ],
        'keywords': {'library', 'borrow book', 'library fine', 'overdue', 'library hours',
                     'book issue', 'library rules', 'library policy', 'no due certificate'},
        'priority': 8,
    },

    # ----------------------------------------------------------------
    # Student Discipline
    # ----------------------------------------------------------------
    {
        'name': 'discipline_rules',
        'patterns': [
            r'(?:discipline|conduct|behaviour|behavior).*(?:rule|policy|regulation)',
            r'(?:dress\s*code|uniform|id\s*card).*(?:rule|policy|required)',
            r'(?:ragging|rag).*(?:rule|policy|prohibition)',
            r'(?:mobile|phone).*(?:campus|class|lab|prohibited)',
            r'(?:smoking|alcohol|drug|substance).*(?:campus|prohibited|rule)',
            r'(?:hostel|dorm).*(?:rule|policy|time|curfew)',
            r'(?:penalty|punishment|fine|suspension|rustication)',
            r'(?:prohibited|banned|not\s*allowed).*(?:campus|class)',
            r'(?:dress|uniform|formal).*(?:code|required)',
        ],
        'keywords': {'discipline', 'conduct', 'dress code', 'ragging', 'mobile phone',
                     'smoking', 'alcohol', 'hostel rules', 'penalty', 'rustication',
                     'id card rules', 'suspension', 'prohibited'},
        'priority': 8,
    },

    # ----------------------------------------------------------------
    # Placement
    # ----------------------------------------------------------------
    {
        'name': 'placement',
        'patterns': [
            r'(?:placement|campus|recruit|job|company|package|ctc|lpa|salary)',
            r'(?:which|when|how).*(?:placement|company|recruit|hired)',
            r'(?:highest|average).*(?:package|salary|ctc|lpa)',
            r'(?:training|internship).*(?:placement|company|industry)',
        ],
        'keywords': {'placement', 'campus recruitment', 'job', 'company', 'package',
                     'lpa', 'salary', 'highest package', 'average package', 'internship'},
        'priority': 7,
    },

    # ----------------------------------------------------------------
    # Back Paper / Supplementary
    # ----------------------------------------------------------------
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

    # ----------------------------------------------------------------
    # Notices
    # ----------------------------------------------------------------
    {
        'name': 'notices',
        'patterns': [
            r'(?:latest|recent|new|any)?\s*(?:notice|announcement|circular|update)',
            r'(?:what|any).*(?:notice|announcement|update|news)',
        ],
        'keywords': {'notice', 'announcement', 'circular', 'update', 'news'},
        'priority': 6,
    },

    # ----------------------------------------------------------------
    # Academic Rules / Policies
    # ----------------------------------------------------------------
    {
        'name': 'academic_rule',
        'patterns': [
            r'(?:rule|policy|regulation|guideline).*(?:about|for|on|regarding)',
            r'(?:what|explain|tell).*(?:rule|policy|regulation)',
            r'(?:branch\s*change|probation|credit|registration)',
        ],
        'keywords': {'rule', 'policy', 'regulation', 'branch change', 'probation',
                     'credit', 'registration'},
        'priority': 6,
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
            if re.search(pattern, text_lower):
                score = max(score, 0.7 + (intent['priority'] * 0.03))
                break

        # Keyword matching (additive)
        keyword_matches = sum(1 for kw in intent['keywords'] if kw in text_lower)
        if keyword_matches > 0:
            kw_score = min(0.5 + keyword_matches * 0.15, 0.9)
            score = max(score, kw_score)

        if score > best_score:
            best_score = score
            best_match = intent['name']

    # Extract numbers from text
    numbers = re.findall(r'\d+\.?\d*', text_lower)
    extracted = {'numbers': [float(n) for n in numbers]}

    # Extract semester number
    sem_match = re.search(r'(?:sem(?:ester)?)\s*(\d+)', text_lower)
    if not sem_match:
        sem_match = re.search(r'(\d+)(?:st|nd|rd|th)\s*sem', text_lower)
    if sem_match:
        extracted['semester'] = int(sem_match.group(1))

    if best_match is None:
        return 'unknown', 0.0, extracted

    return best_match, round(best_score, 2), extracted
