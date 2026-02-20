from locust import HttpUser, task, between
import time
import psycopg2
from consumer.config import settings
import random

class KafkaPipelineUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        self.db = psycopg2.connect(settings.LOCAL_DATABASE_SYNC_URL)

    def on_stop(self):
        self.db.close()

    @task
    def send_event_and_verify(self):
        event_type = random.choice(["io", "cpu"])
        # 1. Отправляем событие через API
        with self.client.post(
            "/api/v1/events",
            json={
                "event_type": event_type,
                "payload": {"some_info": "here", "another_one_info": "and_here"}
            },
            catch_response=True
        ) as response:
            if response.status_code != 201:
                response.failure(f"API failed: {response.status_code}")
                return
            else:
                event_id = response.json().get("id")
                if not event_id:
                    response.failure("No event ID returned")
                    return

        processed = self._wait_until_processed(event_id, timeout=10)

        if processed:
            # Репортим успех с временем обработки
            self.environment.events.request.fire(
                request_type="PIPELINE",
                name="end_to_end_latency",
                response_time=processed["latency_ms"],
                response_length=0,
            )
        else:
            self.environment.events.request.fire(
                request_type="PIPELINE",
                name="end_to_end_latency",
                response_time=10000,
                response_length=0,
                exception=Exception("Timeout: message not processed"),
            )

    def _wait_until_processed(self, event_id: str, timeout: int) -> dict | None:
        start = time.time()
        cursor = self.db.cursor()

        while time.time() - start < timeout:
            cursor.execute(
                "SELECT status, processed_at FROM events WHERE id = %s",
                (event_id,)
            )
            row = cursor.fetchone()

            if row and row[0] == "processed":
                latency_ms = (time.time() - start) * 1000
                return {"latency_ms": latency_ms}

            time.sleep(0.2)  # polling каждые 200ms

        return None