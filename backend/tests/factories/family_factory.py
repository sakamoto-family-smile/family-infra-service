import uuid

from app.models.family import Family


def make_family(**kwargs) -> Family:
    defaults = {
        "id": uuid.uuid4(),
        "name": "Test Family",
        "invite_code": "TESTCODE",
        "plan": "free",
        "icon_url": None,
    }
    defaults.update(kwargs)
    return Family(**defaults)
