import uuid

from fastapi import APIRouter

from app.core.dependencies import CurrentUser, DBSession
from app.schemas.chat_room import ChatRoomCreate, ChatRoomResponse, ChatRoomUpdate
from app.services.chat_service import ChatService

router = APIRouter()


@router.post("/{family_id}/chat-rooms", response_model=ChatRoomResponse, status_code=201)
async def create_chat_room(
    family_id: uuid.UUID,
    data: ChatRoomCreate,
    db: DBSession,
    current_user: CurrentUser,
) -> ChatRoomResponse:
    service = ChatService(db)
    room = await service.create_room(family_id, current_user.id, data)
    return ChatRoomResponse.model_validate(room)


@router.get("/{family_id}/chat-rooms", response_model=list[ChatRoomResponse])
async def list_chat_rooms(
    family_id: uuid.UUID,
    db: DBSession,
    current_user: CurrentUser,
) -> list[ChatRoomResponse]:
    service = ChatService(db)
    rooms = await service.list_by_family(family_id)
    return [ChatRoomResponse.model_validate(r) for r in rooms]


@router.get("/{family_id}/chat-rooms/{room_id}", response_model=ChatRoomResponse)
async def get_chat_room(
    family_id: uuid.UUID,
    room_id: uuid.UUID,
    db: DBSession,
    current_user: CurrentUser,
) -> ChatRoomResponse:
    service = ChatService(db)
    room = await service.get(room_id)
    return ChatRoomResponse.model_validate(room)


@router.patch("/{family_id}/chat-rooms/{room_id}", response_model=ChatRoomResponse)
async def update_chat_room(
    family_id: uuid.UUID,
    room_id: uuid.UUID,
    data: ChatRoomUpdate,
    db: DBSession,
    current_user: CurrentUser,
) -> ChatRoomResponse:
    service = ChatService(db)
    room = await service.update(room_id, family_id, data)
    return ChatRoomResponse.model_validate(room)


@router.delete("/{family_id}/chat-rooms/{room_id}", status_code=204)
async def delete_chat_room(
    family_id: uuid.UUID,
    room_id: uuid.UUID,
    db: DBSession,
    current_user: CurrentUser,
) -> None:
    service = ChatService(db)
    await service.delete(room_id, family_id)
