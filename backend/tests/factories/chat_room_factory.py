import uuid

from app.models.chat_room import ChatRoom


def make_chat_room(**kwargs) -> ChatRoom:
    family_id = kwargs.pop("family_id", uuid.uuid4())
    created_by = kwargs.pop("created_by", uuid.uuid4())
    defaults = {
        "id": uuid.uuid4(),
        "family_id": family_id,
        "name": "General",
        "type": "general",
        "created_by": created_by,
    }
    defaults.update(kwargs)
    return ChatRoom(**defaults)
