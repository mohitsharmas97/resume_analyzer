
# Resume Analyzer Web App

A **Resume Analyzer** built with **Flask** and **NLP tools** to evaluate resumes for skills, readability, and grammar. It provides users with a **score and actionable feedback** to improve their resumes.

---
<img width="1117" height="650" alt="Screenshot 2025-10-18 191847" src="https://github.com/user-attachments/assets/bf598974-d079-4425-8c99-2726553b14af" />
<img width="1161" height="934" alt="Screenshot 2025-10-18 192137" src="https://github.com/user-attachments/assets/9187d32f-76a5-4541-b733-5aff40bcaf9c" />

## Features

- Upload resumes in **PDF** or **DOCX** format.
- **Skills Analysis**: Matches your resume content against a predefined list of industry-standard technical skills.
- **Readability Score**: Measures how easy it is to read your resume using the Flesch Reading Ease metric.
- **Grammar Check**: Detects grammar and spelling errors.
- **Overall Score**: Combines skills, readability, and grammar into a final score.
- **Personalized Feedback**: Suggestions for improvement based on analysis.

---

## Technology Stack

- **Backend**: Flask
- **NLP & Text Processing**: spaCy, regex, docx2txt, PyPDF2
- **Grammar Checking**: language_tool_python
- **Readability Analysis**: textstat
- **Frontend**: HTML/CSS (Flask templates)

---

## How it Works

```mermaid
flowchart TD
    A[User Uploads Resume PDF DOCX] --> B[Extract Text]
    B --> C[Preprocess Text: cleaning, lowercase]
    C --> D[Skills Analysis using spaCy]
    C --> E[Readability Analysis using textstat]
    C --> F[Grammar Check using LanguageTool]
    D --> G[Compute Skills Score]
    E --> H[Compute Readability Score]
    F --> I[Compute Grammar Score]
    G --> J[Final Score Calculation]
    H --> J
    I --> J
    J --> K[Generate Feedback]
    K --> L[Display Results on Web Page]


