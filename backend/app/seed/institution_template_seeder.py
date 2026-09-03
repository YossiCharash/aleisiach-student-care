import uuid

from backend.app.client.students.detail_option_repository import DetailOptionRepository
from backend.app.configuration.institutions.institution_template_settings import (
    InstitutionTemplateSettings,
)
from backend.app.models.client.detail_option import DetailOption
from backend.app.models.client.detail_option_field import DetailOptionField


class InstitutionTemplateSeeder:
    def __init__(
        self, options: DetailOptionRepository, settings: InstitutionTemplateSettings
    ) -> None:
        self._options = options
        self._settings = settings

    def seed(self, institution_id: uuid.UUID) -> None:
        for field, names in self._settings.detail_options.items():
            for order, name in enumerate(names):
                self._options.add(
                    DetailOption(
                        field=DetailOptionField(field),
                        name=name,
                        order=order,
                        is_active=True,
                        institution_id=institution_id,
                    )
                )
        self._options.flush()
