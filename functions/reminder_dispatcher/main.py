"""
Cloud Functions gen2 - HTTP トリガー (Cloud Tasks から呼び出される)
エンドポイント: POST /dispatch_reminder

リクエストボディ (JSON):
  {
    "event_id": "<Firestore イベントドキュメント ID>"
  }

処理:
  1. Firestore の events/{event_id} からイベント情報を取得
  2. イベントの参加者 (attendee_uids) の FCM トークンを収集
  3. FCM でリマインダー通知を一括送信
  4. HTTP 200 を返す
"""

import json
import logging
import os
import sys

# shared モジュールを参照できるようにルートパスを追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import flask

from shared.firestore_client import get_firestore_client
from shared.fcm import send_multicast_notification

logger = logging.getLogger(__name__)

app = flask.Flask(__name__)


@app.post("/dispatch_reminder")
def dispatch_reminder():
    """
    Cloud Tasks から呼び出される HTTP ハンドラー。
    イベント情報を Firestore から取得し、参加者へ FCM 通知を送信する。
    """
    # リクエストボディの解析
    try:
        body = flask.request.get_json(silent=True) or {}
    except Exception as exc:
        logger.error("Failed to parse request body: %s", exc)
        return flask.Response("Bad Request: invalid JSON body", status=400)

    event_id: str = body.get("event_id", "").strip()
    if not event_id:
        logger.warning("dispatch_reminder: event_id is missing in request body")
        return flask.Response("Bad Request: event_id is required", status=400)

    logger.info("dispatch_reminder called: event_id=%s", event_id)

    db = get_firestore_client()

    # Firestore からイベント情報を取得
    try:
        event_doc = db.collection("events").document(event_id).get()
    except Exception as exc:
        logger.error("Failed to fetch event document (event_id=%s): %s", event_id, exc)
        return flask.Response("Internal Server Error: failed to fetch event", status=500)

    if not event_doc.exists:
        logger.warning("Event document not found: %s", event_id)
        return flask.Response(f"Not Found: event '{event_id}' not found", status=404)

    event_data = event_doc.to_dict() or {}
    event_title: str = event_data.get("title", "イベント")
    event_start_at = event_data.get("startAt")  # Firestore Timestamp
    attendee_uids: list[str] = event_data.get("attendeeUids", [])

    if not attendee_uids:
        logger.info("No attendees for event_id=%s, nothing to notify", event_id)
        return flask.Response(
            json.dumps({"status": "ok", "message": "no attendees"}),
            status=200,
            content_type="application/json",
        )

    # 参加者の FCM トークンを収集
    fcm_tokens: list[str] = []
    for uid in attendee_uids:
        token = _get_fcm_token(db, uid)
        if token:
            fcm_tokens.append(token)

    if not fcm_tokens:
        logger.warning(
            "No FCM tokens found for any attendee of event_id=%s", event_id
        )
        return flask.Response(
            json.dumps({"status": "ok", "message": "no fcm tokens"}),
            status=200,
            content_type="application/json",
        )

    # 通知メッセージの構築
    title = f"リマインダー: {event_title}"
    if event_start_at:
        try:
            # Firestore Timestamp は datetime に変換可能
            dt = event_start_at.astimezone()
            time_str = dt.strftime("%m/%d %H:%M")
            body_text = f"{event_title} は {time_str} に予定されています"
        except Exception:
            body_text = f"{event_title} のリマインダーです"
    else:
        body_text = f"{event_title} のリマインダーです"

    # FCM 一括送信
    result = send_multicast_notification(
        tokens=fcm_tokens,
        title=title,
        body=body_text,
        data={
            "type": "event_reminder",
            "eventId": event_id,
        },
    )

    logger.info(
        "Reminder dispatched: event_id=%s, success=%d, failure=%d",
        event_id,
        result["success_count"],
        result["failure_count"],
    )

    response_body = {
        "status": "ok",
        "event_id": event_id,
        "success_count": result["success_count"],
        "failure_count": result["failure_count"],
    }
    return flask.Response(
        json.dumps(response_body),
        status=200,
        content_type="application/json",
    )


def _get_fcm_token(db, uid: str) -> str:
    """Firestore の users/{uid} から fcmToken を取得する。"""
    try:
        user_doc = db.collection("users").document(uid).get()
        if user_doc.exists:
            return (user_doc.to_dict() or {}).get("fcmToken", "")
    except Exception as exc:
        logger.error("Failed to fetch FCM token (uid=%s): %s", uid, exc)
    return ""


# Cloud Functions エントリポイント
# functions_framework または gunicorn から呼び出される
def main(request):
    """Cloud Functions HTTP エントリポイント。"""
    with app.test_request_context(
        path=request.path,
        method=request.method,
        data=request.get_data(),
        content_type=request.content_type,
        headers=dict(request.headers),
    ):
        return app.full_dispatch_request()
