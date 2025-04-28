
import re
import docx2txt
from pdfminer.high_level import extract_text
from sentence_transformers import SentenceTransformer, util
from PIL import Image
import pytesseract

model = SentenceTransformer('all-MiniLM-L6-v2')

def extract_text_from_pdf(file):
    return extract_text(file)

def extract_text_from_docx(file):
    return docx2txt.process(file)

def extract_text_from_image(file):
    image = Image.open(file)
    return pytesseract.image_to_string(image)

def extract_entities(text):
    lines = text.strip().split('\n')
    lines = [l.strip() for l in lines if l.strip() != ""]
    
    name = lines[0] if len(lines[0].split()) <= 4 else ""
    email = re.search(r'[\w\.-]+@[\w\.-]+', text)
    phone = re.search(r'(\+?\d{1,3}[\s-])?(?:\(?\d{2,4}\)?[\s-]?)?\d{6,10}', text)

    keywords = ['python', 'sql', 'excel', 'java', 'react', 'power bi']
    found_skills = [k for k in keywords if k in text.lower()]

    experience = extract_section(text, ['experience', 'work history'])
    education = extract_section(text, ['education', 'academic'])

    return {
        'name': name,
        'email': email.group() if email else None,
        'phone': phone.group() if phone else None,
        'skills': ', '.join(found_skills),
        'experience': experience,
        'education': education
    }

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

def match_score(clean_resume_text, clean_jd_text):
    resume_vec = model.encode(clean_resume_text, convert_to_tensor=True)
    jd_vec = model.encode(clean_jd_text, convert_to_tensor=True)
    return util.cos_sim(resume_vec, jd_vec).item()

def skill_overlap(resume_skills, jd_skills):
    resume_set = set(resume_skills.lower().split(", "))
    jd_set = set(jd_skills.lower().split(", "))
    if not resume_set or not jd_set:
        return 0.0
    return len(resume_set & jd_set) / len(resume_set | jd_set)

def process_resume_file(file, jd_text):
    file_type = file.name.split('.')[-1].lower()
    if file_type == "pdf":
        text = extract_text_from_pdf(file)
    elif file_type == "docx":
        text = extract_text_from_docx(file)
    else:
        text = extract_text_from_image(file)

    entities = extract_entities(text)

    # Match only based on skills and experience
    cleaned_resume = entities['skills'] + " " + entities['experience']
    cleaned_jd = jd_text.lower()
    score = match_score(cleaned_resume, cleaned_jd)

    # Also calculate skill overlap for clarity
    jd_skills = ', '.join([kw for kw in ['python', 'sql', 'excel', 'java', 'react', 'power bi'] if kw in jd_text.lower()])
    overlap_score = skill_overlap(entities['skills'], jd_skills)

    # Average both scores for final
    final_score = (score + overlap_score) / 2

    entities['score'] = final_score
    return entities
