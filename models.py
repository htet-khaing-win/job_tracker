# models.py
from datetime import datetime
import enum

from sqlalchemy import (
    Column, Integer, String, DateTime, Text, Boolean, ForeignKey,
    Enum as SQLEnum, Float
)
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

# Python enums (single source of truth)
class ApplicationStatus(enum.Enum):
    APPLIED = "applied"
    UNDER_REVIEW = "under_review"
    INTERVIEW_SCHEDULED = "interview_scheduled"
    INTERVIEWED = "interviewed"
    REJECTED = "rejected"
    OFFERED = "offered"
    ACCEPTED = "accepted"
    WITHDRAWN = "withdrawn"

class EmailType(enum.Enum):
    APPLICATION_CONFIRMATION = "application_confirmation"
    RECRUITER_RESPONSE = "recruiter_response"
    INTERVIEW_INVITE = "interview_invite"
    REJECTION = "rejection"
    OFFER = "offer"
    FOLLOW_UP = "follow_up"
    OTHER = "other"

class JobPlatform(enum.Enum):
    LINKEDIN = "linkedin"
    JOBSTREET = "jobstreet"
    INDEED = "indeed"
    COMPANY_WEBSITE = "company_website"
    INTERNSG = "internsg"
    OTHER = "other"

# Models
class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    domain = Column(String, nullable=True)
    industry = Column(String, nullable=True)
    size = Column(String, nullable=True)
    location = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    job_applications = relationship("JobApplication", back_populates="company", cascade="all, delete-orphan")
    recruiter_contacts = relationship("RecruiterContact", back_populates="company", cascade="all, delete-orphan")


class JobApplication(Base):
    __tablename__ = "job_applications"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    position_title = Column(String, nullable=False)
    job_description = Column(Text, nullable=True)
    job_url = Column(String, nullable=True)
    platform = Column(SQLEnum(JobPlatform), nullable=False)
    status = Column(SQLEnum(ApplicationStatus), default=ApplicationStatus.APPLIED, nullable=False)
    applied_date = Column(DateTime, nullable=False)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    salary_range = Column(String, nullable=True)
    location = Column(String, nullable=True)
    remote_option = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)

    application_email_id = Column(String, nullable=True)
    notion_page_id = Column(String, nullable=True)

    # Relationships
    company = relationship("Company", back_populates="job_applications")
    email_logs = relationship("EmailLog", back_populates="job_application", cascade="all, delete-orphan")
    interviews = relationship("Interview", back_populates="job_application", cascade="all, delete-orphan")


class RecruiterContact(Base):
    __tablename__ = "recruiter_contacts"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    position = Column(String, nullable=True)
    linkedin_url = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    company = relationship("Company", back_populates="recruiter_contacts")
    email_logs = relationship("EmailLog", back_populates="recruiter_contact", cascade="all, delete-orphan")


class EmailLog(Base):
    __tablename__ = "email_logs"

    id = Column(Integer, primary_key=True, index=True)
    gmail_message_id = Column(String, unique=True, nullable=False)
    job_application_id = Column(Integer, ForeignKey("job_applications.id"), nullable=True)
    recruiter_contact_id = Column(Integer, ForeignKey("recruiter_contacts.id"), nullable=True)

    sender_email = Column(String, nullable=False)
    sender_name = Column(String, nullable=True)
    subject = Column(String, nullable=False)
    body_text = Column(Text, nullable=True)
    body_html = Column(Text, nullable=True)
    received_date = Column(DateTime, nullable=False)

    email_type = Column(SQLEnum(EmailType), nullable=False)
    confidence_score = Column(Float, nullable=True)
    processed = Column(Boolean, default=False)
    processing_notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    job_application = relationship("JobApplication", back_populates="email_logs")
    recruiter_contact = relationship("RecruiterContact", back_populates="email_logs")


class Interview(Base):
    __tablename__ = "interviews"

    id = Column(Integer, primary_key=True, index=True)
    job_application_id = Column(Integer, ForeignKey("job_applications.id"), nullable=False)

    interview_type = Column(String, nullable=True)
    scheduled_date = Column(DateTime, nullable=False)
    duration_minutes = Column(Integer, default=60)
    location = Column(String, nullable=True)
    meeting_link = Column(String, nullable=True)
    interviewer_names = Column(String, nullable=True)
    notes = Column(Text, nullable=True)

    status = Column(String, default="scheduled")
    completed_date = Column(DateTime, nullable=True)
    feedback_notes = Column(Text, nullable=True)

    google_calendar_event_id = Column(String, nullable=True)
    reminder_sent = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    job_application = relationship("JobApplication", back_populates="interviews")


class ApplicationMetrics(Base):
    __tablename__ = "application_metrics"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, nullable=False)

    applications_sent = Column(Integer, default=0)
    responses_received = Column(Integer, default=0)
    interviews_scheduled = Column(Integer, default=0)
    rejections_received = Column(Integer, default=0)
    offers_received = Column(Integer, default=0)

    linkedin_applications = Column(Integer, default=0)
    jobstreet_applications = Column(Integer, default=0)
    indeed_applications = Column(Integer, default=0)
    other_applications = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)


class APILog(Base):
    __tablename__ = "api_logs"

    id = Column(Integer, primary_key=True, index=True)
    api_name = Column(String, nullable=False)
    endpoint = Column(String, nullable=True)
    request_count = Column(Integer, default=1)
    last_request = Column(DateTime, default=datetime.utcnow)
    rate_limit_reset = Column(DateTime, nullable=True)
    error_count = Column(Integer, default=0)
    last_error = Column(Text, nullable=True)
