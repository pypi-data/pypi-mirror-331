# Copyright (c) 2023-2024, NVIDIA CORPORATION.  All rights reserved.
"""
Common response status checks.
"""

import logging
from http import HTTPStatus

from bionemo.api.error import (
    AuthorizationError,
    ClientSideError,
    IncorrectParamsError,
    RequestIDNotFoundError,
    ServerSideError,
    TooManyRequestsError,
)


class ResponseHandler:
    """
    At present just a container of static methods for checking response status.
    """

    @staticmethod
    def handle_response(response, stream=False):
        status_code = response.status_code

        is_binary_content = (
            response.headers.get("content-disposition", "").startswith("attachment")
            or response.headers.get("content-type") == "application/octet-stream"
        )

        if stream:
            decoded_content = "Streaming content"
        elif is_binary_content:
            decoded_content = "Binary content"
        else:
            decoded_content = response.content.decode()
        # successful
        if status_code < HTTPStatus.BAD_REQUEST:

            logging.info(
                f"Request succeeded with HTTP Status Code {status_code} {response.reason} Full response: {decoded_content}"
            )

        # client_side errors
        elif status_code < HTTPStatus.INTERNAL_SERVER_ERROR:
            if status_code == HTTPStatus.BAD_REQUEST:
                raise IncorrectParamsError(
                    status_code=status_code, reason=response.reason, decoded_content=decoded_content
                )
            elif status_code in [HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN]:
                raise AuthorizationError(
                    status_code=status_code, reason=response.reason, decoded_content=decoded_content
                )
            elif status_code == HTTPStatus.NOT_FOUND:
                # Pull the request ID out of the URL.
                path_url = response.request.path_url
                correlation_id = path_url[path_url.rfind("/") + 1 :]
                raise RequestIDNotFoundError(
                    correlation_id, status_code=status_code, reason=response.reason, decoded_content=decoded_content
                )
            elif status_code == HTTPStatus.TOO_MANY_REQUESTS:
                raise TooManyRequestsError(
                    status_code=status_code, reason=response.reason, decoded_content=decoded_content
                )
            else:
                raise ClientSideError(status_code=status_code, reason=response.reason, decoded_content=decoded_content)

        # server side errors
        else:
            raise ServerSideError(status_code=status_code, reason=response.reason, decoded_content=decoded_content)

    @staticmethod
    def post_process_generate_response(response, return_text_completion_only):
        if response.ok:
            response_json = response.json()
        else:
            response_json = {"status": "fail", "msg": str(response.content.decode())}

        if return_text_completion_only:
            return response_json["text"] if "text" in response_json else ""
        return response_json
