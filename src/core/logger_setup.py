import base64
import datetime
import json
import logging
import logging.config
from logging.handlers import QueueHandler, QueueListener
from queue import Queue
from typing import Any

import requests

from core.settings import settings

logger = logging.getLogger(__name__)


def setup_logging():
    log_queue = Queue(-1)

    handlers: list[logging.Handler] = []

    if settings.GRAFANA_LOKI_URL:
        grafana_handler = GrafanaLokiHandler(
            loki_url=settings.GRAFANA_LOKI_URL,
            username=settings.GRAFANA_API_USERNAME,
            password=settings.GRAFANA_API_PASSWORD,
            job_name="fastapi-app"
        )
        grafana_handler.setLevel(settings.LOG_LEVEL)
        grafana_handler.setFormatter(JsonFormatter())
        handlers.append(grafana_handler)

    # Console handler (for local development)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(settings.LOG_LEVEL)
    console_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(console_formatter)
    handlers.append(console_handler)

    queue_handler = QueueHandler(log_queue)

    listener = QueueListener(
        log_queue,
        *handlers,
        respect_handler_level=True
    )
    listener.start()

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(queue_handler)

    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "loggers": {
            "urllib3": {
                "level": "WARNING",
            },
            "urllib3.connectionpool": {
                "level": "WARNING",
            },
        },
    }

    logging.config.dictConfig(logging_config)

    return listener


class GrafanaLokiHandler(logging.Handler):
    def __init__(self, loki_url: str, username: str, password: str, job_name: str = "fastapi", timeout: int = 5):
        super().__init__()
        self.loki_url = loki_url
        self.username = username
        self.password = password
        self.job_name = job_name
        self.timeout = timeout
        self.failed_attempts = 0
        self.max_log_failures = 10

        credentials = base64.b64encode(f"{username}:{password}".encode()).decode()

        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Basic {credentials}"
        }

    def emit(self, record: logging.LogRecord):
        try:
            log_entry = self.format(record)
            timestamp = str(int(datetime.datetime.now().timestamp() * 1e9))

            payload: dict[str, Any] = {
                "streams": [{
                    "stream": {
                        "job": self.job_name,
                        "level": record.levelname.lower(),
                        "logger": record.name,
                    },
                    "values": [[timestamp, log_entry]]
                }]
            }

            response = requests.post(
                self.loki_url,
                json=payload,
                headers=self.headers,
                timeout=self.timeout
            )

            if response.status_code == 204:
                self.failed_attempts = 0
            else:
                if self.failed_attempts < self.max_log_failures:
                    logger.error(f"[Grafana Loki] HTTP {response.status_code}: {response.text[:200]}")
                    self.failed_attempts += 1

        except requests.exceptions.Timeout:
            if self.failed_attempts < self.max_log_failures:
                logger.error(f"[Grafana Loki] Timeout: Could not connect to {self.loki_url}")
                self.failed_attempts += 1
        except requests.exceptions.ConnectionError as e:
            if self.failed_attempts < self.max_log_failures:
                logger.error(f"[Grafana Loki] Connection error: {str(e)[:100]}")
                self.failed_attempts += 1
        except Exception as e:
            if self.failed_attempts < self.max_log_failures:
                logger.error(f"[Grafana Loki] Error: {str(e)[:100]}")
                self.failed_attempts += 1
            self.handleError(record)


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.datetime.now().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        if hasattr(record, "trace_id"):
            log_data["trace_id"] = record.trace_id
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id

        return json.dumps(log_data, default=str, ensure_ascii=False)
