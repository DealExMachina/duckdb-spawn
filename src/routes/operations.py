"""Operations routes for project management."""

import logging
import uuid
from datetime import datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from config.onto_server import ProjectStatus, get_project_schema_jsonld

from ..database.connection_manager import DuckDBConnectionManager

router = APIRouter(prefix="/ops", tags=["Operations"])
logger = logging.getLogger("data_product")
conn_manager = DuckDBConnectionManager()


class ProjectCreate(BaseModel):
    """Project creation model."""

    project_name: str
    total_amount: float
    maturity_years: int
    expected_tri: float
    dscr: float
    description: str | None = None
    status: ProjectStatus = ProjectStatus.PROPOSED
    currency_code: str = "USD"


@router.post("/projects")
async def create_project(project: ProjectCreate):
    """Create a new project based on the ontology schema."""
    try:
        schema = await get_project_schema_jsonld()

        with conn_manager.get_connection() as conn:
            project_id = str(uuid.uuid4())
            now = datetime.now()

            project_data = {
                "project_id": project_id,
                "project_name": project.project_name,
                "description": project.description,
                "total_amount": project.total_amount,
                "maturity_years": project.maturity_years,
                "expected_tri": project.expected_tri,
                "dscr": project.dscr,
                "status": project.status.value,
                "creation_date": now.date(),
                "last_updated": now,
                "currency_code": project.currency_code,
            }

            # Validate against schema
            for col in schema.columns:
                if col.required and col.name not in project_data:
                    raise ValueError(f"Missing required field: {col.name}")

            columns = list(project_data.keys())
            placeholders = ", ".join(["?" for _ in columns])
            query = f"""
                INSERT INTO {schema.name} ({', '.join(columns)})
                VALUES ({placeholders})
            """

            conn.execute(query, tuple(project_data.values()))

            logger.info(f"Project created successfully with ID: {project_id}")
            return {"message": "Project created successfully", "project_id": project_id}
    except ValueError as ve:
        logger.error(f"Validation error: {str(ve)}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error creating project: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/projects")
async def list_projects():
    """List all projects with schema-defined fields."""
    try:
        schema = await get_project_schema_jsonld()
        column_names = [col.name for col in schema.columns]

        with conn_manager.get_connection() as conn:
            result = conn.execute(
                f"""
                SELECT {', '.join(column_names)}
                FROM {schema.name}
                ORDER BY creation_date DESC
            """
            ).fetchall()

            projects = [dict(zip(column_names, row)) for row in result]
            logger.info(f"Retrieved {len(projects)} projects")
            return projects
    except Exception as e:
        logger.error(f"Error listing projects: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/projects/{project_id}")
async def get_project(project_id: str):
    """Get a specific project by ID."""
    try:
        schema = await get_project_schema_jsonld()
        column_names = [col.name for col in schema.columns]

        with conn_manager.get_connection() as conn:
            result = conn.execute(
                f"""
                SELECT {', '.join(column_names)}
                FROM {schema.name}
                WHERE project_id = ?
            """,
                (project_id,),
            ).fetchone()

            if not result:
                logger.warning(f"Project not found: {project_id}")
                raise HTTPException(status_code=404, detail="Project not found")

            project = dict(zip(column_names, result))
            logger.info(f"Retrieved project: {project_id}")
            return project
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving project {project_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/initialize")
async def initialize_database():
    """Initialize the database with schema from onto_server."""
    try:
        schema = await get_project_schema_jsonld()

        with conn_manager.get_connection() as conn:
            # Create columns definition
            columns_def = []
            for col in schema.columns:
                constraint = "NOT NULL" if col.required else ""
                columns_def.append(f"{col.name} {col.type} {constraint}".strip())

            # Create table query without problematic backslashes
            create_table_query = (
                f"CREATE TABLE IF NOT EXISTS {schema.name} (\n"
                + ",\n".join(columns_def)
                + "\n);"
            )

            conn.execute(create_table_query)
            logger.info(f"Database initialized successfully with schema: {schema.name}")
            return {"message": "Database initialized successfully"}
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
