# Event Handler Service

A high-performance, distributed event handling system with real-time notifications. Built with **FastAPI**, **Apache Kafka**, **PostgreSQL**, and **Server-Sent Events (SSE)**, this architecture supports event creation, asynchronous processing, and real-time subscriber notifications.

## 🎯 Core Components

The system consists of three main services:

1. **API Service** (`app_api/`): REST API for event creation and management
2. **Consumer Service** (`consumer/`): Kafka consumer for event processing
3. **Notification Provider** (`notification_provider/`): Real-time event notifications via SSE

## ✨ Key Features

- **Async-First Architecture**: Built on asyncio with uvloop for high performance
- **Event Processing Pipeline**: Kafka-based event streaming with configurable consumer groups
- **Real-Time Notifications**: Server-Sent Events (SSE) for live event updates
- **Persistent Storage**: PostgreSQL with async queries via asyncpg
- **Dependency Injection**: Clean, testable code using Dishka
- **Database Migrations**: Schema versioning with Alembic
- **Docker Native**: Docker Compose setup for infrastructure and applications
- **Performance Testing**: Load testing with Locust for benchmarking
- **Redis Integration**: Caching and session management capabilities
- **Health Monitoring**: Built-in health check endpoints

## 📊 Performance Benchmarks

### Average Processing Times (ms)
- Async IO-bound: ~4,921 ms
- CPU-bound (1 process): ~24,466 ms
- Mixed Workload: ~8,742 ms

### 95th and 99th Percentiles (ms)
- Async IO-bound: 10,967 / 11,581 ms
- CPU-bound: 41,948 / 50,791 ms
- Mixed Workload: 19,730 / 26,249 ms

## 📁 Project Structure

```
event_handler/
├── app_api/                    # FastAPI REST API Service
│   ├── __main__.py            # Server entry point & initialization
│   ├── config.py              # Configuration & settings management
│   ├── di.py                  # Dishka dependency injection container
│   ├── models.py              # SQLAlchemy ORM models
│   ├── routes.py              # API endpoint definitions
│   ├── schemas.py             # Pydantic request/response models
│   └── services.py            # Business logic & event handling
│
├── consumer/                   # Apache Kafka Consumer Service
│   ├── __main__.py            # Consumer entry point & initialization
│   ├── config.py              # Consumer configuration
│   ├── di.py                  # DI container for consumer
│   ├── models.py              # Data models
│   ├── services.py            # Event processing logic
│   ├── schemas.py             # Kafka message schemas
│   └── worker.py              # Kafka consumer worker loop
│
├── notification_provider/      # SSE Notification Service
│   ├── __main__.py            # Notification server entry point
│   ├── config.py              # Notification service config
│   ├── di.py                  # DI container
│   ├── models.py              # Subscriber & notification models
│   ├── routes.py              # SSE endpoints
│   ├── schemas.py             # Notification schemas
│   ├── services.py            # Event subscription logic
│   └── helpers.py             # Utility functions
│
├── alembic/                    # Database Migration Scripts
│   └── versions/              # Migration files
│
├── docker/                     # Container Configurations
│   ├── api/Dockerfile         # API service image
│   └── consumer/Dockerfile    # Consumer service image
│
├── docker_infra_compose.yml    # Infrastructure (PostgreSQL, Kafka, Redis)
├── docker_apps.compose.yml     # Application services (API, Consumer, Notifications)
├── pyproject.toml             # Project metadata & dependencies
├── alembic.ini                # Alembic configuration
├── locust_test.py             # Load testing scenarios
├── sse.py                     # SSE utilities & helpers
├── redis.conf                 # Redis configuration
├── users.acl                  # Access control list
└── .env                       # Environment variables (local)
```

## 🔧 Technology Stack

### Core Technologies
- **Python 3.13+**
- **PostgreSQL 14+** (persistent data store)
- **Apache Kafka** (event streaming)
- **Redis** (caching & sessions)
- **Docker & Docker Compose** (containerization)

### Python Dependencies
- **FastAPI** – Async web framework
- **SQLAlchemy** – ORM for database operations
- **asyncpg** – Async PostgreSQL driver
- **aiokafka** – Async Kafka client
- **Pydantic** – Data validation
- **Dishka** – Dependency injection
- **Alembic** – Database migrations
- **Uvicorn** – ASGI server
- **Uvloop** – High-performance event loop
- **Locust** – Performance testing

## 🚀 Quick Start

### Prerequisites
- Python 3.13+ or Docker
- PostgreSQL 14+ (or use Docker)
- Apache Kafka (or use Docker)

### Local Development Setup

