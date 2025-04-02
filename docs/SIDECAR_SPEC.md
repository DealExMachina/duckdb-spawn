# Technical Specification: Agentic Sidecar for DuckDB Spawn

## Overview

This document provides technical specifications for implementing the agentic sidecar component that will transform the DuckDB Spawn data product into an autonomous entity within our data mesh ecosystem. The sidecar leverages Apple's MLX framework for efficient model inference and implements the Multi-agent Cooperation Protocol (MCP) for coordination with other data products.

## System Requirements

### Hardware Requirements

| Component | Development | Production |
|-----------|-------------|------------|
| CPU | Apple Silicon (M1/M2/M3) | x86_64 (8+ cores) |
| Memory | 8GB minimum | 16GB recommended |
| Storage | 5GB for model artifacts | 10GB for model and knowledge base |
| Network | 100Mbps | 1Gbps |

### Software Requirements

| Component | Version | Purpose |
|-----------|---------|---------|
| Python | 3.10+ | Core runtime |
| MLX | 0.5.0+ | ML acceleration framework |
| FastAPI | 0.100.0+ | API framework |
| Docker | 24.0.0+ | Containerization |
| Kubernetes | 1.27+ | Orchestration |
| Redis | 7.0+ | Cache and message broker |
| DuckDB | 0.9.0+ | Data storage |

## Architecture Components

### 1. MLX-Powered Inference Engine

#### Model Specifications

```python
{
  "model_type": "mistral-7b-instruct",
  "quantization": "int8",
  "max_seq_length": 2048,
  "vocab_size": 32000,
  "hidden_size": 4096,
  "intermediate_size": 14336,
  "num_hidden_layers": 32,
  "num_attention_heads": 32,
  "num_key_value_heads": 8,
  "fine_tuned": true,
  "domain_specific_tokens": 250,
  "size_on_disk_mb": 3800,
  "inference_memory_mb": 1500
}
```

#### Model Distillation Pipeline

The full-size model will be distilled to a smaller, more efficient model using the following process:

1. **Teacher Model**: mistral-7b-instruct (fine-tuned on data operations)
2. **Student Model**: <1B parameter model with MLX optimization
3. **Distillation Dataset**: 
   - 50,000 schema operations examples
   - 25,000 query optimization examples
   - 10,000 agent coordination examples
4. **Distillation Method**: Knowledge distillation with temperature scaling
5. **Evaluation Metrics**: 
   - Accuracy on schema tasks
   - ROUGE/BLEU for generation quality
   - Latency and memory footprint

#### Inference Optimization

1. **MLX Acceleration**: Utilizing MLX for Apple Silicon optimization
2. **Quantization**: INT8 quantization for reduced memory footprint
3. **Caching**: Response caching for common operations
4. **Batching**: Request batching for improved throughput

### 2. Agent Interface

#### REST API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/agent/health` | GET | Health check for the agent |
| `/agent/analyze` | POST | Analyze and suggest improvements |
| `/agent/execute` | POST | Execute approved operations |
| `/agent/message` | POST | Receive MCP messages |
| `/agent/capabilities` | GET | List agent capabilities |

#### API Authentication

1. **JWT Authentication**: For secure communication between data product and agent
2. **API Key**: For external services communication
3. **Role-Based Authorization**: Different access levels for different operations

#### Example Request/Response

```json
// Request to /agent/analyze
{
  "operation_type": "schema_optimization",
  "context": {
    "table_name": "projects",
    "query_patterns": [
      {"query": "SELECT * FROM projects WHERE status = ?", "frequency": 120},
      {"query": "SELECT * FROM projects WHERE creation_date > ?", "frequency": 45}
    ],
    "current_schema": [
      {"name": "project_id", "type": "UUID", "indexed": true},
      {"name": "project_name", "type": "VARCHAR", "indexed": false},
      {"name": "status", "type": "VARCHAR", "indexed": false},
      {"name": "creation_date", "type": "DATE", "indexed": false}
    ]
  }
}

// Response
{
  "suggestion_id": "sugg-123456",
  "suggestions": [
    {
      "type": "add_index",
      "target": "status",
      "reason": "High frequency filtering on non-indexed column",
      "execution_sql": "CREATE INDEX idx_projects_status ON projects (status);",
      "estimated_impact": {
        "query_speedup": "80%",
        "storage_overhead": "2%"
      }
    },
    {
      "type": "add_index",
      "target": "creation_date",
      "reason": "Moderate frequency filtering on date column",
      "execution_sql": "CREATE INDEX idx_projects_creation_date ON projects (creation_date);",
      "estimated_impact": {
        "query_speedup": "60%",
        "storage_overhead": "3%"
      }
    }
  ],
  "confidence": 0.92,
  "requires_approval": true
}
```

