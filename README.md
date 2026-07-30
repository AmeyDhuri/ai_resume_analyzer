# AI Resume Analyzer

A Flask-based web application that uses local AI inference to evaluate resumes, identify gaps, and score them against specific job descriptions — without relying on paid external APIs.

Upload a resume, get structured AI feedback, compare it against a job description, and manage everything through a dashboard with JWT-secured API access.

---

## Why this project

Most resume-screening tools either require sending your data to a third-party API (cost + latency + privacy tradeoffs) or are just static keyword matchers. This project runs inference **locally** via Ollama (Phi-3), so it can be queried repeatedly with no per-request cost, and processes uploads **asynchronously** so the API stays responsive even under load.

---

## Features

### Authentication
- User registration and login
- Secure password hashing
- Session-based authentication
- Password management

### Resume Management
- Upload PDF and DOCX resumes
- Resume storage and organization
- View, search, sort, and delete uploaded resumes

### AI Resume Analysis
- Resume text extraction (handles PDFs and DOCX, including table-based layouts)
- AI-generated feedback across five sections:
  - Strengths
  - Weaknesses
  - Missing Skills
  - ATS Optimization Tips
  - Improvement Recommendations

### Job Matching
- Compare a resume against a specific job description
- Identify skill gaps
- Score relevance for a target role

### Admin Dashboard
- User management
- Resume monitoring
- Audit logs
- Administrative overview

### Security
- File type validation and upload restrictions
- JWT authentication (Flask-JWT-Extended) for API endpoints
- Rate limiting (Flask-Limiter) to prevent upload abuse

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask |
| ORM / Migrations | Flask-SQLAlchemy, Flask-Migrate |
| Auth | Flask-JWT-Extended |
| Rate Limiting | Flask-Limiter |
| Database | PostgreSQL |
| AI Inference | Local Ollama API (Phi-3 model) |
| Document Parsing | pdfplumber, pdfminer.six, python-docx |
| Frontend | HTML, Bootstrap, Jinja2 |

---

## Architecture

```
Client (Browser)
      │
      ▼
Flask App  ──►  JWT Auth Layer  ──►  Rate Limiter
      │
      ▼
Resume Upload (PDF/DOCX)
      │
      ▼
Parser (pdfplumber / python-docx)  ──►  Extracted Text
      │
      ▼
AI Service  ──►  Ollama (Phi-3, local inference)
      │
      ▼
Structured Feedback  ──►  PostgreSQL  ──►  Dashboard
```

---

## Project Structure

```
ai_resume_analyzer/
│
├── app/
│   ├── admin/
│   │   ├── models.py
│   │   ├── routes.py
│   │   └── service.py
│   │
│   ├── ai/
│   │   └── service.py
│   │
│   ├── auth/
│   │   ├── models.py
│   │   ├── routes.py
│   │   └── service.py
│   │
│   ├── resume/
│   │   ├── models.py
│   │   ├── routes.py
│   │   └── service.py
│   │
│   ├── utils/
│   │   ├── analyzer.py
│   │   └── parser.py
│   │
│   ├── templates/
│   ├── extensions.py
│   ├── config.py
│   └── __init__.py
│
├── migrations/
├── uploads/
├── requirements.txt
└── run.py
```

---

## Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/AmeyDhuri/ai_resume_analyzer.git
cd ai_resume_analyzer
```

### 2. Create a virtual environment
```bash
python -m venv venv
```

Activate it:

**Windows**
```bash
venv\Scripts\activate
```

**Linux / Mac**
```bash
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
Create a `.env` file in the project root:
```env
SECRET_KEY=your_secret_key
DATABASE_URL=postgresql://username:password@localhost/ai_resume_analyzer
JWT_SECRET_KEY=your_jwt_secret
```

### 5. Run database migrations
```bash
flask db upgrade
```

### 6. Start Ollama
Make sure Ollama is installed and running locally:
```bash
ollama run phi3
```
The app expects Ollama at `http://127.0.0.1:11434`.

### 7. Start the application
```bash
python run.py
```
Then open `http://127.0.0.1:5000` in your browser.

---

## API Overview

### Resume Upload
- Upload PDF/DOCX resumes
- File type validation
- Rate-limited to prevent abuse

### Resume Management
- List a user's resumes
- Retrieve resume details
- Delete resumes

### Resume Analysis
- Extract resume content
- Run AI-powered review
- Match against a job description

*(For detailed request/response formats, see the route files under `app/resume/routes.py` and `app/auth/routes.py`.)*

---

## AI Feedback Format

Each analysis returns structured feedback across five sections:

1. **Strengths** — what the resume does well
2. **Weaknesses** — gaps in content or presentation
3. **Missing Skills** — relevant skills absent from the resume
4. **ATS Tips** — formatting/keyword changes to pass automated screening
5. **Improvements** — concrete suggestions to strengthen the resume

---

## Roadmap

- [ ] ATS scoring system (numeric match score)
- [ ] Resume version comparison
- [ ] Export analyzed resume as PDF
- [ ] Advanced job matching (weighted skill relevance)
- [ ] Recruiter-facing dashboard
- [ ] Email notifications
- [ ] Resume templates
- [ ] AI-generated resume rewriting

---

## Author

**Amey Dhuri**
GitHub: [@AmeyDhuri](https://github.com/AmeyDhuri)
