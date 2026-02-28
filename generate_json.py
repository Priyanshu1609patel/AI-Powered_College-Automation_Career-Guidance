"""
Script to generate two JSON files from CSE-Subject.pdf:
1. subjects_list.json  - Semester-wise subject list with marks, credits, CIE/ESE breakdown
2. subjects_course_content.json - Course content (units + practical) for each subject
"""

import pdfplumber, json, re, os

OUTPUT_DIR = r"C:\Users\91910\OneDrive\Documents\career_guidance_ai\JSON data"
PDF_PATH   = r"C:\Users\91910\OneDrive\Documents\career_guidance_ai\PDF\CSE-Subject.pdf"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
# 1. Read every page text (from pre-generated full text file for speed)
# ─────────────────────────────────────────────────────────────────────────────
TXT_CACHE = r"C:\Users\91910\OneDrive\Documents\career_guidance_ai\pdf_full.txt"
with open(TXT_CACHE, encoding="utf-8", errors="replace") as f:
    raw = f.read()

# Split into page dict
pages_raw = re.split(r"===== PAGE (\d+) =====", raw)
pages = {}
for i in range(1, len(pages_raw) - 1, 2):
    pages[int(pages_raw[i])] = pages_raw[i + 1].strip()
all_pages = [pages.get(i, "") for i in range(1, max(pages.keys()) + 1)]

# ─────────────────────────────────────────────────────────────────────────────
# 2. JSON 1 – Semester-wise subjects (data from pages 1-8, manually structured)
# ─────────────────────────────────────────────────────────────────────────────

def sub(sr, code, name, cr, th_hr, tut_hr, pr_hr, tot_hr, th_cie, th_ese, pr_cie, pr_ese, marks, cat):
    return {
        "sr_no": sr, "subject_code": code, "subject_name": name, "credits": cr,
        "teaching_scheme": {
            "theory_hours": th_hr, "tutorial_hours": tut_hr,
            "practical_hours": pr_hr, "total_hours_per_week": tot_hr
        },
        "evaluation_scheme": {
            "theory":    {"CIE": th_cie, "ESE": th_ese},
            "practical": {"CIE": pr_cie, "ESE": pr_ese},
            "total_marks": marks
        },
        "category": cat
    }

def pe(sr, grp_name, options, cr, th_hr, tut_hr, pr_hr, tot_hr, th_cie, th_ese, pr_cie, pr_ese, marks, cat):
    return {
        "sr_no": sr, "subject_name": grp_name,
        "elective_options": options, "credits": cr,
        "teaching_scheme": {
            "theory_hours": th_hr, "tutorial_hours": tut_hr,
            "practical_hours": pr_hr, "total_hours_per_week": tot_hr
        },
        "evaluation_scheme": {
            "theory":    {"CIE": th_cie, "ESE": th_ese},
            "practical": {"CIE": pr_cie, "ESE": pr_ese},
            "total_marks": marks
        },
        "category": cat
    }

