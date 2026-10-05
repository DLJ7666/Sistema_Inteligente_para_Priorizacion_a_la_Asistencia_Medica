import joblib
import pandas as pd
from datetime import datetime
from pathlib import Path
from app.schemas.patients import PatientData

BASE_DIR = Path(__file__).resolve().parent.parent.parent
MODEL_PATH = BASE_DIR / "modelos" / "modelo_empaquetado.pkl"


class MLEngine:
    _instance = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MLEngine, cls).__new__(cls)
            cls._instance._load_model()
        return cls._instance

    def _load_model(self):
        try:
            content = joblib.load(MODEL_PATH)
        except FileNotFoundError:
            raise FileNotFoundError(
                f"No se encontró el archivo del modelo predictivo en: {MODEL_PATH}."
            )

        self._model = content.get("modelo")
        self._threshold = content.get("umbral_optimo")

        if self._model is None:
            raise ValueError(
                f"No se encontró ningún modelo predictivo en: {MODEL_PATH}."
            )

        if self._threshold is None:
            raise ValueError(
                f"No se encontró umbral optimo en el modelo predictivo del archivo: {MODEL_PATH}."
            )

    def predict(self, data: PatientData, timestamp: datetime, age: int, gender: str) -> tuple[float, float]:
        nurse_alert_value = 1 if (hasattr(data, "nurse_alert") and data.nurse_alert) else 0

        timestamp_timezoneless = timestamp.replace(tzinfo=None, microsecond=0)

        admission_time_timezoneless = datetime.fromisoformat(data.admission_time).replace(tzinfo=None, microsecond=0)

        hour_from_admission = (timestamp_timezoneless - admission_time_timezoneless).total_seconds() / 3600.0

        admission_type_ed, admission_type_elective, admission_type_transfer = 0, 0, 0
        if data.admission_type == "ED":
            admission_type_ed = 1
        elif data.admission_type == "Elective":
            admission_type_elective = 1
        elif data.admission_type == "Transfer":
            admission_type_transfer = 1

        oxygen_device_none, oxygen_device_nasal, oxygen_device_mask, oxygen_device_hfnc, oxygen_device_niv = 0, 0, 0, 0, 0
        if data.oxygen_device == "none":
            oxygen_device_none = 1
        elif data.oxygen_device == "nasal":
            oxygen_device_nasal = 1
        elif data.oxygen_device == "mask":
            oxygen_device_mask = 1
        elif data.oxygen_device == "hfnc":
            oxygen_device_hfnc = 1
        elif data.oxygen_device == "niv":
            oxygen_device_niv = 1

        feature_dict = {
            "hour_from_admission": hour_from_admission,
            "heart_rate": data.heart_rate,
            "respiratory_rate": data.respiratory_rate,
            "spo2_pct": data.spo2,
            "temperature_c": data.temperature,
            "systolic_bp": data.systolic_bp,
            "diastolic_bp": data.diastolic_bp,
            "oxygen_flow": data.oxygen_flow,
            "mobility_score": data.mobility,
            "nurse_alert": nurse_alert_value,
            "wbc_count": data.wbc_count,
            "lactate": data.lactate,
            "creatinine": data.creatinine,
            "crp_level": data.crp,
            "hemoglobin": data.hemoglobin,
            "sepsis_risk_score": data.sepsis_risk,
            "age": age,
            "comorbidity_index": data.comorbidity,
            "admission_type_ED": admission_type_ed,
            "admission_type_Elective": admission_type_elective,
            "admission_type_Transfer": admission_type_transfer,
            "gender_F": 1 if gender == "F" else 0,
            "gender_M": 1 if gender == "M" else 0,
            "oxygen_device_hfnc": oxygen_device_hfnc,
            "oxygen_device_mask": oxygen_device_mask,
            "oxygen_device_nasal": oxygen_device_nasal,
            "oxygen_device_niv": oxygen_device_niv,
            "oxygen_device_none": oxygen_device_none
        }

        df_features = pd.DataFrame([feature_dict])

        numeric_columns = [
            "heart_rate", "respiratory_rate", "spo2_pct", "temperature_c",
            "systolic_bp", "diastolic_bp", "oxygen_flow", "mobility_score",
            "wbc_count", "lactate", "creatinine", "crp_level",
            "hemoglobin", "sepsis_risk_score", "comorbidity_index", "age"
        ]

        for col in numeric_columns:
            if col in df_features.columns:
                df_features[col] = pd.to_numeric(df_features[col], errors="coerce").astype(float)

        if "nurse_alert" in df_features.columns:
            df_features["nurse_alert"] = df_features["nurse_alert"].map(
                lambda x: bool(x) if (pd.notna(x) and x is not None) else None
            )

        categorical_columns = ["oxygen_device", "gender", "admission_type"]
        for col in categorical_columns:
            if col in df_features.columns:
                df_features[col] = df_features[col].astype("category")

        probabilities = self._model.predict_proba(df_features)
        risk_probability = float(probabilities[0][1])

        return risk_probability, self._threshold


ml_engine = MLEngine()