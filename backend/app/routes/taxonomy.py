import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.app.client.database.provider import get_session
from backend.app.client.taxonomy.taxonomy_repository import TaxonomyRepository
from backend.app.routes.security import CurrentUser, Manager
from backend.app.schema.routes.label_create_request import LabelCreateRequest
from backend.app.schema.routes.label_response import LabelResponse
from backend.app.schema.routes.label_tree_node import LabelTreeNode
from backend.app.schema.routes.label_update_request import LabelUpdateRequest
from backend.app.schema.routes.skill_create_request import SkillCreateRequest
from backend.app.schema.routes.skill_response import SkillResponse
from backend.app.schema.routes.skill_update_request import SkillUpdateRequest
from backend.app.schema.routes.solution_create_request import SolutionCreateRequest
from backend.app.schema.routes.solution_response import SolutionResponse
from backend.app.schema.routes.solution_update_request import SolutionUpdateRequest
from backend.app.schema.routes.sub_label_create_request import SubLabelCreateRequest
from backend.app.schema.routes.sub_label_response import SubLabelResponse
from backend.app.schema.routes.sub_label_update_request import SubLabelUpdateRequest
from backend.app.service.taxonomy.taxonomy_service import TaxonomyService


def get_taxonomy_service(
    session: Annotated[Session, Depends(get_session)],
) -> TaxonomyService:
    return TaxonomyService(TaxonomyRepository(session))


ServiceDep = Annotated[TaxonomyService, Depends(get_taxonomy_service)]

router = APIRouter(prefix="/taxonomy", tags=["taxonomy"])


@router.get("/tree", response_model=list[LabelTreeNode])
def get_tree(service: ServiceDep, _: CurrentUser) -> list[LabelTreeNode]:
    return service.active_tree()


@router.get("/labels", response_model=list[LabelResponse])
def list_labels(
    service: ServiceDep, _: CurrentUser, include_inactive: bool = False
) -> list[LabelResponse]:
    return service.list_labels(include_inactive)


@router.post("/labels", response_model=LabelResponse, status_code=status.HTTP_201_CREATED)
def create_label(request: LabelCreateRequest, service: ServiceDep, _: Manager) -> LabelResponse:
    return service.create_label(request)


@router.patch("/labels/{label_id}", response_model=LabelResponse)
def update_label(
    label_id: uuid.UUID, request: LabelUpdateRequest, service: ServiceDep, _: Manager
) -> LabelResponse:
    return service.update_label(label_id, request)


@router.post("/sub-labels", response_model=SubLabelResponse, status_code=status.HTTP_201_CREATED)
def create_sub_label(
    request: SubLabelCreateRequest, service: ServiceDep, _: Manager
) -> SubLabelResponse:
    return service.create_sub_label(request)


@router.patch("/sub-labels/{sub_label_id}", response_model=SubLabelResponse)
def update_sub_label(
    sub_label_id: uuid.UUID,
    request: SubLabelUpdateRequest,
    service: ServiceDep,
    _: Manager,
) -> SubLabelResponse:
    return service.update_sub_label(sub_label_id, request)


@router.post("/skills", response_model=SkillResponse, status_code=status.HTTP_201_CREATED)
def create_skill(request: SkillCreateRequest, service: ServiceDep, _: Manager) -> SkillResponse:
    return service.create_skill(request)


@router.patch("/skills/{skill_id}", response_model=SkillResponse)
def update_skill(
    skill_id: uuid.UUID, request: SkillUpdateRequest, service: ServiceDep, _: Manager
) -> SkillResponse:
    return service.update_skill(skill_id, request)


@router.post("/solutions", response_model=SolutionResponse, status_code=status.HTTP_201_CREATED)
def create_solution(
    request: SolutionCreateRequest, service: ServiceDep, _: Manager
) -> SolutionResponse:
    return service.create_solution(request)


@router.patch("/solutions/{solution_id}", response_model=SolutionResponse)
def update_solution(
    solution_id: uuid.UUID,
    request: SolutionUpdateRequest,
    service: ServiceDep,
    _: Manager,
) -> SolutionResponse:
    return service.update_solution(solution_id, request)
