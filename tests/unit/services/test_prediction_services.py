import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone
from fastapi import HTTPException

from app.services.prediction import PredictionService
from app.schemas.patients import AdmissionTypeEnum
from app.schemas.prediction import PredictionInput, PredictionFeedbackInput
from app.models.patients import PatientModel, AdmissionDataModel
from app.models.prediction import PredictionModel


@pytest.fixture
def sample_prediction_input():
    return PredictionInput(
        patient_id="PAT-12345",
        heart_rate=85.0,
        respiratory_rate=18.0,
        spo2=97.0,
        temperature=37.0,
        systolic_bp=120.0,
        diastolic_bp=80.0,
        oxygen_flow=2.0,
        oxygen_device="nasal",
        nurse_alert=False,
        wbc_count=8.0,
        lactate=1.2,
        creatinine=0.9,
        crp=6.0,
        hemoglobin=13.5,
        sepsis_risk=0.15
    )

@pytest.fixture
def sample_prediction_feedback_input():
    return PredictionFeedbackInput(
        outcome=True,
        comments="Evolución favorable"
    )

@pytest.fixture
def mock_patient():
    patient = MagicMock(spec=PatientModel)
    patient.patient_id = "PAT-12345"
    patient.age = 65
    patient.gender = "M"
    return patient

@pytest.fixture
def mock_admission():
    admission = MagicMock(spec=AdmissionDataModel)
    admission.admission_data_id = "ADM-9999"
    admission.mobility = 1
    admission.comorbidity = 2
    admission.admission_type = "ED"
    admission.admission_time = datetime(2026, 8, 1, 10, 0, 0)
    admission.discharge_time = None
    return admission


@patch("app.services.prediction.VitalSignsModel")
@patch("app.services.prediction.PredictionModel")
@patch("app.services.prediction.ml_engine")
def test_make_prediction_success_alert_true(mock_ml_engine, _mock_prediction_model,
                                            _mock_vital_signs_model, sample_prediction_input,
                                            mock_patient, mock_admission):
    mock_ml_engine.predict.return_value = (0.85, 0.50)

    mock_db = MagicMock()
    def query_side_effect(model):
        q = MagicMock()
        if model == PatientModel:
            q.filter.return_value.first.return_value = mock_patient
        elif model == AdmissionDataModel:
            q.filter.return_value.order_by.return_value.first.return_value = mock_admission
        return q
    mock_db.query.side_effect = query_side_effect

    service = PredictionService(db=mock_db)
    result = service.make_prediction(sample_prediction_input)

    assert result.patient_id == "PAT-12345"
    assert result.alert is True
    assert result.history_updated is True
    mock_db.commit.assert_called_once()
    mock_db.add.assert_called()

@patch("app.services.prediction.VitalSignsModel")
@patch("app.services.prediction.PredictionModel")
@patch("app.services.prediction.ml_engine")
def test_make_prediction_success_alert_false(mock_ml_engine, _mock_prediction_model,
                                             _mock_vital_signs_model, sample_prediction_input,
                                             mock_patient, mock_admission):
    mock_ml_engine.predict.return_value = (0.20, 0.50)

    mock_db = MagicMock()
    def query_side_effect(model):
        q = MagicMock()
        if model == PatientModel:
            q.filter.return_value.first.return_value = mock_patient
        elif model == AdmissionDataModel:
            q.filter.return_value.order_by.return_value.first.return_value = mock_admission
        return q
    mock_db.query.side_effect = query_side_effect

    service = PredictionService(db=mock_db)
    result = service.make_prediction(sample_prediction_input)

    assert result.alert is False
    assert result.history_updated is True

def test_make_prediction_patient_not_found(sample_prediction_input):
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = None

    service = PredictionService(db=mock_db)

    with pytest.raises(HTTPException) as exc_info:
        service.make_prediction(sample_prediction_input)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Paciente no encontrado."

def test_make_prediction_no_admission_records(sample_prediction_input, mock_patient):
    mock_db = MagicMock()
    def query_side_effect(model):
        q = MagicMock()
        if model == PatientModel:
            q.filter.return_value.first.return_value = mock_patient
        elif model == AdmissionDataModel:
            q.filter.return_value.order_by.return_value.first.return_value = None
        return q
    mock_db.query.side_effect = query_side_effect

    service = PredictionService(db=mock_db)

    with pytest.raises(HTTPException) as exc_info:
        service.make_prediction(sample_prediction_input)

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "No se encontraron registros de admisión para el paciente."

def test_make_prediction_patient_discharged_by_date(sample_prediction_input, mock_patient, mock_admission):
    mock_admission.discharge_time = datetime(2026, 8, 5, 12, 0, 0)

    mock_db = MagicMock()
    def query_side_effect(model):
        q = MagicMock()
        if model == PatientModel:
            q.filter.return_value.first.return_value = mock_patient
        elif model == AdmissionDataModel:
            q.filter.return_value.order_by.return_value.first.return_value = mock_admission
        return q
    mock_db.query.side_effect = query_side_effect

    service = PredictionService(db=mock_db)

    with pytest.raises(HTTPException) as exc_info:
        service.make_prediction(sample_prediction_input)

    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == "No se puede realizar una predicción sobre un paciente dado de alta."

def test_make_prediction_patient_discharged_by_enum(sample_prediction_input, mock_patient, mock_admission):
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

    service = PredictionService(db=mock_db)

    with pytest.raises(HTTPException) as exc_info:
        service.make_prediction(sample_prediction_input)

    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == "No se puede realizar una predicción sobre un paciente dado de alta."

@patch("app.services.prediction.ml_engine")
def test_make_prediction_db_rollback_on_exception(mock_ml_engine, sample_prediction_input, mock_patient, mock_admission):
    mock_ml_engine.predict.return_value = (0.90, 0.50)

    mock_db = MagicMock()
    def query_side_effect(model):
        q = MagicMock()
        if model == PatientModel:
            q.filter.return_value.first.return_value = mock_patient
        elif model == AdmissionDataModel:
            q.filter.return_value.order_by.return_value.first.return_value = mock_admission
        return q
    mock_db.query.side_effect = query_side_effect
    
    # Simulamos fallo en la persistencia
    mock_db.commit.side_effect = Exception("Fallo de conexión en DB")

    service = PredictionService(db=mock_db)
    result = service.make_prediction(sample_prediction_input)

    assert result.history_updated is False
    assert result.alert is True
    mock_db.rollback.assert_called_once()

def test_give_prediction_feedback_success(sample_prediction_feedback_input):
    mock_prediction = MagicMock(spec=PredictionModel)
    
    mock_db = MagicMock()
    mock_db.query.return_value.join.return_value.join.return_value.filter.return_value.order_by.return_value.first.return_value = mock_prediction

    service = PredictionService(db=mock_db)
    service.give_prediction_feedback("PAT-12345", sample_prediction_feedback_input)

    assert mock_prediction.outcome == sample_prediction_feedback_input.outcome
    assert mock_prediction.comments == sample_prediction_feedback_input.comments
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(mock_prediction)

def test_give_prediction_feedback_not_found(sample_prediction_feedback_input):
    mock_db = MagicMock()
    mock_db.query.return_value.join.return_value.join.return_value.filter.return_value.order_by.return_value.first.return_value = None

    service = PredictionService(db=mock_db)

    with pytest.raises(HTTPException) as exc_info:
        service.give_prediction_feedback("PAT-12345", sample_prediction_feedback_input)

    assert exc_info.value.status_code == 404
    assert  "No se encontró ninguna predicción para el paciente" in exc_info.value.detail