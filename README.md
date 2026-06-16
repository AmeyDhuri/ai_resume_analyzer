# AI Resume Analyzer

AI Resume Analyzer is a Flask-based web application that helps users evaluate and improve their resumes using AI-powered feedback and job matching analysis.

The application allows users to upload resumes, analyze them using a locally hosted AI model, compare resumes against job descriptions, and manage uploaded resumes through a user-friendly dashboard.

---

## Features

### Authentication

* User registration and login
* Secure password hashing
* Session-based authentication
* Password management

### Resume Management

* Upload PDF and DOCX resumes
* Resume storage and organization
* View uploaded resumes
* Delete resumes
* Search and sort uploaded resumes

### AI Resume Analysis

* Resume text extraction
* AI-generated feedback
* Strength analysis
* Weakness identification
* Missing skill suggestions
* ATS optimization tips
* Improvement recommendations

### Job Matching

* Compare resumes against job descriptions
* Identify skill gaps
* Evaluate resume relevance for specific roles

### Admin Features

* User management
* Resume monitoring
* Audit logs
* Administrative dashboard

### Security

* File type validation
* Upload restrictions
* JWT authentication for API endpoints
* Rate limiting using Flask-Limiter

---

## Tech Stack

### Backend

* Python
* Flask
* Flask-SQLAlchemy
* Flask-Migrate
* Flask-JWT-Extended
* Flask-Limiter

### Database

* PostgreSQL

### AI Integration

* Local Ollama API
* Phi-3 Model

### Document Processing

* pdfplumber
* pdfminer.six
* python-docx

### Frontend

* HTML
* Bootstrap
* Jinja2 Templates

---

## Project Structure

```text
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

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/AmeyDhuri/ai_resume_analyzer.git
cd ai_resume_analyzer
```

### 2. Create Virtual Environment

```bash
python -m venv venv
```

Activate it:

**Windows**

```bash
venv\Scripts\activate
```

**Linux/Mac**

```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file:

```env
SECRET_KEY=your_secret_key

DATABASE_URL=postgresql://username:password@localhost/ai_resume_analyzer

JWT_SECRET_KEY=your_jwt_secret
```

### 5. Run Database Migrations

```bash
flask db upgrade
```

### 6. Start Ollama

Make sure Ollama is running locally:

```bash
ollama run phi3
```

The application expects Ollama at:

```text
http://127.0.0.1:11434
```

### 7. Start the Application

```bash
python run.py
```

Open:

```text
http://127.0.0.1:5000
```

---

## AI Feedback Format

The AI generates feedback in the following sections:

* Strengths
* Weaknesses
* Missing Skills
* ATS Tips
* Improvements

This helps users identify areas where their resume can be strengthened for better job application success.

---

## API Features

### Resume Upload

* Upload PDF resumes
* Upload DOCX resumes
* File validation
* Rate limiting

### Resume Management

* List user resumes
* Retrieve resume details
* Delete resumes

### Resume Analysis

* Extract resume content
* AI-powered review
* Job description matching

---

## Future Improvements

* ATS scoring system
* Resume version comparison
* Resume export as PDF
* Advanced job matching
* Recruiter dashboard
* Email notifications
* Resume templates
* AI-generated resume rewriting

---

## License

This project is licensed under the MIT License.

---

## Author

**Amey Dhuri**

GitHub: https://github.com/AmeyDhuri