### 3. MCP Protocol Implementation

#### MCP Message Structure

```json
{
  "message_id": "msg-123456",
  "timestamp": "2023-09-15T14:30:00Z",
  "sender": {
    "agent_id": "agent-duckdb-spawn-1",
    "product_id": "duckdb-spawn",
    "domain": "financing"
  },
  "recipient": {
    "agent_id": "agent-risk-assessment-1",
    "product_id": "risk-assessment",
    "domain": "risk"
  },
  "message_type": "schema_proposal",
  "content": {
    "operation": "add_column",
    "details": {
      "table": "projects",
      "column_name": "risk_assessment_id",
      "column_type": "UUID",
      "required": false,
      "description": "Foreign key to Risk Assessment domain",
      "purpose": "Enable cross-domain data joins"
    }
  },
  "requires_response": true,
  "priority": "normal",
  "ttl_seconds": 3600
}
```

#### Protocol Handlers

1. **Message Serialization/Deserialization**: Converting between JSON and internal representations
2. **Message Routing**: Determining the appropriate recipient for each message
3. **Response Handling**: Processing and correlating responses to requests
4. **Error Handling**: Managing timeouts, retries, and failed deliveries
5. **Message Prioritization**: Handling urgent vs. normal priority messages

#### Cross-Domain Discovery

1. **Agent Registry Service**: Central registry for discovery of available agents
2. **Capability Advertisement**: Regular updates of agent capabilities to the registry
3. **Domain Directory**: Mapping of domains to responsible data products and agents

#### Sequence Diagram: Cross-Domain Schema Update

```
┌─────────┐          ┌────────────┐          ┌─────────────┐          ┌────────────┐
│ Finance │          │ Finance    │          │ Risk        │          │ Risk       │
│ Product │          │ Agent      │          │ Agent       │          │ Product    │
└────┬────┘          └─────┬──────┘          └──────┬──────┘          └──────┬─────┘
     │                      │                        │                        │
     │ Schema Change Need   │                        │                        │
     │───────────────────>  │                        │                        │
     │                      │                        │                        │
     │                      │ Analyze Impact         │                        │
     │                      │────────────┐           │                        │
     │                      │            │           │                        │
     │                      │ <──────────┘           │                        │
     │                      │                        │                        │
     │                      │ Schema Proposal Message│                        │
     │                      │───────────────────────>│                        │
     │                      │                        │                        │
     │                      │                        │ Evaluate Proposal      │
     │                      │                        │────────────────────>   │
     │                      │                        │                        │
     │                      │                        │ <───────────────────   │
     │                      │                        │                        │
     │                      │ Acceptance Message     │                        │
     │                      │ <──────────────────────│                        │
     │                      │                        │                        │
     │ Execute Schema Change│                        │                        │
     │ <──────────────────  │                        │                        │
     │                      │                        │                        │
     │ Confirmation         │                        │                        │
     │───────────────────>  │                        │                        │
     │                      │                        │                        │
     │                      │ Completion Notification│                        │
     │                      │───────────────────────>│                        │
     │                      │                        │                        │
     │                      │                        │ Update Related Schema  │
     │                      │                        │────────────────────>   │
     │                      │                        │                        │
     │                      │                        │ <───────────────────   │
     │                      │                        │                        │
     │                      │ Sync Complete Message  │                        │
     │                      │ <──────────────────────│                        │
     │                      │                        │                        │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4. Knowledge Store

#### Schema

```sql
CREATE TABLE agent_decisions (
    decision_id UUID PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    operation_type VARCHAR NOT NULL,
    context JSON NOT NULL,
    suggestion JSON NOT NULL,
    approved BOOLEAN,
    executed BOOLEAN,
    outcome JSON,
    feedback_score FLOAT
);

CREATE TABLE observed_patterns (
    pattern_id UUID PRIMARY KEY,
    pattern_type VARCHAR NOT NULL,
    pattern_data JSON NOT NULL,
    first_observed TIMESTAMP NOT NULL,
    last_observed TIMESTAMP NOT NULL,
    occurrence_count INTEGER NOT NULL,
    confidence FLOAT NOT NULL
);

