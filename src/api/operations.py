from fastapi import APIRouter, HTTPException
from typing import List
from database.duckdb_manager import DuckDBManager
from database.schema import Project, Portfolio
from uuid import UUID

router = APIRouter()
db = DuckDBManager()

@router.post("/projects", response_model=dict)
async def create_project(project: Project):
    try:
        project_id = db.create_project(project.dict())
        return {"project_id": project_id, "message": "Project created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/portfolios", response_model=dict)
async def create_portfolio(portfolio: Portfolio):
    try:
        portfolio_id = db.create_portfolio(portfolio.dict())
        return {"portfolio_id": portfolio_id, "message": "Portfolio created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/portfolios/{portfolio_id}/projects/{project_id}")
async def add_project_to_portfolio(portfolio_id: UUID, project_id: UUID, allocation: float):
    try:
        db.add_project_to_portfolio(str(portfolio_id), str(project_id), allocation)
        return {"message": "Project added to portfolio successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 