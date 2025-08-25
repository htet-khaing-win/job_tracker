# schemas.py
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum

class ApplicationStatus(str, Enum):
    APPLIED = "applied"
    UNDER_REVIEW = "under_review"
    INTERVIEW_SCHEDULED = "interview_scheduled"
    INTERVIEWED = "interviewed"
    REJECTED = "rejected"
    OFFERED = "offered"
    ACCEPTED = "accepted"
    WITHDRAWN = "withdrawn"

class EmailType(str, Enum):
    APPLICATION_CONFIRMATION = "application_confirmation"
    RECRUITER_RESPONSE = "recruiter_response"
    INTERVIEW_INVITE = "interview_invite"
    REJECTION = "rejection"
    OFFER = "offer"
    FOLLOW_UP = "follow_up"
    OTHER = "other"

class JobPlatform(str, Enum):
    LINKEDIN = "linkedin"
    JOBSTREET = "jobstreet"
    INDEED = "indeed"
    COMPANY_WEBSITE = "company_website"
    GLASSDOOR = "glassdoor"
    OTHER = "other"

# Company
class CompanyBase(BaseModel):
    name: str
    domain: Optional[str] = None
    industry: Optional[str] = None
    size: Optional[str] = None
    location: Optional[str] = None
    notes: Optional[str] = None

class CompanyCreate(CompanyBase):
    pass

class Company(CompanyBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# Job Application
class JobApplicationBase(BaseModel):
    position_title: str
    job_description: Optional[str] = None
    job_url: Optional[str] = None
    platform: JobPlatform
    applied_date: datetime
    salary_range: Optional[str] = None
    location: Optional[str] = None
    remote_option: bool = False
    notes: Optional[str] = None

class JobApplicationCreate(JobApplicationBase):
    company_name: str

class JobApplicationUpdate(BaseModel):
    status: Optional[ApplicationStatus] = None
    notes: Optional[str] = None
    salary_range: Optional[str] = None

class JobApplication(JobApplicationBase):
    id: int
    company_id: int
    status: ApplicationStatus
    last_updated: datetime
    application_email_id: Optional[str] = None
    notion_page_id: Optional[str] = None
    company: Company

    class Config:
        orm_mode = True

# Email Log
class EmailLogBase(BaseModel):
    sender_email: EmailStr
    sender_name: Optional[str] = None
    subject: str
    received_date: datetime
    email_type: EmailType
    confidence_score: Optional[float] = None

class EmailLogCreate(EmailLogBase):
    gmail_message_id: str
    body_text: Optional[str] = None
    body_html: Optional[str] = None

class EmailLog(EmailLogBase):
    id: int
    gmail_message_id: str
    job_application_id: Optional[int] = None
    processed: bool
    processing_notes: Optional[str] = None
    created_at: datetime

    class Config:
        orm_mode = True

# Interview
class InterviewBase(BaseModel):
    interview_type: Optional[str] = None
    scheduled_date: datetime
    duration_minutes: int = 60
    location: Optional[str] = None
    meeting_link: Optional[str] = None
    interviewer_names: Optional[str] = None
    notes: Optional[str] = None

class InterviewCreate(InterviewBase):
    job_application_id: int

class InterviewUpdate(BaseModel):
    status: Optional[str] = None
    feedback_notes: Optional[str] = None
    completed_date: Optional[datetime] = None

class Interview(InterviewBase):
    id: int
    job_application_id: int
    status: str
    google_calendar_event_id: Optional[str] = None
    reminder_sent: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

#-----schema for updating company

class CompanyUpdate(BaseModel):
    
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    industry: Optional[str] = Field(None, max_length=100)
    website: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None
    location: Optional[str] = Field(None, max_length=200)
    size: Optional[str] = Field(None, max_length=50)