semesters_data = [
    {"semester": "I", "subjects": [
        sub(1,"MA0111","Calculus",4,3,1,0,4,60,40,0,0,100,"BS"),
        sub(2,"CH0011","Engineering Chemistry",4,3,0,2,5,60,40,60,40,200,"BS"),
        sub(3,"EN0111","Technical Communication",2,1,0,2,3,60,40,60,40,200,"HS"),
        sub(4,None,"Open Elective 1",3,3,0,0,3,60,40,0,0,100,"OE"),
        sub(5,"ME0019","Engineering Graphics",3,1,0,4,5,60,40,60,40,200,"ES"),
        sub(6,"CV0004","Environmental Science",2,2,0,0,2,60,40,0,0,100,"ES"),
        sub(7,None,"Open Elective 2",3,3,0,0,3,60,40,0,0,100,"OE"),
        sub(8,None,"Indian Knowledge System",3,3,0,0,3,100,0,0,0,100,"VA"),
    ]},
    {"semester": "II", "subjects": [
        sub(1,"MA0211","Differential Equations & Linear Algebra",4,3,1,0,4,60,40,0,0,100,"BS"),
        sub(2,"PH0011","Engineering Physics",4,3,0,2,5,60,40,60,40,200,"BS"),
        sub(3,"EN0211","Business Communication & Presentation Skills",2,1,0,2,3,60,40,60,40,200,"HS"),
        sub(4,None,"Open Elective 3",3,3,0,0,3,60,40,0,0,100,"OE"),
        sub(5,"ME0117","Workshop Practice",2,0,0,4,4,0,0,60,40,100,"ES"),
        sub(6,"CE0216","Programming for Problem Solving",4,3,0,2,5,60,40,60,40,200,"ES"),
        sub(7,"IST0001","Indian Science Technology",1,1,0,0,0,100,0,0,0,100,"VA"),
    ]},
    {"semester": "III", "subjects": [
        sub(1,"MA0311","Probability, Statistics & Numerical Methods",4,3,1,0,4,60,40,0,0,100,"BS"),
        sub(2,"CE0320","Computer Organization & Architecture",3,3,0,0,3,60,40,0,0,100,"Core"),
        sub(3,"EC0319","Digital Electronics",4,3,0,2,5,60,40,60,40,200,"ES"),
        sub(4,"CE0316","Object Oriented Concepts with UML",4,3,0,2,5,60,40,60,40,200,"Core"),
        sub(5,"CE0317","Database Management System",4,3,0,2,5,60,40,60,40,200,"Core"),
        sub(6,"SS0301","Human Values and Professional Ethics",2,2,0,0,2,100,0,0,0,100,"HS"),
        sub(7,"CE0318","Internship Credit / Online Courses / MOOC",2,0,0,0,0,0,0,100,0,100,"IC"),
    ]},
    {"semester": "IV", "subjects": [
        sub(1,"CE0425","ICT Tools and Technology",2,0,1,2,3,0,0,100,0,100,"ES"),
        sub(2,"CE0417","Data Structure & Algorithms",4,3,0,2,5,60,40,60,40,200,"Core"),
        sub(3,"CE0418","Operating System",4,3,0,2,5,60,40,60,40,200,"Core"),
        sub(4,"BB0311","Management for Engineers",2,2,0,0,2,60,40,0,0,100,"HS"),
        sub(5,"CE0421","Core Java Programming",4,3,0,2,5,60,40,60,40,200,"Core"),
        sub(6,None,"Open Elective 4",3,3,0,0,3,60,40,0,0,100,"OE"),
        sub(7,None,"Open Elective 5",3,3,0,0,3,60,40,0,0,100,"OE"),
    ]},
    {"semester": "V", "subjects": [
        sub(1,"CE0516","Design and Analysis of Algorithms",4,3,0,2,5,60,40,60,40,200,"Core"),
        sub(2,"CE0517","Microprocessing and Interfacing",4,3,0,2,5,60,40,60,40,200,"ES"),
        sub(3,"CE0518","Computer Networks",4,3,0,2,5,60,40,60,40,200,"Core"),
        sub(4,None,"Open Elective 6",3,3,0,0,3,60,40,0,0,100,"OE"),
        sub(5,"CE0525","Programming for Scientific Computing",4,3,0,2,5,60,40,60,40,200,"Core"),
        sub(6,"CE0522","Web Technology",4,3,0,2,5,60,40,60,40,200,"Core"),
        sub(7,"CE0523","Internship Credit / Online Courses / MOOC",2,0,0,0,0,0,0,100,0,100,"IC"),
    ]},
    {"semester": "VI", "subjects": [
        sub(1,"CE0616","Software Engineering with UML",4,3,0,2,5,60,40,60,40,200,"Core"),
        sub(2,"CE0617","Theory of Computation",4,4,0,0,4,60,40,0,0,100,"Core"),
        pe(3,"Program Elective I (choose one)",
           [{"subject_code":"CE0630","subject_name":"Data Science"},
            {"subject_code":"CE0631","subject_name":"Information Retrieval"},
            {"subject_code":"CE0632","subject_name":"Web Data Management"}],
           4,3,0,2,5,60,40,60,40,200,"PE"),
        pe(4,"Program Elective II (choose one)",
           [{"subject_code":"CE0618","subject_name":"Advanced Java Technology"},
            {"subject_code":"CE0619","subject_name":"Advance .Net Framework"},
            {"subject_code":"CE0628","subject_name":"Mobile Application Development (Android & iOS)"}],
           4,3,0,2,5,60,40,60,40,200,"PE"),
        pe(5,"Program Elective III (choose one)",
           [{"subject_code":"CE0633","subject_name":"Distributed Systems"},
            {"subject_code":"CE0634","subject_name":"Cryptography & Network Security"},
            {"subject_code":"CE0629","subject_name":"Data Compression"}],
           4,3,0,2,5,60,40,60,40,200,"PE"),
        sub(6,None,"Open Elective 7",3,3,0,0,3,60,40,0,0,100,"OE"),
        sub(7,None,"Research Guided Seminar",2,0,2,0,2,100,0,0,0,100,"HS"),
        sub(8,"CE0622","Internet of Things",4,3,0,2,5,60,40,60,40,200,"ES"),
    ]},
    {"semester": "VII", "subjects": [
        pe(1,"Program Elective IV (choose one)",
           [{"subject_code":"CE0716","subject_name":"Data Warehouse & Mining"},
            {"subject_code":"CE0718","subject_name":"Advance Computer Architecture"},
            {"subject_code":"CE0721","subject_name":"Advance Operating System"}],
           4,3,0,2,5,60,40,60,40,200,"PE"),
        sub(2,"CE0717","Compiler Design",4,3,1,0,4,60,40,0,0,100,"Core"),
        pe(3,"Open Elective 8 (choose one)",
           [{"subject_code":None,"subject_name":"Cyber Security"},
            {"subject_code":None,"subject_name":"Block Chaining"},
            {"subject_code":None,"subject_name":"Soft Computing"},
            {"subject_code":None,"subject_name":"Embedded System"}],
           3,2,0,2,4,0,0,0,0,0,"OE"),
        pe(4,"Program Elective V (choose one)",
           [{"subject_code":"CE0728","subject_name":"Natural Language Processing"},
            {"subject_code":"CE0730","subject_name":"Human Computer Interface"},
            {"subject_code":"CE0732","subject_name":"Computer Vision and Applications"},
            {"subject_code":"CE0723","subject_name":"Cloud Computing"}],
           4,3,0,2,5,60,40,60,40,200,"PE"),
        sub(5,"CE0727","Software Group Project-I",2,0,1,2,3,0,0,100,0,100,"PRJ"),
        sub(6,None,"Open Elective 9",3,0,0,0,3,60,40,0,0,100,"OE"),
        sub(7,"CE0726","Internship Credit / Online Courses / MOOC",2,0,0,0,0,0,0,100,0,100,"IC"),
    ]},
    {"semester": "VIII", "subjects": [
        sub(1,"CE0816","Project",14,0,0,28,28,0,0,60,40,100,"PRJ"),
    ]},
]

