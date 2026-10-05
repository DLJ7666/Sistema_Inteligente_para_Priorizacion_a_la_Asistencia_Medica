import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from app.models.patients import PatientModel, AdmissionDataModel, VitalSignsModel
from app.models.prediction import PredictionModel
from app.schemas.patients import PatientData, AdmissionTypeEnum
from app.schemas.prediction import PredictionInput, PredictionOutput, PredictionFeedbackInput
from app.services.ml_engine import ml_engine

class PredictionService:
    def __init__(self, db: Session):
        self.db = db
        self.ml_engine = ml_engine

    def make_prediction(self, data: PredictionInput) -> Optional[PredictionOutput]:
        patient = self.db.query(PatientModel).filter(PatientModel.patient_id == data.patient_id).first()
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Paciente no encontrado."
            )

        latest_admission = (
                    self.db.query(AdmissionDataModel)
                    .filter(AdmissionDataModel.patient_id == data.patient_id)
                    .order_by(AdmissionDataModel.admission_time.desc())
                    .first()
                )

        if not latest_admission:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="No se encontraron registros de admisión para el paciente."
                    )

        if latest_admission.discharge_time is not None or \
            latest_admission.admission_type == AdmissionTypeEnum.DISCHARGED:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="No se puede realizar una predicción sobre un paciente dado de alta."
                )

        patient_data = PatientData(
            mobility=latest_admission.mobility,
            comorbidity=latest_admission.comorbidity,
            admission_type=latest_admission.admission_type,
            admission_time=latest_admission.admission_time.isoformat(),
            heart_rate=data.heart_rate,
            respiratory_rate=data.respiratory_rate,
            spo2=data.spo2,
            temperature=data.temperature,
            systolic_bp=data.systolic_bp,
            diastolic_bp=data.diastolic_bp,
            oxygen_flow=data.oxygen_flow,
            oxygen_device=data.oxygen_device,
            nurse_alert=data.nurse_alert,
            wbc_count=data.wbc_count,
            lactate=data.lactate,
            creatinine=data.creatinine,
            crp=data.crp,
            hemoglobin=data.hemoglobin,
            sepsis_risk=data.sepsis_risk
        )

        timestamp = datetime.now(timezone.utc)

        prediction, threshold = self.ml_engine.predict(patient_data, timestamp, patient.age, patient.gender)

        admission_uuid = latest_admission.admission_data_id.replace("ADM", "")
        vital_signs_id = f"VS{admission_uuid}-{uuid.uuid4().hex[:4]}".upper()

        try:
            vital_signs = VitalSignsModel(
                vital_signs_id=vital_signs_id,
                heart_rate=data.heart_rate,
                respiratory_rate=data.respiratory_rate,
                spo2=data.spo2,
                temperature=data.temperature,
                systolic_bp=data.systolic_bp,
                diastolic_bp=data.diastolic_bp,
                oxygen_device = data.oxygen_device,
                oxygen_flow = data.oxygen_flow,
                nurse_alert = data.nurse_alert,
                wbc_count = data.wbc_count,
                lactate = data.lactate,
                creatinine = data.creatinine,
                crp = data.crp,
                hemoglobin = data.hemoglobin,
                sepsis_risk = data.sepsis_risk,
                timestamp = timestamp,
                alert = prediction >= threshold,
                admission_data=latest_admission
            )

            prediction_record = PredictionModel(
                prediction_id=f"PR{vital_signs_id.replace('VS', '')}".upper(),
                vital_signs=vital_signs,
                prediction=prediction,
                threshold=threshold
            )

            self.db.add(vital_signs)
            self.db.add(prediction_record)
            self.db.commit()
            self.db.refresh(latest_admission)

            return PredictionOutput(
                patient_id=data.patient_id,
                alert=prediction >= threshold,
                timestamp=timestamp.isoformat(),
                history_updated=True
            )

        except Exception as e:
            self.db.rollback()
            print(f"Error al guardar en la base de datos: {str(e)}")
            return PredictionOutput(
                patient_id=data.patient_id,
                alert=prediction >= threshold,
                timestamp=timestamp.isoformat(),
                history_updated=False
            )

    def give_prediction_feedback(self, patient_id: str, data: PredictionFeedbackInput) -> None:
        latest_prediction = (
            self.db.query(PredictionModel)
            .join(PredictionModel.vital_signs)
            .join(VitalSignsModel.admission_data)
            .filter(AdmissionDataModel.patient_id == patient_id)
            .order_by(VitalSignsModel.timestamp.desc())
            .first()
        )

        if not latest_prediction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontró ninguna predicción para el paciente {patient_id}."
            )

        latest_prediction.outcome = data.outcome
        latest_prediction.comments = data.comments
        self.db.commit()
        self.db.refresh(latest_prediction)