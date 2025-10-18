# import streamlit as st
# import re
# import PyPDF2
# import nltk

# from nltk.corpus import stopwords
# from nltk.stem import WordNetLemmatizer
# from nltk.tokenize import word_tokenize
# from sentence_transformers import SentenceTransformer, util


# # --- Pre-load Model & NLTK data ---
# @st.cache_resource
# def load_resources():
#     nltk.download('punkt')
#     nltk.download('punkt_tab') # This line fixes the error
#     nltk.download('stopwords')
#     nltk.download('wordnet')
#     model = SentenceTransformer('all-MiniLM-L6-v2')
#     stop_words = set(stopwords.words('english'))
#     lemmatizer = WordNetLemmatizer()
#     return model, stop_words, lemmatizer

# model, stop_words, lemmatizer = load_resources()

# # --- Function to extract text from a PDF ---
# def extract_text_from_pdf(pdf_file):
#     try:
#         pdf_reader = PyPDF2.PdfReader(pdf_file)
#         text = ""
#         for page in pdf_reader.pages:
#             text += page.extract_text()
#         return text
#     except Exception as e:
#         st.error(f"Error reading PDF file: {e}")
#         return None

# # --- Your existing cleaning function ---
# def clean_resume(text):
#     text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
#     text = re.sub(r'\@\S+', ' ', text)
#     text = re.sub(r'[^a-zA-Z\s]', ' ', text)
#     tokens = word_tokenize(text)
#     cleaned_tokens = [lemmatizer.lemmatize(token.lower()) for token in tokens if token.lower() not in stop_words]
#     return ' '.join(cleaned_tokens)

# # --- The Core Scoring Function ---
# def calculate_match_score(resume_text, job_desc_text):
#     cleaned_resume = clean_resume(resume_text)
#     cleaned_jd = clean_resume(job_desc_text)
#     resume_embedding = model.encode(cleaned_resume, convert_to_tensor=True)
#     jd_embedding = model.encode(cleaned_jd, convert_to_tensor=True)
#     cosine_score = util.cos_sim(resume_embedding, jd_embedding)[0][0]
#     score = cosine_score.item() * 100
#     return score

# # --- Streamlit Web App Interface ---
# st.set_page_config(page_title="ATS Resume Matcher", layout="wide")

# st.title("🚀 Advanced ATS Resume Matcher")
# st.write("""
# This tool helps you see how well your resume aligns with a job description.
# Paste the job description, upload your resume PDF, and get your match score instantly!
# """)

# st.markdown("---")

# col1, col2 = st.columns(2)

# with col1:
#     st.header("Job Description")
#     job_description = st.text_area("Paste the full job description here:", height=300, label_visibility="collapsed")

# with col2:
#     st.header("Your Resume")
#     resume_pdf = st.file_uploader("Upload your resume in PDF format:", type="pdf", label_visibility="collapsed")

# if st.button("Calculate Match Score", type="primary", use_container_width=True):
#     if job_description and resume_pdf is not None:
#         with st.spinner("Analyzing..."):
#             resume_text = extract_text_from_pdf(resume_pdf)
            
#             if resume_text:
#                 score = calculate_match_score(resume_text, job_description)
#                 st.success(f"### Your Resume Match Score is: **{score:.2f}%**")

#                 if score >= 85:
#                     st.balloons()
#                     st.info("**Excellent match!** Your resume is highly aligned with the job description.")
#                 elif score >= 70:
#                     st.info("**Good match.** Your resume has strong potential. Consider tailoring it slightly to better highlight key skills mentioned in the job description.")
#                 elif score >= 50:
#                     st.warning("**Fair match.** Consider revising your resume to include more relevant keywords and experiences from the job description.")
#                 else:
#                     st.error("**Needs improvement.** Your resume may not be a strong fit for this role. Review the job description carefully and update your resume significantly.")
#     else:
#         st.error("Please provide both a job description and upload your resume PDF.")

import os
import re
import spacy
import pandas as pd
import textstat
import language_tool_python
import docx2txt
import PyPDF2
from flask import Flask, request, render_template, redirect, url_for
from werkzeug.utils import secure_filename

