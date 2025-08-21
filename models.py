from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, Enum, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

class ApplicationStatus(enum.Enum):
    APPLIED = "applied"
    UNDER_REVIEW = "under_review"
    INTERVIEW_SCHEDULED = "interview_scheduled"
    INTERVIEWED = "interviewed"
    REJECTED = "rejected"
    OFFERED = "offered"
    ACCEPTED = "accepted"
    WITHDRAWN = "withdrwan"

class EmailType(enum.Enum):
    APPLICATION_CONFIRMATION = "application_confirmation"
    RECRUITER_RESPONSE = "recuriter_response"
    INTERVIEW_INVITE = "interview_invite"
    REJECTION = "rejection"
    OFFER = "offer"
    FOLLOW_UP = "follow_up"
    OTHER = "other"

class JobPlatform(enum.Enum):
    LINKEDIN = "linkedin"
    JOBSTREET = "Jobstreet"
    INDEED = "indeed"
    COMPANY_WEBSITE = "company_website"
    INTERNSG = "internsg"
    OTHER = "other"

class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key= True, Index = True)
    name = Column(String, unique = True, index= True, nullable= False)
    domain = Column(String)
    industry = Column(String)
    size = Column(String)
    location = Column(String)
    notes = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default= datetime.utcnow, onupdate= datetime.utcnow)

    #Relationships
    job_applications = relationship("JobApplication", back_populates= "company")
    recruiter_contacts = relationship("RecruiterContact", back_populates= "company")

class JobApplication(Base):
    __tablename__ = "job_applications"

    id = Column(Integer, primary_key= True, index= True)
    company_id = Column(Integer, ForeignKey="companies.id", nullable= False)
    position_title = Column(String, nullable= False)
    job_description = Column(Text)
    job_url = Column(String)
    platform = Column(Enum(JobPlatform), nullable= False)
    status = Column(Enum(ApplicationStatus), default=ApplicationStatus.APPLIED)
    applied_date = Column(DateTime, nullable= False)
    last_updated = Column(DateTime, default= datetime.utcnowm, onupdate=datetime.utcnow)
    salary_range = Column(String)
    location = Column(String)
    remote_option = Column(Boolean, default= False)
    notes = Column(Text)

    #Tracking fields    
    application_email_id = Column(String) # Gmail message ID for confirmation email
    notion_page_id= Column(String)  # Notion database entry ID

    #Relationships
    company = relationship("Company", back_populates= "job_applications")
    email_logs = relationship("EmailLog", back_populates= "job_applications")
    interviews = relationship("Interview", back_populates= "job_applications")

class RecruiterContact(Base):
    __table__ = "recruiter_contacts"

    id = Column(Integer, primary_key= True, index = True)
    company_id = Column(Integer, ForeignKey= "companies.id", nullable= False)
    name = Column(String)
    email = Column(String)
    phone = Column(String)
    position = Column(String)
    linkedin_url = Column(String)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    #Relationships
    company = relationship("Company", back_populates= "recruiter_contacts")
    email_logs = relationship("EmailLog", back_populates= "recruiter_contacts")

class Emaillog(Base):
    __tablename__ = "email_logs"

    id = Column(Integer, primary_key=True, index=True)
    gmail_message_id = Column(String, unique=True, nullable=False)
    job_application_id = Column(Integer, ForeignKey("job_applications.id"))
    recruiter_contact_id = Column(Integer, ForeignKey("recruiter_contacts.id"))
    
    sender_email = Column(String, nullable=False)
    sender_name = Column(String)
    subject = Column(String, nullable=False)
    body_text = Column(Text)
    body_html = Column(Text)
    received_date = Column(DateTime, nullable=False)
    
    email_type = Column(Enum(EmailType), nullable=False)
    confidence_score = Column(Float)  # ML classification confidence (0-1)
    processed = Column(Boolean, default=False)
    processing_notes = Column(Text)  # Any issues during parsing
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    job_application = relationship("JobApplication", back_populates="email_logs")
    recruiter_contact = relationship("RecruiterContact", back_populates="email_logs")

class Interview(Base):
    __tablename__ = "interviews"
    
    id = Column(Integer, primary_key=True, index=True)
    job_application_id = Column(Integer, ForeignKey("job_applications.id"), nullable=False)
    
    interview_type = Column(String)  
    scheduled_date = Column(DateTime, nullable=False)
    duration_minutes = Column(Integer, default=60)
    location = Column(String)  
    meeting_link = Column(String)
    interviewer_names = Column(String)  # Comma-separated
    notes = Column(Text)
    
    # Status tracking
    status = Column(String, default="scheduled")  # "scheduled", "completed", "cancelled", "rescheduled"
    completed_date = Column(DateTime)
    feedback_notes = Column(Text)
    
    # Calendar integration
    google_calendar_event_id = Column(String)
    reminder_sent = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    job_application = relationship("JobApplication", back_populates="interviews")

class ApplicationMetrics(Base):
    __tablename__ = "application_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, nullable=False)  # Daily aggregation
    
    # Daily counts
    applications_sent = Column(Integer, default=0)
    responses_received = Column(Integer, default=0)
    interviews_scheduled = Column(Integer, default=0)
    rejections_received = Column(Integer, default=0)
    offers_received = Column(Integer, default=0)
    
    # Platform breakdown (JSON or separate table)
    linkedin_applications = Column(Integer, default=0)
    jobstreet_applications = Column(Integer, default=0)
    indeed_applications = Column(Integer, default=0)
    other_applications = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)

# For caching API responses and rate limiting
class APILog(Base):
    __tablename__ = "api_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    api_name = Column(String, nullable=False)  # "gmail", "calendar", "notion"
    endpoint = Column(String)
    request_count = Column(Integer, default=1)
    last_request = Column(DateTime, default=datetime.utcnow)
    rate_limit_reset = Column(DateTime)
    error_count = Column(Integer, default=0)
    last_error = Column(Text)