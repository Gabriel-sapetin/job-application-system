# JobTrack — Job Application System
> Information Management Final Project

A full-stack job application system built with **Plain HTML/CSS/JS**, **FastAPI**, and **Supabase**.

---

## 📁 Project Structure

```
job-application-system/
├── frontend/                  # Client-side (HTML, CSS, JS)
│   ├── index.html             # Landing page
│   ├── css/style.css          # Global stylesheet
│   ├── js/main.js             # API helper & utilities
│   └── pages/
│       ├── jobs.html          # Browse & apply for jobs
│       ├── login.html         # User login
│       ├── register.html      # User registration
│       └── dashboard.html     # Applicant & employer dashboard
├── backend/                   # Server-side (FastAPI + Python)
│   ├── app/
│   │   ├── main.py            # FastAPI entry point
│   │   ├── database.py        # Supabase client
│   │   ├── models.py          # Pydantic schemas
│   │   └── routes/
│   │       ├── auth.py        # Register & Login
│   │       ├── jobs.py        # CRUD for jobs
│   │       └── applications.py # Apply, track, update
│   ├── requirements.txt
│   └── .env.example
└── database/
    ├── schema.sql             # Table definitions
    └── seed.sql               # Sample data for testing
```

---

## 🚀 Setup Instructions

### 1. Database — Supabase

1. Go to [supabase.com](https://supabase.com) and create a free project
2. Open the **SQL Editor** in your Supabase dashboard
3. Run `database/schema.sql` to create the tables
4. Run `database/seed.sql` to insert sample data

### 2. Backend — FastAPI

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and paste your Supabase URL and Key

# Run the server
uvicorn app.main:app --reload
```

API will be available at: `http://localhost:8000`  
Docs (Swagger UI): `http://localhost:8000/docs`

### 3. Frontend — Static Files

Open `frontend/index.html` directly in your browser **or** use a simple local server:

```bash
cd frontend
python -m http.server 5500
# Visit http://localhost:5500
```

> Make sure your FastAPI server is running at `http://localhost:8000`

---

## 👥 User Roles

| Role | Capabilities |
|------|-------------|
| **Applicant** | Browse jobs, submit applications, track application status, withdraw applications |
| **Employer** | Post jobs, view received applications, accept or reject applicants |

---

## 🔗 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Create account |
| POST | `/auth/login` | Login |
| GET | `/jobs` | List all jobs |
| POST | `/jobs` | Post a new job |
| POST | `/applications` | Submit application |
| GET | `/applications/me` | My applications |
| PATCH | `/applications/{id}` | Update status |
| DELETE | `/applications/{id}` | Withdraw application |

---

## 🛠️ Tech Stack

- **Frontend**: Plain HTML5, CSS3, Vanilla JavaScript
- **Backend**: Python, FastAPI, Uvicorn
- **Database**: Supabase (PostgreSQL)
- **Auth**: bcrypt password hashing
