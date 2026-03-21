"""
Cloud Functions gen2 - Firestore トリガー
コレクション: todo_items/{todoId}
イベント: onUpdate

Todo アイテムが更新されたとき、assigned_to フィールドが変更された場合のみ
新しい担当者へ FCM プッシュ通知を送信する。
"""

import logging
import sys
import os

# shared モジュールを参照できるようにルートパスを追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from firebase_functions import firestore_fn

from shared.firestore_client import get_firestore_client
from shared.fcm import send_notification

logger = logging.getLogger(__name__)


@firestore_fn.on_document_updated(document="todo_items/{todoId}")
def on_todo_updated(
    event: firestore_fn.Event[firestore_fn.Change[firestore_fn.DocumentSnapshot]],
) -> None:
    """
    Firestoreの todo_items/{todoId} が更新されたときに呼び出される Cloud Functions。
    assigned_to フィールドが変更された場合のみ新しい担当者へ通知する。
    """
    before_snapshot = event.data.before
    after_snapshot = event.data.after

    if before_snapshot is None or after_snapshot is None:
        logger.warning("on_todo_updated: before or after snapshot is None")
        return

    before_data = before_snapshot.to_dict() or {}
    after_data = after_snapshot.to_dict() or {}

    before_assigned_to: str = before_data.get("assigned_to", "")
    after_assigned_to: str = after_data.get("assigned_to", "")

    # assigned_to が変更されていない場合はスキップ
    if before_assigned_to == after_assigned_to:
        logger.info("on_todo_updated: assigned_to not changed, skipping notification")
        return

    if not after_assigned_to:
        logger.info("on_todo_updated: assigned_to cleared, no notification to send")
        return

    todo_id: str = event.params.get("todoId", "")
    todo_title: str = after_data.get("title", "Todo")

    db = get_firestore_client()

    # 新しい担当者の FCM トークンを取得
    fcm_token = _get_fcm_token(db, after_assigned_to)
    if not fcm_token:
        logger.warning(
            "No FCM token found for assigned user (uid=%s, todoId=%s)",
            after_assigned_to,
            todo_id,
        )
        return

    # 担当者の表示名を取得 (通知の差出人として使用)
    assigner_uid: str = after_data.get("updatedBy", "")
    assigner_name = _get_user_display_name(db, assigner_uid) if assigner_uid else ""

    title = "Todo が割り当てられました"
    if assigner_name:
        body = f"{assigner_name} さんから「{todo_title}」が割り当てられました"
    else:
        body = f"「{todo_title}」があなたに割り当てられました"

    result = send_notification(
        token=fcm_token,
        title=title,
        body=body,
        data={
            "type": "todo_assigned",
            "todoId": todo_id,
            "assignedTo": after_assigned_to,
        },
    )

    if result:
        logger.info(
            "Todo notification sent: todoId=%s, assignedTo=%s", todo_id, after_assigned_to
        )
    else:
        logger.error(
            "Failed to send todo notification: todoId=%s, assignedTo=%s",
            todo_id,
            after_assigned_to,
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
