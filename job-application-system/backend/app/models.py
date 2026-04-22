from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from enum import Enum


class UserRole(str, Enum):
    applicant = "applicant"
    employer  = "employer"

class JobType(str, Enum):
    full_time  = "Full-Time"
    part_time  = "Part-Time"
    internship = "Internship"
    remote     = "Remote"

class JobStatus(str, Enum):
    open   = "open"
    closed = "closed"
    full   = "full"

class AppStatus(str, Enum):
    pending  = "pending"
    reviewed = "reviewed"
    accepted = "accepted"
    rejected = "rejected"


class UserRegister(BaseModel):
    name:     str       = Field(..., min_length=2, max_length=80)
    email:    EmailStr
    password: str       = Field(..., min_length=8, max_length=128)
    role:     UserRole  = UserRole.applicant

    @validator("name")
    def strip_name(cls, v):
        return v.strip()

    @validator("email")
    def lower_email(cls, v):
        return v.lower().strip()


class UserLogin(BaseModel):
    email:    EmailStr
    password: str = Field(..., min_length=1, max_length=128)

    @validator("email")
    def lower_email(cls, v):
        return v.lower().strip()


class UserProfileUpdate(BaseModel):
    about_me:    Optional[str] = Field(None, max_length=500)
    profile_pic: Optional[str] = Field(None)
    banner_url:  Optional[str] = Field(None)                                    # employer cover photo
    instagram:   Optional[str] = Field(None, max_length=30)
    facebook:    Optional[str] = Field(None, max_length=80)
    phone:       Optional[str] = Field(None, max_length=30)    # NEW: contact number
    website:     Optional[str] = Field(None, max_length=2000)  # company website

    @validator("profile_pic", "banner_url", "website")
    def validate_url(cls, v):
        if v and not v.startswith("http") and not v.startswith("data:image"):
            raise ValueError("Must be a valid URL or data URI.")
        return v

    @validator("instagram")
    def clean_instagram(cls, v):
        if v:
            return v.lstrip("@").strip()
        return v


class JobCreate(BaseModel):
    title:          str       = Field(..., min_length=2, max_length=120)
    company:        str       = Field(..., min_length=2, max_length=100)
    location:       str       = Field(..., min_length=2, max_length=100)
    type:           JobType   = JobType.full_time
    salary:         Optional[str] = Field(None, max_length=60)
    description:    Optional[str] = Field(None, max_length=3000)
    employer_id:    Optional[int] = None
    category:       Optional[str] = Field(None, max_length=40)
    max_applicants: Optional[int] = Field(None, ge=1, le=10000)
    deadline:       Optional[str] = Field(None)
    status:         JobStatus = JobStatus.open
    image_url:      Optional[str] = Field(None)                                   # job banner image

    @validator("title", "company", "location")
    def strip_whitespace(cls, v):
        return v.strip()

    @validator("deadline")
    def validate_deadline(cls, v):
        if v:
            import datetime
            try:
                datetime.date.fromisoformat(v)
            except ValueError:
                raise ValueError("Deadline must be YYYY-MM-DD format.")
        return v

    @validator("image_url")
    def validate_image_url(cls, v):
        if v and not v.startswith("http") and not v.startswith("data:image"):
            raise ValueError("image_url must be a valid URL or data URI.")
        return v


class JobUpdate(BaseModel):
    title:          Optional[str]       = Field(None, min_length=2, max_length=120)
    location:       Optional[str]       = Field(None, min_length=2, max_length=100)
    type:           Optional[JobType]   = None
    salary:         Optional[str]       = Field(None, max_length=60)
    description:    Optional[str]       = Field(None, max_length=3000)
    category:       Optional[str]       = Field(None, max_length=40)
    max_applicants: Optional[int]       = Field(None, ge=1, le=10000)
    deadline:       Optional[str]       = None
    status:         Optional[JobStatus] = None
    image_url:      Optional[str]       = Field(None)                                   # job banner image


class ApplicationCreate(BaseModel):
    job_id:       int  = Field(..., ge=1)
    user_id:      int  = Field(..., ge=1)
    name:         str  = Field(..., min_length=2, max_length=80)
    email:        EmailStr
    cover_letter: Optional[str] = Field(None, max_length=2000)
    resume_url:   Optional[str] = Field(None, max_length=500)

    @validator("resume_url")
    def validate_resume(cls, v):
        if v and not v.startswith("http"):
            raise ValueError("Resume URL must start with http.")
        return v

    @validator("name")
    def strip_name(cls, v):
        return v.strip()


class ApplicationStatusUpdate(BaseModel):
    status: AppStatus

class ApplicationNotesUpdate(BaseModel):
    notes: Optional[str] = Field(None, max_length=1000)