import uuid

from backend.app.client.students.student_details_repository import StudentDetailsRepository
from backend.app.models.client.assistive_device import AssistiveDevice
from backend.app.models.client.audit_action import AuditAction
from backend.app.models.client.student_details import StudentDetails
from backend.app.schema.routes.contact_info import ContactInfo
from backend.app.schema.routes.student_details_response import StudentDetailsResponse
from backend.app.schema.routes.student_details_upsert_request import (
    StudentDetailsUpsertRequest,
)
from backend.app.schema.service.audit_entry import AuditEntry
from backend.app.schema.service.student_access_scope import StudentAccessScope
from backend.app.service.audit.audit_logger import AuditLogger
from backend.app.service.students.diagnosis_catalog_service import DiagnosisCatalogService
from backend.app.service.students.student_access_guard import StudentAccessGuard
from backend.app.utils.service.age_calculator import AgeCalculator
from backend.app.utils.service.clock import Clock

_ENTITY_TYPE = "student_details"
_TRACKED_FIELDS = (
    "national_id",
    "date_of_birth",
    "address",
    "home_language",
    "idd_severity",
    "additional_diagnoses",
    "emergency_contacts",
    "legal_status",
    "guardians",
    "has_allergies_or_dietary",
    "allergies_dietary",
    "takes_regular_medication",
    "medications",
    "medication_independence",
    "emergency_protocol",
    "assistive_devices",
    "assistive_device_other",
)


class StudentDetailsService:
    def __init__(
        self,
        details_repository: StudentDetailsRepository,
        diagnosis_catalog: DiagnosisCatalogService,
        access_guard: StudentAccessGuard,
        audit_logger: AuditLogger,
        clock: Clock,
    ) -> None:
        self._details = details_repository
        self._diagnoses = diagnosis_catalog
        self._guard = access_guard
        self._audit = audit_logger
        self._clock = clock

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
        actor_id: uuid.UUID,
    ) -> StudentDetailsResponse:
        self._guard.require(student_id, scope)
        details, created = self._details.get_or_create(student_id)
        before = self._snapshot(details)
        self._apply(details, request, actor_id)
        changed = self._changed_fields(before, self._snapshot(details))
        self._details.flush()
        if changed:
            action = AuditAction.CREATE if created else AuditAction.UPDATE
            self._audit.record(
                AuditEntry(
                    actor_id=actor_id,
                    action=action,
                    entity_type=_ENTITY_TYPE,
                    entity_id=student_id,
                    changes=changed,
                )
            )
        return self._to_response(student_id, details, include_sensitive=True)

    def _apply(
        self,
        details: StudentDetails,
        request: StudentDetailsUpsertRequest,
        actor_id: uuid.UUID,
    ) -> None:
        details.national_id = request.national_id
        details.date_of_birth = request.date_of_birth
        details.address = request.address
        details.home_language = request.home_language
        details.idd_severity = request.idd_severity
        details.additional_diagnoses = self._diagnoses.ensure_names(
            request.additional_diagnoses, actor_id
        )
        details.emergency_contacts = [item.model_dump() for item in request.emergency_contacts]
        details.legal_status = request.legal_status
        details.guardians = [item.model_dump() for item in request.guardians]
        self._apply_medical_profile(details, request)

    def _apply_medical_profile(
        self, details: StudentDetails, request: StudentDetailsUpsertRequest
    ) -> None:
        details.has_allergies_or_dietary = request.has_allergies_or_dietary
        details.allergies_dietary = (
            self._clean(request.allergies_dietary) if request.has_allergies_or_dietary else []
        )
        details.takes_regular_medication = request.takes_regular_medication
        details.medications = (
            self._clean(request.medications) if request.takes_regular_medication else []
        )
        details.medication_independence = (
            request.medication_independence if request.takes_regular_medication else None
        )
        details.emergency_protocol = request.emergency_protocol
        devices = self._unique([device.value for device in request.assistive_devices])
        details.assistive_devices = devices
        details.assistive_device_other = (
            request.assistive_device_other if AssistiveDevice.OTHER.value in devices else None
        )

    def _clean(self, items: list[str]) -> list[str]:
        return self._unique([item.strip() for item in items if item.strip()])

    def _unique(self, items: list[str]) -> list[str]:
        seen: list[str] = []
        for item in items:
            if item not in seen:
                seen.append(item)
        return seen

    def _snapshot(self, details: StudentDetails) -> dict[str, object]:
        return {name: getattr(details, name) for name in _TRACKED_FIELDS}

    def _changed_fields(self, before: dict[str, object], after: dict[str, object]) -> list[str]:
        return [name for name in _TRACKED_FIELDS if before[name] != after[name]]

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
            AgeCalculator.age_in_years(details.date_of_birth, self._clock.today())
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
            idd_severity=details.idd_severity,
            additional_diagnoses=list(details.additional_diagnoses),
            emergency_contacts=[ContactInfo(**item) for item in details.emergency_contacts],
            legal_status=details.legal_status if include_sensitive else None,
            guardians=(
                [ContactInfo(**item) for item in details.guardians] if include_sensitive else []
            ),
            has_allergies_or_dietary=details.has_allergies_or_dietary,
            allergies_dietary=list(details.allergies_dietary),
            takes_regular_medication=details.takes_regular_medication,
            medications=list(details.medications),
            medication_independence=details.medication_independence,
            emergency_protocol=details.emergency_protocol,
            assistive_devices=[AssistiveDevice(value) for value in details.assistive_devices],
            assistive_device_other=details.assistive_device_other,
            sensitive_visible=include_sensitive,
        )
