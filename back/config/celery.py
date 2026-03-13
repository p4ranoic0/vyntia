"""Celery app configuration for RRHH intranet."""

import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

app = Celery("intranet_rrhh")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    """Debug helper task for local verification."""
    print(f"Request: {self.request!r}")
