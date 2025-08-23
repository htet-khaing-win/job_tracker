from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
import uvicorn

from database import get_db, create_tables
from routers import applications, companies, analytics, gmail_sync, notion_sync


#Create tables on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    #startup
    await create_tables()
    yield
    #shutdown

app = FastAPI(
    title = "Job Application Tracker",
    description ="Automated job application tracking and analytics",
    version = "1.0.0",
    lifespan = lifespan
)

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(applications.router, prefix="/api/v1/applications", tags=["applications"])
app.include_router(companies.router, prefix="/api/v1/companies", tags=["companies"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])
app.include_router(gmail_sync.router, prefix="/api/v1/gmail", tags=["gmail"])
app.include_router(notion_sync.router, prefix="/api/v1/notion", tags=["notion"])

@app.get("/")
async def root():
    return {"message": "Job Application Tracker API", "version": "1.0.0"}

@app.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    return {"status": "healthy", "database": "connected"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )