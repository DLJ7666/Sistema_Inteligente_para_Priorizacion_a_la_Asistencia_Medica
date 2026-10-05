from typing import Annotated
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.dependencies import get_current_user
from app.schemas.auth import SupabaseUser
from app.schemas.prediction import PredictionInput, PredictionOutput, PredictionFeedbackInput
from app.services.prediction import PredictionService

router = APIRouter()
def get_prediction_service(db: Annotated[Session, Depends(get_db)]) -> PredictionService:
    return PredictionService(db)

# /prediction
@router.post(
    "",
    response_model=PredictionOutput,
    status_code=status.HTTP_201_CREATED,
    summary="Realizar Predicción de deterioro de Paciente",
    description="Recibe los datos de entrada del paciente y realiza la predicción de riesgo de evento de gravedad en su salud, actualizando el historial del mismo."
)
def post_prediction(
    prediction_in: PredictionInput,
    service: Annotated[PredictionService, Depends(get_prediction_service)],
    current_user: Annotated[SupabaseUser, Depends(get_current_user)]
):
    return service.make_prediction(prediction_in)

# /prediction/{prediction_id}
@router.put(
    "/{patient_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Da feedback sobre la última predicción realizada para el paciente",
    description="Actualiza los datos de la predicción realizaca para el paciente con los datos proporcionados para poder actualizar el modelo."
)
async def give_prediction_feedback(
    patient_id: str,
    prediction_in: PredictionFeedbackInput,
    service: Annotated[PredictionService, Depends(get_prediction_service)],
    current_user: Annotated[SupabaseUser, Depends(get_current_user)]
):
    service.give_prediction_feedback(patient_id, prediction_in)