"""Celery app for use in Django project."""

import django
from celery import Celery
from django.conf import settings

django.setup()

app = Celery("kombu_bug_app")
app.config_from_object("django.conf:settings", namespace="CELERY")
task_packages = ["kombu_bug_app.tasks"]
app.autodiscover_tasks(task_packages)