json1 = {
    "program": "B.Tech Computer Engineering",
    "institute": "Indus Institute of Engineering & Technology, Indus University",
    "semesters": semesters_data
}

with open(os.path.join(OUTPUT_DIR, "subjects_list.json"), "w", encoding="utf-8") as f:
    json.dump(json1, f, indent=2, ensure_ascii=False)

print("OK  subjects_list.json written")

# ─────────────────────────────────────────────────────────────────────────────
# 3. JSON 2 – Course Content (parse full PDF text)
# ─────────────────────────────────────────────────────────────────────────────

def clean_text(t):
    """Normalise whitespace, remove bullet chars."""
    t = t.replace("\uf0b7", "-").replace("\u2022", "-").replace("\uf06e", "-")
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()

# ── Universal unit splitter ───────────────────────────────────────────────────
UNIT_HEADER_RE = re.compile(
    r"(?m)^(?:"
    r"UNIT[-\s]?(?:I{1,3}|IV|VI{0,3}|VII|VIII|IX|X)\b"  # UNIT-I..VIII
    r"|U\s*\d+\s"                                          # U 1 , U 2 (space after)
    r"|Unit\s+\d+\s*[:\.]"                                 # Unit 1: / Unit 1.
    r"|Unit\s+\d+\s"                                       # Unit 1 Title (no letter consumed)
    r"|Unit\s+[A-Za-z]"                                    # Unit Basics / Unit Statistics
    r")"
)

def get_unit_label(hdr):
    """Extract unit label from header string without false Roman numeral matches."""
    m_rom = re.search(r"UNIT[-\s]?(I{1,3}|IV|VI{0,3}|VII|VIII|IX|X)\b", hdr)
    if m_rom:
        return f"Unit {m_rom.group(1).upper()}"
    m_dig = re.search(r"(?:U\s*|Unit\s+)(\d+)", hdr, re.IGNORECASE)
    if m_dig:
        return f"Unit {m_dig.group(1)}"
    m_word = re.search(r"Unit\s+([A-Za-z]\w*)", hdr, re.IGNORECASE)
    if m_word:
        return f"Unit {m_word.group(1)}"
    return hdr.strip()[:15]

