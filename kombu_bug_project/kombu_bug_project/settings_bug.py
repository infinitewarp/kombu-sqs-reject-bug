from kombu_bug_project.settings import *

import environ
env = environ.Env()

INSTALLED_APPS = INSTALLED_APPS + ["kombu_bug_app"]

CELERY_BROKER_URL = env("CELERY_BROKER_URL", default="")
if not CELERY_BROKER_URL:
    import boto3
    from urllib.parse import quote

    session = boto3.Session()
    credentials = session.get_credentials()
    credentials = credentials.get_frozen_credentials()
    access_key = quote(credentials.access_key, safe="")
    secret_key = quote(credentials.secret_key, safe="")

    CELERY_BROKER_URL = f"sqs://{access_key}:{secret_key}@"


CELERY_BROKER_TRANSPORT_OPTIONS = {
    "queue_name_prefix": "kombu-bug",
    "region": "us-east-1",
}

HIDE_TASK_FUNCTION = env.bool("HIDE_TASK_FUNCTION", default=False)
