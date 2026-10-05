import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone
from fastapi import HTTPException

from app.services.patients import PatientService
from app.schemas.patients import PatientInput, PatientPut, AdmissionTypeEnum
from app.models.patients import PatientModel, AdmissionDataModel, VitalSignsModel
import app.models.prediction  # noqa: F401


@pytest.fixture
def sample_patient_input():
    return PatientInput(
        birth_date="1980-05-15",
        gender="M",
        mobility=1,
        comorbidity=2,
        admission_type="ED"
    )

@pytest.fixture
def sample_patient_put():
    return PatientPut(
        mobility=2,
        comorbidity=1,
        admission_type="Elective"
    )

@pytest.fixture
def mock_patient_with_history():
    patient = MagicMock(spec=PatientModel)
    patient.patient_id = "PAC-12345678"

    vs1 = MagicMock(spec=VitalSignsModel)
    vs1.timestamp = datetime(2026, 8, 1, 10, 0, 0)
    vs1.heart_rate = 80.0
    vs1.alert = False
    vs1.oxygen_device = "nasal"

    vs2 = MagicMock(spec=VitalSignsModel)
    vs2.timestamp = datetime(2026, 8, 1, 14, 0, 0)
    vs2.heart_rate = 95.0
    vs2.alert = True
    vs2.oxygen_device = "none"


    admission = MagicMock(spec=AdmissionDataModel)
    admission.mobility = 1
    admission.comorbidity = 2
    admission.admission_type = "ED"
    admission.admission_time = datetime(2026, 8, 1, 9, 0, 0)

    admission.vital_signs = [vs1, vs2]

    patient.admissions = [admission]
    return patient


def test_create_patient_success(sample_patient_input):
    mock_db = MagicMock()
    service = PatientService(db=mock_db)

    result = service.create_patient(sample_patient_input)

    assert result.patient_id.startswith("PAC-")
    assert len(result.patient_id) == 12
    assert mock_db.add.call_count == 2
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()

def test_get_patient_history_success(mock_patient_with_history):
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = mock_patient_with_history

    service = PatientService(db=mock_db)
    history = service.get_patient_history("PAC-12345678")

    assert len(history) == 2
    # Comprobar orden descendente por timestamp
    assert history[0].timestamp == datetime(2026, 8, 1, 14, 0, 0).isoformat()
    assert history[1].timestamp == datetime(2026, 8, 1, 10, 0, 0).isoformat()
    assert history[0].alert is True

def test_get_patient_history_not_found():
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = None

    service = PatientService(db=mock_db)

    with pytest.raises(HTTPException) as exc_info:
        service.get_patient_history("PAC-00000000")

    assert exc_info.value.status_code == 404
    assert "No se encontró ningún paciente" in exc_info.value.detail

def test_get_patient_history_no_admissions():
    mock_patient = MagicMock(spec=PatientModel)
    mock_patient.admissions = []

    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = mock_patient

    service = PatientService(db=mock_db)

    with pytest.raises(HTTPException) as exc_info:
        service.get_patient_history("PAC-12345678")

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "No se encontraron registros de admisión para el paciente."

def test_get_patient_history_missing_timestamp(mock_patient_with_history):
    mock_patient_with_history.admissions[0].vital_signs[0].timestamp = None

    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = mock_patient_with_history

    service = PatientService(db=mock_db)

    with pytest.raises(HTTPException) as exc_info:
        service.get_patient_history("PAC-12345678")

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "No se pudo determinar la marca de tiempo del registro."

@patch("app.services.patients.AdmissionDataModel")
def test_create_patient_admission_success(_mock_admission_model, sample_patient_put):
    mock_patient = MagicMock(spec=PatientModel)
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = mock_patient

    service = PatientService(db=mock_db)
    service.create_patient_admission("PAC-12345678", sample_patient_put)

    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(mock_patient)

