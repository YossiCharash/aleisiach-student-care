import uuid

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.models.client.class_entity import ClassEntity


def _seed_class(session: Session) -> uuid.UUID:
    entity = ClassEntity(name="Aleph")
    session.add(entity)
    session.flush()
    return entity.id


def test_create_and_get_student(api: TestClient, db_session: Session) -> None:
    class_id = _seed_class(db_session)

    created = api.post("/students", json={"full_name": "Dana", "class_id": str(class_id)})
    assert created.status_code == 201
    student_id = created.json()["id"]

    fetched = api.get(f"/students/{student_id}")
    assert fetched.status_code == 200
    assert fetched.json()["full_name"] == "Dana"
    assert fetched.json()["is_archived"] is False


def test_create_with_unknown_class_returns_404(api: TestClient) -> None:
    response = api.post("/students", json={"full_name": "X", "class_id": str(uuid.uuid4())})
    assert response.status_code == 404
    assert response.json()["code"] == "not_found"


def test_get_unknown_student_returns_404(api: TestClient) -> None:
    response = api.get(f"/students/{uuid.uuid4()}")
    assert response.status_code == 404


def test_archive_removes_student_from_list(api: TestClient, db_session: Session) -> None:
    class_id = _seed_class(db_session)
    api.post("/students", json={"full_name": "Stays", "class_id": str(class_id)})
    target = api.post("/students", json={"full_name": "Goes", "class_id": str(class_id)}).json()

    archived = api.post(f"/students/{target['id']}/archive")
    assert archived.status_code == 200
    assert archived.json()["is_archived"] is True

    names = [student["full_name"] for student in api.get("/students").json()]
    assert names == ["Stays"]
