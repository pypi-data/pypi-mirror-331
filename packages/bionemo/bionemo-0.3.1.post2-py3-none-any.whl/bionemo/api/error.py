# Copyright (c) 2023-2024, NVIDIA CORPORATION.  All rights reserved.
class ApiKeyNotSetError(Exception):
    pass


class ServiceError(Exception):

    SOLUTION = ""

    def __init__(self, status_code, reason, decoded_content):
        self.message = f"""Request failed with HTTP Status Code {status_code} {reason} **Solution**: {self.SOLUTION} **Full response**: {decoded_content}"""
        super().__init__(self.message)

    def __str__(self):
        return self.message


class ServerSideError(ServiceError):
    SOLUTION = "Server is unable to handle your request right now. Please retry your request after a brief wait. If this problem persists, please contact Bionemo Service Team"


class ClientSideError(ServiceError):
    pass


class IncorrectParamsError(ClientSideError):
    SOLUTION = "Please update the parameters of your request based on the message"


class ModelOrCustomizationNotFoundError(ClientSideError):
    SOLUTION = "Please check that the model name is valid. To get the list of available models, run 'nemollm list_models' and use the name of a model."


class RequestIDNotFoundError(ClientSideError):
    SOLUTION = "Check request ID."

    def __init__(self, correlation_id, status_code, reason, decoded_content):
        super().__init__(status_code, reason, decoded_content)
        self.message = f"""Request failed with HTTP Status Code {status_code} {reason}, request ID {correlation_id} not found **Solution**: {self.SOLUTION} **Full response**: {decoded_content}"""


class AuthorizationError(ClientSideError):
    SOLUTION = (
        "Please check that you are authorized to use the service/model with the correct NGC API KEY and access rights"
    )


class TooManyRequestsError(ClientSideError):
    SOLUTION = "Please reduce the rate that you are sending requests or ask for a rate limit increase"


class BadRequestId(ClientSideError):
    def __init__(self, badType):
        self.message = f"""Request ID must be a string or RequestId; it was a {str(badType)}."""

    SOLUTION = "Supply a valid correlation ID or RequestId"
