import uuid

from app.models.user import User


def make_user(**kwargs) -> User:
    family_id = kwargs.pop("family_id", uuid.uuid4())
    defaults = {
        "id": uuid.uuid4(),
        "family_id": family_id,
        "firebase_uid": f"firebase-uid-{uuid.uuid4().hex[:8]}",
        "display_name": "Test User",
        "email": "test@example.com",
        "role": "member",
        "is_active": True,
    }
    defaults.update(kwargs)
    return User(**defaults)