def parse_units(content_text):
    """
    Split text into unit segments and extract title + content.
    Handles 5 patterns observed in the PDF.
    """
    # Normalise
    text = clean_text(content_text)
    lines = text.split("\n")

    units = []

    # --- Pattern A: U N/Unit N Title N hours (Calculus / MA0211 style) ---
    # Joins adjacent lines when hours wraps: "...11\nhours" → "...11 hours"
    joined = re.sub(r"(\d+)\n(hours?)", r"\1 \2", text, flags=re.IGNORECASE)
    joined_lines = joined.split("\n")
    UNIT_A_RE  = re.compile(r"^(?:U\s*|Unit\s+)(\d+)\s+(.+?)\s+(\d+)\s+hours?", re.IGNORECASE)
    UNIT_A_HDR = re.compile(r"^(?:U\s*\d+|Unit\s+\d+)\s+\w", re.IGNORECASE)
    # Check if ANY line in the first 30 lines matches Pattern A (not just first line)
    has_pattern_a = any(UNIT_A_RE.match(l) for l in joined_lines[:30])
    if has_pattern_a:
        i = 0
        while i < len(joined_lines):
            m = UNIT_A_RE.match(joined_lines[i])
            if m:
                unit_num = m.group(1)
                title    = m.group(2).strip()
                hours    = int(m.group(3))
                content_lines = []
                i += 1
                while i < len(joined_lines):
                    if UNIT_A_RE.match(joined_lines[i]):
                        break
                    content_lines.append(joined_lines[i])
                    i += 1
                units.append({
                    "unit_number": f"Unit {unit_num}",
                    "title": title,
                    "hours": hours,
                    "content": clean_text("\n".join(content_lines))
                })
            else:
                i += 1
        if units:
            return units

    # --- Pattern B & C & D: UNIT-I / Unit N: style (most subjects) ---
    # Split on unit headers
    segments = UNIT_HEADER_RE.split(text)
    headers  = UNIT_HEADER_RE.findall(text)

    if len(headers) < 2:
        # Single or no unit found – return whole text as one unit
        if text.strip():
            return [{"unit_number": "Unit 1", "title": "Course Content", "hours": None,
                     "content": text.strip()}]
        return []

    for idx, hdr in enumerate(headers):
        seg = segments[idx + 1] if idx + 1 < len(segments) else ""
        seg_lines = [l.strip() for l in seg.split("\n")]
        seg_lines = [l for l in seg_lines if l]

        hdr = hdr.strip()
        unit_label = get_unit_label(hdr)

        # Try to extract title and hours from first 1-2 lines of segment
        title = ""
        hours = None
        content_start = 0

        if seg_lines:
            first = seg_lines[0]

            # Pattern: [N hours] or [N]
            hours_m = re.match(r"^\[(\d+)(?:\s*hours?)?\]$", first, re.IGNORECASE)
            if hours_m:
                hours = int(hours_m.group(1))
                # Title on next line
                if len(seg_lines) > 1:
                    second = seg_lines[1]
                    # Check if second line is the title (not all caps and not another unit header)
                    if not UNIT_HEADER_RE.match(second):
                        title = second
                        content_start = 2
                    else:
                        content_start = 1
                else:
                    content_start = 1
            else:
                # Title may be on the same first line as header or on seg first line
                # Check: "Title [N Hours]" or "Title N hours"
                th_m = re.search(r"(.+?)\s*\[?(\d+)\]?\s*[Hh]ours?", first)
                if th_m:
                    title = th_m.group(1).strip(" :-")
                    hours = int(th_m.group(2))
                    content_start = 1
                elif first and not UNIT_HEADER_RE.match(first):
                    # Title is first line, no hours specified
                    # Remove trailing colon
                    title = first.strip(" :-")
                    content_start = 1
                else:
                    content_start = 0

        # If title still empty, try header itself (Unit Basics → "Basics")
        if not title:
            title_from_hdr = re.sub(r"^(?:UNIT[-\s]?[IVX]+|U\s*\d+|Unit\s+\d+\s*[:.]?)\s*", "",
                                    hdr, flags=re.IGNORECASE).strip(" :-")
            title = title_from_hdr

        content = clean_text("\n".join(seg_lines[content_start:]))

        units.append({
            "unit_number": unit_label,
            "title": title,
            "hours": hours,
            "content": content
        })

    return units