1. **Clone & Install**
   ```bash
   git clone <repository>
   cd event_handler
   pip install uv
   uv sync
   ```

2. **Environment Configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your database, Kafka, and Redis settings
   ```

3. **Database Setup**
   ```bash
   alembic upgrade head
   ```

4. **Run Services Locally**
   ```bash
   # Terminal 1: Start API
   python -m app_api
   
   # Terminal 2: Start Consumer
   python -m consumer
   
   # Terminal 3: Start Notification Provider
   python -m notification_provider
   ```

### Docker Compose Setup (Recommended)

1. **Start Infrastructure** (PostgreSQL, Kafka, Redis)
   ```bash
   docker-compose -f docker_infra_compose.yml up -d
   ```

2. **Start Application Services** (API, Consumer, Notifications)
   ```bash
   docker-compose -f docker_apps.compose.yml up -d
   ```

3. **Monitor Logs**
   ```bash
   docker-compose -f docker_apps.compose.yml logs -f api
   docker-compose -f docker_apps.compose.yml logs -f consumer
   docker-compose -f docker_apps.compose.yml logs -f notification-provider
   ```

4. **Verify Services**
   ```bash
   curl http://localhost:8000/health
   ```

## ⚙️ Configuration

Environment variables control all configuration with the `EVENT_HANDLER_SERVICE_` prefix.

### Database Settings
```
POSTGRES_USER          PostgreSQL username
POSTGRES_PASSWORD      PostgreSQL password  
POSTGRES_HOST          PostgreSQL hostname
POSTGRES_DB            PostgreSQL database name
POSTGRES_PORT          PostgreSQL port (default: 5432)
POSTGRES_OUT_PORT      PostgreSQL external port (default: 1234)
```

### Message Queue Settings
```
KAFKA_HOST             Kafka broker hostname
KAFKA_PORT             Kafka broker port (default: 9092)
TOPIC_NAME             Kafka topic for events
```

### Redis Settings
```
REDIS_HOST             Redis hostname
REDIS_PORT             Redis port (default: 6379)
```

### Application Settings
```
DEBUG                  Enable debug logging (default: false)
IS_DOCKER              Running in Docker environment
SERVICE_NAME           Service identifier
```

See `.env.example` for a complete template.

### Configuration Files Reference

The project includes example configuration files to help you get started:

#### `.env.example` - Environment Variables Template
Comprehensive environment configuration template with:
- PostgreSQL connection settings
- Kafka broker configuration
- Redis cache settings
- API service ports and hosts
- Docker Compose setup instructions
- Commented examples for different deployment scenarios

**Usage:**
```bash
cp .env.example .env
# Edit .env with your specific values
```

#### `redis.conf.example` - Redis Server Configuration
Complete Redis server configuration with:
- Network binding and port settings
- Authentication and ACL configuration
- Persistence (RDB and AOF) options
- Replication settings
- Memory management policies
- Client output buffer limits
- Performance tuning recommendations

**Usage:**
```bash
cp redis.conf.example redis.conf
# Customize for your environment
docker-compose -f docker_infra_compose.yml up -d  # Uses redis.conf
```

#### `users.acl.example` - Redis ACL (Access Control List)
User permission templates for Redis with:
- Default user configuration
- Notification service user (pre-configured)
- Monitoring user example
- Development user example
- Production setup templates with restricted permissions

**Usage:**
```bash
cp users.acl.example users.acl
# Customize user credentials and permissions
# Referenced by redis.conf: aclfile /etc/redis/users.acl
```

**Common User Roles:**
- `notification_user`: Full access for notification provider caching
- `monitor`: Read-only access for monitoring and health checks
- `dev_user`: Unrestricted access (development only)
- `admin`: Full administrative access (production)

## 📡 API Reference

### Health & Status
```bash
GET /health
```
Returns service health status and availability.

### Event Management API
All event endpoints are prefixed with `/api/v1/events`

#### Create Event
```bash
POST /api/v1/events
Header: service-name: <service_identifier>

