from enum import Enum
from datetime import date
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


class GenderEnum(str, Enum):
    M = "M"
    F = "F"


class AdmissionTypeEnum(str, Enum):
    ED = "ED"
    ELECTIVE = "Elective"
    TRANSFER = "Transfer"
    DISCHARGED = "Discharged"


class OxygenDeviceEnum(str, Enum):
    NONE = "none"
    NASAL = "nasal"
    MASK = "mask"
    HFNC = "hfnc"
    NIV = "niv"


class PatientInput(BaseModel):
    birth_date: date = Field(..., description="Fecha de nacimiento del paciente")
    gender: GenderEnum = Field(..., description="Género del paciente")
    mobility: Optional[int] = Field(None, ge=0, le=4, description="Puntuación de movilidad")
    comorbidity: Optional[int] = Field(None, ge=0, le=8, description="Índice de comorbilidad")
    admission_type: Optional[AdmissionTypeEnum] = Field(None, description="Tipo de admisión hospitalaria")

    @field_validator("birth_date")
    @classmethod
    def validate_birth_date_not_in_future(cls, v: date) -> date:
        if v > date.today():
            raise ValueError("La fecha de nacimiento no puede ser una fecha futura.")
        return v


class PatientPut(BaseModel):
    mobility: Optional[int] = Field(None, ge=0, le=4, description="Puntuación de movilidad")
    comorbidity: Optional[int] = Field(None, ge=0, le=8, description="Índice de comorbilidad")
    admission_type: Optional[AdmissionTypeEnum] = Field(None, description="Tipo de admisión hospitalaria")


class PatientData(BaseModel):
    mobility: Optional[int] = None
    comorbidity: Optional[int] = None
    admission_type: Optional[AdmissionTypeEnum] = None
    admission_time: Optional[str] = None
    heart_rate: Optional[float] = None
    respiratory_rate: Optional[float] = None
    spo2: Optional[float] = None
    temperature: Optional[float] = None
    systolic_bp: Optional[float] = None
    diastolic_bp: Optional[float] = None
    oxygen_device: Optional[OxygenDeviceEnum] = None
    oxygen_flow: Optional[float] = None
    nurse_alert: Optional[bool] = None
    wbc_count: Optional[float] = None
    lactate: Optional[float] = None
    creatinine: Optional[float] = None
    crp: Optional[float] = None
    hemoglobin: Optional[float] = None
    sepsis_risk: Optional[float] = None

    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)


class PatientOutput(BaseModel):
    timestamp: str
    alert: bool
    data: PatientData

    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)

class PatientId(BaseModel):
    patient_id: str

    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)