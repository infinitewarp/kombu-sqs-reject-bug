# README

This is a minimal Django project + app that demonstrates a SQS message rejection bug in Celery Kombu 5.1.0.

If a Celery worker tries to handle a task via SQS, but the underlying function for that task is not available and the Celery SQS config has no `predefined_queues`, the worker crashes out due to `AttributeError` being raised deep within Kombu's SQS Channel.

This is a major problem if you have multiple tasks being sent to the default `celery` queue. One bad task can crash the whole worker and stop later tasks from running.

Probable fix is [kombu/pull/1372](https://github.com/celery/kombu/pull/1372).

## How to demonstrate this bug

[This asciinema recording](https://asciinema.org/a/431428) follows all the same steps described below.

1. Set up the environment

    1. `python -m venv .venv && source .venv/bin/activate`
    2. `pip install -r requirements.txt && python -c 'import pycurl'`
    3. If the above python command fails with `ImportError`, see "Troubleshooting pycurl" below before proceeding.
    4. Get an AWS profile or keys that have read/write access to SQS

2. Spawn the task

    ```sh
    export AWS_PROFILE=dev01  # your AWS profile, or just set the keys directly in the env
    export DJANGO_SETTINGS_MODULE=kombu_bug_project.settings_bug
    ./kombu_bug_project/manage.py shell
    ```

    ```python
    from kombu_bug_app import tasks
    tasks.task_b.delay()
    # multiple instance so we can see that the worker crashes immediately after the first
    tasks.task_b.delay()
    tasks.task_b.delay()
    ```

3. Run the Celery worker with the underlying task function hidden

    ```sh
    export AWS_PROFILE=dev01  # your AWS profile, or just set the keys directly in the env
    export DJANGO_SETTINGS_MODULE=kombu_bug_project.settings_bug
    export HIDE_TASK_FUNCTION=True
    celery --app kombu_bug_project --workdir kombu_bug_project \
        worker --concurrency 1 --task-events --queues celery

4. Observe the *unhandled* exception! It should end with something like this:

    ```
    File "/Users/infinitewarp/projects/kombu-bug/.venv/lib/python3.8/site-packages/kombu/transport/SQS.py", line 176, in reject
        self._extract_backoff_policy_configuration_and_message(
    File "/Users/infinitewarp/projects/kombu-bug/.venv/lib/python3.8/site-packages/kombu/transport/SQS.py", line 190, in _extract_backoff_policy_configuration_and_message
        queue_config = self.channel.predefined_queues.get(routing_key, {})
    AttributeError: 'NoneType' object has no attribute 'get'
    ```
    
    If you check the AWS SQS console (or use the `aws` cli), you will observe that only the *first* message was read before the Celery worker crashed.


## Troubleshooting pycurl

pycurl may not build and install correctly by default, and you may need to give some lib paths. If the `import pycurl` command raises `ImportError` mentioning "libcurl link-time ssl backend (openssl)", on macOS with homebrew, try the following steps to rebuild and reinstall pycurl:

```sh
brew update
brew install openssl curl-openssl

BREW_PATH=$(brew --prefix)
export LDFLAGS="-L${BREW_PATH}/opt/curl/lib -L${BREW_PATH}/opt/openssl/lib"
export CPPFLAGS="-I${BREW_PATH}/opt/curl/include -I${BREW_PATH}/opt/openssl/include"
export PYCURL_SSL_LIBRARY="openssl"

pip uninstall -y pycurl && pip install -r requirements.txt
```
