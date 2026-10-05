from datetime import date

from app.models.base import Base
from sqlalchemy import Boolean, Column, Float, ForeignKey, String
from sqlalchemy.orm import relationship


class PredictionModel(Base):
    __tablename__ = "predictions"

    prediction_id = Column(String, primary_key=True, index=True)
    prediction = Column(Float, nullable=False)
    threshold = Column(Float, nullable=False)
    outcome = Column(Boolean, nullable=True)
    comments = Column(String, nullable=True)

    vital_signs_id = Column(
            String,
            ForeignKey("vital_signs.vital_signs_id", ondelete="CASCADE"),
            nullable=False
        )
    vital_signs = relationship("VitalSignsModel", back_populates="predictions")

    @property
    def decision(self) -> bool:
        return self.prediction >= self.threshold

    @property
    def correct(self) -> bool | None:
        if self.outcome is None:
            return None
        return self.decision == self.outcome