{
  "name": "user.created",
  "data": {
    "user_id": 123,
    "email": "user@example.com"
  }
}
```
Returns: `201 Created`

### Real-Time Notifications (SSE)
Server-Sent Events endpoint for subscribing to real-time updates.

```bash
GET /api/v1/subscribe?user_id=<user_id>
```

Connect to receive event notifications as they are processed. Keep the connection open to maintain the stream.

**Example with curl:**
```bash
curl -N http://localhost:8001/api/v1/subscribe?user_id=123
```

## 🛠️ Development & Deployment

### Running Services

**API Server** (REST endpoints, port 8000)
```bash
python -m app_api
```

**Consumer Worker** (Kafka event processing)
```bash
python -m consumer
```

**Notification Provider** (SSE real-time updates, port 8001)
```bash
python -m notification_provider
```

### Testing & Quality

**Run Tests**
```bash
python -m pytest
```

**Code Quality Checks**
```bash
ruff check .
```

**Load Testing with Locust**
```bash
locust -f locust_test.py --host=http://localhost:8000
```

### Database Migrations

**Generate Migration**
```bash
alembic revision --autogenerate -m "Add new column"
```

**Apply Migrations**
```bash
alembic upgrade head
```

**Revert Last Migration**
```bash
alembic downgrade -1
```

**Reset to Base** (development only)
```bash
alembic downgrade base
alembic upgrade head
```

## 🏗️ Architecture Deep Dive

### Event Flow Pipeline

```
┌─────────────┐      ┌──────────────┐      ┌───────────────┐      ┌──────────────┐
│   Client    │─────▶│   API Service│─────▶│ Apache Kafka  │─────▶│   Consumer   │
│  (REST)     │      │  (FastAPI)   │      │   (Events)    │      │   (Worker)   │
└─────────────┘      └──────────────┘      └───────────────┘      └──────────────┘
                                                                           │
                                                                           ▼
                                                                    ┌────────────────┐
                                                                    │  PostgreSQL    │
                                                                    │  (Persist)     │
                                                                    └────────────────┘
                                                                           │
                                                                           ▼
                                                                    ┌────────────────┐
                                                                    │  Redis Cache   │
                                                                    └────────────────┘
                                                                           │
                                                                           ▼
                                                         ┌──────────────────────────┐
                                                         │ Notification Provider    │
                                                         │ (SSE Subscriptions)      │
                                                         └──────────────────────────┘
                                                                           │
                                                                           ▼
                                                         ┌──────────────────────────┐
                                                         │  Connected Subscribers   │
                                                         │  (Real-time Updates)     │
                                                         └──────────────────────────┘
```

### Service Responsibilities

**API Service** (`app_api/`)
- Receives HTTP requests for event creation
- Validates events using Pydantic schemas
- Publishes events to Kafka topic
- Stores initial event state in PostgreSQL
- Returns immediate confirmation to client

**Consumer Worker** (`consumer/`)
- Subscribes to Kafka topic for events
- Processes events asynchronously
- Executes business logic and transformations
- Updates event status in database
- Caches results in Redis
- Notifies subscribers of completion

**Notification Provider** (`notification_provider/`)
- Maintains persistent SSE connections
- Subscribes to event updates
- Streams real-time notifications to clients
- Manages subscriber connections and cleanup
- Handles connection failures gracefully

### Dependency Injection Pattern

The system uses **Dishka** for dependency injection, providing:
- Centralized container setup per service
- Clean separation of concerns
- Easy testing with mock dependencies
- Lifecycle management (startup/shutdown)
- Request-scoped and singleton services

### Async Architecture

All I/O operations are non-blocking:
- **asyncpg**: Async PostgreSQL driver for database queries
- **aiokafka**: Async Kafka client for event streaming
- **uvloop**: High-performance event loop implementation
- **asyncio**: Native Python async/await patterns

This enables efficient handling of thousands of concurrent connections.

## 📊 Monitoring & Observability

### Health Endpoints
```bash
# API Service Health
curl http://localhost:8000/health

# Check consumer status
Check logs for processing metrics

# Monitor Kafka topic
kafka-consumer-groups --bootstrap-server localhost:9092 --describe --group event_handler
```

### Key Metrics to Monitor
- Event creation rate (events/sec)
- Consumer lag (pending messages in Kafka)
- Database query response times
- SSE active subscriber count
- Redis cache hit ratio

### Troubleshooting

**Connection Issues**
```bash
# Verify PostgreSQL
psql -h localhost -U postgres -d event_handler

# Check Kafka connectivity
kafka-broker-api-versions --bootstrap-server localhost:9092

# Test Redis connection
redis-cli ping
```

**Consumer Not Processing Events**
- Check consumer logs: `docker logs <consumer_container>`
- Verify Kafka topic exists: `kafka-topics --list --bootstrap-server localhost:9092`
- Monitor consumer group lag
- Ensure database migrations are applied

**Database Migration Errors**
```bash
# Reset migrations (development only)
alembic downgrade base
alembic upgrade head
```

**High Event Processing Latency**
- Check database query performance
- Monitor CPU and memory usage
- Verify Redis is responsive
- Scale consumer workers horizontally