def extract_practical(text, total_marks):
    """
    If total_marks == 200, extract LIST OF EXPERIMENTS section.
    Otherwise return "Practical not available".
    """
    if total_marks != 200:
        return "Practical not available"

    # Find LIST OF EXPERIMENTS or LIST OF PRACTICALS section
    m = re.search(
        r"LIST OF (?:EXPERIMENTS?|PRACTICALS?)(.*?)(?=Text Books?:|Reference Books?:|Web Resources?:|$)",
        text, re.IGNORECASE | re.DOTALL
    )
    if not m:
        return {"available": True, "note": "Practical experiments listed in PDF",
                "list_of_experiments": []}

    raw = clean_text(m.group(1))

    # Remove table header rows (common PDF table header patterns)
    raw = re.sub(
        r"(?m)^(?:Practical\s*No\.?|Sr\.?\s*No\.?|S\.?\s*No\.?|Experi\w*\s*No\.?|No\.?)"
        r"[^\n]*(?:Title|Learning|Outcome)[^\n]*\n?",
        "", raw, flags=re.IGNORECASE
    )
    # Also remove standalone "No. Title Learning Outcomes" variants
    raw = re.sub(r"No\.?\s+(?:Title|Outcomes?)[^\n]*\n?", "", raw, flags=re.IGNORECASE)
    # Remove broken "Experi\nment.\nNo." header fragments from PDF tables
    raw = re.sub(r"Experi\s*\n?\s*ment\.?\s*\n?\s*No\.?\s*\n?", "", raw, flags=re.IGNORECASE)
    raw = re.sub(r"(?m)^ment\.\s*$", "", raw, flags=re.IGNORECASE)

    # Split on numbered entries: "1 Text", "2. Text", "3 Text" at line start
    parts = re.split(r"(?m)^\s*(\d{1,2})\s*[\.\)]\s*", raw)

    experiments = []
    # parts alternates: pre-text, num, text, num, text ...
    i = 1
    while i + 1 < len(parts):
        num   = parts[i].strip()
        body  = parts[i + 1].strip()
        # Remove trailing CO-refs and learning outcomes text
        body = re.sub(r"\s+CO[-\d,\s]+$", "", body)
        body = re.sub(r"\s*(?:Knowledge of|Students|Upon|Develop|Apply|Understand)\s+.*$", "", body, flags=re.DOTALL)
        body = clean_text(body)
        if body and len(body) > 5:
            experiments.append(f"{num}. {body[:200]}")
        i += 2

    # Fallback: if numbered split didn't work, take whole section
    if not experiments and raw.strip():
        experiments = [clean_text(raw[:800])]

    return {
        "available": True,
        "list_of_experiments": experiments
    }


# ── Build subject lookup tables ───────────────────────────────────────────────
code_to_sem   = {}
code_to_marks = {}
code_to_name  = {}
for sem in semesters_data:
    for s in sem["subjects"]:
        code = s.get("subject_code")
        marks = s["evaluation_scheme"]["total_marks"]
        if code:
            code_to_sem[code]   = sem["semester"]
            code_to_marks[code] = marks
            code_to_name[code]  = s["subject_name"]
        for opt in s.get("elective_options", []):
            oc = opt.get("subject_code")
            if oc:
                code_to_sem[oc]   = sem["semester"]
                code_to_marks[oc] = marks
                code_to_name[oc]  = opt["subject_name"]

# ── Identify subject start pages ──────────────────────────────────────────────
subj_re = re.compile(r"Subject\s*:\s*(.+)", re.IGNORECASE)
# Code can appear as "Subject Code: CE0720" or within "Subject: CE0716" (when PDF has swapped fields)
# or as "Subject Code: :CE0723" (extra colon)
code_re = re.compile(r"(?:Subject\s+Code\s*[:\-]+\s*[:]*|Subject\s*:\s*)([A-Z]{2,5}\d{3,6})", re.IGNORECASE)
sem_re  = re.compile(r"\bSemester\s*[:\-]?\s*(I{1,3}|IV|VI{0,3}|VII|VIII|IX|X|\d+)\s*$", re.IGNORECASE | re.MULTILINE)

subject_starts = []
for idx, pg in enumerate(all_pages):
    if subj_re.search(pg):
        subject_starts.append(idx)

