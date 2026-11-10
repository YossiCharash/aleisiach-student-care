import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.client.risk_assessment import RiskAssessment


class RiskAssessmentRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, assessment: RiskAssessment) -> RiskAssessment:
        self._session.add(assessment)
        self._session.flush()
        return assessment

    def flush(self) -> None:
        self._session.flush()

    def get(self, assessment_id: uuid.UUID) -> RiskAssessment | None:
        return self._session.get(RiskAssessment, assessment_id)

    def list_for_student(self, student_id: uuid.UUID) -> list[RiskAssessment]:
        statement = (
            select(RiskAssessment)
            .where(
                RiskAssessment.student_id == student_id,
                RiskAssessment.is_archived.is_(False),
            )
            .order_by(
                RiskAssessment.assessment_date.desc(),
                RiskAssessment.created_at.desc(),
                RiskAssessment.id.desc(),
            )
        )
        return list(self._session.scalars(statement).all())
