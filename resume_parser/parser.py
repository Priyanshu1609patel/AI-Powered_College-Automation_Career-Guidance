import spacy
import fitz  # PyMuPDF
from docx import Document

nlp = spacy.load("en_core_web_sm")

COMMON_SKILLS = [
    'python', 'java', 'sql', 'machine learning', 'data analysis',
    'c++', 'excel', 'html', 'css', 'javascript', 'flask', 'django',
    'aws', 'azure', 'linux', 'git', 'figma', 'leadership', 'agile', 'communication', 'networking', 'security'
]

def extract_text(file_path):
    if file_path.endswith('.pdf'):
        return extract_text_from_pdf(file_path)
    elif file_path.endswith('.docx'):
        return extract_text_from_docx(file_path)
    else:
        return ""

def extract_text_from_pdf(path):
    text = ""
    doc = fitz.open(path)
    for page in doc:
        text += page.get_text()
    return text

def extract_text_from_docx(path):
    text = ""
    doc = Document(path)
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text

def extract_resume_data(text):
    doc = nlp(text)
    skills = set()
    for token in doc:
        if token.text.lower() in COMMON_SKILLS:
            skills.add(token.text.lower())
    education = []
    experience = []
    for ent in doc.ents:
        if ent.label_ == "ORG" or ent.label_ == "EDUCATION":
            education.append(ent.text)
        if ent.label_ == "DATE":
            experience.append(ent.text)
    return {
        "skills": ", ".join(skills),
        "education": ", ".join(set(education)),
        "experience": ", ".join(set(experience))
    }