import firebase_admin
from firebase_admin import credentials, firestore

_db = None


def get_firestore_client():
    """firebase_admin を初期化し、Firestore クライアントを返す。"""
    global _db

    if not firebase_admin._apps:
        firebase_admin.initialize_app()

    if _db is None:
        _db = firestore.client()

    return _db