CREATE TABLE agent_messages (
    message_id UUID PRIMARY KEY,
    sender_id VARCHAR NOT NULL,
    recipient_id VARCHAR NOT NULL,
    message_type VARCHAR NOT NULL,
    content JSON NOT NULL,
    sent_timestamp TIMESTAMP NOT NULL,
    delivery_status VARCHAR NOT NULL,
    response_id UUID
);
```

#### Storage Backend Options

1. **Primary**: SQLite for lightweight deployment
2. **Alternative**: DuckDB for analytical capabilities
3. **Distributed**: PostgreSQL for multi-node deployment

#### Knowledge Persistence

1. **Periodic Snapshots**: Full database dump at regular intervals
2. **Transaction Log**: Continuous logging of all operations
3. **Backup Strategy**: Encrypted backups to secure storage

### 5. Human-in-the-Loop Interface

#### Approval Workflow

1. **Notification System**: Email/Slack notifications for pending approvals
2. **Web Dashboard**: UI for reviewing and approving agent suggestions
3. **CLI Interface**: Command-line tools for administrators

#### Explanation Generation

1. **Decision Factors**: List of factors that influenced the decision
2. **Alternative Options**: Other considered options and why they were rejected
3. **Expected Impact**: Quantitative metrics for expected improvements
4. **Risk Assessment**: Potential downsides or risks

#### Feedback Loop

1. **Action Outcome Tracking**: Measuring actual vs. expected outcomes
2. **User Feedback Collection**: Collecting explicit feedback on suggestions
3. **Model Refinement**: Using feedback to improve future suggestions

## Implementation Plan

### Phase 1: MLX Integration (January 15 - February 15, 2025) ✅ COMPLETED

1. ✅ Set up MLX development environment
2. ✅ Implement distillation pipeline for domain-specific model
3. ✅ Create basic inference API
4. ✅ Benchmark performance and optimize

### Phase 2: Agent Interface (February 15 - March 15, 2025) ✅ COMPLETED

1. ✅ Design and implement REST API
2. ✅ Create schema analysis capability
3. ✅ Implement secure authentication
4. ✅ Develop suggestion generation logic

### Phase 3: Knowledge Store (March 1 - March 31, 2025) ✅ COMPLETED

1. ✅ Implement database schema
2. ✅ Create persistence mechanisms
3. ✅ Develop pattern recognition capabilities
4. ✅ Set up backup procedures

### Phase 4: MCP Implementation (April 1 - May 15, 2025) 🔄 IN PROGRESS

1. ✅ Design MCP message formats for data operations
2. 🔄 Implement message handling logic (60% complete)
3. 🔄 Create agent discovery mechanism (40% complete)
4. ⏳ Test cross-agent communication

### Phase 5: Human Interface (May 1 - June 15, 2025) 🔄 STARTED

1. ✅ Develop approval workflows
2. 🔄 Create explanation generation (20% complete)
3. ⏳ Implement feedback collection
4. ⏳ Design administrative dashboard

### Phase 6: Testing & Integration (June 15 - August 31, 2025) ⏳ PLANNED

1. ⏳ Unit testing all components
2. ⏳ Integration testing with DuckDB Spawn
3. ⏳ Performance testing under load
4. ⏳ Security assessment

## Current Implementation Status (April 2025)

As of April 2025, we have completed Phases 1-3 and are actively working on Phase 4, with initial work beginning on Phase 5:

### Completed Components

1. **MLX Inference Engine**: 
   - Successfully distilled MLX-MistralFineTuned to 700M parameters
   - Achieved 85ms average inference time for schema operations
   - Implemented INT8 quantization reducing memory footprint to 1.2GB
   - Containerized deployment with optimized resource utilization

2. **Agent Interface**:
   - RESTful API with all planned endpoints implemented
   - JWT authentication and role-based access control
   - Schema analysis capability with promising initial results
   - Query pattern detection framework implemented

3. **Knowledge Store**:
   - Implemented DuckDB-backed persistence layer
   - Transaction logging and encrypted backups
   - Pattern recognition framework for query optimization
   - Historical decision tracking

### In Progress

1. **MCP Implementation**:
   - Message format design completed
   - Basic message passing implementation (60% complete)
   - Agent discovery mechanism in development (40% complete)
   - Cross-agent communication protocols in design phase

2. **Human Interface**:
   - Approval workflows completed and deployed
   - Explanation generation in early development (20% complete)
   - Feedback collection and dashboard design in planning phase

### Performance Metrics (Preliminary)

Initial performance testing of completed components shows promising results:

- **Latency**: 85ms average inference time (p95: 120ms)
- **Resource Utilization**: 1.2GB memory, 0.5 CPU average
- **Accuracy**: Early testing shows ~80% of suggestions appear viable (human validation pending)
- **Overhead**: Currently adds 3.8% additional load on data product (target: <5%)

### Next Steps (April-May 2025)

The primary focus for the next 6 weeks is to:

1. Complete the MCP Implementation phase
   - Finish message handling logic implementation
   - Complete the agent discovery mechanism
   - Begin testing cross-agent communication

2. Make progress on the Human Interface phase
   - Advance explanation generation capabilities
   - Begin implementing feedback collection mechanism
   - Create initial designs for the administrative dashboard

3. Prepare for the Testing & Integration phase
   - Develop test plans and automation
   - Create integration test environment
   - Define performance benchmarks

## Deployment Timeline

| Milestone | Target Date | Description |
|-----------|-------------|-------------|
| Alpha Release | June 2025 | Internal testing with limited users |
| Beta Release | August 2025 | Expanded testing with selected partners |
| Integration with v2.0.0 | November 2025 | First production-ready features |
| Full Deployment | Q1 2026 | Complete feature set deployment |

## Deployment Strategy

### Container Configuration

```yaml
# Docker Compose snippet for the agent sidecar
version: '3.8'
services:
  agent-sidecar:
    image: duckdb-spawn/agent-sidecar:${TAG:-latest}
    build:
      context: ./agent
      dockerfile: Dockerfile
      args:
        - MODEL_VERSION=${MODEL_VERSION:-v1}
    volumes:
      - agent-data:/app/data
    environment:
      - DATA_PRODUCT_API=http://duckdb-spawn:8000
      - MCP_REGISTRY_URL=http://mcp-registry:8080
      - LOG_LEVEL=info
      - AUTH_SECRET=${AUTH_SECRET}
    ports:
      - "9000:9000"
    depends_on:
      - duckdb-spawn
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/agent/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G