# Build blocks
subject_blocks = []
for i, start_i in enumerate(subject_starts):
    end_i = subject_starts[i + 1] if i + 1 < len(subject_starts) else len(all_pages)
    block = "\n".join(all_pages[start_i:end_i])
    subject_blocks.append(block)

print(f"Found {len(subject_blocks)} subject blocks")

# ── Parse each subject block ──────────────────────────────────────────────────
course_list = []

for block in subject_blocks:
    block_clean = clean_text(block)

    # Subject name
    m_name = subj_re.search(block_clean)
    name = m_name.group(1).strip() if m_name else "Unknown"
    # Drop trailing "Program: ..." part
    name = re.split(r"\s+Program\s*:", name, flags=re.IGNORECASE)[0].strip()
    # Drop trailing segment label like "(ES)"
    name = re.sub(r"\s*\([A-Z]+\)\s*$", "", name).strip()

    # Subject code – search first few lines only to avoid picking up experiment codes
    header_block = "\n".join(block_clean.split("\n")[:15])
    m_code = code_re.search(header_block)
    # If "Subject: CE0716" style (code in subject name position), name will be a code
    if not m_code:
        m_code = code_re.search(block_clean[:500])
    code = m_code.group(1).strip().upper() if m_code else None

    # If name looks like a code (e.g. "CE0716"), swap name and look for real name
    if name and re.match(r"^[A-Z]{2,5}\d{3,6}$", name):
        code = name  # name field actually contained the code
        # Use JSON1 lookup first
        if code in code_to_name:
            name = code_to_name[code]
        else:
            # Try to find real name from "Subject Code: Data Warehouse &\nMining" pattern
            real_name_m = re.search(
                r"Subject\s+Code\s*[:\-]+\s*(?:[A-Z]{2,5}\d{3,6}\s+)?(.+?)(?:\n|Program\s*:)",
                header_block, re.IGNORECASE
            )
            if real_name_m:
                name = real_name_m.group(1).strip()
    # Final fallback: use the canonical name from JSON1 if available
    if code and code in code_to_name and not re.match(r"^[A-Z]{2,5}\d{3,6}$", name):
        pass  # keep parsed name (may have more detail than JSON1)
    elif code and code in code_to_name:
        name = code_to_name[code]

    # Semester – use code_to_sem lookup first (most reliable), fallback to regex
    sem = code_to_sem.get(code)
    if not sem:
        m_sem = sem_re.search(header_block)
        sem = m_sem.group(1).strip() if m_sem else "Unknown"

    # Total marks – from JSON1 lookup first, else parse from block
    marks = code_to_marks.get(code)
    if marks is None:
        # Look for evaluation table value 100 or 200 at line end
        m_mk = re.search(r"\b(200|100)\s*$", block_clean, re.MULTILINE)
        marks = int(m_mk.group(1)) if m_mk else 100

    # --- Extract CONTENT section ---
    # Remove everything before "CONTENT" keyword (objectives, header etc.)
    content_m = re.search(
        r"(?:CONTENT|Course Content|COURSE CONTENT|CONTENTS)\s*\n(.*?)(?=Text Books?:|Reference Books?:|Web Resources?:|LIST OF EXPERIMENTS|$)",
        block_clean, re.IGNORECASE | re.DOTALL
    )
    content_section = content_m.group(1) if content_m else block_clean

    units = parse_units(content_section)

    practical = extract_practical(block_clean, marks)

    course_list.append({
        "subject_code": code,
        "subject_name": name,
        "semester": sem,
        "total_marks": marks,
        "course_units": units,
        "practical": practical
    })

with open(os.path.join(OUTPUT_DIR, "subjects_course_content.json"), "w", encoding="utf-8") as f:
    json.dump(course_list, f, indent=2, ensure_ascii=False)

print(f"OK  subjects_course_content.json written  ({len(course_list)} subjects)")
print("\nDone! Both JSON files saved to:", OUTPUT_DIR)

# Quick validation
print("\n--- Quick validation ---")
for entry in course_list:
    n_units = len(entry["course_units"])
    has_prac = entry["practical"] != "Practical not available"
    marks = entry["total_marks"]
    code  = entry["subject_code"] or "???"
    print(f"  [{code}] {entry['subject_name'][:45]:45s} Sem:{entry['semester']:5s} "
          f"Marks:{marks:3d}  Units:{n_units}  Practical:{'Yes' if has_prac else 'No '}")
