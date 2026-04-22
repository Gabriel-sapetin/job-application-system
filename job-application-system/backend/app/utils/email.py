"""
Email notification utility — JobTrack
Uses fastapi-mail. Add to requirements.txt: fastapi-mail==1.4.1

Environment variables needed in .env:
  MAIL_USERNAME=your@gmail.com
  MAIL_PASSWORD=your_app_password
  MAIL_FROM=your@gmail.com
  MAIL_PORT=587
  MAIL_SERVER=smtp.gmail.com
"""
import os
from typing import Optional

# ── Check if fastapi-mail is installed ──────────────────
try:
    from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
    MAIL_ENABLED = True
except ImportError:
    MAIL_ENABLED = False
    print("⚠  fastapi-mail not installed. Run: pip install fastapi-mail==1.4.1")

# ── Mail config (reads from .env) ────────────────────────
def _get_mail_config():
    if not MAIL_ENABLED:
        return None
    try:
        return ConnectionConfig(
            MAIL_USERNAME   = os.getenv("MAIL_USERNAME", ""),
            MAIL_PASSWORD   = os.getenv("MAIL_PASSWORD", ""),
            MAIL_FROM       = os.getenv("MAIL_FROM", "noreply@jobtrack.com"),
            MAIL_PORT       = int(os.getenv("MAIL_PORT", "587")),
            MAIL_SERVER     = os.getenv("MAIL_SERVER", "smtp.gmail.com"),
            MAIL_STARTTLS   = True,
            MAIL_SSL_TLS    = False,
            USE_CREDENTIALS = True,
            VALIDATE_CERTS  = True,
        )
    except Exception as e:
        print(f"⚠  Mail config error: {e}")
        return None

# ── Email templates ──────────────────────────────────────
def _accepted_html(applicant_name: str, job_title: str, company: str) -> str:
    return f"""
    <div style="font-family:Arial,sans-serif;max-width:560px;margin:0 auto;background:#0a0a0a;color:#f2f2f2;border-radius:12px;overflow:hidden;">
      <div style="background:#111;padding:24px;border-bottom:1px solid #222;">
        <span style="font-size:18px;font-weight:700;">Job<span style="color:#7fff00;">Track</span></span>
      </div>
      <div style="padding:32px;">
        <h2 style="color:#44dd88;margin:0 0 12px;">🎉 Congratulations, {applicant_name}!</h2>
        <p style="color:#a0a0a0;line-height:1.7;">
          Your application for <strong style="color:#f2f2f2;">{job_title}</strong>
          at <strong style="color:#f2f2f2;">{company}</strong> has been
          <span style="color:#44dd88;font-weight:700;">accepted</span>.
        </p>
        <p style="color:#a0a0a0;line-height:1.7;">
          The employer will be in touch with next steps. Best of luck!
        </p>
        <a href="http://127.0.0.1:5500/job-application-system/frontend/pages/dashboard.html"
           style="display:inline-block;margin-top:20px;padding:12px 24px;background:#7fff00;color:#000;
                  border-radius:8px;text-decoration:none;font-weight:700;">
          View Dashboard →
        </a>
      </div>
      <div style="padding:16px 32px;border-top:1px solid #222;font-size:11px;color:#555;">
        JobTrack — Information Management Final Project
      </div>
    </div>
    """

def _rejected_html(applicant_name: str, job_title: str, company: str) -> str:
    return f"""
    <div style="font-family:Arial,sans-serif;max-width:560px;margin:0 auto;background:#0a0a0a;color:#f2f2f2;border-radius:12px;overflow:hidden;">
      <div style="background:#111;padding:24px;border-bottom:1px solid #222;">
        <span style="font-size:18px;font-weight:700;">Job<span style="color:#7fff00;">Track</span></span>
      </div>
      <div style="padding:32px;">
        <h2 style="color:#f2f2f2;margin:0 0 12px;">Application Update</h2>
        <p style="color:#a0a0a0;line-height:1.7;">
          Hi {applicant_name}, thank you for applying for
          <strong style="color:#f2f2f2;">{job_title}</strong>
          at <strong style="color:#f2f2f2;">{company}</strong>.
        </p>
        <p style="color:#a0a0a0;line-height:1.7;">
          After careful consideration, the employer has decided not to move forward
          with your application at this time. Don't be discouraged — keep applying!
        </p>
        <a href="http://127.0.0.1:5500/job-application-system/frontend/pages/jobs.html"
           style="display:inline-block;margin-top:20px;padding:12px 24px;background:#f2f2f2;color:#000;
                  border-radius:8px;text-decoration:none;font-weight:700;">
          Browse More Jobs →
        </a>
      </div>
      <div style="padding:16px 32px;border-top:1px solid #222;font-size:11px;color:#555;">
        JobTrack — Information Management Final Project
      </div>
    </div>
    """

def _reviewed_html(applicant_name: str, job_title: str, company: str) -> str:
    return f"""
    <div style="font-family:Arial,sans-serif;max-width:560px;margin:0 auto;background:#0a0a0a;color:#f2f2f2;border-radius:12px;overflow:hidden;">
      <div style="background:#111;padding:24px;border-bottom:1px solid #222;">
        <span style="font-size:18px;font-weight:700;">Job<span style="color:#7fff00;">Track</span></span>
      </div>
      <div style="padding:32px;">
        <h2 style="color:#4d9fff;margin:0 0 12px;">👀 Application Under Review</h2>
        <p style="color:#a0a0a0;line-height:1.7;">
          Hi {applicant_name}, your application for
          <strong style="color:#f2f2f2;">{job_title}</strong>
          at <strong style="color:#f2f2f2;">{company}</strong>
          is currently being reviewed by the employer.
        </p>
        <p style="color:#a0a0a0;line-height:1.7;">
          You'll receive another update once a decision has been made. Hang tight!
        </p>
      </div>
      <div style="padding:16px 32px;border-top:1px solid #222;font-size:11px;color:#555;">
        JobTrack — Information Management Final Project
      </div>
    </div>
    """

# ── Public send function ─────────────────────────────────
async def send_status_email(
    to_email: str,
    applicant_name: str,
    job_title: str,
    company: str,
    new_status: str,
) -> bool:
    """Send email notification on application status change.
    Returns True if sent, False if skipped/failed.
    """
    if not MAIL_ENABLED:
        print(f"[Email] Skipped (fastapi-mail not installed): {new_status} → {to_email}")
        return False

    config = _get_mail_config()
    if not config or not os.getenv("MAIL_USERNAME"):
        print(f"[Email] Skipped (mail not configured): {new_status} → {to_email}")
        return False

    templates = {
        "accepted": (_accepted_html(applicant_name, job_title, company),
                     f"🎉 You've been accepted — {job_title}"),
        "rejected": (_rejected_html(applicant_name, job_title, company),
                     f"Application update — {job_title}"),
        "reviewed": (_reviewed_html(applicant_name, job_title, company),
                     f"👀 Your application is being reviewed — {job_title}"),
    }

    if new_status not in templates:
        return False

    html, subject = templates[new_status]

    try:
        message = MessageSchema(
            subject    = subject,
            recipients = [to_email],
            body       = html,
            subtype    = MessageType.html,
        )
        fm = FastMail(config)
        await fm.send_message(message)
        print(f"[Email] Sent '{new_status}' notification → {to_email}")
        return True
    except Exception as e:
        print(f"[Email] Failed to send: {e}")
        return False
