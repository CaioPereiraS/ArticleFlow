# ArticleFlow
Event-driven article collection platform built with Python, RabbitMQ, and FastAPI. Collects articles from RSS feeds, processes them asynchronously, stores structured data in PostgreSQL, and exposes it through a REST API.

---

## Architecture Overview

This project is structured as a **containerized, event-driven system** composed of independent services, each with a single, well-defined responsibility.

The architecture is designed to:

* Decouple RSS discovery from article processing
* Enable asynchronous and scalable workloads
* Isolate dependencies and runtime environments
* Allow each component to be built, run, and scaled independently

RabbitMQ acts as the backbone of the system, transporting article URLs as events between services. PostgreSQL is used as the persistent storage, while a read-only API exposes the processed data.

---

## Why Each Service Has Its Own Dockerfile

Each core service (`collector`, `worker`, and `api`) has its own Dockerfile to ensure **clear isolation and reproducibility**.

This approach provides:

* **Independent dependency management**
  Each service installs only what it needs, keeping images smaller and responsibilities clear.
* **Explicit runtime definition**
  The Dockerfile defines exactly what process runs when the container starts, removing ambiguity.
* **Independent scaling**
  Services can be scaled horizontally (e.g., multiple workers) without impacting others.
* **Production-like architecture**
  Mirrors real-world systems where services are deployed, updated, and operated separately.

When `docker-compose up` is executed, Docker builds each image from its respective Dockerfile and starts the container using the defined entrypoint, automatically running the service’s main process.

This design keeps the system modular, resilient, and easy to reason about, while remaining simple enough for a portfolio project.

uvicorn services.api.main:app --reload --port 8001
