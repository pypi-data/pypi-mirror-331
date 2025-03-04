# Copyright (c) 2023-2024, NVIDIA CORPORATION.  All rights reserved.
"""This module contains functionality to log and track requests."""

import functools
import json
import logging
import os
import tempfile
from typing import Callable, Optional

from bionemo.api.request_id import REQUEST_STATUS_OPTIONS, RequestId

_JSON_LOGGER_NAME = "JSON_logger"


class _JSONRequestFormatter(logging.Formatter):
    """Simple line-delimited JSON Wrapper for log file output. Does not contain most of the usual logging metadata."""

    def format(self, record):
        log_data = {
            "timestamp": record.created,
            "request": record.msg,
        }
        return json.dumps(log_data)


def load_log_file(file: str):
    """Parse a JSONL log file, returning each line as a list entry in dictionary form."""
    with open(file, "r") as f:
        return [json.loads(line) for line in f]


def set_request_log_file(do_logging: bool, file_path: Optional[str] = None, append: bool = True) -> str:
    """Initialize request logging. If not set prior to logging, will be invoked with default options.

    Args:
        do_logging: Whether to write the log file or not
        file_path: Optional path to a log file to create, if not set will create a temporary file
        append: If file is set and exists, appends to that file if True, overrides if False
    Returns:
        The path to the log file
    """
    logger = logging.getLogger(_JSON_LOGGER_NAME)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    if not do_logging:
        handler = logging.NullHandler()
        logger.addHandler(handler)
        return ""

    if not file_path:
        f = tempfile.NamedTemporaryFile(prefix="bionemo_python_client_service_log_", suffix=".json", delete=False)
        file_path = f.name
    if os.path.isfile(file_path) and not append:
        open(file_path, "w").close()
    logging.debug(f"Logging requests to {file_path}")
    file_handler = logging.FileHandler(file_path)
    formatter = _JSONRequestFormatter()
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return file_path


def log_request_status(corr_id: str, action: str, model: str, status: str):
    """Log a single request status.

    To specify log location, call set_request_log_file() prior to using the service.

    Args:
        corr_id: Correlation ID
        action: Detail on the request, such as "request_inference" or "check_request_status"
        model: Name of the model for this request
        status: Should be one of DONE, CREATED, PROCESSING, SUBMITTED, ERROR
    Returns:
        Function wrapper to log request info
    """
    if status not in REQUEST_STATUS_OPTIONS:
        logging.warning(
            f"Request with corr_id:{corr_id}, model:{model} has an invalid status '{status}'."
            f"Options are {REQUEST_STATUS_OPTIONS}"
        )
    logger = logging.getLogger(_JSON_LOGGER_NAME)
    if not logger.hasHandlers():
        set_request_log_file(do_logging=True)
    msg = {"corr_id": corr_id, "action": action, "model": model, "status": status}
    logger.info(msg)
