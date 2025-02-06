"""Database schema definitions."""

from enum import Enum

from pydantic import BaseModel

# Core schema definitions
SCHEMA_DEFINITIONS = {
    "projects": """
        CREATE TABLE IF NOT EXISTS projects (
            project_id UUID PRIMARY KEY,
            project_name VARCHAR NOT NULL,
            description TEXT,
            total_amount DECIMAL(20,2) NOT NULL,
            maturity_years INTEGER NOT NULL,
            expected_tri DECIMAL(5,2) NOT NULL,
            dscr DECIMAL(5,2) NOT NULL,
            status VARCHAR NOT NULL,
            creation_date DATE NOT NULL,
            last_updated TIMESTAMP NOT NULL,
            currency_code CHAR(3) NOT NULL DEFAULT 'USD'
        )
    """,
    "portfolios": """
        CREATE TABLE IF NOT EXISTS portfolios (
            portfolio_id UUID PRIMARY KEY,
            portfolio_name VARCHAR NOT NULL,
            description TEXT,
            risk_profile VARCHAR NOT NULL,
            total_committed_amount DECIMAL(20,2) NOT NULL,
            inception_date DATE NOT NULL,
            last_updated TIMESTAMP NOT NULL
        )
    """,
    "portfolio_projects": """
        CREATE TABLE IF NOT EXISTS portfolio_projects (
            portfolio_id UUID REFERENCES portfolios(portfolio_id),
            project_id UUID REFERENCES projects(project_id),
            allocation_percentage DECIMAL(5,2) NOT NULL,
            entry_date DATE NOT NULL,
            PRIMARY KEY (portfolio_id, project_id)
        )
    """,
}


class ProjectStatus(str, Enum):
    """Project status enumeration."""

    PROPOSED = "PROPOSED"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"


class Project(BaseModel):
    """Project model."""

    project_name: str
    description: str | None = None
    total_amount: float
    maturity_years: int
    expected_tri: float
    dscr: float
    status: ProjectStatus
    currency_code: str = "USD"


class RiskProfile(str, Enum):
    """Risk profile enumeration."""

    CONSERVATIVE = "CONSERVATIVE"
    MODERATE = "MODERATE"
    AGGRESSIVE = "AGGRESSIVE"


class Portfolio(BaseModel):
    """Portfolio model."""

    portfolio_name: str
    description: str | None = None
    risk_profile: RiskProfile
    total_committed_amount: float
