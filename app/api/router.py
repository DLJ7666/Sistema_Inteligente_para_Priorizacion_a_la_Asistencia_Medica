from fastapi import APIRouter
from app.api.endpoints import auth, patients, prediction

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Autenticación"])
api_router.include_router(patients.router, prefix="/patients", tags=["Histórico"])
api_router.include_router(prediction.router, prefix="/prediction", tags=["Predicción"])

@api_router.get("/health", tags=["Health Check"])
async def health_check():
    return {"status": "ok", "message": "SIPAM API funcionando correctamente"}