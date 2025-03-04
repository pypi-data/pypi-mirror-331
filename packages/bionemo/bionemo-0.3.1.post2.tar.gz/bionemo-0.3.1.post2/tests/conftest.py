# Copyright (c) 2023-2024, NVIDIA CORPORATION.  All rights reserved.

import os
import pytest

from bionemo.api import BionemoClient


@pytest.fixture(
    scope="module",
    # First parameter is API endpoint.
    # Second parameter is the envvar which hold the API key (The constructor uses NGC_API_KEY
    # by default, however we add configurability here so we can use separate CI gitlab var
    # for staging environment.
    # To test against prod, set the environment variable `HOST_ADDRESS` to "https://api.bionemo.ngc.nvidia.com/v1"
    # And set your API KEY `NGC_API_KEY`
    params=[
        [os.getenv('HOST_ADDRESS', "https://stg.bionemo.ngc.nvidia.com/v1")],
    ],
)
def make_python_client(request):
    """
    A parameterized function to create python clients for different API endpoints.

    Returns:
        bionemo.BionemoClient: the python client
    """
    if request.param[0] == "https://stg.bionemo.ngc.nvidia.com/v1":
        api_host = request.param[0]
        if not "NGC_API_KEY_STAGING" in os.environ:
            raise ValueError(
                "Missing environment variable NGC_API_KEY_STAGING which is required to"
                "run unit tests against the staging server."
            )
        api_key = os.environ['NGC_API_KEY_STAGING']
    else:
        api_host = "https://api.bionemo.ngc.nvidia.com/v1"
        if not "NGC_API_KEY" in os.environ:
            raise ValueError(
                "Missing environment variable NGC_API_KEY which is required to"
                "run unit tests against the prod server."
            )
        api_key = os.environ['NGC_API_KEY']

    def maker(file_path=None, append=True):
        return BionemoClient(
            api_host=api_host,
            api_key=api_key,
            do_logging=True,
            log_file_path=file_path,
            log_file_append=append,
        )

    return maker
