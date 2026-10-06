Distributed Task Queue & Worker Engine

<div align="center">

<br/>

**A distributed asynchronous task queue engine built with Python, FastAPI, and Redis Sorted Sets, featuring priority scheduling, delayed jobs, automatic retries, dead-letter queues, worker pool management, idempotency, and a real-time monitoring dashboard.**

[Live Dashboard](#-live-monitoring-dashboard) · [Architecture](#-architecture) · [Quickstart](#-quickstart-with-docker) · [Job Handlers](#-job-handlers) · [Deployment](#-cloud-deployment)

</div>

---

## 🚀 Key Features

- **⚡ Priority Scheduling**  
  Tasks are scored and scheduled using Redis Sorted Sets with configurable priority levels.

- **⏱️ Scheduled & Delayed Jobs**  
  Supports future job execution using configurable delays.

- **🔄 Exponential Backoff Retries**  
  Automatically retries failed tasks using increasing backoff intervals.

- **💀 Dead-Letter Queue (DLQ)**  
  Tasks that exceed the maximum retry limit are moved to a dedicated dead-letter queue for inspection and manual replay.

- **🔑 Idempotency Deduplication**  
  Idempotency key hashing helps prevent duplicate job execution across concurrent API requests.

- **📊 Real-Time Monitoring Dashboard**  
  Interactive dashboard displaying worker activity, queue depth, task throughput, processing state, and execution logs.

- **🛡️ In-Memory Fallback**  
  Provides a local in-memory priority queue fallback when Redis is unavailable.

---

## 🏛️ Architecture

```text
                         +-------------------------------+
                         |      FastAPI Job Producer     |
                         |             API               |
                         +---------------+---------------+
                                         |
                                         | POST /api/jobs
                                         v
                     +-------------------+-------------------+
                     |       Redis Priority Sorted Sets      |
                     |                                       |
                     |   queue:jobs   |   queue:dlq          |
                     |   job:*        |   job metadata       |
                     +-------------------+-------------------+
                                         |
                 +-----------------------+-----------------------+
                 |                       |                       |
                 v                       v                       v
          +---------------+       +---------------+       +---------------+
          |   Worker 1    |       |   Worker 2    |       |   Worker N    |
          | Handler Pool  |       | Handler Pool  |       | Handler Pool  |
          +-------+-------+       +-------+-------+       +-------+-------+
                  |                       |                       |
                  +-----------------------+-----------------------+
                                          |
                                          v
                              +-----------------------+
                              |   Task Execution &    |
                              |   Status Tracking     |
                              +-----------------------+
```

### Processing Flow

```text
Client
  |
  v
FastAPI
  |
  v
Redis Queue
  |
  +----> Worker 1
  |
  +----> Worker 2
  |
  +----> Worker N
           |
           v
      Task Handler
           |
       +---+---+
       |       |
    Success  Failure
       |       |
       v       v
   Complete   Retry
               |
          +----+----+
          |         |
        Retry      Max Attempts
          |         |
          v         v
       Queue       DLQ
```

---

## 💻 Live Monitoring Dashboard

The application includes an interactive monitoring interface served at `/`.

### Dashboard Features

- **Live Cluster Gauges**  
  Displays queue depth, completed tasks, and worker health.

- **Job Dispatcher**  
  Provides an interface for submitting test jobs to registered handlers.

- **Task Activity Stream**  
  Displays task processing state, execution information, and logs.

### Available Dashboard

After starting the application:

**Dashboard:**  
http://localhost:8000

**Swagger API Documentation:**  
http://localhost:8000/docs

---

## 🧩 Job Handlers

The task queue supports multiple registered background job handlers.

Current examples include:

- `send_email`
- `http_webhook`
- `generate_report`
- `resize_image`

Additional handlers can be added to extend the worker system.

---

## ⚡ Quickstart with Docker

### Prerequisites

- Docker
- Docker Compose

### Start the Application

```bash
docker compose up -d --build
```

The API and worker services will start using Docker Compose.

### Access the Application

**Task Dashboard**

```text
http://localhost:8000
```

**Swagger API Documentation**

```text
http://localhost:8000/docs
```

---

## 🛠️ Local Development

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

```bash
cp .env.example .env
```

Update the environment variables as required.

### 3. Start the API Server

```bash
uvicorn app.main:app --reload --port 8000
```

### 4. Start the Worker Pool

Open a separate terminal:

```bash
python -m app.worker.pool
```

The application will then be available at:

```text
http://localhost:8000
```

---

## 🧪 Running Automated Tests

Run the test suite using:

```bash
pytest -v
```

---

## ☁️ Cloud Deployment

A `render.yaml` deployment blueprint is included for cloud deployment.

The application can be configured with:

- API service
- Background worker processes
- Managed Redis
- Environment variables

For more information about deployment:

[Render](https://render.com)

---

## 🔐 Reliability

The system incorporates multiple mechanisms for reliable asynchronous task execution:

- Priority-based scheduling
- Automatic retries
- Exponential backoff
- Dead-letter queues
- Idempotency protection
- Distributed worker processes
- Redis-backed queue state
- Task status tracking
- In-memory fallback queue

These mechanisms allow failed tasks to be isolated, retried, and inspected without interrupting the entire task-processing system.

---

## 📁 Project Structure

```text
.
├── app/
│   ├── main.py
│   ├── worker/
│   │   └── pool.py
│   └── ...
├── tests/
├── requirements.txt
├── docker-compose.yml
├── Dockerfile
├── render.yaml
├── .env.example
└── README.md
```

---

## 📄 License

This project is licensed under the MIT License.

See the `LICENSE` file for the complete license terms.