def test_create_patient_admission_not_found(sample_patient_put):
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = None

    service = PatientService(db=mock_db)

    with pytest.raises(HTTPException) as exc_info:
        service.create_patient_admission("PAC-00000000", sample_patient_put)

    assert exc_info.value.status_code == 404
    assert "No se encontró ningún paciente con el identificador " in exc_info.value.detail

@pytest.mark.parametrize("admission_type", [
    ("ED"),
    ("Elective"),
    ("Transfer")
])
def test_discharge_patient_success(admission_type):
    mock_patient = MagicMock(spec=PatientModel)
    mock_admission = MagicMock(spec=AdmissionDataModel)
    mock_admission.discharge_time = None
    mock_admission.admission_type = admission_type

    mock_db = MagicMock()
    def query_side_effect(model):
        q = MagicMock()
        if model == PatientModel:
            q.filter.return_value.first.return_value = mock_patient
        elif model == AdmissionDataModel:
            q.filter.return_value.order_by.return_value.first.return_value = mock_admission
        return q
    mock_db.query.side_effect = query_side_effect

    service = PatientService(db=mock_db)
    service.discharge_patient("PAC-12345678")

    assert mock_admission.admission_type == AdmissionTypeEnum.DISCHARGED
    assert mock_admission.discharge_time is not None
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(mock_admission)

def test_discharge_patient_not_found():
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = None

    service = PatientService(db=mock_db)

    with pytest.raises(HTTPException) as exc_info:
        service.discharge_patient("PAC-00000000")

    assert exc_info.value.status_code == 404
    assert "No se encontró ningún paciente con el identificador " in exc_info.value.detail

def test_discharge_patient_no_admissions():
    mock_patient = MagicMock(spec=PatientModel)
    mock_db = MagicMock()

    def query_side_effect(model):
        q = MagicMock()
        if model == PatientModel:
            q.filter.return_value.first.return_value = mock_patient
        elif model == AdmissionDataModel:
            q.filter.return_value.order_by.return_value.first.return_value = None
        return q
    mock_db.query.side_effect = query_side_effect

    service = PatientService(db=mock_db)

    with pytest.raises(HTTPException) as exc_info:
        service.discharge_patient("PAC-12345678")

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "No se encontraron registros de admisión para el paciente."

def test_discharge_patient_already_discharged_by_date():
    mock_patient = MagicMock(spec=PatientModel)
    mock_admission = MagicMock(spec=AdmissionDataModel)
    mock_admission.discharge_time = datetime(2026, 8, 2, 12, 0, 0)

    mock_db = MagicMock()
    def query_side_effect(model):
        q = MagicMock()
        if model == PatientModel:
            q.filter.return_value.first.return_value = mock_patient
        elif model == AdmissionDataModel:
            q.filter.return_value.order_by.return_value.first.return_value = mock_admission
        return q
    mock_db.query.side_effect = query_side_effect

    service = PatientService(db=mock_db)

    with pytest.raises(HTTPException) as exc_info:
        service.discharge_patient("PAC-12345678")

    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == "El paciente ya ha sido dado de alta."

def test_discharge_patient_already_discharged_by_enum():
    mock_patient = MagicMock(spec=PatientModel)
    mock_admission = MagicMock(spec=AdmissionDataModel)
    mock_admission.discharge_time = None
    mock_admission.admission_type = AdmissionTypeEnum.DISCHARGED

    mock_db = MagicMock()
    def query_side_effect(model):
        q = MagicMock()
        if model == PatientModel:
            q.filter.return_value.first.return_value = mock_patient
        elif model == AdmissionDataModel:
            q.filter.return_value.order_by.return_value.first.return_value = mock_admission
        return q
    mock_db.query.side_effect = query_side_effect

    service = PatientService(db=mock_db)

    with pytest.raises(HTTPException) as exc_info:
        service.discharge_patient("PAC-12345678")

    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == "El paciente ya ha sido dado de alta."