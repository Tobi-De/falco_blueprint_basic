# pylint: disable=invalid-name
# Gunicorn configuration file
# https://docs.gunicorn.org/en/stable/configure.html#configuration-file
# https://docs.gunicorn.org/en/stable/settings.html
# https://adamj.eu/tech/2021/12/29/set-up-a-gunicorn-configuration-file-and-test-it/
from __future__ import annotations

import multiprocessing
from pathlib import Path

bind = "0.0.0.0:8000"

chdir = str(Path(__file__).parent.parent)

workers = multiprocessing.cpu_count() * 2 + 1

max_requests = 1000
max_requests_jitter = 50

accesslog = "-"
errorlog = "-"

timeout = 120