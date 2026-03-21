from datetime import datetime, timedelta, timezone

from app.config import settings
from app.utils.cloud_tasks import CloudTasksClient


class NotificationService:
    def __init__(self) -> None:
        self.tasks_client = CloudTasksClient(
            project=settings.GCP_PROJECT_ID,
            location=settings.CLOUD_TASKS_LOCATION,
            queue=settings.CLOUD_TASKS_QUEUE,
        )

    async def schedule_reminder(
        self,
        event_id: str,
        start_at: datetime,
        reminder_minutes: int,
    ) -> None:
        schedule_time = start_at - timedelta(minutes=reminder_minutes)
        if schedule_time <= datetime.now(tz=timezone.utc):
            return

        await self.tasks_client.create_task(
            url=f"{settings.CLOUD_RUN_SERVICE_URL}/internal/reminders",
            payload={"event_id": event_id, "type": "calendar_reminder"},
            schedule_time=schedule_time,
        )

    async def schedule_todo_due_alert(
        self,
        todo_item_id: str,
        due_date: datetime,
        assigned_to: str,
    ) -> None:
        alert_time = due_date - timedelta(days=1)
        if alert_time <= datetime.now(tz=timezone.utc):
            return

        await self.tasks_client.create_task(
            url=f"{settings.CLOUD_RUN_SERVICE_URL}/internal/todo-alerts",
            payload={
                "todo_item_id": todo_item_id,
                "assigned_to": assigned_to,
                "type": "todo_due_alert",
            },
            schedule_time=alert_time,
        )
