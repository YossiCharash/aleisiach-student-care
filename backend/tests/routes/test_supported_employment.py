import uuid
from collections.abc import Callable

from fastapi.testclient import TestClient

from backend.app.models.client.user import User
from backend.app.models.client.user_role import UserRole

SeedUser = Callable[..., User]
AuthHeaders = Callable[..., dict[str, str]]
SeedWorkshop = Callable[..., uuid.UUID]
SeedStudent = Callable[..., uuid.UUID]

_BODY = {
    "workplace": "מאפייה מרכזית",
    "address": "רחוב הפרחים 5",
    "activity_type": "אריזה",
    "work_process": "אריזת מאפים",
    "work_environment": "מטבח תעשייתי",
    "required_body_functions": "עמידה ממושכת",
    "hazards_and_safety": "תנור חם",
    "workplace_contact": "דנה",
    "escort_contact": "יוסי",
    "mobility": "הסעה מאורגנת",
    "work_hours": "08:00-14:00",
}


def test_manager_writes_and_reads(
    api: TestClient,
    seed_workshop: SeedWorkshop,
    seed_student: SeedStudent,
    seed_user: SeedUser,
    auth_headers: AuthHeaders,
) -> None:
    workshop_id = seed_workshop("Aleph")
    student_id = seed_student(workshop_id, full_name="Noa")
    seed_user("boss", UserRole.MANAGER)
    headers = auth_headers(api, "boss")

    put = api.put(f"/students/{student_id}/supported-employment", headers=headers, json=_BODY)
    assert put.status_code == 200
    payload = put.json()
    assert payload["exists"] is True
    assert payload["workplace"] == "מאפייה מרכזית"
    assert payload["work_hours"] == "08:00-14:00"

    got = api.get(f"/students/{student_id}/supported-employment", headers=headers)
    assert got.status_code == 200
    assert got.json()["hazards_and_safety"] == "תנור חם"


def test_get_before_write_returns_empty(
    api: TestClient,
    seed_workshop: SeedWorkshop,
    seed_student: SeedStudent,
    seed_user: SeedUser,
    auth_headers: AuthHeaders,
) -> None:
    workshop_id = seed_workshop("Aleph")
    student_id = seed_student(workshop_id)
    seed_user("boss", UserRole.MANAGER)

    got = api.get(f"/students/{student_id}/supported-employment", headers=auth_headers(api, "boss"))

    assert got.status_code == 200
    payload = got.json()
    assert payload["exists"] is False
    assert payload["workplace"] == ""


def test_instructor_cannot_read_or_write(
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

    assert (
        api.get(f"/students/{student_id}/supported-employment", headers=headers).status_code == 403
    )
    write = api.put(f"/students/{student_id}/supported-employment", headers=headers, json=_BODY)
    assert write.status_code == 403


def test_professional_teacher_cannot_read_or_write(
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

    assert (
        api.get(f"/students/{student_id}/supported-employment", headers=headers).status_code == 403
    )
    write = api.put(f"/students/{student_id}/supported-employment", headers=headers, json=_BODY)
    assert write.status_code == 403


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
    api.put(f"/students/{student_id}/supported-employment", headers=headers, json=_BODY)

    pdf = api.get(f"/students/{student_id}/supported-employment/pdf", headers=headers)
    assert pdf.status_code == 200
    assert pdf.headers["content-type"] == "application/pdf"


def test_requires_authentication(
    api: TestClient, seed_workshop: SeedWorkshop, seed_student: SeedStudent
) -> None:
    workshop_id = seed_workshop("Aleph")
    student_id = seed_student(workshop_id)

    assert api.get(f"/students/{student_id}/supported-employment").status_code == 401
