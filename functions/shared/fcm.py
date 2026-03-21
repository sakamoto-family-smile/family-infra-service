import logging
from typing import Optional

import firebase_admin
from firebase_admin import messaging

logger = logging.getLogger(__name__)


def _ensure_app_initialized():
    """firebase_admin が未初期化の場合に初期化する。"""
    if not firebase_admin._apps:
        firebase_admin.initialize_app()


def send_notification(
    token: str,
    title: str,
    body: str,
    data: Optional[dict] = None,
) -> Optional[str]:
    """
    FCM プッシュ通知を単一デバイストークンへ送信する。

    Args:
        token: FCM デバイストークン
        title: 通知タイトル
        body: 通知本文
        data: 追加データペイロード (文字列キー・文字列値の辞書)

    Returns:
        FCM メッセージ ID (送信成功時)、失敗時は None
    """
    if data is None:
        data = {}

    _ensure_app_initialized()

    # data の値はすべて文字列である必要がある
    str_data = {k: str(v) for k, v in data.items()}

    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        data=str_data,
        token=token,
    )

    try:
        response = messaging.send(message)
        logger.info("FCM notification sent successfully: %s", response)
        return response
    except messaging.UnregisteredError:
        logger.warning("FCM token is unregistered: %s", token)
    except messaging.SenderIdMismatchError:
        logger.warning("FCM sender ID mismatch for token: %s", token)
    except Exception as exc:
        logger.error("Failed to send FCM notification to %s: %s", token, exc)

    return None


def send_multicast_notification(
    tokens: list[str],
    title: str,
    body: str,
    data: Optional[dict] = None,
) -> dict:
    """
    FCM プッシュ通知を複数デバイストークンへ一括送信する。

    Args:
        tokens: FCM デバイストークンのリスト
        title: 通知タイトル
        body: 通知本文
        data: 追加データペイロード (文字列キー・文字列値の辞書)

    Returns:
        {"success_count": int, "failure_count": int} の辞書
    """
    if not tokens:
        return {"success_count": 0, "failure_count": 0}

    if data is None:
        data = {}

    _ensure_app_initialized()

    str_data = {k: str(v) for k, v in data.items()}

    multicast_message = messaging.MulticastMessage(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        data=str_data,
        tokens=tokens,
    )

    try:
        response = messaging.send_each_for_multicast(multicast_message)
        logger.info(
            "Multicast FCM: success=%d, failure=%d",
            response.success_count,
            response.failure_count,
        )
        for idx, result in enumerate(response.responses):
            if not result.success:
                logger.warning(
                    "FCM send failed for token[%d]: %s", idx, result.exception
                )
        return {
            "success_count": response.success_count,
            "failure_count": response.failure_count,
        }
    except Exception as exc:
        logger.error("Failed to send multicast FCM notification: %s", exc)
        return {"success_count": 0, "failure_count": len(tokens)}
