from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from pydantic import BaseModel

router = APIRouter(prefix="/ops", tags=["Operations"])

class ProjectCreate(BaseModel):
    project_name: str
    total_amount: float
    maturity_years: int
    expected_tri: float
    dscr: float

@router.post("/projects")
async def create_project(project: ProjectCreate):
    """Create a new project"""
    try:
        # TODO: Implement project creation in DuckDB
        return {"message": "Project created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 