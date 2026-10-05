from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.patients import OxygenDeviceEnum

class PredictionInput(BaseModel):
    patient_id: str = Field(..., description="Identificador del paciente")
    heart_rate: Optional[float] = Field(None, ge=0, description="Frecuencia cardíaca en pulsaciones por minuto")
    respiratory_rate: Optional[float] = Field(None, ge=0, description="Frecuencia respiratoria en respiraciones por minuto")
    spo2: Optional[float] = Field(None, ge=0, le=100, description="Saturación de oxígeno en porcentaje")
    temperature: Optional[float] = Field(None, description="Temperatura corporal")
    systolic_bp: Optional[float] = Field(None, ge=0, description="Presión arterial sistólica")
    diastolic_bp: Optional[float] = Field(None, ge=0, description="Presión arterial diastólica")
    oxygen_device: Optional[OxygenDeviceEnum] = Field(None, description="Dispositivo de oxígeno utilizado")
    oxygen_flow: Optional[float] = Field(None, ge=0, description="Flujo de oxígeno")
    nurse_alert: Optional[bool] = Field(None, description="Emergencia de enfermería necesaria")
    wbc_count: Optional[float] = Field(None, ge=0, description="Recuento de glóbulos blancos")
    lactate: Optional[float] = Field(None, ge=0, description="Lactato")
    creatinine: Optional[float] = Field(None, ge=0, description="Creatinina")
    crp: Optional[float] = Field(None, ge=0, description="Proteína C reactiva")
    hemoglobin: Optional[float] = Field(None, ge=0, description="Hemoglobina")
    sepsis_risk: Optional[float] = Field(None, ge=0, le=1, description="Riesgo de infección bacteriana")

class PredictionOutput(BaseModel):
    patient_id: str
    alert: bool
    timestamp: str
    history_updated: bool

    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)

class PredictionFeedbackInput(BaseModel):
    outcome: bool = Field(..., description="Resultado del paciente (True si hubo evento, False si no)")
    comments: Optional[str] = Field(None, description="Comentarios adicionales sobre la predicción")

    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)