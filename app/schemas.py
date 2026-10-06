from datetime import date
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RecipientInput(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    email: EmailStr
    course_name: str = Field(min_length=1, max_length=200)
    completion_date: date


class JobCreate(BaseModel):
    event_name: str = Field(min_length=1, max_length=200)
    issuer_name: str = Field(min_length=1, max_length=200)
    recipients: list[RecipientInput] = Field(min_length=1, max_length=10000)


class CertificateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    recipient_name: str
    recipient_email: str
    status: str
    download_url: str | None = None
    error_message: str | None = None


class JobResponse(BaseModel):
    id: str
    event_name: str
    issuer_name: str
    status: str
    total_count: int
    completed_count: int
    failed_count: int
    progress_percent: float
    certificates: list[CertificateResponse]
