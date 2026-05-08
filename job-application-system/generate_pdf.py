"""
Generate a professional PDF document for the JobTrack Job Application System.
Sections: Objectives, Methodology, Results and Discussion.
"""

from fpdf import FPDF
import os, datetime

OUTPUT = os.path.join(os.path.dirname(__file__), "JobTrack_System_Document.pdf")


class DocPDF(FPDF):
    BLUE = (30, 58, 138)
    DARK = (31, 41, 55)
    GRAY = (107, 114, 128)
    ACCENT = (59, 130, 246)
    WHITE = (255, 255, 255)
    LIGHT_BG = (243, 244, 246)

    def header(self):
        if self.page_no() == 1:
            return
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*self.GRAY)
        self.cell(0, 8, "JobTrack - Job Application System", align="L")
        self.cell(0, 8, f"Page {self.page_no()}", align="R", new_x="LMARGIN", new_y="NEXT")
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(4)

    def footer(self):
        if self.page_no() == 1:
            self.set_y(-15)
            self.set_font("Helvetica", "I", 7)
            self.set_text_color(*self.GRAY)
            self.cell(0, 10, "Information Management - Final Project", align="C")

    # -- helpers --
    def section_title(self, num, title):
        self.ln(6)
        self.set_font("Helvetica", "B", 16)
        self.set_text_color(*self.BLUE)
        self.cell(0, 10, f"{num}. {title}", new_x="LMARGIN", new_y="NEXT")
        y = self.get_y()
        self.set_draw_color(*self.ACCENT)
        self.set_line_width(0.7)
        self.line(self.l_margin, y, self.l_margin + 60, y)
        self.ln(5)

    def sub_title(self, label):
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(*self.DARK)
        self.cell(0, 8, label, new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def body(self, txt):
        self.set_font("Helvetica", "", 11)
        self.set_text_color(*self.DARK)
        self.multi_cell(0, 6.5, txt.strip())
        self.ln(3)

    def bullet(self, items):
        self.set_font("Helvetica", "", 11)
        self.set_text_color(*self.DARK)
        for item in items:
            self.cell(6)
            self.cell(5, 6.5, "-")
            self.multi_cell(0, 6.5, item)
        self.ln(2)

    def key_value_block(self, pairs):
        self.set_fill_color(*self.LIGHT_BG)
        for k, v in pairs:
            self.set_font("Helvetica", "B", 10)
            self.set_text_color(*self.BLUE)
            self.cell(50, 7, k, fill=True)
            self.set_font("Helvetica", "", 10)
            self.set_text_color(*self.DARK)
            self.cell(0, 7, v, fill=True, new_x="LMARGIN", new_y="NEXT")
        self.ln(3)

    def table(self, headers, rows):
        w = (self.w - self.l_margin - self.r_margin) / len(headers)
        self.set_font("Helvetica", "B", 10)
        self.set_fill_color(*self.BLUE)
        self.set_text_color(*self.WHITE)
        for h in headers:
            self.cell(w, 8, h, border=1, fill=True, align="C")
        self.ln()
        self.set_font("Helvetica", "", 10)
        self.set_text_color(*self.DARK)
        fill = False
        for row in rows:
            if self.get_y() > 260:
                self.add_page()
            if fill:
                self.set_fill_color(248, 250, 252)
            else:
                self.set_fill_color(*self.WHITE)
            for val in row:
                self.cell(w, 7, str(val), border=1, fill=True, align="C")
            self.ln()
            fill = not fill
        self.ln(3)


def build():
    pdf = DocPDF("P", "mm", "A4")
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.set_left_margin(20)
    pdf.set_right_margin(20)

    # ====================================================
    # TITLE PAGE
    # ====================================================
    pdf.add_page()
    pdf.ln(50)
    pdf.set_font("Helvetica", "B", 28)
    pdf.set_text_color(*pdf.BLUE)
    pdf.cell(0, 14, "JobTrack", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 18)
    pdf.set_text_color(*pdf.DARK)
    pdf.cell(0, 10, "Job Application System", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)
    pdf.set_draw_color(*pdf.ACCENT)
    pdf.set_line_width(0.8)
    mid = pdf.w / 2
    pdf.line(mid - 30, pdf.get_y(), mid + 30, pdf.get_y())
    pdf.ln(10)
    pdf.set_font("Helvetica", "I", 13)
    pdf.set_text_color(*pdf.GRAY)
    pdf.cell(0, 8, "Information Management - Final Project", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(30)
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(*pdf.DARK)
    today = datetime.date.today().strftime("%B %d, %Y")
    pdf.cell(0, 7, f"Date: {today}", align="C", new_x="LMARGIN", new_y="NEXT")

    # ====================================================
    # 1. OBJECTIVES
    # ====================================================
    pdf.add_page()
    pdf.section_title("I", "OBJECTIVES")

    pdf.sub_title("1.1  General Objective")
    pdf.body(
        "To design and develop a full-stack, web-based Job Application System (JobTrack) "
        "that streamlines the end-to-end hiring workflow by connecting job-seeking applicants "
        "with employers through a secure, intuitive, and feature-rich platform, while "
        "demonstrating applied competencies in information management, database design, "
        "RESTful API development, and modern front-end engineering."
    )

    pdf.sub_title("1.2  Specific Objectives")
    pdf.bullet([
        "Implement a role-based authentication system (Applicant, Employer, Admin) with secure "
        "password hashing (bcrypt) and JWT-based session management.",
        "Build a comprehensive job listing module that supports CRUD operations, full-text search, "
        "category filtering, pagination, deadline enforcement, and maximum applicant slots.",
        "Develop an application tracking workflow enabling applicants to submit, monitor, and "
        "withdraw applications, and employers to review, accept, or reject candidates.",
        "Provide real-time analytics and dashboards for employers, including view counts, "
        "application timelines, acceptance rates, and slot fill rates.",
        "Integrate an in-app notification system and email alerts (via SMTP) to keep users "
        "informed of status changes and new applications.",
        "Incorporate a messaging/chat module tied to applications, enabling direct communication "
        "between employers and applicants.",
        "Design and enforce an admin panel for platform governance, including job/user reporting, "
        "employer verification, and content moderation.",
        "Apply security best practices such as CORS policies, CSRF origin checks, rate limiting, "
        "HTTP security headers (HSTS, CSP), and input validation.",
        "Utilize Supabase (PostgreSQL) as the cloud database with a well-normalized relational "
        "schema and appropriate indexes for performance optimization.",
        "Deploy the system on a cloud platform (Render) with keep-alive mechanisms to ensure "
        "availability on the free tier.",
    ])

    # ====================================================
    # 2. METHODOLOGY
    # ====================================================
    pdf.add_page()
    pdf.section_title("II", "METHODOLOGY")

    pdf.sub_title("2.1  Development Approach")
    pdf.body(
        "The project followed an Agile-inspired iterative methodology. Features were "
        "developed in incremental sprints, with each sprint delivering a functional vertical "
        "slice (database migration, API route, and UI page). Continuous testing and user "
        "feedback informed subsequent iterations. Version control was managed with Git, "
        "enabling safe experimentation through branching and rollback."
    )

    pdf.sub_title("2.2  Technology Stack")
    pdf.table(
        ["Layer", "Technology", "Purpose"],
        [
            ["Frontend", "HTML5 / CSS3 / JS", "User interface & interactions"],
            ["Backend", "Python + FastAPI", "RESTful API server"],
            ["Database", "Supabase (PostgreSQL)", "Cloud-hosted relational data"],
            ["Auth", "bcrypt + PyJWT", "Password hashing & tokens"],
            ["Email", "fastapi-mail (SMTP)", "Transactional notifications"],
            ["Hosting", "Render (Free Tier)", "Cloud deployment"],
            ["Tooling", "Uvicorn / pip / Git", "Dev server, packages, VCS"],
        ],
    )

    pdf.sub_title("2.3  System Architecture")
    pdf.body(
        "JobTrack adopts a classic three-tier architecture:\n\n"
        "Presentation Tier - Static HTML/CSS/JS pages served independently and communicating "
        "with the API via fetch(). No build tools or framework overhead is introduced, keeping "
        "the front-end lightweight and easily deployable.\n\n"
        "Application Tier - A FastAPI application organized into modular routers: Auth, Jobs, "
        "Applications, Users, Upload, Analytics, Chat, Admin, Saved Jobs, and Notifications. "
        "Middleware layers handle CORS, CSRF origin checks, rate limiting, request logging, "
        "and security header injection.\n\n"
        "Data Tier - Supabase provides a managed PostgreSQL instance. The schema evolved "
        "through six incremental SQL migrations (V1-V6), adding tables for users, jobs, "
        "applications, reports, user reports, and messages."
    )

    pdf.sub_title("2.4  Database Design")
    pdf.body("The relational schema consists of the following core tables:")
    pdf.table(
        ["Table", "Key Columns", "Relationships"],
        [
            ["users", "id, name, email, role", "Referenced by jobs, apps"],
            ["jobs", "id, title, company, status", "FK employer_id -> users"],
            ["applications", "id, job_id, user_id, status", "FK job_id, user_id"],
            ["reports", "id, job_id, reporter_id", "FK to jobs, users"],
            ["user_reports", "id, reported_id, reporter_id", "FK to users"],
            ["messages", "id, application_id, sender_id", "FK to applications, users"],
        ],
    )
    pdf.body(
        "Performance indexes were created on frequently queried columns such as job type, "
        "location, status, category, application status, and message read flags. "
        "Referential integrity is enforced through foreign key constraints with ON DELETE "
        "CASCADE and ON DELETE SET NULL policies as appropriate."
    )

    pdf.sub_title("2.5  Security Measures")
    pdf.bullet([
        "Password Hashing: bcrypt with 12 salt rounds ensures passwords are stored irreversibly.",
        "JWT Authentication: Tokens are issued on login with a 7-day TTL, transmitted via "
        "HTTP-only cookies and Authorization headers, and validated on every protected route.",
        "Rate Limiting: A global middleware throttles excessive requests; a dedicated login "
        "rate limiter locks accounts after 5 failed attempts within a 5-minute window.",
        "CORS: An explicit allow-list of origins prevents unauthorized cross-origin requests.",
        "CSRF: Origin header validation blocks state-changing requests from unknown origins.",
        "HTTP Security Headers: X-Content-Type-Options, Referrer-Policy, Content-Security-Policy, "
        "X-Frame-Options, HSTS, and Permissions-Policy are injected via middleware.",
        "Input Validation: Pydantic models enforce type, length, and format constraints on "
        "every incoming request body.",
    ])

    pdf.sub_title("2.6  Key Features Implemented")
    pdf.bullet([
        "User Registration and Login with role selection (Applicant / Employer).",
        "Job Posting (Employer): create, edit, delete listings with image, category, salary, "
        "deadline, and max applicant settings.",
        "Job Browsing (Applicant): search, filter by type/location/category, paginate results.",
        "Application Submission with resume URL and cover letter; duplicate prevention.",
        "Application Status Tracking: pending -> reviewed -> accepted/rejected pipeline.",
        "Employer Dashboard with analytics charts (timeline, status breakdown, fill rate).",
        "Saved Jobs: applicants can bookmark listings for later review.",
        "In-App Notifications for new applications and status changes.",
        "Email Notifications via SMTP for acceptance, rejection, and review updates.",
        "Messaging/Chat between employers and applicants per application.",
        "Admin Panel: manage users, verify employers, review job/user reports.",
        "Password Reset via email with secure time-limited tokens.",
        "User Profiles with bio, social links, profile picture, and banner.",
        "File Upload support for profile images and resumes.",
    ])

    # ====================================================
    # 3. RESULTS AND DISCUSSION
    # ====================================================
    pdf.add_page()
    pdf.section_title("III", "RESULTS AND DISCUSSION")

    pdf.sub_title("3.1  System Functionality Results")
    pdf.body(
        "The completed JobTrack system successfully delivers a fully functional, multi-role "
        "job application platform. All planned features were implemented and tested across "
        "the three user roles. The table below summarizes the functional test results:"
    )
    pdf.table(
        ["Feature", "Status", "Notes"],
        [
            ["User Registration", "Passed", "Role-based, validated"],
            ["Login / JWT Auth", "Passed", "Cookie + header support"],
            ["Job CRUD", "Passed", "Employer-only access"],
            ["Job Search & Filter", "Passed", "Full-text + ilike fallback"],
            ["Apply for Jobs", "Passed", "Duplicate & deadline checks"],
            ["Status Updates", "Passed", "Email + in-app alerts"],
            ["Analytics Dashboard", "Passed", "Charts and metrics"],
            ["Chat / Messaging", "Passed", "Per-application threads"],
            ["Admin Panel", "Passed", "Reports, verification"],
            ["Password Reset", "Passed", "Email with token"],
            ["Notifications", "Passed", "Real-time in-app"],
            ["Saved Jobs", "Passed", "Bookmark / unbookmark"],
        ],
    )

    pdf.sub_title("3.2  Architecture Evaluation")
    pdf.body(
        "The three-tier separation proved effective for independent development and deployment. "
        "The frontend can be hosted on any static file server (or CDN), while the API runs "
        "as an isolated containerized service. Supabase eliminated the need for self-managed "
        "database infrastructure, significantly reducing DevOps overhead.\n\n"
        "FastAPI's automatic OpenAPI documentation (/docs) provided a built-in testing "
        "interface during development, accelerating API debugging cycles. The modular router "
        "pattern (10 route modules) kept individual files focused and maintainable."
    )

    pdf.sub_title("3.3  Security Analysis")
    pdf.body(
        "The multi-layered security approach addresses the OWASP Top 10 risks relevant to "
        "the application:\n\n"
        "Broken Authentication is mitigated by bcrypt hashing, JWT with expiration, and "
        "login rate limiting. Injection attacks are prevented through Supabase's parameterized "
        "queries and Pydantic's strict input validation. Cross-Site Request Forgery is blocked "
        "by origin header checking. Security misconfiguration is addressed by injecting "
        "protective HTTP headers on every response.\n\n"
        "A notable limitation is the in-memory storage of password reset tokens, which does "
        "not persist across server restarts. For production, these should be stored in Redis "
        "or the database."
    )

    pdf.sub_title("3.4  Performance Considerations")
    pdf.body(
        "Database performance is optimized through targeted indexes on high-cardinality "
        "columns (status, type, location, category) and composite unique constraints to "
        "prevent duplicate applications at the database level. Pagination on the jobs listing "
        "endpoint (default 50, max 100 per page) ensures consistent response times regardless "
        "of dataset size.\n\n"
        "The Render free-tier deployment required a keep-alive mechanism (self-ping every "
        "13 minutes) to prevent cold starts. While acceptable for a student project, a "
        "production deployment would use a paid tier with guaranteed uptime."
    )

    pdf.sub_title("3.5  Challenges and Lessons Learned")
    pdf.bullet([
        "Supabase JWT conflicts during migrations required running SQL blocks individually "
        "and re-authenticating the dashboard session.",
        "CORS configuration needed careful tuning to support both local development "
        "(localhost:5500) and production (Render domain) origins simultaneously.",
        "The free-tier Render deployment spins down after inactivity, necessitating the "
        "keep-alive background thread workaround.",
        "Balancing security strictness (CSP, CSRF) with developer experience required "
        "environment-aware toggles (e.g., relaxed CSRF in development mode).",
        "Iterative schema evolution (6 migrations) highlighted the importance of planning "
        "the data model upfront to minimize breaking changes.",
    ])

    pdf.sub_title("3.6  Recommendations for Future Work")
    pdf.bullet([
        "Implement WebSocket-based real-time notifications and chat for instant updates.",
        "Add resume parsing (PDF extraction) to auto-populate applicant profiles.",
        "Integrate OAuth2 social login (Google, LinkedIn) for faster onboarding.",
        "Migrate reset tokens and rate-limit state to Redis for persistence and scalability.",
        "Introduce automated testing (unit + integration) with pytest and CI/CD pipelines.",
        "Add accessibility (WCAG 2.1) compliance auditing to the frontend.",
        "Implement advanced analytics with data visualization libraries (Chart.js).",
    ])

    # === Save ===
    pdf.output(OUTPUT)
    print(f"\nPDF generated successfully!")
    print(f"Saved to: {OUTPUT}")


if __name__ == "__main__":
    build()
