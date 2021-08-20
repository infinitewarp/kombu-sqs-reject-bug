"""Module that may or may not have `task_b` defined at runtime."""

from django.conf import settings

if not settings.HIDE_TASK_FUNCTION:
    from celery import shared_task

    @shared_task
    def task_b():
        print("b")
