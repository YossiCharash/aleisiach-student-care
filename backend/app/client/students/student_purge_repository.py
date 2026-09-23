import uuid

from sqlalchemy import select
from sqlalchemy.orm import InstrumentedAttribute, Session

from backend.app.models.base import Base
from backend.app.models.client.functional_report import FunctionalReport
from backend.app.models.client.program import Program
from backend.app.models.client.program_plan import ProgramPlan
from backend.app.models.client.reception_report import ReceptionReport
from backend.app.models.client.social_note_entry import SocialNoteEntry
from backend.app.models.client.student import Student
from backend.app.models.client.student_details import StudentDetails
from backend.app.models.client.student_extra_section import StudentExtraSection
from backend.app.models.client.supported_employment import SupportedEmployment
from backend.app.models.client.team_meeting import TeamMeeting

_CHILD_MODELS: tuple[tuple[type[Base], InstrumentedAttribute[uuid.UUID]], ...] = (
    (Program, Program.student_id),
    (ProgramPlan, ProgramPlan.student_id),
    (TeamMeeting, TeamMeeting.student_id),
    (SocialNoteEntry, SocialNoteEntry.student_id),
    (StudentExtraSection, StudentExtraSection.student_id),
    (StudentDetails, StudentDetails.student_id),
    (FunctionalReport, FunctionalReport.student_id),
    (ReceptionReport, ReceptionReport.student_id),
    (SupportedEmployment, SupportedEmployment.student_id),
)


class StudentPurgeRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def purge(self, student_id: uuid.UUID) -> None:
        for model, student_column in _CHILD_MODELS:
            for child in self._session.scalars(
                select(model).where(student_column == student_id)
            ).all():
                self._session.delete(child)
        self._session.flush()
        student = self._session.get(Student, student_id)
        if student is not None:
            self._session.delete(student)
            self._session.flush()
