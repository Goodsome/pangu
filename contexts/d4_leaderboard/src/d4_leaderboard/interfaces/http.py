from datetime import datetime
from uuid import UUID
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from d4_leaderboard.application.commands.create_entry import CreateEntryCommand
from d4_leaderboard.application.commands.delete_entry import DeleteEntryCommand
from d4_leaderboard.application.commands.update_entry import UpdateEntryCommand
from d4_leaderboard.application.dtos.entry_dto import EntryDto
from d4_leaderboard.application.dtos.entry_filter import EntryFilter
from d4_leaderboard.application.ports.entry_query_service import EntryQueryService
from d4_leaderboard.container import Container
from d4_types.enums.player_class import PlayerClass
from d4_leaderboard.domain.identities.entry_id import EntryId
from foundation.common_types.page import Page, PageQuery
from foundation.message_bus.message_bus import AsyncBaseMessageBus


class CreateEntryRequest(BaseModel):
    player_name: str
    player_class: PlayerClass
    tier: int = Field(..., ge=1, le=150)
    duration_ms: int = Field(..., ge=0, le=600000)
    occurred_at: datetime


class UpdateEntryRequest(BaseModel):
    player_name: str | None = None
    player_class: PlayerClass | None = None
    tier: int | None = Field(None, ge=1, le=150)
    duration_ms: int | None = Field(None, ge=0, le=600000)
    occurred_at: datetime | None = None


router = APIRouter(prefix="/entries", tags=["entries"])


@router.post("/", status_code=status.HTTP_201_CREATED)
@inject
async def create_entry(
    req: CreateEntryRequest,
    message_bus: AsyncBaseMessageBus = Depends(Provide[Container.message_bus]),
) -> None:
    cmd = CreateEntryCommand(
        player_name=req.player_name,
        player_class=req.player_class,
        tier=req.tier,
        duration_ms=req.duration_ms,
        occurred_at=req.occurred_at,
    )
    await message_bus.handle(cmd)


@router.get("/{entry_id}", response_model=EntryDto)
@inject
async def get_entry(
    entry_id: UUID,
    query_service: EntryQueryService = Depends(Provide[Container.entry_query_service]),
) -> EntryDto:
    try:
        return await query_service.get(EntryId.reconstitute(entry_id))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.get("/", response_model=Page[EntryDto])
@inject
async def list_entries(
    current: int = Query(default=1, ge=1),
    size: int = Query(default=10, ge=1, le=100),
    query_service: EntryQueryService = Depends(Provide[Container.entry_query_service]),
) -> Page[EntryDto]:
    page_query = PageQuery[EntryFilter](
        current=current, size=size, condition=EntryFilter()
    )
    return await query_service.find_by_query(page_query)


@router.put("/{entry_id}", status_code=status.HTTP_200_OK)
@inject
async def update_entry(
    entry_id: UUID,
    req: UpdateEntryRequest,
    message_bus: AsyncBaseMessageBus = Depends(Provide[Container.message_bus]),
) -> None:
    eid = EntryId.reconstitute(entry_id)
    cmd = UpdateEntryCommand(
        id=eid,
        player_name=req.player_name,
        player_class=req.player_class,
        tier=req.tier,
        duration_ms=req.duration_ms,
        occurred_at=req.occurred_at,
    )
    try:
        await message_bus.handle(cmd)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_entry(
    entry_id: UUID,
    message_bus: AsyncBaseMessageBus = Depends(Provide[Container.message_bus]),
) -> None:
    eid = EntryId.reconstitute(entry_id)
    cmd = DeleteEntryCommand(id=eid)
    try:
        await message_bus.handle(cmd)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
