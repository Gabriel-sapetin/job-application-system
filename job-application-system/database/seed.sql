-- ============================================================
-- JobTrack — Seed Data
-- Run AFTER schema.sql to populate the database with test data
-- ============================================================


-- ── SEED USERS ───────────────────────────────────────────────
-- Passwords are bcrypt hashed. Plain text: "password123"
INSERT INTO users (name, email, password, role) VALUES
    ('Admin Employer',  'employer@jobtrack.com',  '$2b$12$KIXBisZCL5V0Kfb1Qm2vYu6t8Hk5F0J3K7N1Qw4R8U2V6X0T4Y9A', 'employer'),
    ('Juan Dela Cruz',  'juan@email.com',          '$2b$12$KIXBisZCL5V0Kfb1Qm2vYu6t8Hk5F0J3K7N1Qw4R8U2V6X0T4Y9A', 'applicant'),
    ('Maria Santos',    'maria@email.com',         '$2b$12$KIXBisZCL5V0Kfb1Qm2vYu6t8Hk5F0J3K7N1Qw4R8U2V6X0T4Y9A', 'applicant')
ON CONFLICT (email) DO NOTHING;


-- ── SEED JOBS ────────────────────────────────────────────────
INSERT INTO jobs (title, company, location, type, salary, description, employer_id) VALUES
    (
        'Frontend Developer',
        'TechCorp Philippines',
        'Davao City',
        'Full-Time',
        '₱35,000 – ₱45,000',
        'We are looking for a skilled frontend developer proficient in HTML, CSS, and JavaScript.',
        1
    ),
    (
        'Data Analyst',
        'Insights Inc.',
        'Remote',
        'Remote',
        '₱28,000 – ₱38,000',
        'Analyze business data and generate reports using SQL and Excel.',
        1
    ),
    (
        'IT Support Intern',
        'StartupHub Cebu',
        'Cebu City',
        'Internship',
        '₱8,000 / month',
        'Assist the IT team with hardware troubleshooting and user support.',
        1
    ),
    (
        'Backend Engineer',
        'CloudSoft Solutions',
        'Manila',
        'Full-Time',
        '₱50,000 – ₱65,000',
        'Build and maintain REST APIs using Python FastAPI and PostgreSQL.',
        1
    ),
    (
        'UI/UX Designer',
        'Creative Co.',
        'Davao City',
        'Part-Time',
        '₱18,000 – ₱25,000',
        'Design user interfaces for mobile and web applications using Figma.',
        1
    )
ON CONFLICT DO NOTHING;


-- ── SEED APPLICATIONS ────────────────────────────────────────
INSERT INTO applications (job_id, name, email, cover_letter, resume_url, status) VALUES
    (
        1,
        'Juan Dela Cruz',
        'juan@email.com',
        'I am a passionate developer with 2 years of experience in web development.',
        'https://drive.google.com/sample-resume-juan',
        'reviewed'
    ),
    (
        2,
        'Maria Santos',
        'maria@email.com',
        'I have strong analytical skills and experience with data visualization tools.',
        'https://drive.google.com/sample-resume-maria',
        'pending'
    ),
    (
        3,
        'Juan Dela Cruz',
        'juan@email.com',
        'I am eager to gain hands-on IT experience through this internship.',
        'https://drive.google.com/sample-resume-juan',
        'accepted'
    )
ON CONFLICT DO NOTHING;