# --- INITIALIZATIONS ---

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Downloading 'en_core_web_sm' model...")
    from spacy.cli import download
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# Initialize LanguageTool for grammar checking
tool = language_tool_python.LanguageTool('en-US')

# Predefined list of skills to match against
TARGET_SKILLS = [
    'python', 'java', 'c++', 'javascript', 'sql', 'html', 'css', 'react', 'angular', 'vue',
    'nodejs', 'django', 'flask', 'git', 'docker', 'kubernetes', 'aws', 'azure', 'gcp',
    'machine learning', 'deep learning', 'nlp', 'data analysis', 'pandas', 'numpy', 'scikit-learn',
    'tensorflow', 'pytorch', 'api', 'rest', 'mongodb', 'postgresql', 'mysql'
]

# --- HELPER FUNCTIONS ---

def extract_text_from_pdf(file_path):
    """Extracts text from a PDF file."""
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ''.join(page.extract_text() for page in reader.pages if page.extract_text())
    return text

def extract_text_from_docx(file_path):
    """Extracts text from a DOCX file."""
    return docx2txt.process(file_path)

def preprocess_text(text):
    """Cleans and preprocesses the text."""
    text = re.sub(r'\s+', ' ', text)  # Remove extra whitespace
    text = re.sub(r'[^\x00-\x7F]+', ' ', text) # Remove non-ASCII characters
    return text.strip().lower()

# --- ANALYSIS FUNCTIONS ---

def analyze_skills(text):
    """Finds matched skills from the predefined list."""
    doc = nlp(text)
    found_skills = set()
    for token in doc:
        # Simple token match
        if token.text in TARGET_SKILLS:
            found_skills.add(token.text)
    # Check for multi-word skills (e.g., "machine learning")
    for skill in TARGET_SKILLS:
        if ' ' in skill and skill in text:
            found_skills.add(skill)
    return list(found_skills)

def calculate_readability_score(text):
    """Calculates Flesch Reading Ease score and normalizes it."""
    score = textstat.flesch_reading_ease(text)
    # Normalize score to be between 0 and 100 for simplicity
    return max(0, min(100, score))

def check_grammar(text):
    """Checks for grammar errors and returns a score."""
    matches = tool.check(text)
    num_errors = len(matches)
    # Score inversely proportional to errors. More errors = lower score.
    # We penalize more heavily after a certain threshold of errors.
    score = max(0, 100 - (num_errors * 5))
    return score, matches

# --- FLASK ROUTES ---

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'resume' not in request.files:
            return redirect(request.url)
        file = request.files['resume']
        if file.filename == '':
            return redirect(request.url)
        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # --- CORE ANALYSIS PIPELINE ---
            # 1. Extract Text
            if filename.endswith('.pdf'):
                raw_text = extract_text_from_pdf(file_path)
            elif filename.endswith('.docx'):
                raw_text = extract_text_from_docx(file_path)
            else:
                return "Unsupported file type. Please upload a PDF or DOCX."

            # 2. Preprocess Text
            resume_text = preprocess_text(raw_text)

            # 3. Perform NLP Analysis
            matched_skills = analyze_skills(resume_text)
            readability_score = calculate_readability_score(resume_text)
            grammar_score, grammar_errors = check_grammar(raw_text) # Use raw text for context

            # 4. Generate Overall Score
            skills_score = min(100, len(matched_skills) * 10) # Simple scoring: 10 points per skill found
            
            final_score = (skills_score * 0.4) + (readability_score * 0.3) + (grammar_score * 0.3)

            # 5. Generate Feedback
            feedback = {
                "skills": "Great job on listing relevant skills!" if skills_score > 50 else f"Consider adding more industry-standard skills. We found: {', '.join(matched_skills)}.",
                "readability": "Your resume is easy to read." if readability_score > 60 else "Your resume could be easier to read. Try using shorter sentences and simpler words.",
                "grammar": "Excellent grammar and spelling." if grammar_score > 80 else f"Found {len(grammar_errors)} potential grammar issues. Proofread carefully."
            }

            return render_template('result.html',
                                   score=round(final_score),
                                   skills_score=round(skills_score),
                                   readability_score=round(readability_score),
                                   grammar_score=round(grammar_score),
                                   matched_skills=matched_skills,
                                   feedback=feedback)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
