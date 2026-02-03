import os

from celery import Celery
from kombu import Queue

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Topic.settings")

app = Celery("Topic")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=100,
    task_default_queue="email.default",
    task_queues=(
        Queue("email.default", routing_key="email.default"),
        Queue("email.confirm", routing_key="email.confirm"),
        Queue("email.reset", routing_key="email.reset"),
        # DLQ очереди
        Queue("email.confirm.dlq"),
        Queue("email.reset.dlq"),
    ),
)

app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
