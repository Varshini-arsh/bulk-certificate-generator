import os
import uuid
from pathlib import Path

from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from .db import Base, engine, get_db
from .models import Certificate, CertificateStatus, GenerationJob, JobStatus
from .schemas import CertificateResponse, JobCreate, JobResponse
from .worker import process_job


Base.metadata.create_all(bind=engine)
app = FastAPI(title="Bulk Certificate Generator", version="1.0.0")
STORAGE_DIR = Path(os.getenv("CERTIFICATE_STORAGE_DIR", "certificates"))


def job_response(job: GenerationJob) -> JobResponse:
    certificates = [CertificateResponse(
        id=item.id, recipient_name=item.recipient_name, recipient_email=item.recipient_email,
        status=item.status, download_url=f"/api/certificates/{item.id}/download" if item.file_path else None,
        error_message=item.error_message,
    ) for item in job.certificates]
    progress = ((job.completed_count + job.failed_count) / job.total_count * 100) if job.total_count else 0
    return JobResponse(id=job.id, event_name=job.event_name, issuer_name=job.issuer_name,
                       status=job.status, total_count=job.total_count,
                       completed_count=job.completed_count, failed_count=job.failed_count,
                       progress_percent=round(progress, 2), certificates=certificates)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/jobs/", response_model=JobResponse, status_code=202)
def create_job(payload: JobCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)) -> JobResponse:
    job = GenerationJob(id=str(uuid.uuid4()), event_name=payload.event_name,
                        issuer_name=payload.issuer_name, status=JobStatus.PENDING,
                        total_count=len(payload.recipients))
    for recipient in payload.recipients:
        job.certificates.append(Certificate(
            id=str(uuid.uuid4()), recipient_name=recipient.name.strip(), recipient_email=str(recipient.email),
            course_name=recipient.course_name.strip(), completion_date=recipient.completion_date.isoformat(),
            status=CertificateStatus.PENDING,
        ))
    db.add(job)
    db.commit()
    db.refresh(job)
    background_tasks.add_task(process_job, job.id, STORAGE_DIR)
    return job_response(job)


@app.get("/api/jobs/{job_id}/", response_model=JobResponse)
def get_job(job_id: str, db: Session = Depends(get_db)) -> JobResponse:
    job = db.get(GenerationJob, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Generation job not found")
    return job_response(job)


@app.get("/api/certificates/{certificate_id}/download")
def download_certificate(certificate_id: str, db: Session = Depends(get_db)) -> FileResponse:
    certificate = db.get(Certificate, certificate_id)
    if not certificate:
        raise HTTPException(status_code=404, detail="Certificate not found")
    if certificate.status != CertificateStatus.COMPLETED or not certificate.file_path:
        raise HTTPException(status_code=409, detail="Certificate is not available")
    path = Path(certificate.file_path)
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Certificate file not found")
    return FileResponse(path, media_type="application/pdf", filename=f"{certificate.recipient_name}.pdf")
