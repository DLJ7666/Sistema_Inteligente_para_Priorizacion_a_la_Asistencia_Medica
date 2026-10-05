import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from fastapi import HTTPException, status

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
    {"birth_date": "1980-05-15", "gender": "M", "mobility": 1, "comorbidity": 3, "admission_type": "ED"},
    {"birth_date": "1980-02-29", "gender": "M", "mobility": 1, "comorbidity": 3, "admission_type": "ED"},
    {"birth_date": "1980-05-15", "gender": "M", "mobility": 0, "comorbidity": 3, "admission_type": "ED"},
    {"birth_date": "1980-05-15", "gender": "M", "mobility": 4, "comorbidity": 3, "admission_type": "ED"},
    {"birth_date": "1980-05-15", "gender": "M", "mobility": 1, "comorbidity": 0, "admission_type": "ED"},
    {"birth_date": "1980-05-15", "gender": "M", "mobility": 1, "comorbidity": 8, "admission_type": "ED"},
    {"birth_date": "1980-05-15", "gender": "M"},
    {"birth_date": "1980-05-15", "gender": "M", "mobility": 1},
    {"birth_date": "1980-05-15", "gender": "M", "comorbidity": 3},
    {"birth_date": "1980-05-15", "gender": "M", "admission_type": "ED"},
    {"birth_date": "1980-05-15", "gender": "M", "mobility": 1, "comorbidity": 3},
    {"birth_date": "1980-05-15", "gender": "M", "mobility": 1, "admission_type": "ED"},
    {"birth_date": "1980-05-15", "gender": "M", "comorbidity": 3, "admission_type": "ED"}
])
@patch("app.services.patients.PatientService.create_patient")
def test_create_patient_success(mock_create, payload):
    mock_create.return_value = {"patient_id": "PAC-12345678"}

    response = client.post("api/v1/patients/", json=payload)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["patient_id"] == "PAC-12345678"

@pytest.mark.parametrize("invalid_payload", [
    {"birth_date": "15/05/1980", "gender": "F", "mobility": 1, "comorbidity": 3, "admission_type": "ED"},
    {"birth_date": "1980-13-15", "gender": "F", "mobility": 1, "comorbidity": 3, "admission_type": "ED"},
    {"birth_date": "1980-05-32", "gender": "F", "mobility": 1, "comorbidity": 3, "admission_type": "ED"},
    {"birth_date": "1980-04-31", "gender": "F", "mobility": 1, "comorbidity": 3, "admission_type": "ED"},
    {"birth_date": "1981-02-29", "gender": "F", "mobility": 1, "comorbidity": 3, "admission_type": "ED"},
    {"birth_date": "9999-12-31", "gender": "F", "mobility": 1, "comorbidity": 3, "admission_type": "ED"},
    {"birth_date": "1980-05-15", "gender": "INVALID", "mobility": 1, "comorbidity": 3, "admission_type": "ED"},
    {"birth_date": "1980-05-15", "gender": "F", "mobility": 1, "comorbidity": 3, "admission_type": "URGENCIA_ICU"},
    {"birth_date": "1980-05-15", "gender": "F", "mobility": -1, "comorbidity": 3, "admission_type": "ED"},
    {"birth_date": "1980-05-15", "gender": "F", "mobility": 5, "comorbidity": 3, "admission_type": "ED"},
    {"birth_date": "1980-05-15", "gender": "F", "mobility": 1, "comorbidity": -1, "admission_type": "ED"},
    {"birth_date": "1980-05-15", "gender": "F", "mobility": 1, "comorbidity": 9, "admission_type": "ED"},
    {},
    {"birth_date": "1980-05-15", "gender": "F", "mobility": 1, "comorbidity": 3, "admission_type": 40},
    {"birth_date": "1980-05-15", "gender": "F", "mobility": 1, "comorbidity": "tres", "admission_type":"ED"},
    {"birth_date": "1980-05-15", "gender": "F", "mobility": "uno", "comorbidity": 3, "admission_type": "ED"},
    {"birth_date": "1980-05-15", "gender": 33, "mobility": 1, "comorbidity": 3, "admission_type": "ED"},
    {"birth_date": 1992, "gender": "F", "mobility": 1, "comorbidity": 3, "admission_type": "ED"},
])
def test_create_patient_invalid_schema(invalid_payload):
    response = client.post("api/v1/patients/", json=invalid_payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

@patch("app.services.patients.PatientService.get_patient_history")
def test_get_patient_history_success(mock_get_history):
    mock_get_history.return_value = [
        {
            "timestamp": "2026-08-08T10:00:00.000000",
            "alert": False,
            "data": {
                "mobility": 1,
                "comorbidity": 2,
                "admission_type": "ED",
                "admission_time": "2026-08-01T10:00:00",
                "heart_rate": 80.0,
                "respiratory_rate": 18.0,
                "spo2": 98.0,
                "temperature": 36.5,
                "systolic_bp": 120.0,
                "diastolic_bp": 80.0,
                "oxygen_flow": 2.0,
                "oxygen_device": "nasal",
                "nurse_alert": False,
                "wbc_count": 7.5,
                "lactate": 1.1,
                "creatinine": 0.9,
                "crp": 5.0,
                "hemoglobin": 14.0,
                "sepsis_risk": 0.1
            }
        }
    ]

    response = client.get("api/v1/patients/PAC-12345678")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["alert"] is False

@patch("app.services.patients.PatientService.get_patient_history")
def test_get_patient_history_not_found(mock_get_history):
    mock_get_history.side_effect = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="No se encontró ningún paciente"
    )

    response = client.get("api/v1/patients/PAC-00000000")

    assert response.status_code == status.HTTP_404_NOT_FOUND

