# Copyright (c) 2023-2024, NVIDIA CORPORATION.  All rights reserved.
"""
Created on May 3, 2023

@author: adunstan
"""
from typing import Set

# TODO: Request all possible return values from the server
REQUEST_STATUS_OPTIONS: Set[str] = {"DONE", "CREATED", "PROCESSING", "SUBMITTED", "ERROR", "UNKNOWN", "CANCELLED"}


class RequestId:
    """
    Everything we know about a request.  Which BioNeMo model_name, the correlation ID (lets
    us get the results) and timeout (if any).
    """

    def __init__(self, model_name: str, correlation_id: str, timeout=None, status=None):
        """
        Constructor.

        Args:
            model_name (str): Name of the model.  esmfold, moflow, protgpt2, etc.
            correlation_id (str): Correlation ID.  A UUID.
            timeout (int or flow): How long this call should wait before timing out.  In seconds.
                Will be None if unknown i.e. the RequestId came from a call BionemoClient.fetch_tasks().
            status (str or None): One of DONE, CREATED, SUBMITTED, PROCESSING or ERROR.  None, if unknown.
        """
        self.model_name = model_name
        self.correlation_id = correlation_id
        self.timeout = timeout
        self.status = status

    def __eq__(self, rhs):
        if not isinstance(rhs, RequestId):
            return False
        # A different timeout doesn't really make it a different RequestId.
        return rhs.model_name == self.model_name and rhs.correlation_id == self.correlation_id

    def __str__(self):
        return f"{self.model_name}:{self.correlation_id}"

    def __repr__(self):
        return f"{self.model_name}:{self.correlation_id}"
