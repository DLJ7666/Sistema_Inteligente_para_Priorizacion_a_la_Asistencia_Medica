import pytest

from app.models.prediction import PredictionModel
import app.models.patients  # noqa: F401

@pytest.mark.parametrize("prediction, threshold, expected_decision", [
    (0.8, 0.5, True),
    (0.5, 0.5, True),
    (0.3, 0.5, False),
])
def test_decision_threshold_evaluations(prediction, threshold, expected_decision):
    model = PredictionModel(prediction=prediction, threshold=threshold)
    assert model.decision is expected_decision

def test_decision_missing_prediction():
    prediction_model = PredictionModel(prediction=None, threshold=0.5)

    with pytest.raises(TypeError):
        _ = prediction_model.decision

def test_decision_missing_threshold():
    prediction_model = PredictionModel(prediction=0.8, threshold=None)

    with pytest.raises(TypeError):
        _ = prediction_model.decision

def test_correct_none_when_outcome_is_none():
    model = PredictionModel(prediction=0.8, threshold=0.5, outcome=None)
    
    assert model.correct is None

@pytest.mark.parametrize("prediction, threshold, outcome, expected_correct", [
    (0.8, 0.5, True, True),
    (0.3, 0.5, False, True),
    (0.8, 0.5, False, False),
    (0.3, 0.5, True, False),
])
def test_correct_evaluations(prediction, threshold, outcome, expected_correct):
    model = PredictionModel(prediction=prediction, threshold=threshold, outcome=outcome)
    
    assert model.correct is expected_correct

def test_correct_missing_prediction():
    prediction_model = PredictionModel(prediction=None, threshold=0.5, outcome=True)

    with pytest.raises(TypeError):
        _ = prediction_model.correct

def test_correct_missing_threshold():
    prediction_model = PredictionModel(prediction=0.8, threshold=None, outcome=True)

    with pytest.raises(TypeError):
        _ = prediction_model.correct