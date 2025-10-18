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
