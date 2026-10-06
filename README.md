# 📦 TaskPulse — Distributed Task Queue & Worker Engine

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white)

<br/>

**A production-ready distributed asynchronous task queue engine built with Python, FastAPI, and Redis Sorted Sets featuring priority scoring, exponential backoff retries, dead-letter queues (DLQ), worker pool management, and a live web dashboard.**

[Live Dashboard UI](#-live-monitoring-dashboard) · [Architecture](#-architecture) · [Quickstart with Docker](#-quickstart-with-docker) · [Job Handlers](#-registered-job-handlers) · [Deployment](#-cloud-deployment)

</div>

---

## 🚀 Key Features

* **⚡ Priority Scheduling**: Tasks scored and scheduled with Redis Sorted Sets (`HIGH` 100, `NORMAL` 50, `LOW` 10).
* **⏱️ Scheduled & Delayed Jobs**: Support for future job execution with custom delays (`delay_seconds`).
* **🔄 Exponential Backoff Retries**: Configurable automatic retry attempts with increasing backoff intervals upon failure.
* **💀 Dead-Letter Queue (DLQ)**: Failed tasks exceeding max retries are safely quarantined in a dedicated DLQ for inspection and manual replay.
* **🔑 Idempotency Deduplication**: Idempotency key hashing prevents duplicate job execution across concurrent API calls.
* **📊 Real-Time Monitoring Dashboard**: Interactive web UI showing active worker counts, queue depth, throughput metrics, and task streams.
* **🛡️ Zero-Dependency Fallback**: Graceful in-memory priority queue fallback for instant local evaluation without requiring Redis running.

---

## 🏛️ Architecture

```
                          +-------------------------------+
                          |   FastAPI Job Producer API    |
                          +---------------+---------------+
                                          | (POST /api/jobs)
                                          v
                      +-------------------+-------------------+
                      |       Redis Priority Sorted Sets      |
                      |   (queue:jobs, queue:dlq, job:*)      |
                      +-------------------+-------------------+
                                          |
                +-------------------------+-------------------------+
                |                         |                         |
                v                         v                         v
        +---------------+         +---------------+         +---------------+
        | Worker Node 1 |         | Worker Node 2 |         | Worker Node N |
        | (Handler Pool)|         | (Handler Pool)|         | (Handler Pool)|
        +---------------+         +---------------+         +---------------+
```

---

## 💻 Live Monitoring Dashboard

TaskPulse includes an interactive monitoring interface served at `/`:

* **Live Cluster Gauges**: Instant feedback on queue depth, completed tasks, and worker health.
* **Job Dispatcher**: Interactive form to enqueue test jobs across handlers (`send_email`, `http_webhook`, `generate_report`, `resize_image`).
* **Task Activity Stream**: Real-time auto-refreshing table displaying processing state and logs.

---

## ⚡ Quickstart with Docker

```bash
# Clone the repository
git clone https://github.com/Manziine/distributed-task-queue.git
cd distributed-task-queue

# Start API & Worker Pool with Docker Compose
docker compose up -d --build
```

Access services:
* **Task Dashboard**: [http://localhost:8000](http://localhost:8000)
* **Swagger API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🛠️ Local Development

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env

# 3. Start API server
uvicorn app.main:app --reload --port 8000

# 4. Start Worker Pool in separate terminal
python -m app.worker.pool
```

---

## 🧪 Running Automated Tests

```bash
pytest -v
```

---

## ☁️ Cloud Deployment

A `render.yaml` deployment blueprint is included. Connect the repository to [Render](https://render.com) for automated deployment with managed Redis and background worker processes.

---

## 👤 Author

**Arnaud Ineza Manzi**
* GitHub: [@Manziine](https://github.com/Manziine)
* LinkedIn: [Arnaud Ineza Manzi](https://linkedin.com/in/arnaud-ineza-manzi-471221272)
* Email: [ainezamanzi@gmail.com](mailto:ainezamanzi@gmail.com)

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
