"""Mock responses for the onto server until it's implemented"""

MOCK_PROJECT_SCHEMA = {
    "name": "projects",
    "description": "Project information and metrics schema",
    "columns": [
        {
            "name": "project_id",
            "type": "UUID",
            "description": "Unique identifier for the project",
            "required": True
        },
        {
            "name": "project_name",
            "type": "VARCHAR",
            "description": "Name of the project",
            "required": True
        },
        {
            "name": "description",
            "type": "TEXT",
            "description": "Project description",
            "required": False
        },
        {
            "name": "total_amount",
            "type": "DECIMAL(20,2)",
            "description": "Total project amount",
            "required": True
        },
        {
            "name": "maturity_years",
            "type": "INTEGER",
            "description": "Project maturity in years",
            "required": True
        },
        {
            "name": "expected_tri",
            "type": "DECIMAL(5,2)",
            "description": "Expected TRI",
            "required": True
        },
        {
            "name": "dscr",
            "type": "DECIMAL(5,2)",
            "description": "Debt Service Coverage Ratio",
            "required": True
        },
        {
            "name": "status",
            "type": "VARCHAR",
            "description": "Project status (PROPOSED, ACTIVE, COMPLETED)",
            "required": True
        },
        {
            "name": "creation_date",
            "type": "DATE",
            "description": "Date of creation",
            "required": True
        },
        {
            "name": "last_updated",
            "type": "TIMESTAMP",
            "description": "Last update timestamp",
            "required": True
        },
        {
            "name": "currency_code",
            "type": "CHAR(3)",
            "description": "Currency code (ISO)",
            "required": True
        }
    ]
}

MOCK_RESPONSES = {
    "project_schema": MOCK_PROJECT_SCHEMA,
    "health": {"status": "healthy", "version": "1.0.0"}
}

def get_mock_response(schema_id: str) -> dict:
    """Get a mock response for a given schema ID"""
    return MOCK_RESPONSES.get(schema_id, {
        "error": "Schema not found",
        "schema_id": schema_id
    }) 