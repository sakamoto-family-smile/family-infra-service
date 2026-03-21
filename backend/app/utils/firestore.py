import firebase_admin.firestore


def get_firestore_client() -> firebase_admin.firestore.firestore.AsyncClient:
    return firebase_admin.firestore.AsyncClient()
