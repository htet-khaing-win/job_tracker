from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from database import get_db
from models import Company
from schemas import Company as CompanySchema, CompanyCreate, CompanyUpdate

router = APIRouter(prefix="/companies", tags=["companies"])


@router.get("/", response_model=List[CompanySchema])
async def get_companies(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    name: Optional[str] = Query(None, description="Filter by company name (partial match)"),
    db: AsyncSession = Depends(get_db)
):
    #Get paginated list of companies with optional name filtering.
    query = select(Company)
    
    # Apply name filter if provided
    if name:
        query = query.where(Company.name.ilike(f"%{name}%"))
    
    # Apply pagination
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    companies = result.scalars().all()
    
    return companies


@router.get("/{company_id}", response_model=CompanySchema)
async def get_company(
    company_id: int,
    db: AsyncSession = Depends(get_db)
):
    #Get a single company by ID.
    result = await db.execute(select(Company).where(Company.id == company_id))
    company = result.scalar_one_or_none()
    
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    return company


@router.post("/", response_model=CompanySchema, status_code=201)
async def create_company(
    company_data: CompanyCreate,
    db: AsyncSession = Depends(get_db)
):
    #Create a new company.
    try:
        # Check if company with same name already exists
        result = await db.execute(select(Company).where(Company.name == company_data.name))
        existing_company = result.scalar_one_or_none()
        
        if existing_company:
            raise HTTPException(status_code=409, detail="Company with this name already exists")
        
        # Create new company
        company = Company(**company_data.model_dump())
        db.add(company)
        await db.commit()
        await db.refresh(company)
        
        return company
        
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Company with this name already exists")


@router.put("/{company_id}", response_model=CompanySchema)
async def update_company(
    company_id: int,
    company_data: CompanyUpdate,
    db: AsyncSession = Depends(get_db)
):
    #Update a company
    
    result = await db.execute(select(Company).where(Company.id == company_id))
    company = result.scalar_one_or_none()
    
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    try:
        # Check if updating name would create duplicate
        if company_data.name and company_data.name != company.name:
            result = await db.execute(select(Company).where(Company.name == company_data.name))
            existing_company = result.scalar_one_or_none()
            
            if existing_company:
                raise HTTPException(status_code=409, detail="Company with this name already exists")
        
        # Update fields (only update non-None values for partial updates)
        update_data = company_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(company, field, value)
        
        await db.commit()
        await db.refresh(company)
        
        return company
        
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Company with this name already exists")


@router.delete("/{company_id}", status_code=204)
async def delete_company(
    company_id: int,
    db: AsyncSession = Depends(get_db)
):
    #Delete a company (actual delete for now).
    result = await db.execute(select(Company).where(Company.id == company_id))
    company = result.scalar_one_or_none()
    
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    await db.delete(company)
    await db.commit()
    
    # Return 204 No Content (no response body)