import uuid
from collections.abc import Callable

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.models.client.student_details import StudentDetails
from backend.app.models.client.user import User
from backend.app.models.client.user_role import UserRole

SeedUser = Callable[..., User]
AuthHeaders = Callable[..., dict[str, str]]
SeedWorkshop = Callable[..., uuid.UUID]
SeedStudent = Callable[..., uuid.UUID]

_BODY = {
    "general_background": "רקע כללי",
    "vocational_domain": "תחום תעסוקתי",
    "behavioral_emotional_domain": "תחום רגשי",
    "communication_social_domain": "תחום תקשורתי",
    "independence_life_skills_domain": "עצמאות",
    "summary_recommendations": "סיכום",
}


def _seed_details(session: Session, student_id: uuid.UUID) -> None:
    session.add(StudentDetails(student_id=student_id, national_id="123456782"))
    session.flush()


def test_manager_writes_and_reads_report(
    api: TestClient,
    db_session: Session,
    seed_workshop: SeedWorkshop,
    seed_student: SeedStudent,
    seed_user: SeedUser,
    auth_headers: AuthHeaders,
) -> None:
    workshop_id = seed_workshop("Aleph")
    student_id = seed_student(workshop_id, full_name="Noa")
    _seed_details(db_session, student_id)
    seed_user("boss", UserRole.MANAGER)
    headers = auth_headers(api, "boss")

    put = api.put(f"/students/{student_id}/functional-report", headers=headers, json=_BODY)
    assert put.status_code == 200
    payload = put.json()
    assert payload["exists"] is True
    assert payload["general_background"] == "רקע כללי"
    assert payload["student_name"] == "Noa"
    assert payload["national_id"] == "123456782"
    assert payload["written_by_name"] == "User"

    got = api.get(f"/students/{student_id}/functional-report", headers=headers)
    assert got.status_code == 200
    assert got.json()["summary_recommendations"] == "סיכום"


def test_get_before_write_returns_identity_only(
    api: TestClient,
    db_session: Session,
    seed_workshop: SeedWorkshop,
    seed_student: SeedStudent,
    seed_user: SeedUser,
    auth_headers: AuthHeaders,
) -> None:
    workshop_id = seed_workshop("Aleph")
    student_id = seed_student(workshop_id, full_name="Noa")
    _seed_details(db_session, student_id)
    seed_user("boss", UserRole.MANAGER)

    got = api.get(f"/students/{student_id}/functional-report", headers=auth_headers(api, "boss"))

    assert got.status_code == 200
    payload = got.json()
    assert payload["exists"] is False
    assert payload["student_name"] == "Noa"
    assert payload["general_background"] == ""


def test_instructor_reads_own_workshop_but_cannot_write(
    api: TestClient,
    seed_workshop: SeedWorkshop,
    seed_student: SeedStudent,
    seed_user: SeedUser,
    auth_headers: AuthHeaders,
) -> None:
    workshop_id = seed_workshop("Aleph")
    student_id = seed_student(workshop_id)
    seed_user("teacher", UserRole.INSTRUCTOR, workshop_id=workshop_id)
    headers = auth_headers(api, "teacher")

    assert api.get(f"/students/{student_id}/functional-report", headers=headers).status_code == 200
    write = api.put(f"/students/{student_id}/functional-report", headers=headers, json=_BODY)
    assert write.status_code == 403


def test_professional_teacher_reads_but_cannot_write(
    api: TestClient,
    seed_workshop: SeedWorkshop,
    seed_student: SeedStudent,
    seed_user: SeedUser,
    auth_headers: AuthHeaders,
) -> None:
    workshop_id = seed_workshop("Aleph")
    student_id = seed_student(workshop_id)
    seed_user("prof", UserRole.PROFESSIONAL_TEACHER)
    headers = auth_headers(api, "prof")

    assert api.get(f"/students/{student_id}/functional-report", headers=headers).status_code == 200
    write = api.put(f"/students/{student_id}/functional-report", headers=headers, json=_BODY)
    assert write.status_code == 403


def test_instructor_cannot_read_other_workshop(
    api: TestClient,
    seed_workshop: SeedWorkshop,
    seed_student: SeedStudent,
    seed_user: SeedUser,
    auth_headers: AuthHeaders,
) -> None:
    class_a = seed_workshop("Aleph")
    class_b = seed_workshop("Bet")
    student_id = seed_student(class_b)
    seed_user("teacher", UserRole.INSTRUCTOR, workshop_id=class_a)
    headers = auth_headers(api, "teacher")

    assert api.get(f"/students/{student_id}/functional-report", headers=headers).status_code == 404


def test_pdf_export(
    api: TestClient,
    seed_workshop: SeedWorkshop,
    seed_student: SeedStudent,
    seed_user: SeedUser,
    auth_headers: AuthHeaders,
) -> None:
    workshop_id = seed_workshop("Aleph")
    student_id = seed_student(workshop_id)
    seed_user("boss", UserRole.MANAGER)
    headers = auth_headers(api, "boss")
    api.put(f"/students/{student_id}/functional-report", headers=headers, json=_BODY)

    pdf = api.get(f"/students/{student_id}/functional-report/pdf", headers=headers)
    assert pdf.status_code == 200
    assert pdf.headers["content-type"] == "application/pdf"


def test_report_requires_authentication(
    api: TestClient, seed_workshop: SeedWorkshop, seed_student: SeedStudent
) -> None:
    workshop_id = seed_workshop("Aleph")
    student_id = seed_student(workshop_id)

    assert api.get(f"/students/{student_id}/functional-report").status_code == 401
