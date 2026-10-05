from typing import Annotated
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.dependencies import get_current_user
from app.schemas.auth import SupabaseUser
from app.schemas.patients import (
    PatientId,
    PatientInput,
    PatientPut,
    PatientOutput
)
from app.services.patients import PatientService

router = APIRouter()
def get_patient_service(db: Annotated[Session, Depends(get_db)]) -> PatientService:
    return PatientService(db)

# /patients
@router.post(
    "",
    response_model=PatientId,
    status_code=status.HTTP_201_CREATED,
    summary="Dar de Alta a un Nuevo Paciente",
    description="Crea el registro del paciente con sus datos de entrada e instancia automáticamente su admisión inicial."
)
async def create_patient(
    patient_in: PatientInput,
    service: Annotated[PatientService, Depends(get_patient_service)],
    current_user: Annotated[SupabaseUser, Depends(get_current_user)]
):
    return service.create_patient(patient_in)


# /patients/{patient_id}
@router.get(
    "/{patient_id}",
    response_model=list[PatientOutput],
    status_code=status.HTTP_200_OK,
    summary="Obtener Histórico del Paciente",
    description="Recupera los el histórico de admisiones del paciente, incluyendo constantes vitales y métricas de laboratorio."
)
async def get_patient_history(
    patient_id: str,
    service: Annotated[PatientService, Depends(get_patient_service)],
    current_user: Annotated[SupabaseUser, Depends(get_current_user)]
):
    return service.get_patient_history(patient_id)


@router.put(
    "/{patient_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Crea nueva Admisión para el Paciente",
    description="Crea una nueva admisión para el paciente con los datos proporcionados."
)
async def create_patient_admission(
    patient_id: str,
    patient_in: PatientPut,
    service: Annotated[PatientService, Depends(get_patient_service)],
    current_user: Annotated[SupabaseUser, Depends(get_current_user)]
):
    service.create_patient_admission(patient_id, patient_in)

@router.patch(
    "/{patient_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Dar de Alta al Paciente",
    description="Da de alta a un paciente y cierra su registro de admisión actual."
)
async def discharge_patient(
    patient_id: str,
    service: Annotated[PatientService, Depends(get_patient_service)],
    current_user: Annotated[SupabaseUser, Depends(get_current_user)]
):
    service.discharge_patient(patient_id)