import logging
import pytest #noqa: F401
import numpy as np
from unittest.mock import patch, MagicMock
from datetime import datetime
from fastapi.testclient import TestClient
from openapi_spec_validator import validate_spec

from app.main import app
from app.api.dependencies import get_current_user
from app.core.config import settings
from app.schemas.patients import PatientData
from app.services.ml_engine import ml_engine

client = TestClient(app, raise_server_exceptions=False)

NOW = datetime.now()

SAMPLE_PAYLOAD = {
    "patient_id": "8f3b2a1c-9d8e-4a7b-8c9d-0e1f2a3b4c5d",
    "admission_id": "1a2b3c4d-5e6f-7a8b-9c0d-1e2f3a4b5c6d",
    "admission_time": NOW.isoformat(),
    "heart_rate": 82.0,
    "sbp": 125.0,
    "dbp": 82.0,
    "resp_rate": 18.0,
    "spo2": 97.0,
    "temperature": 36.8,
    "wbc": 6.8,
    "creatinine": 0.95,
    "lactate": 1.2
}

AUTH_MOCK_USER = {"id": "medico-test-uuid", "email": "medico@sipam.com"}

def get_mock_active_admission():
    mock_adm = MagicMock()
    mock_adm.discharge_time = None
    mock_adm.admission_time = NOW
    mock_adm.admission_type = "ED"
    mock_adm.patient_id = SAMPLE_PAYLOAD["patient_id"]
    mock_adm.id = SAMPLE_PAYLOAD["admission_id"]
    return mock_adm


def test_security_and_jwt():
    assert settings.SUPABASE_URL.startswith("https://"), (
        "La URL de conexión a Supabase debe utilizar obligatoriamente el protocolo seguro HTTPS"
    )

    public_endpoints = ["/api/v1/health", "/api/v1/openapi.json", "/docs"]
    for endpoint in public_endpoints:
        res = client.get(endpoint)
        assert res.status_code == 200
        if hasattr(settings, "SUPABASE_SERVICE_KEY") and settings.SUPABASE_SERVICE_KEY:
            assert settings.SUPABASE_SERVICE_KEY not in res.text
        if hasattr(settings, "SUPABASE_JWT_SECRET") and settings.SUPABASE_JWT_SECRET:
            assert settings.SUPABASE_JWT_SECRET not in res.text

    unauthorized_res = client.post(
        "/api/v1/prediction",
        json=SAMPLE_PAYLOAD,
        headers={}
    )
    assert unauthorized_res.status_code == 401, (
        f"Se esperaba 401 sin autenticar, pero se obtuvo {unauthorized_res.status_code}"
    )

    tampered_headers = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.token_falso.firma_invalida"}
    invalid_token_res = client.post(
        "/api/v1/prediction",
        json=SAMPLE_PAYLOAD,
        headers=tampered_headers
    )
    assert invalid_token_res.status_code == 401, (
        "El sistema debe rechazar tokens con firmas no validadas por Supabase"
    )

    health_res = client.get("/api/v1/health")
    assert health_res.headers.get("x-content-type-options") == "nosniff"
    assert health_res.headers.get("x-frame-options") in ["DENY", "SAMEORIGIN"]


def test_resilience_and_graceful_degradation():
    app.dependency_overrides[get_current_user] = lambda: AUTH_MOCK_USER
    try:
        with patch.object(ml_engine, "predict", side_effect=Exception("Database or service unavailable")):
            with patch("sqlalchemy.orm.Query.first", return_value=get_mock_active_admission()):
                response = client.post("/api/v1/prediction", json=SAMPLE_PAYLOAD)

                assert response.status_code in [500, 503]
                assert "password" not in response.text.lower()
                assert "user=" not in response.text.lower()
    finally:
        app.dependency_overrides.pop(get_current_user, None)


def test_ml_model_decoupling_and_hot_swap():
    test_time = datetime.now()
    test_age = 65
    test_gender = "M"
    service = ml_engine

    patient_data_obj = PatientData(**SAMPLE_PAYLOAD)

    initial_prob, initial_threshold = service.predict(patient_data_obj, test_time, test_age, test_gender)
    assert 0.0 <= initial_prob <= 1.0
    assert 0.0 <= initial_threshold <= 1.0

    class ReTrainedModelMock:
        def predict_proba(self, features):
            return np.array([[0.05, 0.95]])

    service._model = ReTrainedModelMock()
    new_prob, new_threshold = service.predict(patient_data_obj, test_time, test_age, test_gender)

    assert new_threshold == 0.76
    assert new_prob == 0.95


def test_openapi_formal_schema_validation():
    response = client.get("/api/v1/openapi.json")
    assert response.status_code == 200

    openapi_dict = response.json()
    validate_spec(openapi_dict)

    paths = openapi_dict["paths"]
    assert "/api/v1/patients" in paths
    assert "/api/v1/prediction" in paths
    assert "/api/v1/feedback" in paths or "post" in paths["/api/v1/prediction"]


def test_structured_logging_and_phi_masking(caplog):
    caplog.clear()

    app.dependency_overrides[get_current_user] = lambda: AUTH_MOCK_USER

    payload_with_notes = {
        **SAMPLE_PAYLOAD,
        "comments": "Paciente diagnosticado con shock séptico refractario"
    }

    try:
        with patch.object(ml_engine, "predict", return_value=(0.85, 1.0)):
            with caplog.at_level(logging.INFO):
                with patch("sqlalchemy.orm.Query.first", return_value=get_mock_active_admission()):
                    response = client.post("/api/v1/prediction", json=payload_with_notes)
                    
                    assert response.status_code in [200, 201]

                    logs = caplog.text
                    assert "POST /api/v1/prediction" in logs or str(response.status_code) in logs
                    assert "shock séptico refractario" not in logs
    finally:
        app.dependency_overrides.pop(get_current_user, None)