@patch("app.services.patients.PatientService.get_patient_history")
def test_get_patient_history_no_admissions(mock_get_history):
    mock_get_history.side_effect = HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="No se encontraron registros de admisión para el paciente."
    )

    response = client.get("api/v1/patients/PAC-12345678")

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.json()["detail"] == "No se encontraron registros de admisión para el paciente."

@patch("app.services.patients.PatientService.get_patient_history")
def test_get_patient_history_missing_timestamp(mock_get_history):
    mock_get_history.side_effect = HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="No se pudo determinar la marca de tiempo del registro."
    )

    response = client.get("api/v1/patients/PAC-12345678")

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.json()["detail"] == "No se pudo determinar la marca de tiempo del registro."

@pytest.mark.parametrize("payload", [
    {"mobility": 2, "comorbidity": 3, "admission_type": "Elective"},
    {"mobility": 0, "comorbidity": 3, "admission_type": "Transfer"},
    {"mobility": 4, "comorbidity": 3, "admission_type": "ED"},
    {"mobility": 2, "comorbidity": 0, "admission_type": "Elective"},
    {"mobility": 2, "comorbidity": 8, "admission_type": "Elective"},
    {},
    {"mobility": 2,},
    {"comorbidity": 3,},
    {"admission_type": "Elective"},
    {"mobility": 2, "comorbidity": 3},
    {"mobility": 2, "admission_type": "Elective"},
    {"comorbidity": 3, "admission_type": "Elective"},
])
@patch("app.services.patients.PatientService.create_patient_admission")
def test_create_patient_admission_success(mock_create_admission, payload):
    mock_create_admission.return_value = None

    response = client.put("api/v1/patients/PAC-12345678", json=payload)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    mock_create_admission.assert_called_once()

@patch("app.services.patients.PatientService.create_patient_admission")
def test_create_patient_admission_not_found(mock_create_admission):
        mock_create_admission.side_effect = HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró ningún paciente con el identificador 'PAC-00000000'."
        )

        payload = {"mobility": 2, "comorbidity": 3, "admission_type": "Elective"}
        response = client.put("api/v1/patients/PAC-00000000", json=payload)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "No se encontró ningún paciente con el identificador" in response.json()["detail"]

@pytest.mark.parametrize("invalid_payload", [
    {"mobility": -1, "comorbidity": 3, "admission_type": "Elective"},
    {"mobility": 5, "comorbidity": 3, "admission_type": "Elective"},
    {"mobility": 2, "comorbidity": -1, "admission_type": "Elective"},
    {"mobility": 2, "comorbidity": 9, "admission_type": "Elective"},
    {"mobility": 2, "comorbidity": 3, "admission_type": "INVALID_TYPE"},
    {"mobility": 2, "comorbidity": 3, "admission_type": 40},
    {"mobility": 2, "comorbidity": "tres", "admission_type":"Elective"},
    {"mobility": "dos", "comorbidity": 3, "admission_type": "Elective"}
])
def test_create_patient_admission_invalid_schema(invalid_payload):
    response = client.put("api/v1/patients/PAC-12345678", json=invalid_payload)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

@patch("app.services.patients.PatientService.discharge_patient")
def test_discharge_patient_success(mock_discharge):
    mock_discharge.return_value = None

    response = client.patch("api/v1/patients/PAC-12345678")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    mock_discharge.assert_called_once_with("PAC-12345678")

@patch("app.services.patients.PatientService.discharge_patient")
def test_discharge_patient_conflict(mock_discharge):
    mock_discharge.side_effect = HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="El paciente ya ha sido dado de alta."
    )

    response = client.patch("api/v1/patients/PAC-12345678")

    assert response.status_code == status.HTTP_409_CONFLICT

@patch("app.services.patients.PatientService.discharge_patient")
def test_discharge_patient_not_found(mock_discharge):
    mock_discharge.side_effect = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="No se encontró ningún paciente con el identificador 'PAC-00000000'."
    )

    response = client.patch("api/v1/patients/PAC-00000000")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "No se encontró ningún paciente con el identificador" in response.json()["detail"]

@patch("app.services.patients.PatientService.discharge_patient")
def test_discharge_patient_no_admissions(mock_discharge):
    mock_discharge.side_effect = HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="No se encontraron registros de admisión para el paciente."
    )

    response = client.patch("api/v1/patients/PAC-12345678")

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.json()["detail"] == "No se encontraron registros de admisión para el paciente."