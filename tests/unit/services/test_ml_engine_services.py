import pytest
import pandas as pd
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone
from app.schemas.patients import PatientData
from app.services.ml_engine import MLEngine

MODEL_PATH = "test/path/a/modelo_empaquetado.pkl"

@pytest.fixture
def sample_patient_data():
    return PatientData(
        mobility=1,
        comorbidity=2,
        admission_type="ED",
        admission_time="2026-08-01T10:00:00",
        heart_rate=80.0,
        respiratory_rate=18.0,
        spo2=98.0,
        temperature=36.5,
        systolic_bp=120.0,
        diastolic_bp=80.0,
        oxygen_device="nasal",
        oxygen_flow=2.0,
        nurse_alert=False,
        wbc_count=7.5,
        lactate=1.1,
        creatinine=0.9,
        crp=5.0,
        hemoglobin=14.0,
        sepsis_risk=0.1
    )

@pytest.fixture(autouse=True)
def mock_environment(monkeypatch):
    monkeypatch.setattr("app.services.ml_engine.MODEL_PATH", MODEL_PATH)
    
    MLEngine._instance = None
    
    yield
    
    MLEngine._instance = None

@pytest.fixture
def mock_ml_engine():
    with patch("joblib.load") as mock_joblib:
        mock_model = MagicMock()
        mock_model.predict_proba.return_value = [[0.2, 0.8]]
        
        mock_joblib.return_value = {
            "modelo": mock_model,
            "umbral_optimo": 0.50
        }
        
        engine = MLEngine()
        yield engine, mock_model


@patch("app.services.ml_engine.joblib.load")
def test_ml_engine_init_success(mock_joblib):
    mock_model = MagicMock()
    mock_joblib.return_value = {
        "modelo": mock_model,
        "umbral_optimo": 0.50
    }

    engine = MLEngine()

    assert engine._model == mock_model
    assert engine._threshold == 0.50
    mock_joblib.assert_called_once_with(MODEL_PATH)

def test_ml_engine_init_no_file():
    with patch("app.services.ml_engine.joblib.load", side_effect=FileNotFoundError):
        with pytest.raises(FileNotFoundError) as exc_info:
            MLEngine()

    assert str(exc_info.value) == f"No se encontró el archivo del modelo predictivo en: {MODEL_PATH}."

@patch("app.services.ml_engine.joblib.load")
def test_ml_engine_predict_model_not_loaded(mock_joblib):

    mock_joblib.return_value = {
        "modelo": None,
        "umbral_optimo": 0.5
    }

    with pytest.raises(ValueError) as exc_info:
        MLEngine()

    assert str(exc_info.value) == f"No se encontró ningún modelo predictivo en: {MODEL_PATH}."

@patch("app.services.ml_engine.joblib.load")
def test_ml_engine_init_threshold_not_loaded(mock_joblib):
    mock_joblib.return_value = {
        "modelo": MagicMock(),
        "umbral_optimo": None
    }

    with pytest.raises(ValueError) as exc_info:
        MLEngine()

    assert str(exc_info.value) == \
    f"No se encontró umbral optimo en el modelo predictivo del archivo: {MODEL_PATH}."

@patch("app.services.ml_engine.joblib.load")
def test_predict_success(_mock_joblib, sample_patient_data):
    mock_model = MagicMock()
    mock_model.predict_proba.return_value = [[0.2, 0.8]]

    engine = MLEngine()
    engine._model = mock_model
    engine._threshold = 0.5

    now = datetime(2026, 8, 1, 14, 23, 0, tzinfo=timezone.utc)
    risk_prob, threshold = engine.predict(sample_patient_data, timestamp=now, age=65, gender="M")

    assert risk_prob == 0.8
    assert threshold == 0.5
    mock_model.predict_proba.assert_called_once()

    df_passed: pd.DataFrame = mock_model.predict_proba.call_args[0][0]
    assert pytest.approx(df_passed["hour_from_admission"].iloc[0], 0.0001) == 4.3833

