import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from fastapi import status, HTTPException

from app.main import app
from app.api.dependencies import get_current_user
from app.schemas.auth import SupabaseUser

client = TestClient(app)

@pytest.fixture(autouse=True)
def override_auth_dependency():
    app.dependency_overrides[get_current_user] = lambda: SupabaseUser(
        id="user-123", email="medico@hospital.com", role="doctor"
    )
    yield
    app.dependency_overrides.clear()


@pytest.mark.parametrize("payload", [
    {"patient_id": "PAT-12345", "heart_rate": 80.0, "respiratory_rate": 18.0, "spo2": 98.0,
        "temperature": 36.5, "systolic_bp": 120.0, "diastolic_bp": 80.0, "oxygen_device": "nasal",
        "oxygen_flow": 2.0, "nurse_alert": False, "wbc_count": 7.5, "lactate": 1.1,
        "creatinine": 0.9, "crp": 5.0, "hemoglobin": 14.0, "sepsis_risk": 0.1},
    {"patient_id": "PAT-12345", "heart_rate": 0.0, "respiratory_rate": 18.0, "spo2": 98.0,
        "temperature": 36.5, "systolic_bp": 120.0, "diastolic_bp": 80.0, "oxygen_device": "nasal",
        "oxygen_flow": 2.0, "nurse_alert": False, "wbc_count": 7.5, "lactate": 1.1,
        "creatinine": 0.9, "crp": 5.0, "hemoglobin": 14.0, "sepsis_risk": 0.1},
    {"patient_id": "PAT-12345", "heart_rate": 80, "respiratory_rate": 18.0, "spo2": 98.0,
        "temperature": 36.5, "systolic_bp": 120.0, "diastolic_bp": 80.0, "oxygen_device": "nasal",
        "oxygen_flow": 2.0, "nurse_alert": False, "wbc_count": 7.5, "lactate": 1.1,
        "creatinine": 0.9, "crp": 5.0, "hemoglobin": 14.0, "sepsis_risk": 0.1},
    {"patient_id": "PAT-12345", "heart_rate": 80.0, "respiratory_rate": 0.0, "spo2": 98.0,
        "temperature": 36.5, "systolic_bp": 120.0, "diastolic_bp": 80.0, "oxygen_device": "nasal",
        "oxygen_flow": 2.0, "nurse_alert": False, "wbc_count": 7.5, "lactate": 1.1,
        "creatinine": 0.9, "crp": 5.0, "hemoglobin": 14.0, "sepsis_risk": 0.1},
    {"patient_id": "PAT-12345", "heart_rate": 80.0, "respiratory_rate": 18, "spo2": 98.0,
        "temperature": 36.5, "systolic_bp": 120.0, "diastolic_bp": 80.0, "oxygen_device": "nasal",
        "oxygen_flow": 2.0, "nurse_alert": False, "wbc_count": 7.5, "lactate": 1.1,
        "creatinine": 0.9, "crp": 5.0, "hemoglobin": 14.0, "sepsis_risk": 0.1},
    {"patient_id": "PAT-12345", "heart_rate": 80.0, "respiratory_rate": 18.0, "spo2": 0.0,
        "temperature": 36.5, "systolic_bp": 120.0, "diastolic_bp": 80.0, "oxygen_device": "nasal",
        "oxygen_flow": 2.0, "nurse_alert": False, "wbc_count": 7.5, "lactate": 1.1,
        "creatinine": 0.9, "crp": 5.0, "hemoglobin": 14.0, "sepsis_risk": 0.1},
    {"patient_id": "PAT-12345", "heart_rate": 80.0, "respiratory_rate": 18.0, "spo2": 100.0,
        "temperature": 36.5, "systolic_bp": 120.0, "diastolic_bp": 80.0, "oxygen_device": "nasal",
        "oxygen_flow": 2.0, "nurse_alert": False, "wbc_count": 7.5, "lactate": 1.1,
        "creatinine": 0.9, "crp": 5.0, "hemoglobin": 14.0, "sepsis_risk": 0.1},
    {"patient_id": "PAT-12345", "heart_rate": 80.0, "respiratory_rate": 18.0, "spo2": 98,
        "temperature": 36.5, "systolic_bp": 120.0, "diastolic_bp": 80.0, "oxygen_device": "nasal",
        "oxygen_flow": 2.0, "nurse_alert": False, "wbc_count": 7.5, "lactate": 1.1,
        "creatinine": 0.9, "crp": 5.0, "hemoglobin": 14.0, "sepsis_risk": 0.1},
    {"patient_id": "PAT-12345", "heart_rate": 80.0, "respiratory_rate": 18.0, "spo2": 98.0,
        "temperature": 0.0, "systolic_bp": 120.0, "diastolic_bp": 80.0, "oxygen_device": "nasal",
        "oxygen_flow": 2.0, "nurse_alert": False, "wbc_count": 7.5, "lactate": 1.1,
        "creatinine": 0.9, "crp": 5.0, "hemoglobin": 14.0, "sepsis_risk": 0.1},
    {"patient_id": "PAT-12345", "heart_rate": 80.0, "respiratory_rate": 18.0, "spo2": 98.0,
        "temperature": 36, "systolic_bp": 120.0, "diastolic_bp": 80.0, "oxygen_device": "nasal",
        "oxygen_flow": 2.0, "nurse_alert": False, "wbc_count": 7.5, "lactate": 1.1,
        "creatinine": 0.9, "crp": 5.0, "hemoglobin": 14.0, "sepsis_risk": 0.1},
    {"patient_id": "PAT-12345", "heart_rate": 80.0, "respiratory_rate": 18.0, "spo2": 98.0,
        "temperature": 36.5, "systolic_bp": 0.0, "diastolic_bp": 80.0, "oxygen_device": "nasal",
        "oxygen_flow": 2.0, "nurse_alert": False, "wbc_count": 7.5, "lactate": 1.1,
        "creatinine": 0.9, "crp": 5.0, "hemoglobin": 14.0, "sepsis_risk": 0.1},
    {"patient_id": "PAT-12345", "heart_rate": 80.0, "respiratory_rate": 18.0, "spo2": 98.0,
        "temperature": 36.5, "systolic_bp": 120, "diastolic_bp": 80.0, "oxygen_device": "nasal",
        "oxygen_flow": 2.0, "nurse_alert": False, "wbc_count": 7.5, "lactate": 1.1,
        "creatinine": 0.9, "crp": 5.0, "hemoglobin": 14.0, "sepsis_risk": 0.1},
    {"patient_id": "PAT-12345", "heart_rate": 80.0, "respiratory_rate": 18.0, "spo2": 98.0,
        "temperature": 36.5, "systolic_bp": 120.0, "diastolic_bp": 0.0, "oxygen_device": "nasal",
        "oxygen_flow": 2.0, "nurse_alert": False, "wbc_count": 7.5, "lactate": 1.1,
        "creatinine": 0.9, "crp": 5.0, "hemoglobin": 14.0, "sepsis_risk": 0.1},
    {"patient_id": "PAT-12345", "heart_rate": 80.0, "respiratory_rate": 18.0, "spo2": 98.0,
        "temperature": 36.5, "systolic_bp": 120.0, "diastolic_bp": 80, "oxygen_device": "nasal",
        "oxygen_flow": 2.0, "nurse_alert": False, "wbc_count": 7.5, "lactate": 1.1,
        "creatinine": 0.9, "crp": 5.0, "hemoglobin": 14.0, "sepsis_risk": 0.1},
    {"patient_id": "PAT-12345", "heart_rate": 80.0, "respiratory_rate": 18.0, "spo2": 98.0,
        "temperature": 36.5, "systolic_bp": 120.0, "diastolic_bp": 80.0, "oxygen_device": "nasal",
        "oxygen_flow": 0.0, "nurse_alert": False, "wbc_count": 7.5, "lactate": 1.1,
        "creatinine": 0.9, "crp": 5.0, "hemoglobin": 14.0, "sepsis_risk": 0.1},
    {"patient_id": "PAT-12345", "heart_rate": 80.0, "respiratory_rate": 18.0, "spo2": 98.0,
        "temperature": 36.5, "systolic_bp": 120.0, "diastolic_bp": 80.0, "oxygen_device": "nasal",
        "oxygen_flow": 2, "nurse_alert": False, "wbc_count": 7.5, "lactate": 1.1,
        "creatinine": 0.9, "crp": 5.0, "hemoglobin": 14.0, "sepsis_risk": 0.1},
    {"patient_id": "PAT-12345", "heart_rate": 80.0, "respiratory_rate": 18.0, "spo2": 98.0,
        "temperature": 36.5, "systolic_bp": 120.0, "diastolic_bp": 80.0, "oxygen_device": "nasal",
        "oxygen_flow": 2.0, "nurse_alert": False, "wbc_count": 0.0, "lactate": 1.1,
        "creatinine": 0.9, "crp": 5.0, "hemoglobin": 14.0, "sepsis_risk": 0.1},
    {"patient_id": "PAT-12345", "heart_rate": 80.0, "respiratory_rate": 18.0, "spo2": 98.0,
        "temperature": 36.5, "systolic_bp": 120.0, "diastolic_bp": 80.0, "oxygen_device": "nasal",
        "oxygen_flow": 2.0, "nurse_alert": False, "wbc_count": 7, "lactate": 1.1,
        "creatinine": 0.9, "crp": 5.0, "hemoglobin": 14.0, "sepsis_risk": 0.1},
    {"patient_id": "PAT-12345", "heart_rate": 80.0, "respiratory_rate": 18.0, "spo2": 98.0,
        "temperature": 36.5, "systolic_bp": 120.0, "diastolic_bp": 80.0, "oxygen_device": "nasal",
        "oxygen_flow": 2.0, "nurse_alert": False, "wbc_count": 7.5, "lactate": 0.0,
        "creatinine": 0.9, "crp": 5.0, "hemoglobin": 14.0, "sepsis_risk": 0.1},
    {"patient_id": "PAT-12345", "heart_rate": 80.0, "respiratory_rate": 18.0, "spo2": 98.0,
        "temperature": 36.5, "systolic_bp": 120.0, "diastolic_bp": 80.0, "oxygen_device": "nasal",
        "oxygen_flow": 2.0, "nurse_alert": False, "wbc_count": 7.5, "lactate": 1,
        "creatinine": 0.9, "crp": 5.0, "hemoglobin": 14.0, "sepsis_risk": 0.1},
    {"patient_id": "PAT-12345", "heart_rate": 80.0, "respiratory_rate": 18.0, "spo2": 98.0,
        "temperature": 36.5, "systolic_bp": 120.0, "diastolic_bp": 80.0, "oxygen_device": "nasal",
        "oxygen_flow": 2.0, "nurse_alert": False, "wbc_count": 7.5, "lactate": 1.1,
        "creatinine": 0.0, "crp": 5.0, "hemoglobin": 14.0, "sepsis_risk": 0.1},
    {"patient_id": "PAT-12345", "heart_rate": 80.0, "respiratory_rate": 18.0, "spo2": 98.0,
        "temperature": 36.5, "systolic_bp": 120.0, "diastolic_bp": 80.0, "oxygen_device": "nasal",
        "oxygen_flow": 2.0, "nurse_alert": False, "wbc_count": 7.5, "lactate": 1.1,
        "creatinine": 1, "crp": 5.0, "hemoglobin": 14.0, "sepsis_risk": 0.1},
    {"patient_id": "PAT-12345", "heart_rate": 80.0, "respiratory_rate": 18.0, "spo2": 98.0,
        "temperature": 36.5, "systolic_bp": 120.0, "diastolic_bp": 80.0, "oxygen_device": "nasal",
        "oxygen_flow": 2.0, "nurse_alert": False, "wbc_count": 7.5, "lactate": 1.1,
        "creatinine": 0.9, "crp": 0.0, "hemoglobin": 14.0, "sepsis_risk": 0.1},
    {"patient_id": "PAT-12345", "heart_rate": 80.0, "respiratory_rate": 18.0, "spo2": 98.0,
        "temperature": 36.5, "systolic_bp": 120.0, "diastolic_bp": 80.0, "oxygen_device": "nasal",
        "oxygen_flow": 2.0, "nurse_alert": False, "wbc_count": 7.5, "lactate": 1.1,
        "creatinine": 0.9, "crp": 5, "hemoglobin": 14.0, "sepsis_risk": 0.1},
    {"patient_id": "PAT-12345", "heart_rate": 80.0, "respiratory_rate": 18.0, "spo2": 98.0,
        "temperature": 36.5, "systolic_bp": 120.0, "diastolic_bp": 80.0, "oxygen_device": "nasal",
        "oxygen_flow": 2.0, "nurse_alert": False, "wbc_count": 7.5, "lactate": 1.1,
        "creatinine": 0.9, "crp": 5.0, "hemoglobin": 0.0, "sepsis_risk": 0.1},
    {"patient_id": "PAT-12345", "heart_rate": 80.0, "respiratory_rate": 18.0, "spo2": 98.0,
        "temperature": 36.5, "systolic_bp": 120.0, "diastolic_bp": 80.0, "oxygen_device": "nasal",
        "oxygen_flow": 2.0, "nurse_alert": False, "wbc_count": 7.5, "lactate": 1.1,
        "creatinine": 0.9, "crp": 5.0, "hemoglobin": 14, "sepsis_risk": 0.1},
    {"patient_id": "PAT-12345", "heart_rate": 80.0, "respiratory_rate": 18.0, "spo2": 98.0,
        "temperature": 36.5, "systolic_bp": 120.0, "diastolic_bp": 80.0, "oxygen_device": "nasal",
        "oxygen_flow": 2.0, "nurse_alert": False, "wbc_count": 7.5, "lactate": 1.1,
        "creatinine": 0.9, "crp": 5.0, "hemoglobin": 14.0, "sepsis_risk": 1.0},
    {"patient_id": "PAT-12345", "heart_rate": 80.0, "respiratory_rate": 18.0, "spo2": 98.0,
        "temperature": 36.5, "systolic_bp": 120.0, "diastolic_bp": 80.0, "oxygen_device": "nasal",
        "oxygen_flow": 2.0, "nurse_alert": False, "wbc_count": 7.5, "lactate": 1.1,
        "creatinine": 0.9, "crp": 5.0, "hemoglobin": 14.0, "sepsis_risk": 0},
    {"patient_id": "PAT-12345", "respiratory_rate": 18.0, "spo2": 98.0,
        "temperature": 36.5, "systolic_bp": 120.0, "diastolic_bp": 80.0, "oxygen_device": "nasal",
        "oxygen_flow": 2.0, "nurse_alert": False, "wbc_count": 7.5, "lactate": 1.1,
        "creatinine": 0.9, "crp": 5.0, "hemoglobin": 14.0, "sepsis_risk": 0.1},
    {"patient_id": "PAT-12345", "heart_rate": 80.0, "spo2": 98.0,
        "temperature": 36.5, "systolic_bp": 120.0, "diastolic_bp": 80.0, "oxygen_device": "nasal",
        "oxygen_flow": 2.0, "nurse_alert": False, "wbc_count": 7.5, "lactate": 1.1,
        "creatinine": 0.9, "crp": 5.0, "hemoglobin": 14.0, "sepsis_risk": 0.1},
    {"patient_id": "PAT-12345", "heart_rate": 80.0, "respiratory_rate": 18.0,
        "temperature": 36.5, "systolic_bp": 120.0, "diastolic_bp": 80.0, "oxygen_device": "nasal",
        "oxygen_flow": 2.0, "nurse_alert": False, "wbc_count": 7.5, "lactate": 1.1,
        "creatinine": 0.9, "crp": 5.0, "hemoglobin": 14.0, "sepsis_risk": 0.1},
    {"patient_id": "PAT-12345", "heart_rate": 80.0, "respiratory_rate": 18.0, "spo2": 98.0,
        "systolic_bp": 120.0, "diastolic_bp": 80.0, "oxygen_device": "nasal",
        "oxygen_flow": 2.0, "nurse_alert": False, "wbc_count": 7.5, "lactate": 1.1,
        "creatinine": 0.9, "crp": 5.0, "hemoglobin": 14.0, "sepsis_risk": 0.1},
    {"patient_id": "PAT-12345", "heart_rate": 80.0, "respiratory_rate": 18.0, "spo2": 98.0,
        "temperature": 36.5, "diastolic_bp": 80.0, "oxygen_device": "nasal",
        "oxygen_flow": 2.0, "nurse_alert": False, "wbc_count": 7.5, "lactate": 1.1,
        "creatinine": 0.9, "crp": 5.0, "hemoglobin": 14.0, "sepsis_risk": 0.1},
    {"patient_id": "PAT-12345", "heart_rate": 80.0, "respiratory_rate": 18.0, "spo2": 98.0,
        "temperature": 36.5, "systolic_bp": 120.0, "oxygen_device": "nasal",
        "oxygen_flow": 2.0, "nurse_alert": False, "wbc_count": 7.5, "lactate": 1.1,
        "creatinine": 0.9, "crp": 5.0, "hemoglobin": 14.0, "sepsis_risk": 0.1},
    {"patient_id": "PAT-12345", "heart_rate": 80.0, "respiratory_rate": 18.0, "spo2": 98.0,
        "temperature": 36.5, "systolic_bp": 120.0, "diastolic_bp": 80.0,
        "oxygen_flow": 2.0, "nurse_alert": False, "wbc_count": 7.5, "lactate": 1.1,
        "creatinine": 0.9, "crp": 5.0, "hemoglobin": 14.0, "sepsis_risk": 0.1},
    {"patient_id": "PAT-12345", "heart_rate": 80.0, "respiratory_rate": 18.0, "spo2": 98.0,
        "temperature": 36.5, "systolic_bp": 120.0, "diastolic_bp": 80.0, "oxygen_device": "nasal",
        "nurse_alert": False, "wbc_count": 7.5, "lactate": 1.1,
        "creatinine": 0.9, "crp": 5.0, "hemoglobin": 14.0, "sepsis_risk": 0.1},
    {"patient_id": "PAT-12345", "heart_rate": 80.0, "respiratory_rate": 18.0, "spo2": 98.0,
        "temperature": 36.5, "systolic_bp": 120.0, "diastolic_bp": 80.0, "oxygen_device": "nasal",
        "oxygen_flow": 2.0, "wbc_count": 7.5, "lactate": 1.1,
        "creatinine": 0.9, "crp": 5.0, "hemoglobin": 14.0, "sepsis_risk": 0.1},
    {"patient_id": "PAT-12345", "heart_rate": 80.0, "respiratory_rate": 18.0, "spo2": 98.0,
        "temperature": 36.5, "systolic_bp": 120.0, "diastolic_bp": 80.0, "oxygen_device": "nasal",
        "oxygen_flow": 2.0, "nurse_alert": False, "lactate": 1.1,
        "creatinine": 0.9, "crp": 5.0, "hemoglobin": 14.0, "sepsis_risk": 0.1},
    {"patient_id": "PAT-12345", "heart_rate": 80.0, "respiratory_rate": 18.0, "spo2": 98.0,
        "temperature": 36.5, "systolic_bp": 120.0, "diastolic_bp": 80.0, "oxygen_device": "nasal",
        "oxygen_flow": 2.0, "nurse_alert": False, "wbc_count": 7.5,
        "creatinine": 0.9, "crp": 5.0, "hemoglobin": 14.0, "sepsis_risk": 0.1},
    {"patient_id": "PAT-12345", "heart_rate": 80.0, "respiratory_rate": 18.0, "spo2": 98.0,
        "temperature": 36.5, "systolic_bp": 120.0, "diastolic_bp": 80.0, "oxygen_device": "nasal",
        "oxygen_flow": 2.0, "nurse_alert": False, "wbc_count": 7.5, "lactate": 1.1,
        "crp": 5.0, "hemoglobin": 14.0, "sepsis_risk": 0.1},
    {"patient_id": "PAT-12345", "heart_rate": 80.0, "respiratory_rate": 18.0, "spo2": 98.0,
        "temperature": 36.5, "systolic_bp": 120.0, "diastolic_bp": 80.0, "oxygen_device": "nasal",
        "oxygen_flow": 2.0, "nurse_alert": False, "wbc_count": 7.5, "lactate": 1.1,
        "creatinine": 0.9, "hemoglobin": 14.0, "sepsis_risk": 0.1},
    {"patient_id": "PAT-12345", "heart_rate": 80.0, "respiratory_rate": 18.0, "spo2": 98.0,
        "temperature": 36.5, "systolic_bp": 120.0, "diastolic_bp": 80.0, "oxygen_device": "nasal",
        "oxygen_flow": 2.0, "nurse_alert": False, "wbc_count": 7.5, "lactate": 1.1,
        "creatinine": 0.9, "crp": 5.0, "sepsis_risk": 0.1},
    {"patient_id": "PAT-12345", "heart_rate": 80.0, "respiratory_rate": 18.0, "spo2": 98.0,
        "temperature": 36.5, "systolic_bp": 120.0, "diastolic_bp": 80.0, "oxygen_device": "nasal",
        "oxygen_flow": 2.0, "nurse_alert": False, "wbc_count": 7.5, "lactate": 1.1,
        "creatinine": 0.9, "crp": 5.0, "hemoglobin": 14.0}
])
@patch("app.services.prediction.PredictionService.make_prediction")
def test_make_prediction_success(mock_make_prediction, payload):
    """Caso Positivo: Retorna la probabilidad y la alerta calculada."""
    mock_make_prediction.return_value = {
        "patient_id": "PAT-12345",
        "alert": True,
        "timestamp": "2026-08-08T12:00:00.000000+00:00",
        "history_updated": True
    }

    response = client.post("api/v1/prediction", json=payload)

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["alert"] is True
    assert data["history_updated"] is True

