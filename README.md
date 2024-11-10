# Project Finance Data Product

A streamlined data product for managing project finance portfolios.

## Quick Start

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Run the application:

```bash
uvicorn src.main:app --reload
```

3. Access the API documentation:

- Open http://localhost:8000/docs in your browser

## Example Usage

1. Create a project:

```bash
curl -X POST http://localhost:8000/ops/projects \
  -H "Content-Type: application/json" \
  -d '{
    "project_name": "Green Energy Plant",
    "total_amount": 1000000,
    "maturity_years": 10,
    "expected_tri": 12.5,
    "dscr": 1.5,
    "status": "PROPOSED"
  }'
```

2. Create a portfolio:

```bash
curl -X POST http://localhost:8000/ops/portfolios \
  -H "Content-Type: application/json" \
  -d '{
    "portfolio_name": "Renewable Energy",
    "risk_profile": "MODERATE",
    "total_committed_amount": 5000000
  }'
```

## Project Structure

- `src/database/`: Database models and manager
- `src/api/`: API endpoints
- `src/main.py`: Application entry point
