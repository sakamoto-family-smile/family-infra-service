"""Tests for todo_notification Cloud Function."""
import sys
import os
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def _make_change(before_data: dict, after_data: dict) -> MagicMock:
    before = MagicMock()
    before.to_dict.return_value = before_data

    after = MagicMock()
    after.to_dict.return_value = after_data

    change = MagicMock()
    change.before = before
    change.after = after
    return change


def _make_event(change, todo_id: str = "todo-1") -> MagicMock:
    event = MagicMock()
    event.data = change
    event.params = {"todoId": todo_id}
    return event


class TestGetFcmToken:
    def test_returns_token(self):
        from todo_notification.main import _get_fcm_token

        db = MagicMock()
        doc = MagicMock()
        doc.exists = True
        doc.to_dict.return_value = {"fcmToken": "token-xyz"}
        db.collection.return_value.document.return_value.get.return_value = doc

        result = _get_fcm_token(db, "uid-1")
        assert result == "token-xyz"

    def test_returns_empty_on_missing_token(self):
        from todo_notification.main import _get_fcm_token

        db = MagicMock()
        doc = MagicMock()
        doc.exists = True
        doc.to_dict.return_value = {}
        db.collection.return_value.document.return_value.get.return_value = doc

        result = _get_fcm_token(db, "uid-no-token")
        assert result == ""


class TestOnTodoUpdated:
    def test_skips_when_assigned_to_unchanged(self):
        from todo_notification.main import on_todo_updated

        change = _make_change(
            before_data={"assigned_to": "uid-a", "title": "Task"},
            after_data={"assigned_to": "uid-a", "title": "Task"},
        )
        event = _make_event(change)

        with patch("todo_notification.main.get_firestore_client") as mock_db:
            on_todo_updated(event)
            mock_db.assert_not_called()

    def test_skips_when_assigned_to_cleared(self):
        from todo_notification.main import on_todo_updated

        change = _make_change(
            before_data={"assigned_to": "uid-a"},
            after_data={"assigned_to": ""},
        )
        event = _make_event(change)

        with patch("todo_notification.main.get_firestore_client") as mock_db:
            on_todo_updated(event)
            mock_db.assert_not_called()

    def test_sends_notification_when_assigned_to_changed(self):
        from todo_notification.main import on_todo_updated

        change = _make_change(
            before_data={"assigned_to": "uid-old", "title": "Clean kitchen"},
            after_data={"assigned_to": "uid-new", "title": "Clean kitchen", "updatedBy": "uid-boss"},
        )
        event = _make_event(change, todo_id="todo-42")

        mock_db = MagicMock()
        token_doc = MagicMock()
        token_doc.exists = True
        token_doc.to_dict.return_value = {"fcmToken": "token-new"}

        assigner_doc = MagicMock()
        assigner_doc.exists = True
        assigner_doc.to_dict.return_value = {"displayName": "Boss"}

        mock_db.collection.return_value.document.return_value.get.side_effect = [
            token_doc,
            assigner_doc,
        ]

        with patch("todo_notification.main.get_firestore_client", return_value=mock_db), \
             patch("todo_notification.main.send_notification", return_value=True) as mock_send:
            on_todo_updated(event)
            mock_send.assert_called_once()
            call_kwargs = mock_send.call_args
            assert call_kwargs.kwargs["token"] == "token-new"

    def test_skips_when_no_fcm_token(self):
        from todo_notification.main import on_todo_updated

        change = _make_change(
            before_data={"assigned_to": "uid-old"},
            after_data={"assigned_to": "uid-new", "title": "Task"},
        )
        event = _make_event(change)

        mock_db = MagicMock()
        doc = MagicMock()
        doc.exists = True
        doc.to_dict.return_value = {}  # no fcmToken
        mock_db.collection.return_value.document.return_value.get.return_value = doc

        with patch("todo_notification.main.get_firestore_client", return_value=mock_db), \
             patch("todo_notification.main.send_notification") as mock_send:
            on_todo_updated(event)
            mock_send.assert_not_called()
