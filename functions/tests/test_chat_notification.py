"""Tests for chat_notification Cloud Function."""
import sys
import os
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def _make_snapshot(data: dict | None) -> MagicMock:
    snapshot = MagicMock()
    snapshot.to_dict.return_value = data
    return snapshot


def _make_event(snapshot, room_id: str = "room-1") -> MagicMock:
    event = MagicMock()
    event.data = snapshot
    event.params = {"roomId": room_id}
    return event


class TestGetUserDisplayName:
    def test_returns_display_name(self):
        from chat_notification.main import _get_user_display_name

        db = MagicMock()
        doc = MagicMock()
        doc.exists = True
        doc.to_dict.return_value = {"displayName": "Taro"}
        db.collection.return_value.document.return_value.get.return_value = doc

        result = _get_user_display_name(db, "uid-1")
        assert result == "Taro"

    def test_returns_empty_when_user_not_found(self):
        from chat_notification.main import _get_user_display_name

        db = MagicMock()
        doc = MagicMock()
        doc.exists = False
        db.collection.return_value.document.return_value.get.return_value = doc

        result = _get_user_display_name(db, "uid-missing")
        assert result == ""

    def test_returns_empty_on_exception(self):
        from chat_notification.main import _get_user_display_name

        db = MagicMock()
        db.collection.return_value.document.return_value.get.side_effect = Exception("DB error")

        result = _get_user_display_name(db, "uid-error")
        assert result == ""


class TestGetFcmToken:
    def test_returns_token(self):
        from chat_notification.main import _get_fcm_token

        db = MagicMock()
        doc = MagicMock()
        doc.exists = True
        doc.to_dict.return_value = {"fcmToken": "token-abc"}
        db.collection.return_value.document.return_value.get.return_value = doc

        result = _get_fcm_token(db, "uid-1")
        assert result == "token-abc"

    def test_returns_empty_when_no_token(self):
        from chat_notification.main import _get_fcm_token

        db = MagicMock()
        doc = MagicMock()
        doc.exists = True
        doc.to_dict.return_value = {}
        db.collection.return_value.document.return_value.get.return_value = doc

        result = _get_fcm_token(db, "uid-no-token")
        assert result == ""

    def test_returns_empty_on_exception(self):
        from chat_notification.main import _get_fcm_token

        db = MagicMock()
        db.collection.return_value.document.return_value.get.side_effect = Exception("timeout")

        result = _get_fcm_token(db, "uid-err")
        assert result == ""


class TestOnMessageCreated:
    def test_skips_when_snapshot_is_none(self):
        from chat_notification.main import on_message_created

        event = _make_event(None)
        # Should return without raising
        with patch("chat_notification.main.get_firestore_client") as mock_db:
            on_message_created(event)
            mock_db.assert_not_called()

    def test_skips_when_message_data_empty(self):
        from chat_notification.main import on_message_created

        snapshot = _make_snapshot({})
        event = _make_event(snapshot)

        with patch("chat_notification.main.get_firestore_client") as mock_db:
            on_message_created(event)
            mock_db.assert_not_called()

    def test_sends_notification_to_other_members(self):
        from chat_notification.main import on_message_created

        snapshot = _make_snapshot({
            "senderUid": "sender-uid",
            "text": "Hello!",
        })
        event = _make_event(snapshot, room_id="room-1")

        mock_db = MagicMock()
        # Room doc with two members
        room_doc = MagicMock()
        room_doc.exists = True
        room_doc.to_dict.return_value = {"memberUids": ["sender-uid", "other-uid"]}
        mock_db.collection.return_value.document.return_value.get.side_effect = [
            # sender display name
            MagicMock(exists=True, to_dict=lambda: {"displayName": "Sender"}),
            room_doc,
            # fcm token for other-uid
            MagicMock(exists=True, to_dict=lambda: {"fcmToken": "token-other"}),
        ]

        with patch("chat_notification.main.get_firestore_client", return_value=mock_db), \
             patch("chat_notification.main.send_multicast_notification",
                   return_value={"success_count": 1, "failure_count": 0}) as mock_fcm:
            on_message_created(event)
            mock_fcm.assert_called_once()

    def test_skips_when_no_other_members(self):
        from chat_notification.main import on_message_created

        snapshot = _make_snapshot({
            "senderUid": "only-uid",
            "text": "Hello!",
        })
        event = _make_event(snapshot, room_id="room-1")

        mock_db = MagicMock()
        room_doc = MagicMock()
        room_doc.exists = True
        room_doc.to_dict.return_value = {"memberUids": ["only-uid"]}

        sender_doc = MagicMock()
        sender_doc.exists = True
        sender_doc.to_dict.return_value = {"displayName": "Only User"}

        mock_db.collection.return_value.document.return_value.get.side_effect = [
            sender_doc,
            room_doc,
        ]

        with patch("chat_notification.main.get_firestore_client", return_value=mock_db), \
             patch("chat_notification.main.send_multicast_notification") as mock_fcm:
            on_message_created(event)
            mock_fcm.assert_not_called()
