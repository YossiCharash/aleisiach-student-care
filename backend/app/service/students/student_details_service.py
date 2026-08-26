import uuid
from datetime import date

from backend.app.client.students.student_details_repository import StudentDetailsRepository
from backend.app.models.client.student_details import StudentDetails
from backend.app.schema.routes.contact_info import ContactInfo
from backend.app.schema.routes.diagnosis import Diagnosis
from backend.app.schema.routes.student_details_response import StudentDetailsResponse
from backend.app.schema.routes.student_details_upsert_request import (
    StudentDetailsUpsertRequest,
)
from backend.app.schema.service.student_access_scope import StudentAccessScope
from backend.app.service.students.student_access_guard import StudentAccessGuard
from backend.app.utils.service.age_calculator import AgeCalculator


class StudentDetailsService:
    def __init__(
        self,
        details_repository: StudentDetailsRepository,
        access_guard: StudentAccessGuard,
    ) -> None:
        self._details = details_repository
        self._guard = access_guard

    def get(
        self, student_id: uuid.UUID, scope: StudentAccessScope, include_sensitive: bool
    ) -> StudentDetailsResponse:
        self._guard.require(student_id, scope)
        details = self._details.get(student_id)
        return self._to_response(student_id, details, include_sensitive)

    def upsert(
        self,
        student_id: uuid.UUID,
        request: StudentDetailsUpsertRequest,
        scope: StudentAccessScope,
    ) -> StudentDetailsResponse:
        self._guard.require(student_id, scope)
        details = self._details.get(student_id) or StudentDetails(student_id=student_id)
        self._apply(details, request)
        self._details.add(details)
        return self._to_response(student_id, details, include_sensitive=True)

    def _apply(self, details: StudentDetails, request: StudentDetailsUpsertRequest) -> None:
        details.national_id = request.national_id
        details.date_of_birth = request.date_of_birth
        details.address = request.address
        details.home_language = request.home_language
        details.medical_diagnoses = [item.model_dump() for item in request.medical_diagnoses]
        details.emergency_contacts = [item.model_dump() for item in request.emergency_contacts]
        details.legal_status = request.legal_status
        details.guardians = [item.model_dump() for item in request.guardians]

    def _to_response(
        self,
        student_id: uuid.UUID,
        details: StudentDetails | None,
        include_sensitive: bool,
    ) -> StudentDetailsResponse:
        if details is None:
            return StudentDetailsResponse(
                student_id=student_id, sensitive_visible=include_sensitive
            )
        age = (
            AgeCalculator.age_in_years(details.date_of_birth, date.today())
            if details.date_of_birth is not None
            else None
        )
        return StudentDetailsResponse(
            student_id=student_id,
            national_id=details.national_id,
            date_of_birth=details.date_of_birth,
            age=age,
            address=details.address,
            home_language=details.home_language,
            medical_diagnoses=[Diagnosis(**item) for item in details.medical_diagnoses],
            emergency_contacts=[ContactInfo(**item) for item in details.emergency_contacts],
            legal_status=details.legal_status if include_sensitive else None,
            guardians=(
                [ContactInfo(**item) for item in details.guardians] if include_sensitive else []
            ),
            sensitive_visible=include_sensitive,
        )
