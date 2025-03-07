"""
This module provides the implementation of the JSONLogger class.
It includes methods for logging in JSON format with OpenTelemetry and Loki support.
"""

import json
import logging
from logging.handlers import RotatingFileHandler
import datetime
import requests
from opentelemetry import trace


class JSONLogger:
    """
    A custom logger that logs messages in JSON format, including OpenTelemetry context.

    Attributes:
        logger (logging.Logger): The standard Python logger instance.
        loki_url (str, optional): The URL of the Loki instance to send logs to.
        loki_labels (dict, optional): Labels to be added to the log sent to Loki.
    """

    def __init__(
        self,
        log_file=None,
        max_bytes=1000000,
        backup_count=3,
        loki_url=None,
        loki_labels=None,
    ):
        # pylint: disable=R0913
        # pylint: disable=R0917
        """
        JSON Logger with Loki and OpenTelemetry support.

        :param log_file: File to store logs (if None, logs to stdout).
        :param max_bytes: Max log file size before rotation (default: 1MB).
        :param backup_count: Number of backup log files to keep.
        :param loki_url: Loki HTTP endpoint (if None, logs are not sent to Loki).
        :param loki_labels: Dictionary of labels for Loki logs.
            Ignored if loki_url is None.
        """
        self.log_file = log_file
        self.loki_url = loki_url
        self.loki_labels = (
            loki_labels if loki_url else None
        )  # Only use labels if Loki is enabled
        self.logger = logging.getLogger("JSONLogger")
        self.logger.setLevel(logging.INFO)

        if log_file:
            handler = RotatingFileHandler(
                log_file, maxBytes=max_bytes, backupCount=backup_count
            )
        else:
            handler = logging.StreamHandler()

        handler.setFormatter(
            logging.Formatter("%(message)s")
        )  # Store logs as plain JSON lines
        self.logger.addHandler(handler)

    def log(self, level, message, **kwargs):
        """
        Logs a message in JSON format, including OpenTelemetry trace context.
        """
        current_span = trace.get_current_span()
        trace_id = current_span.get_span_context().trace_id
        span_id = current_span.get_span_context().span_id

        log_entry = {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "level": level.upper(),
            "message": message,
            "trace_id": f"{trace_id:032x}" if trace_id else None,
            "span_id": f"{span_id:016x}" if span_id else None,
            **kwargs,
        }

        log_json = json.dumps(log_entry)
        self.logger.log(getattr(logging, level.upper(), logging.INFO), log_json)

        if self.loki_url:
            self.send_to_loki(log_json)

    def send_to_loki(self, log_json):
        """
        Sends logs to Loki via HTTP API, only if Loki is enabled.
        """
        if not self.loki_url or not self.loki_labels:
            return  # Do nothing if Loki is not configured

        try:
            log_line = {
                "streams": [
                    {
                        "stream": self.loki_labels,
                        "values": [
                            [
                                str(int(datetime.datetime.utcnow().timestamp() * 1e9)),
                                log_json,
                            ]
                        ],
                    }
                ]
            }
            headers = {"Content-Type": "application/json"}
            response = requests.post(
                self.loki_url, data=json.dumps(log_line), headers=headers, timeout=10
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            self.logger.error("Failed to send log to Loki: %s", str(e))

    def info(self, message, **kwargs):
        """
        Logs a message with level 'INFO'.
        Args:
            message (str): The log message.
            **kwargs: Additional key-value pairs to include in the log entry.
        """
        self.log("INFO", message, **kwargs)

    def debug(self, message, **kwargs):
        """
        Logs a message with level 'DEBUG'.
        Args:
            message (str): The log message.
            **kwargs: Additional key-value pairs to include in the log entry.
        """
        self.log("DEBUG", message, **kwargs)

    def error(self, message, **kwargs):
        """
        Logs a message with level 'ERROR'.
        Args:
            message (str): The log message.
            **kwargs: Additional key-value pairs to include in the log entry.
        """
        self.log("ERROR", message, **kwargs)


# Example usage
if __name__ == "__main__":
    # Case 1: Logs only to file (no Loki)
    logger1 = JSONLogger(log_file="app.log")
    logger1.info("This goes to file only", module="main")

    # Case 2: Logs to file and sends to Loki
    logger2 = JSONLogger(
        log_file="app.log",
        loki_url="http://localhost:3100/loki/api/v1/push",
        loki_labels={"job": "my_app", "module": "main"},
    )
    logger2.info("This goes to Loki and file", module="main")
