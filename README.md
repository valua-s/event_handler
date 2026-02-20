# Event Handler Service

A high-performance, asynchronous event handling system built with FastAPI, Kafka, and PostgreSQL. This system provides both an API for event creation and a consumer worker for processing events.

## Features

- **FastAPI REST API**: Async event creation and management endpoints
- **Kafka Consumer**: Scalable event processing with 3 consumer replicas
- **PostgreSQL Database**: Persistent event storage with async queries
- **Dependency Injection**: Clean architecture using Dishka
- **Health Checks**: Built-in health monitoring endpoints
- **Database Migrations**: Alembic for schema versioning
- **Docker Support**: Docker Compose setup for local development
- **Load Testing**: Locust integration for performance testing

## Project Structure

```
event_handler/
├── app_api/              # FastAPI application
│   ├── __main__.py      # API server entry point
│   ├── config.py        # Configuration and settings
│   ├── di.py            # Dependency injection setup
│   ├── models.py        # SQLAlchemy ORM models
│   ├── routes.py        # API endpoints
│   ├── schemas.py       # Pydantic request/response schemas
│   └── services.py      # Business logic
├── consumer/            # Kafka consumer
│   ├── __main__.py      # Consumer entry point
│   ├── config.py        # Consumer configuration
│   ├── di.py            # Dependency injection setup
│   ├── models.py        # Data models
│   ├── services.py      # Consumer business logic
│   ├── schemas.py       # Message schemas
│   └── worker.py        # Kafka consumer worker
├── docker/              # Docker configurations
│   ├── api/Dockerfile
│   └── consumer/Dockerfile
├── alembic/             # Database migrations
├── docker_app.compose.yml
├── docker_infra_compose.yml
├── pyproject.toml       # Project metadata and dependencies
└── .env                 # Environment variables
```

## Requirements

- Python 3.13+
- PostgreSQL 14+
- Apache Kafka
- Docker & Docker Compose (optional)

## Installation

### Local Setup

1. **Clone the repository**
   ```bash
   git clone <repository>
   cd event_handler
   ```

2. **Install dependencies** (using uv)
   ```bash
   pip install uv
   uv sync
   ```


3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

4. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

### Docker Setup

1. **Start infrastructure** (PostgreSQL, Kafka)
   ```bash
   docker-compose -f docker_infra_compose.yml up -d
   ```

2. **Start application** (API + Consumer)
   ```bash
   docker-compose -f docker_app.compose.yml up -d
   ```

3. **View logs**
   ```bash
   docker-compose -f docker_app.compose.yml logs -f api
   docker-compose -f docker_app.compose.yml logs -f consumer
   ```

## Configuration

All configuration is managed through environment variables with the `EVENT_HANDLER_SERVICE_` prefix.

### Required Variables

- `POSTGRES_USER`: PostgreSQL username
- `POSTGRES_PASSWORD`: PostgreSQL password
- `POSTGRES_HOST`: PostgreSQL hostname
- `POSTGRES_DB`: PostgreSQL database name
- `KAFKA_HOST`: Kafka broker hostname
- `TOPIC_NAME`: Kafka topic name for events

### Optional Variables

- `POSTGRES_PORT`: PostgreSQL port (default: 5432)
- `POSTGRES_OUT_PORT`: PostgreSQL external port (default: 1234)
- `KAFKA_PORT`: Kafka broker port (default: 9092)
- `DEBUG`: Enable debug mode (default: false)
- `IS_DOCKER`: Running in Docker (automatically set by compose)

See `.env.example` for a complete template.

## API Endpoints

### Health Check
```bash
GET /health
```
Returns service health status.

### Events API
All endpoints are prefixed with `/api/v1/events`

- **Create Event**
  ```bash
  POST /api/v1/events
  ```
  Request body:
  ```json
  {
    "name": "user.created",
    "data": {"user_id": 123}
  }
  ```

## Running Locally

### Start API Server
```bash
python -m app_api
```
Server runs on `http://localhost:8000`

### Start Consumer Worker
```bash
python -m consumer
```

### Run Tests
```bash
python -m pytest
```

### Performance Testing
```bash
locust -f locust_test.py
```

## Database Migrations

### Create New Migration
```bash
alembic revision --autogenerate -m "description"
```

### Apply Migrations
```bash
alembic upgrade head
```

### Revert Migrations
```bash
alembic downgrade -1
```

## Development

### Code Style
The project follows Python best practices. Use the included linting tools:
```bash
ruff check .
```

### Async/Await
- All database operations use asyncpg (async PostgreSQL driver)
- All I/O operations are async using uvloop event loop
- Services use dependency injection for cleaner code

## Architecture

### API Layer (`app_api/`)
- **Routes**: REST endpoint definitions
- **Schemas**: Pydantic models for request/response validation
- **Services**: Business logic for event operations
- **Models**: SQLAlchemy ORM model definitions
- **DI**: Dependency injection container setup

### Consumer Layer (`consumer/`)
- **Worker**: Kafka consumer worker that processes events
- **Services**: Event processing business logic
- **Schemas**: Kafka message format definitions
- **DI**: Dependency injection container for consumer services

### Shared Components
- **Config**: Centralized settings management
- **Models**: Shared data models for database

## Monitoring

- **Health Endpoint**: `/health` - Service availability
- **Logs**: Check container or console output
- **Database**: Monitor PostgreSQL query performance
- **Kafka**: Monitor consumer lag and throughput

## Troubleshooting

### Connection Issues
- Ensure PostgreSQL is running and accessible
- Verify Kafka broker is reachable
- Check `.env` configuration

### Database Migration Errors
```bash
# Reset migrations (development only)
alembic downgrade base
alembic upgrade head
```

### Consumer Lag
- Check consumer logs for errors
- Verify Kafka topic exists
- Monitor consumer group status

## Dependencies

- **FastAPI**: Modern async web framework
- **SQLAlchemy**: ORM for database operations
- **asyncpg**: Async PostgreSQL driver
- **aiokafka**: Async Kafka client
- **Pydantic**: Data validation
- **Dishka**: Dependency injection container
- **Alembic**: Database migration tool
- **Uvicorn**: ASGI server
- **Uvloop**: High-performance event loop

See `pyproject.toml` for complete dependencies.