@patch("app.services.ml_engine.joblib.load")
@pytest.mark.parametrize("gender_in, expected_f, expected_m", [
    ("F", 1, 0),
    ("M", 0, 1)
])
def test_predict_gender_encoding(_mock_joblib, sample_patient_data, gender_in, expected_f, expected_m):
    engine = MLEngine()
    mock_model = MagicMock()
    mock_model.predict_proba.return_value = [[0.3, 0.7]]
    engine._model = mock_model
    engine._threshold = 0.5

    engine.predict(sample_patient_data, datetime.now(timezone.utc), age=40, gender=gender_in)

    df_passed: pd.DataFrame = mock_model.predict_proba.call_args[0][0]
    assert df_passed["gender_F"].iloc[0] == expected_f
    assert df_passed["gender_M"].iloc[0] == expected_m

@patch("app.services.ml_engine.joblib.load")
@pytest.mark.parametrize("nurse_input, expected_output", [
    (True, 1),
    (False, 0),
    (None, 0),
])
def test_predict_nurse_alert_transformation(_mock_joblib, sample_patient_data, nurse_input,
                                            expected_output):
    engine = MLEngine()
    mock_model = MagicMock()
    mock_model.predict_proba.return_value = [[0.5, 0.5]]
    engine._model = mock_model
    engine._threshold = 0.5

    sample_patient_data.nurse_alert = nurse_input
    engine.predict(sample_patient_data, datetime.now(timezone.utc), age=30, gender="M")

    df_passed: pd.DataFrame = mock_model.predict_proba.call_args[0][0]
    assert df_passed["nurse_alert"].iloc[0] == expected_output

@patch("app.services.ml_engine.joblib.load")
@pytest.mark.parametrize("admission_type, expected_ed, expected_elective, expected_transfer", [
    ("ED", 1, 0, 0),
    ("Elective", 0, 1, 0),
    ("Transfer", 0, 0, 1),
    (None, 0, 0, 0),
])
def test_predict_admission_type_encoding(_mock_joblib, sample_patient_data, admission_type,
                                         expected_ed, expected_elective, expected_transfer):
    engine = MLEngine()
    mock_model = MagicMock()
    mock_model.predict_proba.return_value = [[0.4, 0.6]]
    engine._model = mock_model
    engine._threshold = 0.5

    sample_patient_data.admission_type = admission_type
    engine.predict(sample_patient_data, datetime.now(timezone.utc), age=50, gender="F")

    df_passed: pd.DataFrame = mock_model.predict_proba.call_args[0][0]
    assert df_passed["admission_type_ED"].iloc[0] == expected_ed
    assert df_passed["admission_type_Elective"].iloc[0] == expected_elective
    assert df_passed["admission_type_Transfer"].iloc[0] == expected_transfer

@patch("app.services.ml_engine.joblib.load")
@pytest.mark.parametrize("oxygen_device, expected_none, expected_nasal, expected_mask, expected_hfnc, expected_niv", [
    ("none", 1, 0, 0, 0, 0),
    ("nasal", 0, 1, 0, 0, 0),
    ("mask", 0, 0, 1, 0, 0),
    ("hfnc", 0, 0, 0, 1, 0),
    ("niv", 0, 0, 0, 0, 1),
    (None, 0, 0, 0, 0, 0),
])
def test_predict_oxygen_device_encoding(_mock_joblib, sample_patient_data, oxygen_device,
                                        expected_none, expected_nasal, expected_mask, expected_hfnc,
                                        expected_niv):
    engine = MLEngine()
    mock_model = MagicMock()
    mock_model.predict_proba.return_value = [[0.6, 0.4]]
    engine._model = mock_model
    engine._threshold = 0.5

    sample_patient_data.oxygen_device = oxygen_device
    engine.predict(sample_patient_data, datetime.now(timezone.utc), age=60, gender="M")

    df_passed: pd.DataFrame = mock_model.predict_proba.call_args[0][0]
    assert df_passed["oxygen_device_none"].iloc[0] == expected_none
    assert df_passed["oxygen_device_nasal"].iloc[0] == expected_nasal
    assert df_passed["oxygen_device_mask"].iloc[0] == expected_mask
    assert df_passed["oxygen_device_hfnc"].iloc[0] == expected_hfnc
    assert df_passed["oxygen_device_niv"].iloc[0] == expected_niv