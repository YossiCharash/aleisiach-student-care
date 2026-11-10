from collections.abc import Callable

from fastapi.testclient import TestClient

from backend.app.models.client.user import User
from backend.app.models.client.user_role import UserRole

SeedUser = Callable[..., User]
AuthHeaders = Callable[..., dict[str, str]]


def test_manager_adds_renames_and_deactivates_a_domain(
    api: TestClient, seed_user: SeedUser, auth_headers: AuthHeaders
) -> None:
    seed_user("boss", UserRole.MANAGER)
    headers = auth_headers(api, "boss")

    created = api.post(
        "/risk-domains", headers=headers, json={"name": "שימוש בטלפון", "category": "behavioral"}
    )
    assert created.status_code == 201
    domain = created.json()
    assert domain["category_label"] == "התנהגותי"

    renamed = api.patch(
        f"/risk-domains/{domain['id']}", headers=headers, json={"name": "שימוש בסלולרי"}
    )
    assert renamed.json()["name"] == "שימוש בסלולרי"

    api.patch(f"/risk-domains/{domain['id']}", headers=headers, json={"is_active": False})
    active = api.get("/risk-domains", headers=headers).json()
    everything = api.get("/risk-domains?include_inactive=true", headers=headers).json()
    assert domain["id"] not in [item["id"] for item in active]
    assert domain["id"] in [item["id"] for item in everything]


def test_unknown_category_is_rejected(
    api: TestClient, seed_user: SeedUser, auth_headers: AuthHeaders
) -> None:
    seed_user("boss", UserRole.MANAGER)

    response = api.post(
        "/risk-domains",
        headers=auth_headers(api, "boss"),
        json={"name": "x", "category": "financial"},
    )

    assert response.status_code == 422


def test_non_managers_read_but_cannot_change_domains(
    api: TestClient, seed_user: SeedUser, auth_headers: AuthHeaders
) -> None:
    seed_user("prof", UserRole.PROFESSIONAL_TEACHER)
    headers = auth_headers(api, "prof")

    assert api.get("/risk-domains", headers=headers).status_code == 200
    created = api.post("/risk-domains", headers=headers, json={"name": "x", "category": "medical"})
    assert created.status_code == 403
