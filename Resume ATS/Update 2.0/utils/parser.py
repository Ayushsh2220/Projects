import re
import docx2txt
from pdfminer.high_level import extract_text as extract_pdf_text
from PIL import Image
import pytesseract
from sentence_transformers import SentenceTransformer, util


# =====================
# BERT Model Initialization
# =====================
def load_bert_model():
    return SentenceTransformer('all-MiniLM-L6-v2')


# =====================
# Text Extraction Handlers
# =====================
def extract_text_from_pdf(file):
    return extract_pdf_text(file)

def extract_text_from_docx(file):
    return docx2txt.process(file)

def extract_text_from_image(file):
    image = Image.open(file)
    return pytesseract.image_to_string(image)


# =====================
# Section Extractor
# =====================
def extract_section(text, keywords):
    lines = text.lower().split('\n')
    section = []
    found = False
    for line in lines:
        if any(k in line for k in keywords):
            found = True
            continue
        if found and line.strip() == "":
            break
        if found:
            section.append(line)
    return '\n'.join(section).strip()


# =====================
# Skill Extraction
# =====================
def extract_skills_from_jd(jd_text):
    jd_text = jd_text.replace("\n", " ")
    words = re.findall(r'\b([A-Za-z0-9\+\.#]+)\b', jd_text)
    stopwords = {'the', 'and', 'with', 'for', 'you', 'are', 'our', 'this', 'that', 'have'}
    filtered = [w.lower() for w in words if len(w) > 2 and w.lower() not in stopwords]
    return list(set(filtered))


# =====================
# Entity & Skill Matcher
# =====================
def extract_entities(text, jd_text):
    lines = text.strip().split('\n')
    lines = [l.strip() for l in lines if l.strip()]

    name = lines[0] if len(lines[0].split()) <= 4 else ""
    email_match = re.search(r'[\w\.-]+@[\w\.-]+', text)
    phone_match = re.search(r'(\+?\d{1,3}[\s-])?(?:\(?\d{2,4}\)?[\s-]?)?\d{6,10}', text)

    jd_skills = extract_skills_from_jd(jd_text)
    resume_skills = [kw for kw in jd_skills if kw.lower() in text.lower()]

    experience = extract_section(text, ['experience', 'work history'])
    education = extract_section(text, ['education', 'academic'])

    return {
        'name': name,
        'email': email_match.group() if email_match else None,
        'phone': phone_match.group() if phone_match else None,
        'skills': ', '.join(resume_skills),
        'experience': experience,
        'education': education,
        'jd_skills': ', '.join(jd_skills)
    }


# =====================
# BERT Score Calculator
# =====================
def match_score_bert(resume_text, jd_text, model):
    resume_embedding = model.encode(resume_text, convert_to_tensor=True)
    jd_embedding = model.encode(jd_text, convert_to_tensor=True)
    score = util.cos_sim(resume_embedding, jd_embedding)
    return float(score.item())


# =====================
# File Processor (PDF, DOCX, IMAGE)
# =====================
def process_resume_file(file, jd_text, model):
    file_type = file.name.split('.')[-1].lower()
    if file_type == "pdf":
        text = extract_text_from_pdf(file)
    elif file_type == "docx":
        text = extract_text_from_docx(file)
    else:
        text = extract_text_from_image(file)

    entities = extract_entities(text, jd_text)
    entities['score'] = match_score_bert(text, jd_text, model)
    return entities
