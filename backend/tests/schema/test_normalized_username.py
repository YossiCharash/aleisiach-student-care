import pytest
from pydantic import ValidationError

from backend.app.schema.routes.invitation_accept_request import InvitationAcceptRequest
from backend.app.schema.routes.login_request import LoginRequest


def test_login_request_strips_surrounding_whitespace() -> None:
    request = LoginRequest(username="  yossi  ", password="secret")

    assert request.username == "yossi"


def test_login_request_rejects_whitespace_only_username() -> None:
    with pytest.raises(ValidationError):
        LoginRequest(username="   ", password="secret")


def test_invitation_accept_request_strips_surrounding_whitespace() -> None:
    request = InvitationAcceptRequest(
        token="t", username="  newuser  ", password="Str0ng!Passw0rd"
    )

    assert request.username == "newuser"


def test_invitation_accept_request_counts_length_after_stripping() -> None:
    with pytest.raises(ValidationError):
        InvitationAcceptRequest(
            token="t", username="  ab  ", password="Str0ng!Passw0rd"
        )
