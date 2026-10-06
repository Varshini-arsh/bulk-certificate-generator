from pathlib import Path

from .certificate_service import generate_certificate
from .db import SessionLocal
from .models import CertificateStatus, GenerationJob, JobStatus


def process_job(job_id: str, storage_dir: Path) -> None:
    db = SessionLocal()
    try:
        job = db.get(GenerationJob, job_id)
        if not job:
            return
        job.status = JobStatus.PROCESSING
        db.commit()
        for certificate in job.certificates:
            if certificate.status == CertificateStatus.FAILED:
                db.commit()
                continue
            try:
                filename = f"{certificate.id}.pdf"
                path = storage_dir / filename
                generate_certificate(path, certificate.recipient_name, certificate.course_name,
                                     certificate.completion_date, job.event_name, job.issuer_name)
                certificate.file_path = str(path)
                certificate.status = CertificateStatus.COMPLETED
                job.completed_count += 1
            except Exception as exc:  # one bad certificate must not stop the batch
                certificate.status = CertificateStatus.FAILED
                certificate.error_message = str(exc)
                job.failed_count += 1
            db.commit()
        job.status = (JobStatus.COMPLETED_WITH_ERRORS if job.failed_count else JobStatus.COMPLETED)
        db.commit()
    finally:
        db.close()