@pytest.mark.parametrize("invalid_payload", [
    {},
    {"heart_rate": 80.0, "respiratory_rate": 18.0, "spo2": 98.0,
        "temperature": 36.5, "systolic_bp": 120.0, "diastolic_bp": 80.0, "oxygen_device": "nasal",
        "oxygen_flow": 2.0, "nurse_alert": False, "wbc_count": 7.5, "lactate": 1.1,
        "creatinine": 0.9, "crp": 5.0, "hemoglobin": 14.0, "sepsis_risk": 0.1},
    {"patient_id": 80, "heart_rate": 80.0, "respiratory_rate": 18.0, "spo2": 98.0,
            "temperature": 36.5, "systolic_bp": 120.0, "diastolic_bp": 80.0, "oxygen_device": "nasal",
            "oxygen_flow": 2.0, "nurse_alert": False, "wbc_count": 7.5, "lactate": 1.1,
            "creatinine": 0.9, "crp": 5.0, "hemoglobin": 14.0, "sepsis_risk": 0.1},
    {"patient_id": "PAT-12345", "heart_rate": "ochenta", "respiratory_rate": 18.0, "spo2": 98.0,
            "temperature": 36.5, "systolic_bp": 120.0, "diastolic_bp": 80.0, "oxygen_device": "nasal",
            "oxygen_flow": 2.0, "nurse_alert": False, "wbc_count": 7.5, "lactate": 1.1,
            "creatinine": 0.9, "crp": 5.0, "hemoglobin": 14.0, "sepsis_risk": 0.1},
    {"patient_id": "PAT-12345", "heart_rate": -1.3, "respiratory_rate": 18.0, "spo2": 98.0,
            "temperature": 36.5, "systolic_bp": 120.0, "diastolic_bp": 80.0, "oxygen_device": "nasal",
            "oxygen_flow": 2.0, "nurse_alert": False, "wbc_count": 7.5, "lactate": 1.1,
            "creatinine": 0.9, "crp": 5.0, "hemoglobin": 14.0, "sepsis_risk": 0.1},
    {"patient_id": "PAT-12345", "heart_rate": 80.0, "respiratory_rate": "dieciocho", "spo2": 98.0,
            "temperature": 36.5, "systolic_bp": 120.0, "diastolic_bp": 80.0, "oxygen_device": "nasal",
            "oxygen_flow": 2.0, "nurse_alert": False, "wbc_count": 7.5, "lactate": 1.1,
            "creatinine": 0.9, "crp": 5.0, "hemoglobin": 14.0, "sepsis_risk": 0.1},
    {"patient_id": "PAT-12345", "heart_rate": 80.0, "respiratory_rate": -12.5, "spo2": 98.0,
            "temperature": 36.5, "systolic_bp": 120.0, "diastolic_bp": 80.0, "oxygen_device": "nasal",
            "oxygen_flow": 2.0, "nurse_alert": False, "wbc_count": 7.5, "lactate": 1.1,
            "creatinine": 0.9, "crp": 5.0, "hemoglobin": 14.0, "sepsis_risk": 0.1},
    {"patient_id": "PAT-12345", "heart_rate": 80.0, "respiratory_rate": 18.0, "spo2": "noventa y ocho",
            "temperature": 36.5, "systolic_bp": 120.0, "diastolic_bp": 80.0, "oxygen_device": "nasal",
            "oxygen_flow": 2.0, "nurse_alert": False, "wbc_count": 7.5, "lactate": 1.1,
            "creatinine": 0.9, "crp": 5.0, "hemoglobin": 14.0, "sepsis_risk": 0.1},
    {"patient_id": "PAT-12345", "heart_rate": 80.0, "respiratory_rate": 18.0, "spo2": -77.7,
            "temperature": 36.5, "systolic_bp": 120.0, "diastolic_bp": 80.0, "oxygen_device": "nasal",
            "oxygen_flow": 2.0, "nurse_alert": False, "wbc_count": 7.5, "lactate": 1.1,
            "creatinine": 0.9, "crp": 5.0, "hemoglobin": 14.0, "sepsis_risk": 0.1},
    {"patient_id": "PAT-12345", "heart_rate": 80.0, "respiratory_rate": 18.0, "spo2": 133.3,
            "temperature": 36.5, "systolic_bp": 120.0, "diastolic_bp": 80.0, "oxygen_device": "nasal",
            "oxygen_flow": 2.0, "nurse_alert": False, "wbc_count": 7.5, "lactate": 1.1,
            "creatinine": 0.9, "crp": 5.0, "hemoglobin": 14.0, "sepsis_risk": 0.1},
    {"patient_id": "PAT-12345", "heart_rate": 80.0, "respiratory_rate": 18.0, "spo2": 98.0,
            "temperature": "treinta y tres", "systolic_bp": 120.0, "diastolic_bp": 80.0,
            "oxygen_device": "nasal", "oxygen_flow": 2.0, "nurse_alert": False, "wbc_count": 7.5,
            "lactate": 1.1, "creatinine": 0.9, "crp": 5.0, "hemoglobin": 14.0, "sepsis_risk": 0.1},
    {"patient_id": "PAT-12345", "heart_rate": 80.0, "respiratory_rate": 18.0, "spo2": 98.0,
            "temperature": 36.5, "systolic_bp": "ciento quince", "diastolic_bp": 80.0,
            "oxygen_device": "nasal", "oxygen_flow": 2.0, "nurse_alert": False, "wbc_count": 7.5,
            "lactate": 1.1, "creatinine": 0.9, "crp": 5.0, "hemoglobin": 14.0, "sepsis_risk": 0.1},
    {"patient_id": "PAT-12345", "heart_rate": 80.0, "respiratory_rate": 18.0, "spo2": 98.0,
            "temperature": 36.5, "systolic_bp": -4.4, "diastolic_bp": 80.0,
            "oxygen_device": "nasal", "oxygen_flow": 2.0, "nurse_alert": False, "wbc_count": 7.5,
            "lactate": 1.1, "creatinine": 0.9, "crp": 5.0, "hemoglobin": 14.0, "sepsis_risk": 0.1},
    {"patient_id": "PAT-12345", "heart_rate": 80.0, "respiratory_rate": 18.0, "spo2": 98.0,
            "temperature": 36.5, "systolic_bp": 120.0, "diastolic_bp": "sesenta y nueve",
            "oxygen_device": "nasal", "oxygen_flow": 2.0, "nurse_alert": False, "wbc_count": 7.5,
            "lactate": 1.1, "creatinine": 0.9, "crp": 5.0, "hemoglobin": 14.0, "sepsis_risk": 0.1},
    {"patient_id": "PAT-12345", "heart_rate": 80.0, "respiratory_rate": 18.0, "spo2": 98.0,
            "temperature": 36.5, "systolic_bp": 120.0, "diastolic_bp": -8.9,
            "oxygen_device": "nasal", "oxygen_flow": 2.0, "nurse_alert": False, "wbc_count": 7.5,
            "lactate": 1.1, "creatinine": 0.9, "crp": 5.0, "hemoglobin": 14.0, "sepsis_risk": 0.1},
    {"patient_id": "PAT-12345", "heart_rate": 80.0, "respiratory_rate": 18.0, "spo2": 98.0,
            "temperature": 36.5, "systolic_bp": 120.0, "diastolic_bp": 80.0,
            "oxygen_device": "ninguno", "oxygen_flow": 2.0, "nurse_alert": False, "wbc_count": 7.5,
            "lactate": 1.1, "creatinine": 0.9, "crp": 5.0, "hemoglobin": 14.0, "sepsis_risk": 0.1},
    {"patient_id": "PAT-12345", "heart_rate": 80.0, "respiratory_rate": 18.0, "spo2": 98.0,
            "temperature": 36.5, "systolic_bp": 120.0, "diastolic_bp": 80.0, "oxygen_device": -15,
            "oxygen_flow": 2.0, "nurse_alert": False, "wbc_count": 7.5, "lactate": 1.1,
            "creatinine": 0.9, "crp": 5.0, "hemoglobin": 14.0, "sepsis_risk": 0.1},
    {"patient_id": "PAT-12345", "heart_rate": 80.0, "respiratory_rate": 18.0, "spo2": 98.0,
            "temperature": 36.5, "systolic_bp": 120.0, "diastolic_bp": 80.0, "oxygen_device": "nasal",
            "oxygen_flow": "tres", "nurse_alert": False, "wbc_count": 7.5, "lactate": 1.1,
            "creatinine": 0.9, "crp": 5.0, "hemoglobin": 14.0, "sepsis_risk": 0.1},
    {"patient_id": "PAT-12345", "heart_rate": 80.0, "respiratory_rate": 18.0, "spo2": 98.0,
            "temperature": 36.5, "systolic_bp": 120.0, "diastolic_bp": 80.0, "oxygen_device": "nasal",
            "oxygen_flow": -3.3, "nurse_alert": False, "wbc_count": 7.5, "lactate": 1.1,
            "creatinine": 0.9, "crp": 5.0, "hemoglobin": 14.0, "sepsis_risk": 0.1},
    {"patient_id": "PAT-12345", "heart_rate": 80.0, "respiratory_rate": 18.0, "spo2": 98.0,
            "temperature": 36.5, "systolic_bp": 120.0, "diastolic_bp": 80.0, "oxygen_device": "nasal",
            "oxygen_flow": 2.0, "nurse_alert": 99, "wbc_count": 7.5, "lactate": 1.1,
            "creatinine": 0.9, "crp": 5.0, "hemoglobin": 14.0, "sepsis_risk": 0.1},
    {"patient_id": "PAT-12345", "heart_rate": 80.0, "respiratory_rate": 18.0, "spo2": 98.0,
            "temperature": 36.5, "systolic_bp": 120.0, "diastolic_bp": 80.0, "oxygen_device": "nasal",
            "oxygen_flow": 2.0, "nurse_alert": False, "wbc_count": "cinco", "lactate": 1.1,
            "creatinine": 0.9, "crp": 5.0, "hemoglobin": 14.0, "sepsis_risk": 0.1},
    {"patient_id": "PAT-12345", "heart_rate": 80.0, "respiratory_rate": 18.0, "spo2": 98.0,
            "temperature": 36.5, "systolic_bp": 120.0, "diastolic_bp": 80.0, "oxygen_device": "nasal",
            "oxygen_flow": 2.0, "nurse_alert": False, "wbc_count": -5.5, "lactate": 1.1,
            "creatinine": 0.9, "crp": 5.0, "hemoglobin": 14.0, "sepsis_risk": 0.1},
    {"patient_id": "PAT-12345", "heart_rate": 80.0, "respiratory_rate": 18.0, "spo2": 98.0,
            "temperature": 36.5, "systolic_bp": 120.0, "diastolic_bp": 80.0, "oxygen_device": "nasal",
            "oxygen_flow": 2.0, "nurse_alert": False, "wbc_count": 7.5, "lactate": "uno con uno",
            "creatinine": 0.9, "crp": 5.0, "hemoglobin": 14.0, "sepsis_risk": 0.1},
    {"patient_id": "PAT-12345", "heart_rate": 80.0, "respiratory_rate": 18.0, "spo2": 98.0,
            "temperature": 36.5, "systolic_bp": 120.0, "diastolic_bp": 80.0, "oxygen_device": "nasal",
            "oxygen_flow": 2.0, "nurse_alert": False, "wbc_count": 7.5, "lactate": -1.4,
            "creatinine": 0.9, "crp": 5.0, "hemoglobin": 14.0, "sepsis_risk": 0.1},
    {"patient_id": "PAT-12345", "heart_rate": 80.0, "respiratory_rate": 18.0, "spo2": 98.0,
            "temperature": 36.5, "systolic_bp": 120.0, "diastolic_bp": 80.0, "oxygen_device": "nasal",
            "oxygen_flow": 2.0, "nurse_alert": False, "wbc_count": 7.5, "lactate": 1.1,
            "creatinine": "cero con nueve", "crp": 5.0, "hemoglobin": 14.0, "sepsis_risk": 0.1},
    {"patient_id": "PAT-12345", "heart_rate": 80.0, "respiratory_rate": 18.0, "spo2": 98.0,
            "temperature": 36.5, "systolic_bp": 120.0, "diastolic_bp": 80.0, "oxygen_device": "nasal",
            "oxygen_flow": 2.0, "nurse_alert": False, "wbc_count": 7.5, "lactate": 1.1,
            "creatinine": -0.9, "crp": 5.0, "hemoglobin": 14.0, "sepsis_risk": 0.1},
    {"patient_id": "PAT-12345", "heart_rate": 80.0, "respiratory_rate": 18.0, "spo2": 98.0,
            "temperature": 36.5, "systolic_bp": 120.0, "diastolic_bp": 80.0, "oxygen_device": "nasal",
            "oxygen_flow": 2.0, "nurse_alert": False, "wbc_count": 7.5, "lactate": 1.1,
            "creatinine": 0.9, "crp": "seis", "hemoglobin": 14.0, "sepsis_risk": 0.1},
    {"patient_id": "PAT-12345", "heart_rate": 80.0, "respiratory_rate": 18.0, "spo2": 98.0,
            "temperature": 36.5, "systolic_bp": 120.0, "diastolic_bp": 80.0, "oxygen_device": "nasal",
            "oxygen_flow": 2.0, "nurse_alert": False, "wbc_count": 7.5, "lactate": 1.1,
            "creatinine": 0.9, "crp": -6.6, "hemoglobin": 14.0, "sepsis_risk": 0.1},
    {"patient_id": "PAT-12345", "heart_rate": 80.0, "respiratory_rate": 18.0, "spo2": 98.0,
            "temperature": 36.5, "systolic_bp": 120.0, "diastolic_bp": 80.0, "oxygen_device": "nasal",
            "oxygen_flow": 2.0, "nurse_alert": False, "wbc_count": 7.5, "lactate": 1.1,
            "creatinine": 0.9, "crp": 5.0, "hemoglobin": "catorce", "sepsis_risk": 0.1},
    {"patient_id": "PAT-12345", "heart_rate": 80.0, "respiratory_rate": 18.0, "spo2": 98.0,
            "temperature": 36.5, "systolic_bp": 120.0, "diastolic_bp": 80.0, "oxygen_device": "nasal",
            "oxygen_flow": 2.0, "nurse_alert": False, "wbc_count": 7.5, "lactate": 1.1,
            "creatinine": 0.9, "crp": 5.0, "hemoglobin": -14.4, "sepsis_risk": 0.1},
    {"patient_id": "PAT-12345", "heart_rate": 80.0, "respiratory_rate": 18.0, "spo2": 98.0,
            "temperature": 36.5, "systolic_bp": 120.0, "diastolic_bp": 80.0, "oxygen_device": "nasal",
            "oxygen_flow": 2.0, "nurse_alert": False, "wbc_count": 7.5, "lactate": 1.1,
            "creatinine": 0.9, "crp": 5.0, "hemoglobin": 14.0, "sepsis_risk": "10%"},
    {"patient_id": "PAT-12345", "heart_rate": 80.0, "respiratory_rate": 18.0, "spo2": 98.0,
            "temperature": 36.5, "systolic_bp": 120.0, "diastolic_bp": 80.0, "oxygen_device": "nasal",
            "oxygen_flow": 2.0, "nurse_alert": False, "wbc_count": 7.5, "lactate": 1.1,
            "creatinine": 0.9, "crp": 5.0, "hemoglobin": 14.0, "sepsis_risk": -0.1},
    {"patient_id": "PAT-12345", "heart_rate": 80.0, "respiratory_rate": 18.0, "spo2": 98.0,
            "temperature": 36.5, "systolic_bp": 120.0, "diastolic_bp": 80.0, "oxygen_device": "nasal",
            "oxygen_flow": 2.0, "nurse_alert": False, "wbc_count": 7.5, "lactate": 1.1,
            "creatinine": 0.9, "crp": 5.0, "hemoglobin": 14.0, "sepsis_risk": 1.1}
])
def test_make_prediction_validation_errors(invalid_payload):
    response = client.post("api/v1/prediction", json=invalid_payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

@patch("app.services.prediction.PredictionService.make_prediction")
def test_make_prediction_patient_not_found(mock_make_prediction):
    mock_make_prediction.side_effect = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="No se encontró ningún paciente con el identificador 'PAC-00000000'."
    )

    payload = {
        "patient_id": "PAC-00000000",
        "heart_rate": 80.0,
        "respiratory_rate": 18.0,
        "spo2": 98.0,
        "temperature": 36.5,
        "systolic_bp": 120.0,
        "diastolic_bp": 80.0,
        "oxygen_device": "nasal",
        "oxygen_flow": 2.0,
        "nurse_alert": False,
        "wbc_count": 7.5
    }

    response = client.post("api/v1/prediction", json=payload)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "No se encontró ningún paciente con el identificador 'PAC-00000000'."

