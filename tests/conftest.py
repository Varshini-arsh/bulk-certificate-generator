import os

os.environ["DATABASE_URL"] = "sqlite:///./test_certificate_generator.db"

import pytest
from fastapi.testclient import TestClient

from app.db import Base, engine
from app.main import app


@pytest.fixture()
def client(tmp_path, monkeypatch):
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    monkeypatch.setattr("app.main.STORAGE_DIR", tmp_path / "certificates")
    with TestClient(app) as test_client:
        yield test_client
    Base.metadata.drop_all(bind=engine)
