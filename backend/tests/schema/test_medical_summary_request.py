import pytest
from pydantic import ValidationError

from backend.app.schema.routes.medical_summary_create_request import MedicalSummaryCreateRequest
from backend.app.schema.routes.medical_summary_entry_response import MedicalSummaryEntryResponse
from backend.app.schema.routes.medical_summary_request import MedicalSummaryRequest


def test_known_options_are_kept_once_in_order() -> None:
    request = MedicalSummaryRequest(mobility=["aids", "escort", "aids"])

    assert request.mobility == ["aids", "escort"]


def test_unknown_option_is_rejected() -> None:
    with pytest.raises(ValidationError):
        MedicalSummaryRequest(diet=["keto"])


def test_response_reads_back_values_no_longer_in_the_catalog() -> None:
    response = MedicalSummaryEntryResponse.model_validate(
        {
            "id": "00000000-0000-0000-0000-000000000002",
            "student_id": "00000000-0000-0000-0000-000000000001",
            "summary_date": "2026-11-10",
            "author_id": "00000000-0000-0000-0000-000000000003",
            "created_at": "2026-11-10T10:00:00Z",
            "updated_at": "2026-11-10T10:00:00Z",
            "diet": ["retired_value"],
        }
    )

    assert response.diet == ["retired_value"]


def test_create_request_requires_a_date() -> None:
    with pytest.raises(ValidationError):
        MedicalSummaryCreateRequest.model_validate({"allergies": "בוטנים"})


def test_create_request_validates_options() -> None:
    with pytest.raises(ValidationError):
        MedicalSummaryCreateRequest.model_validate({"summary_date": "2026-11-10", "diet": ["keto"]})
