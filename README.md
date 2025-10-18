# AI-Powered Resume Analyzer
<img width="1117" height="650" alt="Screenshot 2025-10-18 191847" src="https://github.com/user-attachments/assets/bf598974-d079-4425-8c99-2726553b14af" />
<img width="1161" height="934" alt="Screenshot 2025-10-18 192137" src="https://github.com/user-attachments/assets/9187d32f-76a5-4541-b733-5aff40bcaf9c" />



##  Description
**IntelliResume** is an AI-driven resume analysis system built using **Flask** and **NLP**.  
It evaluates resumes based on **skills, grammar accuracy, and readability** — giving both job seekers and recruiters actionable insights to improve resume quality.

---

##  Features
-  **Multi-format Upload:** Supports `.pdf` and `.docx` resumes  
-  **Skill Extraction:** Detects technical skills like Python, React, Flask, etc.  
-  **Grammar Checking:** Uses LanguageTool to detect and score grammatical correctness  
-  **Readability Analysis:** Evaluates how easy your resume is to read using Flesch Reading Ease  
-  **Composite Scoring:** Combines Skills + Grammar + Readability for a final score  
-  **Actionable Feedback:** Provides detailed improvement suggestions  

---

##  Tech Stack

| Component | Technology Used |
|------------|----------------|
| Backend | Flask |
| NLP Engine | spaCy |
| Grammar Checking | LanguageTool |
| Readability | Textstat |
| File Parsing | PyPDF2, docx2txt |
| Language Processing | Regex, Python |
| Frontend | HTML + Jinja2 Templates |

---

##  System Architecture

```mermaid
flowchart TD
    A["User Uploads Resume (.pdf/.docx)"] --> B["System Extracts Text"]
    B --> C["NLP Processes Resume"]
    C --> D["Matches with Job Description"]
    D --> E["ATS Score Generated"]
    E --> F["User Gets Feedback / Ranking"]

    %% Optional: Add decision step
    D --> G{"Match Threshold Met?"}
    G -->|Yes| F
    G -->|No| H["Suggest Improvements"]
    H --> F