volumes:
  agent-data:
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: agent-sidecar
  namespace: data-products
spec:
  replicas: 1
  selector:
    matchLabels:
      app: agent-sidecar
  template:
    metadata:
      labels:
        app: agent-sidecar
    spec:
      containers:
      - name: agent-sidecar
        image: duckdb-spawn/agent-sidecar:latest
        resources:
          limits:
            cpu: "2"
            memory: "4Gi"
          requests:
            cpu: "1"
            memory: "2Gi"
        ports:
        - containerPort: 9000
        env:
        - name: DATA_PRODUCT_API
          value: "http://duckdb-spawn:8000"
        - name: MCP_REGISTRY_URL
          value: "http://mcp-registry:8080"
        - name: LOG_LEVEL
          value: "info"
        - name: AUTH_SECRET
          valueFrom:
            secretKeyRef:
              name: agent-secrets
              key: auth-secret
        volumeMounts:
        - name: agent-data
          mountPath: /app/data
        livenessProbe:
          httpGet:
            path: /agent/health
            port: 9000
          initialDelaySeconds: 40
          periodSeconds: 30
      volumes:
      - name: agent-data
        persistentVolumeClaim:
          claimName: agent-data-pvc
```

## Security Considerations

### Data Protection

1. **Encryption at Rest**: All persistent data encrypted
2. **Encryption in Transit**: TLS for all API communication
3. **Access Control**: Strict authentication and authorization

### Prompt Injection Protection

1. **Input Sanitization**: Remove potential injection attempts
2. **Input Classification**: Detect and reject adversarial inputs
3. **Response Validation**: Validate model outputs before execution

### Operational Security

1. **Least Privilege**: Containers run with minimal permissions
2. **Secrets Management**: Secure handling of credentials
3. **Vulnerability Scanning**: Regular container image scanning

## Monitoring and Observability

### Metrics

1. **Performance Metrics**:
   - Inference latency (p50, p95, p99)
   - Memory usage
   - CPU utilization
   - Request throughput

2. **Operational Metrics**:
   - Success/failure rates
   - Suggestion approval rate
   - Impact of implemented suggestions
   - Message delivery rates

### Logging

1. **Structured Logging**: JSON format with standardized fields
2. **Log Levels**: ERROR, WARNING, INFO, DEBUG
3. **Sensitive Data Handling**: Redaction of sensitive information

### Alerting

1. **Error Rate Thresholds**: Alert on elevated error rates
2. **Latency Thresholds**: Alert on performance degradation
3. **Resource Utilization**: Alert on memory/CPU constraints

## Conclusion

This technical specification provides a comprehensive guide for implementing the agentic sidecar component for DuckDB Spawn using MLX for model inference and MCP for multi-agent coordination. By following this specification, we aim to create an efficient, secure, and effective autonomous data product that enhances our data mesh architecture while maintaining governance and control. 