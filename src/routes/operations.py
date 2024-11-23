from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from pydantic import BaseModel
import duckdb
import uuid
from datetime import datetime
import logging

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
        # Connect to the DuckDB database
        conn = duckdb.connect('data_product.db')
        
        # Generate a unique project ID
        project_id = str(uuid.uuid4())
        
        # Insert the new project into the projects table
        conn.execute("""
            INSERT INTO projects (project_id, project_name, total_amount, maturity_years, expected_tri, dscr, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (project_id, project.project_name, project.total_amount, project.maturity_years, project.expected_tri, project.dscr, datetime.now(), datetime.now()))
        
        return {"message": "Project created successfully", "project_id": project_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/projects", response_model=List[Dict[str, Any]])
async def list_projects():
    """List all projects"""
    try:
        # Connect to the DuckDB database
        conn = duckdb.connect('data_product.db')
        
        # Execute the query to list projects
        result = conn.execute("SELECT * FROM projects").fetchall()
        
        # Convert the result to a list of dictionaries
        projects = [dict(row) for row in result]
        
        return projects
    except Exception as e:
        # Log the error for debugging purposes
        logger.error(f"Error listing projects: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/initialize")
async def initialize_database():
    """Initialize the database with necessary tables"""
    try:
        conn = duckdb.connect('data_product.db')
        conn.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                project_id UUID PRIMARY KEY,
                project_name VARCHAR,
                total_amount DOUBLE,
                maturity_years INTEGER,
                expected_tri DOUBLE,
                dscr DOUBLE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        return {"message": "Database initialized successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 