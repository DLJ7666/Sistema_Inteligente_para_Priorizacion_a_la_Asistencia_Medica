from datetime import date
from sqlalchemy import Column, String, Integer, Date, DateTime, Enum, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base
from app.schemas.patients import GenderEnum, AdmissionTypeEnum, OxygenDeviceEnum


class PatientModel(Base):
    __tablename__ = "patients"

    patient_id = Column(String, primary_key=True, index=True)
    birth_date = Column(Date, nullable=False)
    gender = Column(Enum(GenderEnum), nullable=True)

    admissions = relationship(
        "AdmissionDataModel",
        back_populates="patient",
        cascade="all, delete-orphan"
    )

    @property
    def age(self) -> int:

        today = date.today()
        age = today.year - self.birth_date.year
        if (today.month, today.day) < (self.birth_date.month, self.birth_date.day):
            age -= 1
        return age

class AdmissionDataModel(Base):
    __tablename__ = "admission_data"

    admission_data_id = Column(String, primary_key=True, index=True)
    mobility = Column(Integer, nullable=True)
    comorbidity = Column(Integer, nullable=True)
    admission_type = Column(Enum(AdmissionTypeEnum), nullable=True)
    admission_time = Column(DateTime, nullable=False)
    discharge_time = Column(DateTime, nullable=True)

    patient_id = Column(
        String,
        ForeignKey("patients.patient_id", ondelete="CASCADE"),
        nullable=False
    )
    patient = relationship("PatientModel", back_populates="admissions")

    vital_signs = relationship(
        "VitalSignsModel",
        back_populates="admission_data",
        cascade="all, delete-orphan"
    )


class VitalSignsModel(Base):
    __tablename__ = "vital_signs"

    vital_signs_id = Column(String, primary_key=True, index=True)
    heart_rate = Column(Float, nullable=True)
    respiratory_rate = Column(Float, nullable=True)
    spo2 = Column(Float, nullable=True)
    temperature = Column(Float, nullable=True)
    systolic_bp = Column(Float, nullable=True)
    diastolic_bp = Column(Float, nullable=True)
    oxygen_device = Column(Enum(OxygenDeviceEnum), nullable=True)
    oxygen_flow = Column(Float, nullable=True)
    nurse_alert = Column(Boolean, nullable=True)
    wbc_count = Column(Float, nullable=True)
    lactate = Column(Float, nullable=True)
    creatinine = Column(Float, nullable=True)
    crp = Column(Float, nullable=True)
    hemoglobin = Column(Float, nullable=True)
    sepsis_risk = Column(Float, nullable=True)
    timestamp = Column(DateTime, nullable=False)
    alert = Column(Boolean, nullable=True)

    admission_data_id = Column(
        String,
        ForeignKey("admission_data.admission_data_id", ondelete="CASCADE"),
        nullable=False
    )
    admission_data = relationship("AdmissionDataModel", back_populates="vital_signs")
    
    predictions = relationship(
        "PredictionModel",
        back_populates="vital_signs",
        cascade="all, delete-orphan"
    )