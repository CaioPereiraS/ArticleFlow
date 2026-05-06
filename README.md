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

uvicorn services.api.main:app --reload --port 8001
