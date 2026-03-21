"""Tests for reminder_dispatcher Cloud Function."""
import json
import sys
import os
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from reminder_dispatcher.main import app as flask_app


@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as c:
        yield c


def _post(client, body: dict):
    return client.post(
        "/dispatch_reminder",
        data=json.dumps(body),
        content_type="application/json",
    )


class TestDispatchReminder:
    def test_returns_400_when_event_id_missing(self, client):
        resp = _post(client, {})
        assert resp.status_code == 400
        assert b"event_id" in resp.data

    def test_returns_404_when_event_not_found(self, client):
        mock_db = MagicMock()
        event_doc = MagicMock()
        event_doc.exists = False
        mock_db.collection.return_value.document.return_value.get.return_value = event_doc

        with patch("reminder_dispatcher.main.get_firestore_client", return_value=mock_db):
            resp = _post(client, {"event_id": "nonexistent-event"})

        assert resp.status_code == 404

    def test_returns_200_with_no_attendees(self, client):
        mock_db = MagicMock()
        event_doc = MagicMock()
        event_doc.exists = True
        event_doc.to_dict.return_value = {
            "title": "Team Meeting",
            "attendeeUids": [],
        }
        mock_db.collection.return_value.document.return_value.get.return_value = event_doc

        with patch("reminder_dispatcher.main.get_firestore_client", return_value=mock_db):
            resp = _post(client, {"event_id": "event-1"})

        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data["message"] == "no attendees"

    def test_sends_notifications_to_attendees(self, client):
        mock_db = MagicMock()
        event_doc = MagicMock()
        event_doc.exists = True
        event_doc.to_dict.return_value = {
            "title": "Family Dinner",
            "startAt": None,
            "attendeeUids": ["uid-1", "uid-2"],
        }

        token_doc_1 = MagicMock()
        token_doc_1.exists = True
        token_doc_1.to_dict.return_value = {"fcmToken": "token-1"}

        token_doc_2 = MagicMock()
        token_doc_2.exists = True
        token_doc_2.to_dict.return_value = {"fcmToken": "token-2"}

        mock_db.collection.return_value.document.return_value.get.side_effect = [
            event_doc,
            token_doc_1,
            token_doc_2,
        ]

        with patch("reminder_dispatcher.main.get_firestore_client", return_value=mock_db), \
             patch("reminder_dispatcher.main.send_multicast_notification",
                   return_value={"success_count": 2, "failure_count": 0}) as mock_fcm:
            resp = _post(client, {"event_id": "event-1"})

        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data["success_count"] == 2
        mock_fcm.assert_called_once()

    def test_returns_200_when_no_fcm_tokens(self, client):
        mock_db = MagicMock()
        event_doc = MagicMock()
        event_doc.exists = True
        event_doc.to_dict.return_value = {
            "title": "Event",
            "attendeeUids": ["uid-no-token"],
        }

        user_doc = MagicMock()
        user_doc.exists = True
        user_doc.to_dict.return_value = {}  # no fcmToken

        mock_db.collection.return_value.document.return_value.get.side_effect = [
            event_doc,
            user_doc,
        ]

        with patch("reminder_dispatcher.main.get_firestore_client", return_value=mock_db):
            resp = _post(client, {"event_id": "event-2"})

        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data["message"] == "no fcm tokens"

    def test_returns_500_on_firestore_error(self, client):
        mock_db = MagicMock()
        mock_db.collection.return_value.document.return_value.get.side_effect = Exception("DB down")

        with patch("reminder_dispatcher.main.get_firestore_client", return_value=mock_db):
            resp = _post(client, {"event_id": "event-err"})

        assert resp.status_code == 500
