import os
import sys
import uuid
import subprocess
import shutil
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.db.session import SessionLocal
from app.models.patients import PatientModel, AdmissionDataModel, VitalSignsModel
from app.models.prediction import PredictionModel
from app.schemas.patients import GenderEnum, AdmissionTypeEnum
sys.path.append(str(BASE_DIR))


class TestsEndToEnd:

    def __init__(self, collection_path: str):
        self.collection_path = collection_path

    def reset_and_seed_db(self) -> None:
        db = SessionLocal()
        
        try:
            db.query(PredictionModel).delete()
            db.query(VitalSignsModel).delete()
            db.query(AdmissionDataModel).delete()
            db.query(PatientModel).delete()
            db.commit()

            now = datetime.now(timezone.utc)

            patient1 = PatientModel(
                patient_id="PAC-12345678",
                birth_date=date(1990, 5, 15),
                gender=GenderEnum.M
            )
            admission1 = AdmissionDataModel(
                admission_data_id=f"ADM-12345678-{uuid.uuid4().hex[:4].upper()}",
                mobility=3,
                comorbidity=2,
                admission_type=AdmissionTypeEnum.ED,
                admission_time=now - timedelta(hours=12),
                discharge_time=None,
                patient_id=patient1.patient_id
            )

            patient2 = PatientModel(
                patient_id="PAC-AABBCCDD",
                birth_date=date(1982, 11, 20),
                gender=GenderEnum.F
            )
            admission2 = AdmissionDataModel(
                admission_data_id=f"ADM-AABBCCDD-{uuid.uuid4().hex[:4].upper()}",
                mobility=1,
                comorbidity=5,
                admission_type=AdmissionTypeEnum.ELECTIVE,
                admission_time=now - timedelta(days=5),
                discharge_time=now - timedelta(days=1),
                patient_id=patient2.patient_id
            )

            db.add_all([patient1, patient2, admission1, admission2])
            db.commit()

        except Exception as e:
            db.rollback()
            print(f"❌ Error al resetear/poblar la base de datos: {e}")
            raise e
        finally:
            db.close()

    def run_postman_tests(self) -> bool:
        print("\n🧪 Ejecutando tests end to end...")

        if not os.path.exists(self.collection_path):
            print(f"❌ Error: No se encuentra la colección Postman en '{self.collection_path}'")
            return False

        executable = shutil.which("newman")
        
        if not executable:
            print("\n❌ Error: 'newman' no se encuentra instalado o no está en el PATH del sistema.")
            print("1. Verifica que Node.js está instalado.")
            print("2. Instálalo globalmente ejecutando: npm install -g newman")
            return False

        command = [executable, "run", self.collection_path]

        try:
            result = subprocess.run(command, check=True, shell=True)
            print("\n✅ ¡Todos los tests end to end han pasado con éxito!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"\n❌ Detectados fallos en los tests (Código de salida: {e.returncode}).")
            return False
        except FileNotFoundError:
            print("\n❌ Error: no se encontró archivo de tests end-to-end.")
            print("Instálalo globalmente ejecutando: npm install -g newman")
            return False

    def run_all(self) -> bool:
        print("=" * 65)
        print("🚀 INICIANDO SUITE COMPLETA DE PRUEBAS END TO END")
        print("=" * 65)

        self.reset_and_seed_db()
        success = self.run_postman_tests()

        print("\n" + "=" * 65)
        if success:
            print("🎉 PROCESO FINALIZADO SIN ERRORES")
        else:
            print("💥 PROCESO FINALIZADO CON ERRORES EN LOS TESTS")
        print("=" * 65)

        return success


if __name__ == "__main__":
    SCRIPT_DIR = Path(__file__).resolve().parent
    COLLECTION_FILE = SCRIPT_DIR / "TEST_SIPAM_API.postman_collection.json"

    runner = TestsEndToEnd(
        collection_path=COLLECTION_FILE
    )
    
    success = runner.run_all()
    
    sys.exit(0 if success else 1)