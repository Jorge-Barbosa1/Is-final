# Microservices Media Platform

A media-platform backend implemented as a set of independent services that communicate over different protocols, designed to demonstrate distributed-systems patterns: synchronous gRPC for service-to-service calls, REST and GraphQL for client APIs, and a RabbitMQ-backed worker for asynchronous CSV ingestion.

Built as the final project for the **Integrated Systems** course in the Bachelor's Degree in Informatics Engineering at IPVC.

## Architecture

```
                 ┌──────────────┐                ┌──────────────┐
   client ─────▶ │  REST API    │ ───── gRPC ──▶ │ gRPC server  │ ──▶ media files
   (HTTP/JSON)   │   (Django)   │                │  (Python)    │
                 └──────┬───────┘                └──────┬───────┘
                        │                               │
                        ▼                               ▼
                 ┌──────────────┐                ┌──────────────┐
                 │  PostgreSQL  │ ◀──────────────│              │
                 └──────────────┘                │              │
                                                 ▼
   client ─────▶ ┌──────────────┐         ┌──────────────┐
   (GraphQL)     │  GraphQL     │ ──────▶ │  RabbitMQ    │ ──▶ CSV worker
                 │   server     │         │  (broker)    │     (async ingest)
                 └──────────────┘         └──────────────┘
```

## Services

| Service | Tech | Purpose |
|---|---|---|
| `rest_api_server` | Django, SQLite/Postgres | Public HTTP/JSON API for clients |
| `graphql-server` | Python, Django | Alternative GraphQL API |
| `grpc-server` | Python, gRPC, `.proto` | Internal RPC for media access |
| `worker-rabbit-csv` | Python, RabbitMQ consumer | Async CSV ingestion pipeline |
| `rabbitmq` | RabbitMQ 3 + management UI | Message broker |
| `db` | PostgreSQL | Shared persistence |

The `.proto` contract for the gRPC service is at `grpc-server/server_services.proto`.

## Run it

Everything is in `docker-compose.yml`:

```bash
docker compose up --build
```

Default ports:

| Service | URL |
|---|---|
| REST API | `http://localhost:8000` |
| gRPC | `localhost:50051` |
| RabbitMQ broker | `localhost:5672` |
| RabbitMQ management UI | `http://localhost:15672` (user `user` / pass `password`) |
| PostgreSQL | `localhost:5432` (user `myuser` / db `mydatabase`) |

The REST API talks to the gRPC server using `GRPC_HOST=grpc-server` and `GRPC_PORT=50051` (set via env in the compose file).

## What I learned building this

- Designing **service contracts** with three different paradigms (REST, GraphQL, gRPC) for the same underlying data.
- Wiring **synchronous + asynchronous** flows: REST/GraphQL handle the request lifecycle; the RabbitMQ worker handles long CSV imports without blocking the API.
- **Service-to-service auth and discovery** inside a Docker network.
- Writing a `.proto` and generating Python stubs for gRPC.

## Status

Course project, not maintained as a product. Useful as a reference for setting up a multi-protocol microservices stack with Docker Compose.

## License

MIT.
