import pytest
from pydantic import ValidationError

from backend.app.schema.routes.medical_summary_request import MedicalSummaryRequest
from backend.app.schema.routes.medical_summary_response import MedicalSummaryResponse


def test_known_options_are_kept_once_in_order() -> None:
    request = MedicalSummaryRequest(mobility=["aids", "escort", "aids"])

    assert request.mobility == ["aids", "escort"]


def test_unknown_option_is_rejected() -> None:
    with pytest.raises(ValidationError):
        MedicalSummaryRequest(diet=["keto"])


def test_response_reads_back_values_no_longer_in_the_catalog() -> None:
    response = MedicalSummaryResponse.model_validate(
        {
            "student_id": "00000000-0000-0000-0000-000000000001",
            "student_name": "נועה",
            "diet": ["retired_value"],
        }
    )

    assert response.diet == ["retired_value"]
