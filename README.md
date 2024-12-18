# DuckDB Spawn API

A FastAPI service that manages project data using DuckDB with dynamic schema support from an ontology server.

## Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        Client[API Clients]
    end

    subgraph "API Layer"
        FastAPI[FastAPI Service]
        Cache[Schema Cache]
        ConnMgr[Connection Manager]
    end

    subgraph "Data Layer"
        DuckDB[(DuckDB)]
    end

    subgraph "Schema Layer"
        OntoServer[Ontology Server]
        MockServer[Mock Server]
        SchemaAdapter[Schema Adapter]
    end

    Client --> FastAPI
    FastAPI --> ConnMgr
    ConnMgr --> DuckDB
    FastAPI --> SchemaAdapter
    SchemaAdapter --> |Primary| OntoServer
    SchemaAdapter --> |Fallback| MockServer
    SchemaAdapter --> |Cache| Cache
    Cache --> FastAPI
```

## Deployment Architecture

```mermaid
graph TD
    subgraph Local Environment
        LocalDev[Local Development]
        Docker[Docker Container]
    end

    subgraph Infrastructure
        CI/CD[CI/CD Pipeline]
        Monitoring[Monitoring Tools]
    end

    subgraph Staging Environment
        KoyebStaging[Koyeb Staging]
    end

    subgraph Production Environment
        KoyebProd[Koyeb Production]
    end

    LocalDev --> Docker
    Docker --> CI/CD
    CI/CD --> KoyebStaging
    CI/CD --> KoyebProd
    KoyebStaging --> Monitoring
    KoyebProd --> Monitoring
```

## Overview

DuckDB Spawn API provides a dynamic project management system where the database schema is controlled by an external ontology server. The system includes:

- **Dynamic Schema Management**: Database tables are created and updated based on schemas from the ontology server
- **Connection Management**: Thread-safe DuckDB connections with proper transaction handling
- **Mock Support**: Built-in mock responses for development when the ontology server is unavailable
- **Health Monitoring**: System metrics and health checks including ontology server status

## Key Features

- Async API endpoints for project management
- Schema-driven database operations
- Prometheus metrics integration
- Structured JSON logging
- Health monitoring endpoints
- Mock server support for development

## Configuration

Environment variables:

```bash
# Ontology Server Configuration
ONTO_SERVER_URL=http://localhost:8001
ONTO_SERVER_TIMEOUT=5
USE_MOCK_ONTO_SERVER=true  # Use mock responses for development

# Database Configuration
DUCKDB_PATH=data_product.db
```

## API Endpoints

### Operations

- `POST /ops/projects`: Create a new project
- `GET /ops/projects`: List all projects
- `GET /ops/projects/{project_id}`: Get project details
- `POST /ops/initialize`: Initialize database with schema

### Admin

- `POST /admin/tables`: Create tables from schema
- `GET /admin/tables`: List all tables
- `PUT /admin/tables/{table_name}`: Update table schema
- `DELETE /admin/tables/{table_name}`: Delete table
- `POST /admin/logging/level`: Update logging level

### Monitoring

- `GET /monitoring/health`: System health status
- `GET /monitoring/metrics/system`: System metrics

## Development

1. Clone the repository

2. Create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # Unix
.venv\Scripts\activate     # Windows
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Run the application:

```bash
uvicorn src.main:app --reload
```

## Testing

Run tests with pytest:

```bash
pytest
```

## Project Structure

```text
duckdb-spawn/
├── config/
│   ├── __init__.py
│   ├── onto_server.py           # Schema server interface
│   └── mock_onto_responses.py   # Mock responses
├── infrastructure/
│   ├── pulumi/                  # Infrastructure as Code
│   │   ├── __main__.py         # Main Pulumi program
│   │   ├── Pulumi.yaml         # Pulumi project file
│   │   └── Pulumi.dev.yaml     # Development stack configuration
│   ├── docker/
│   │   ├── Dockerfile          # Application container
│   │   └── docker-compose.yml  # Local development setup
│   └── monitoring/
│       ├── prometheus/
│       │   └── prometheus.yml  # Prometheus configuration
│       └── grafana/
│           └── dashboards/     # Grafana dashboard definitions
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── routes/
│   │   ├── admin.py           # Admin endpoints
│   │   ├── operations.py      # Project operations
│   │   └── monitoring.py      # Health checks
│   ├── database/
│   │   ├── connection_manager.py
│   │   └── schema.py
│   └── utils/
│       ├── logging_config.py
│       └── metrics.py
├── tests/
│   └── test_routes/
├── .github/
│   └── workflows/
│       ├── ci.yml             # CI pipeline
│       └── koyeb-deploy.yml   # Deployment pipeline
└── deployment/
    ├── staging/              # Staging environment configs
    └── production/           # Production environment configs
```

## Infrastructure

### Local Development

The project includes a Docker Compose setup for local development:

```bash
# Start local development environment
docker-compose -f infrastructure/docker/docker-compose.yml up -d

# View logs
docker-compose -f infrastructure/docker/docker-compose.yml logs -f
```

### Infrastructure as Code

The project uses Pulumi for infrastructure management:

```bash
# Initialize Pulumi stack
cd infrastructure/pulumi
pulumi stack init dev

# Deploy infrastructure
pulumi up

# Destroy infrastructure
pulumi destroy
```

### Monitoring Setup

The monitoring stack includes:

- Prometheus for metrics collection
- Grafana for visualization
- Custom dashboards for DuckDB metrics

To deploy the monitoring stack:

```bash
cd infrastructure/monitoring
docker-compose up -d
```

### CI/CD Pipeline

The project uses GitHub Actions for CI/CD:

1. **Continuous Integration**:
   - Automated testing
   - Code quality checks
   - Container image building

2. **Continuous Deployment**:
   - Automated deployment to Koyeb
   - Environment-specific configurations
   - Health check verification

### Environment Management

The project supports multiple environments:

- **Development**: Local development environment
- **Staging**: Pre-production testing environment
- **Production**: Production environment

Environment-specific configurations are managed through:
- Environment variables
- Pulumi stacks
- Koyeb configurations

## Deployment

### Koyeb Deployment

1. Set up Koyeb credentials:

```bash
export KOYEB_TOKEN=your_token
```

2. Deploy using GitHub Actions:
   - Push to `main` branch for staging deployment
   - Create a release for production deployment

### Infrastructure Updates

To update the infrastructure:

1. Modify Pulumi configurations:

```bash
cd infrastructure/pulumi
# Edit __main__.py or Pulumi.dev.yaml
pulumi up
```

2. Update monitoring configurations:

```bash
cd infrastructure/monitoring
# Edit prometheus.yml or grafana dashboards
docker-compose up -d --force-recreate
```

## License

MIT License

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Contact

- Author: Jean-Baptiste Dezard
- Email: [jeanbapt@dealexmachina.com](mailto:jeanbapt@dealexmachina.com)
- Project: [GitHub Repository](https://github.com/jeanbapt/duckdb-spawn)
