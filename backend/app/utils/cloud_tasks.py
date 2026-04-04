import asyncio
import json
from datetime import datetime, timezone

from google.cloud import tasks_v2
from google.protobuf import timestamp_pb2


class CloudTasksClient:
    def __init__(self, project: str, location: str, queue: str) -> None:
        self.project = project
        self.location = location
        self.queue = queue
        self._client = tasks_v2.CloudTasksClient()
        self._queue_path = self._client.queue_path(project, location, queue)

    async def create_task(
        self,
        url: str,
        payload: dict,
        schedule_time: datetime | None = None,
    ) -> tasks_v2.Task:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None, self._create_task_sync, url, payload, schedule_time
        )

    def _create_task_sync(
        self,
        url: str,
        payload: dict,
        schedule_time: datetime | None,
    ) -> tasks_v2.Task:
        task: dict = {
            "http_request": {
                "http_method": tasks_v2.HttpMethod.POST,
                "url": url,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(payload).encode(),
                "oidc_token": {
                    "service_account_email": f"family-app@{self.project}.iam.gserviceaccount.com"
                },
            }
        }

        if schedule_time:
            ts = timestamp_pb2.Timestamp()
            ts.FromDatetime(
                schedule_time.astimezone(timezone.utc).replace(tzinfo=None)
            )
            task["schedule_time"] = ts

        return self._client.create_task(
            request={"parent": self._queue_path, "task": task}
        )
