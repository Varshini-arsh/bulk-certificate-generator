from app.db import SessionLocal
from app.models import Certificate, CertificateStatus


PAYLOAD = {
    "event_name": "Python Bootcamp",
    "issuer_name": "Example Academy",
    "recipients": [{
        "name": "Ada Lovelace", "email": "ada@example.com",
        "course_name": "Advanced Python", "completion_date": "2026-10-01"
    }]
}


def test_create_job_and_generate_certificate(client):
    response = client.post("/api/jobs/", json=PAYLOAD)
    assert response.status_code == 202
    data = response.json()
    assert data["total_count"] == 1
    job = client.get(f"/api/jobs/{data['id']}/").json()
    assert job["status"] == "COMPLETED"
    assert job["completed_count"] == 1
    certificate_id = job["certificates"][0]["id"]
    download = client.get(f"/api/certificates/{certificate_id}/download")
    assert download.status_code == 200
    assert download.headers["content-type"] == "application/pdf"


def test_validation_error(client):
    invalid = {**PAYLOAD, "recipients": [{**PAYLOAD["recipients"][0], "email": "not-an-email"}]}
    assert client.post("/api/jobs/", json=invalid).status_code == 422


def test_one_failure_does_not_stop_other_recipients(client, monkeypatch):
    from app import worker
    original = worker.generate_certificate
    calls = {"count": 0}

    def fail_first(*args, **kwargs):
        calls["count"] += 1
        if calls["count"] == 1:
            raise RuntimeError("simulated failure")
        return original(*args, **kwargs)

    monkeypatch.setattr(worker, "generate_certificate", fail_first)
    payload = {**PAYLOAD, "recipients": [PAYLOAD["recipients"][0], {
        "name": "Grace Hopper", "email": "grace@example.com",
        "course_name": "Advanced Python", "completion_date": "2026-10-01"
    }]}
    response = client.post("/api/jobs/", json=payload)
    job = client.get(f"/api/jobs/{response.json()['id']}/").json()
    assert job["status"] == "COMPLETED_WITH_ERRORS"
    assert job["completed_count"] == 1
    assert job["failed_count"] == 1