@pytest.mark.parametrize("payload", [
    {"outcome": True, "comments": "El paciente necesitó atención médica."},
    {"outcome": False}
])
@patch("app.services.prediction.PredictionService.give_prediction_feedback")
def test_give_prediction_feedback_success(mock_feedback, payload):
    mock_feedback.return_value = None

    response = client.put("api/v1/prediction/PAC-12345", json=payload)

    assert response.status_code == status.HTTP_204_NO_CONTENT

@pytest.mark.parametrize("invalid_payload", [
    {},
    {"comments": "El paciente necesitó atención médica."},
    {"outcome": "sí", "comments": "El paciente necesitó atención médica."},
    {"outcome": True, "comments": 12345}
])
@patch("app.services.prediction.PredictionService.give_prediction_feedback")
def test_give_prediction_feedback_validation_errors(mock_feedback, invalid_payload):
    response = client.put("api/v1/prediction/PAC-12345", json=invalid_payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

@patch("app.services.prediction.PredictionService.give_prediction_feedback")
def test_give_prediction_feedback_patient_not_found(mock_feedback):
    mock_feedback.side_effect = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="No se encontró ninguna predicción para el paciente 'PAC-00000000'."
    )

    payload = {
        "outcome": True,
        "comments": "El paciente necesitó atención médica."
    }

    response = client.put("api/v1/prediction/PAC-00000000", json=payload)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert  "No se encontró ninguna predicción para el paciente" in response.json()["detail"]