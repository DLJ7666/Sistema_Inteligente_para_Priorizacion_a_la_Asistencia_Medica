import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.patients import PatientModel, AdmissionDataModel, VitalSignsModel
from app.schemas.patients import (
    PatientId,
    PatientInput,
    PatientPut,
    PatientOutput,
    PatientData,
    AdmissionTypeEnum,
)


class PatientService:
    def __init__(self, db: Session):
        self.db = db

    def _to_patient_output(self, patient: PatientModel) -> PatientOutput:
        res = []
        if patient.admissions:
            for admission in patient.admissions:
                if admission.vital_signs:
                    for vs in admission.vital_signs:
                        res.append(self._to_patient_data(admission, vs))
    
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No se encontraron registros de admisión para el paciente."
            )
    
        res.sort(key=lambda x: x.timestamp, reverse=True)
    
        return res

    def _to_patient_data(self, admission: AdmissionDataModel, vs: VitalSignsModel) -> PatientData:
        patient_data = PatientData(
            mobility=admission.mobility,
            comorbidity=admission.comorbidity,
            admission_type=admission.admission_type,
            admission_time=admission.admission_time.isoformat(),
            
            heart_rate=getattr(vs, "heart_rate", None),
            respiratory_rate=getattr(vs, "respiratory_rate", None),
            spo2=getattr(vs, "spo2", None),
            temperature=getattr(vs, "temperature", None),
            systolic_bp=getattr(vs, "systolic_bp", None),
            diastolic_bp=getattr(vs, "diastolic_bp", None),
            oxygen_device=getattr(vs, "oxygen_device", None),
            oxygen_flow=getattr(vs, "oxygen_flow", None),
            nurse_alert=getattr(vs, "nurse_alert", None),
            wbc_count=getattr(vs, "wbc_count", None),
            lactate=getattr(vs, "lactate", None),
            creatinine=getattr(vs, "creatinine", None),
            crp=getattr(vs, "crp", None),
            hemoglobin=getattr(vs, "hemoglobin", None),
            sepsis_risk=getattr(vs, "sepsis_risk", None),
        )
        timestamp_str = getattr(vs, "timestamp")
        if not timestamp_str:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No se pudo determinar la marca de tiempo del registro."
            )
        alert_status = getattr(vs, "alert", None)

        return PatientOutput(
            timestamp=timestamp_str.isoformat(),
            alert=alert_status,
            data=patient_data
        )

    
    def create_patient(self, patient_in: PatientInput) -> PatientOutput:
        patient_id_uuid = uuid.uuid4().hex[:8].upper()
        patient_id = f"PAC-{patient_id_uuid}"
        
        new_patient = PatientModel(
            patient_id=patient_id,
            birth_date=patient_in.birth_date,
            gender=patient_in.gender
        )
    
        initial_admission = AdmissionDataModel(
            admission_data_id=f"ADM-{patient_id_uuid}-{uuid.uuid4().hex[:4].upper()}",
            mobility=patient_in.mobility,
            comorbidity=patient_in.comorbidity,
            admission_type=patient_in.admission_type,
            admission_time=datetime.now(timezone.utc),
            patient=new_patient
        )
    
        self.db.add(new_patient)
        self.db.add(initial_admission)
        self.db.commit()
        self.db.refresh(new_patient)

        return PatientId(patient_id=patient_id)

    def get_patient_history(self, patient_id: str) -> Optional[PatientOutput]:
        patient = self.db.query(PatientModel).filter(PatientModel.patient_id == patient_id).first()
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontró ningún paciente con el identificador '{patient_id}'."
            )
        return self._to_patient_output(patient)

    def create_patient_admission(self, patient_id: str, patient_in: PatientPut) -> None:
        admission_time = datetime.now(timezone.utc)
        patient = self.db.query(PatientModel).filter(PatientModel.patient_id == patient_id).first()
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontró ningún paciente con el identificador '{patient_id}'."
            )
    
        patient_id_uuid = patient_id.split('-')[1]
        new_admission = AdmissionDataModel(
            admission_data_id=f"ADM-{patient_id_uuid}-{uuid.uuid4().hex[:4].upper()}",
            **patient_in.model_dump(exclude_unset=True),
            admission_time=admission_time,
            patient=patient
        )
    
        self.db.add(new_admission)
        self.db.commit()
        self.db.refresh(patient)

    def discharge_patient(self, patient_id: str) -> None:
        patient = self.db.query(PatientModel).filter(PatientModel.patient_id == patient_id).first()
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontró ningún paciente con el identificador '{patient_id}'."
            )
    
        latest_admission = (
            self.db.query(AdmissionDataModel)
            .filter(AdmissionDataModel.patient_id == patient_id)
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
                    detail="El paciente ya ha sido dado de alta."
                )

        latest_admission.admission_type = AdmissionTypeEnum.DISCHARGED
        latest_admission.discharge_time = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(latest_admission)