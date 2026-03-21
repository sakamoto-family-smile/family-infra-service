from typing import Annotated

import firebase_admin.auth
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.exceptions import UnauthorizedException

security = HTTPBearer()


async def verify_firebase_token(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> dict:
    try:
        decoded_token = firebase_admin.auth.verify_id_token(credentials.credentials)
        return decoded_token
    except firebase_admin.auth.InvalidIdTokenError:
        raise UnauthorizedException("Invalid token")
    except firebase_admin.auth.ExpiredIdTokenError:
        raise UnauthorizedException("Token expired")
    except Exception:
        raise UnauthorizedException("Token verification failed")


FirebaseToken = Annotated[dict, Depends(verify_firebase_token)]
