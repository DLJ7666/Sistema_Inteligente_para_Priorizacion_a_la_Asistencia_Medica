import pytest
from datetime import date
from unittest.mock import patch

from app.models.patients import PatientModel
import app.models.prediction  # noqa: F401


@patch("app.models.patients.date")
def test_age_birthday_already_passed_this_year(mock_date):
    # Fijamos 'hoy' en el 15 de Agosto de 2026
    mock_date.today.return_value = date(2026, 8, 15)

    # Nacido el 10 de Mayo de 1990 (mayo < agosto)
    patient = PatientModel(birth_date=date(1990, 5, 10))

    assert patient.age == 36

@patch("app.models.patients.date")
def test_age_birthday_not_yet_passed_this_year(mock_date):
    # Fijamos 'hoy' en el 15 de Agosto de 2026
    mock_date.today.return_value = date(2026, 8, 15)

    # Nacido el 20 de Noviembre de 1990 (noviembre > agosto)
    patient = PatientModel(birth_date=date(1990, 11, 20))

    assert patient.age == 35

@patch("app.models.patients.date")
def test_age_birthday_is_today(mock_date):
    # Fijamos 'hoy' en el 15 de Agosto de 2026
    mock_date.today.return_value = date(2026, 8, 15)

    # Nacido el 15 de Agosto de 1990
    patient = PatientModel(birth_date=date(1990, 8, 15))

    assert patient.age == 36

@patch("app.models.patients.date")
def test_age_newborn_born_today(mock_date):
    mock_date.today.return_value = date(2026, 8, 15)

    patient = PatientModel(birth_date=date(2026, 8, 15))

    assert patient.age == 0

@pytest.mark.parametrize("today_date, expected_age", [
    (date(2025, 2, 28), 24),
    (date(2025, 3, 1), 25)
])
@patch("app.models.patients.date")
def test_age_leap_year_bisiesto_birth_date(mock_date, today_date, expected_age  ):
    mock_date.today.return_value = today_date

    patient = PatientModel(birth_date=date(2000, 2, 29))
    assert patient.age == expected_age

def test_age_missing_birth_date():
    patient = PatientModel(birth_date=None)

    with pytest.raises(AttributeError):
        _ = patient.age