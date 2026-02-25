from locust import HttpUser, task, between
import time
import gevent
import psycopg2
from consumer.config import settings
import random
from psycopg2 import pool

_db_pool = pool.ThreadedConnectionPool(
    minconn=2,
    maxconn=10,
    dsn=settings.LOCAL_DATABASE_SYNC_URL
)

class KafkaPipelineUser(HttpUser):
    wait_time = between(1, 3)
    
    def _get_cursor(self):
        try:
            self.db.cursor().execute("SELECT 1")
        except psycopg2.OperationalError:
            self.db = _db_pool.getconn()
        return self.db.cursor()

    @task
    def send_event_and_verify(self):
        event_type = random.choice(["io", "cpu"])
        # event_type = "cpu"
        # start = time.time()
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

        # processed = self._wait_until_processed(event_id, timeout=10, start=start)

        # if processed:
        #     # Репортим успех с временем обработки
        #     self.environment.events.request.fire(
        #         request_type="PIPELINE",
        #         name="end_to_end_latency",
        #         response_time=processed["latency_ms"],
        #         response_length=0,
        #     )
        # else:
        #     self.environment.events.request.fire(
        #         request_type="PIPELINE",
        #         name="end_to_end_latency",
        #         response_time=10000,
        #         response_length=0,
        #         exception=Exception("Timeout: message not processed"),
        #     )

    def _wait_until_processed(self, event_id: str, timeout: int, start: float) -> dict | None:
        conn = _db_pool.getconn()
        try:
            with conn.cursor() as cursor:
                while time.time() - start < timeout:
                    cursor.execute(
                        "SELECT status, processed_at FROM events WHERE id = %s",
                        (event_id,)
                    )
                    row = cursor.fetchone()

                    if row and row[0] == "processed":
                        latency_ms = (time.time() - start) * 1000
                        return {"latency_ms": latency_ms}

                    gevent.sleep(0.2)  # polling каждые 200ms
        finally:
            _db_pool.putconn(conn)  # возвращаем сразу после использования
        return None