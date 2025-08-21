from pydantic import BaseModel, EmailStr
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

# Base schemas
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
        from_attributes = True

# Job Application schemas
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
    company_name: str  # We'll find or create company

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
        from_attributes = True

# Email schemas
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
        from_attributes = True

# Interview schemas
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
        from_attributes = True

# Analytics schemas
class ApplicationStats(BaseModel):
    total_applications: int
    pending_applications: int
    interviews_scheduled: int
    offers_received: int
    rejection_rate: float
    response_rate: float
    avg_response_time_days: Optional[float] = None

class PlatformStats(BaseModel):
    platform: JobPlatform
    application_count: int
    response_count: int
    response_rate: float
    interview_count: int

class CompanyStats(BaseModel):
    company_name: str
    application_count: int
    last_application_date: datetime
    status_breakdown: dict

class DashboardData(BaseModel):
    stats: ApplicationStats
    recent_applications: List[JobApplication]
    upcoming_interviews: List[Interview]
    recent_emails: List[EmailLog]
    platform_breakdown: List[PlatformStats]
    top_companies: List[CompanyStats]

# Gmail API schemas
class GmailSyncRequest(BaseModel):
    days_back: int = 30
    force_resync: bool = False

class GmailSyncResponse(BaseModel):
    emails_processed: int
    new_applications_found: int
    new_responses_found: int
    errors: List[str]

# Notion sync schemas
class NotionSyncResponse(BaseModel):
    synced_applications: int
    created_pages: int
    updated_pages: int
    errors: List[str]