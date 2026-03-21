"""
Cloud Functions gen2 - Firestore トリガー
コレクション: rooms/{roomId}/messages/{messageId}
イベント: onCreate

新しいメッセージが投稿されたとき、ルーム内の他のメンバーへ
FCM プッシュ通知を送信する。
"""

import logging
import sys
import os

# shared モジュールを参照できるようにルートパスを追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from firebase_functions import firestore_fn
from google.cloud.firestore_v1.base_document import DocumentSnapshot

from shared.firestore_client import get_firestore_client
from shared.fcm import send_multicast_notification

logger = logging.getLogger(__name__)


@firestore_fn.on_document_created(document="rooms/{roomId}/messages/{messageId}")
def on_message_created(event: firestore_fn.Event[firestore_fn.DocumentSnapshot]) -> None:
    """
    Firestoreの rooms/{roomId}/messages/{messageId} に新規ドキュメントが
    作成されたときに呼び出される Cloud Functions。
    """
    snapshot: DocumentSnapshot = event.data
    if snapshot is None:
        logger.warning("on_message_created: event.data is None")
        return

    message_data = snapshot.to_dict()
    if not message_data:
        logger.warning("on_message_created: message document is empty")
        return

    sender_uid: str = message_data.get("senderUid", "")
    message_text: str = message_data.get("text", "")
    room_id: str = event.params.get("roomId", "")

    if not sender_uid:
        logger.warning("on_message_created: senderUid not found in message")
        return

    db = get_firestore_client()

    # 送信者の表示名を取得
    sender_display_name = _get_user_display_name(db, sender_uid)

    # ルーム情報からメンバー一覧を取得
    room_ref = db.collection("rooms").document(room_id)
    try:
        room_doc = room_ref.get()
    except Exception as exc:
        logger.error("Failed to fetch room document (roomId=%s): %s", room_id, exc)
        return

    if not room_doc.exists:
        logger.warning("Room document not found: %s", room_id)
        return

    room_data = room_doc.to_dict() or {}
    member_uids: list[str] = room_data.get("memberUids", [])

    # 送信者以外のメンバーの FCM トークンを収集
    fcm_tokens: list[str] = []
    for uid in member_uids:
        if uid == sender_uid:
            continue
        token = _get_fcm_token(db, uid)
        if token:
            fcm_tokens.append(token)

    if not fcm_tokens:
        logger.info(
            "No FCM tokens to notify for roomId=%s (all members may be the sender)", room_id
        )
        return

    title = sender_display_name or "新しいメッセージ"
    body = message_text if message_text else "(メッセージ)"

    result = send_multicast_notification(
        tokens=fcm_tokens,
        title=title,
        body=body,
        data={
            "type": "chat_message",
            "roomId": room_id,
            "senderUid": sender_uid,
        },
    )
    logger.info(
        "Chat notification sent: roomId=%s, success=%d, failure=%d",
        room_id,
        result["success_count"],
        result["failure_count"],
    )


def _get_user_display_name(db, uid: str) -> str:
    """Firestore の users/{uid} から displayName を取得する。"""
    try:
        user_doc = db.collection("users").document(uid).get()
        if user_doc.exists:
            return (user_doc.to_dict() or {}).get("displayName", "")
    except Exception as exc:
        logger.error("Failed to fetch user displayName (uid=%s): %s", uid, exc)
    return ""


def _get_fcm_token(db, uid: str) -> str:
    """Firestore の users/{uid} から fcmToken を取得する。"""
    try:
        user_doc = db.collection("users").document(uid).get()
        if user_doc.exists:
            return (user_doc.to_dict() or {}).get("fcmToken", "")
    except Exception as exc:
        logger.error("Failed to fetch FCM token (uid=%s): %s", uid, exc)
    return ""
