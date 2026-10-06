# Bulk Certificate Generator

A FastAPI backend that accepts one request containing many recipients, generates a PDF certificate for each recipient, tracks individual results, and exposes completed certificates for download.

## Setup

Requires Python 3.11+.

```powershell
cd D:\bulk-certificate-generator
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API is available at `http://127.0.0.1:8000`. Interactive documentation is at `/docs`.

## API

### Create a generation job

`POST /api/jobs/`

```json
{
  "event_name": "Python Bootcamp",
  "issuer_name": "Example Academy",
  "recipients": [
    {
      "name": "Ada Lovelace",
      "email": "ada@example.com",
      "course_name": "Advanced Python",
      "completion_date": "2026-10-01"
    }
  ]
}
```

The endpoint returns `202 Accepted` and a job object. Generation runs as a background task. Each recipient is represented by an individual certificate record.

### Check job status

`GET /api/jobs/{job_id}/`

The response includes `total_count`, `completed_count`, `failed_count`, `progress_percent`, and the result of every recipient. A job ends as `COMPLETED` or `COMPLETED_WITH_ERRORS`.

### Download a certificate

`GET /api/certificates/{certificate_id}/download`

Completed certificates are returned as PDF files. Pending certificates return `409`; missing jobs/certificates return `404`.

## Testing

```powershell
pytest -q
```

The tests cover job creation, Pydantic validation, PDF generation, progress/result reporting, individual failure isolation, and certificate retrieval.

## Architecture and design decisions

- FastAPI provides request validation, automatic OpenAPI documentation, and a small HTTP surface.
- SQLAlchemy with SQLite stores jobs and per-recipient certificate records. PostgreSQL can be used by setting `DATABASE_URL`.
- ReportLab generates PDFs from one predefined template in `app/certificate_service.py`.
- FastAPI `BackgroundTasks` keeps the upload request responsive for ordinary bulk jobs. For very large production workloads, this worker should be moved to Celery/RQ with Redis or a message broker.
- Each recipient is processed independently. Exceptions are stored on that certificate and do not prevent later recipients from running.
- Recipient validation is also per-item: a malformed recipient is recorded as `FAILED` while valid recipients in the same request continue through generation.
- Files are stored in the `certificates/` directory. Object storage such as S3 would be preferable in a multi-instance deployment.

## Learning and future scope

This project demonstrates API design, relational persistence, validation, background processing, PDF generation, and resilient batch handling. Future improvements include authentication, rate limits, idempotency keys, email delivery, signed download URLs, template configuration, retry policies, Docker deployment, and a real task queue.
