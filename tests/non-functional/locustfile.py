from locust import HttpUser, task, between
from datetime import datetime

class SIPAMLoadUser(HttpUser):
    wait_time = between(0.1, 0.5)

    def on_start(self):
        """Se ejecuta al iniciar cada usuario virtual: configura cabeceras globales."""
        self.headers = {
            "Content-Type": "application/json",
        }
        self.patient_id = None

        login_data = {
                    "username": "medico1@sipam.es",
                    "password": "1234567890"
            }
    
        response = self.client.post(
            "/api/v1/auth/token",
            data=login_data,
            name="AUTH: /api/v1/auth/token"
        )

        if response.status_code == 200:
            token = response.json().get("access_token")
            self.headers["Authorization"] = f"Bearer {token}"
        else:
            print(f"⚠️ Error al autenticar usuario virtual: {response.status_code} - {response.text}")

        patient_payload = {
            "birth_date": "1975-12-04",
            "gender": "M",
            "mobility": 2,
            "comorbidity": 1,
            "admission_type": "ED"
        }

        patient_response = self.client.post(
            "/api/v1/patients",
            json=patient_payload,
            headers=self.headers,
            name="SETUP: POST /api/v1/patients"
        )

        if patient_response.status_code == 201:
            resp_json = patient_response.json()
            self.patient_id = resp_json.get("patient_id", self.patient_id)
        else:
            print(f"⚠️ Error al crear paciente inicial: {patient_response.status_code} - {patient_response.text}")

    @task(3)
    def test_prediction_flow(self):
        payload = {
            "patient_id": self.patient_id,
            "heart_rate": 82.0,
            "sbp": 125.0,
            "dbp": 82.0,
            "resp_rate": 18.0,
            "spo2": 97.0,
            "temperature": 36.8,
            "wbc": 6.8,
            "creatinine": 0.95,
            "lactate": 1.2
        }
        self.client.post("/api/v1/prediction", json=payload, headers=self.headers, name="POST /api/v1/prediction")

    @task(1)
    def test_health_check(self):
        self.client.get("/api/v1/health", headers=self.headers, name="GET /api/v1/health")