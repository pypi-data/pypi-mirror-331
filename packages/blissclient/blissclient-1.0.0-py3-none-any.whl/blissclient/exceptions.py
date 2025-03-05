import json
from httpx import Response


class BlissRESTBaseException(Exception):
    """Base Bliss REST API Exception"""

    pass


class BlissRESTValidationError(BlissRESTBaseException):
    """Bliss REST API Parameter Validation Error"""

    pass


class BlissRESTNotFound(BlissRESTBaseException):
    """Bliss REST API Object Not Found"""

    pass


class BlissRESTTerminalBusy(BlissRESTBaseException):
    """Bliss REST API Terminal Busy"""

    pass


class BlissRESTException(BlissRESTBaseException):
    "Bliss REST API Exception (with traceback)"
    pass


class BlissRESTError(BlissRESTBaseException):
    "Bliss REST API Error"
    pass


class BlissRESTUnserialisableResponse(BlissRESTBaseException):
    "Bliss REST API Cannot Serialise Response"
    pass


class BlissRESTUnhandledException(BlissRESTBaseException):
    "Bliss REST API Unhandled Exception"
    pass


def parse_http_error_response(response: Response):
    try:
        error_json = response.json()
        if response.status_code == 422:
            # Direct pydantic validation error
            # [
            #   {
            #     "type": "int_parsing",
            #     "loc": [
            #       "h"
            #     ],
            #     "msg": "Input should be a valid integer, unable to parse string as an integer",
            #     "input": "string",
            #     "url": "https://errors.pydantic.dev/2.5/v/int_parsing"
            #   }
            # ]
            if isinstance(error_json, list) and "loc" in error_json[0]:
                first_error = error_json[0]
                raise BlissRESTValidationError(
                    f"Invalid parameters for `{first_error['loc']}`: {first_error['msg']}"
                )

            # Hardware is a special 422 case, as it is validated at runtime based on the object type
            else:
                raise BlissRESTValidationError(error_json["error"])

        if response.status_code == 400:
            raise BlissRESTError(error_json["error"])

        if response.status_code == 404:
            raise BlissRESTNotFound(error_json["error"])

        if response.status_code == 429:
            raise BlissRESTTerminalBusy(error_json["error"])

        if response.status_code == 500:
            raise BlissRESTException(
                f"{error_json['traceback']}\n{error_json['exception']}"
            )

        if response.status_code == 503:
            raise BlissRESTUnserialisableResponse(error_json["error"])

        raise BlissRESTUnhandledException(
            f"Response code: {response.status_code} - {error_json['error']}"
        )

    # No json body, probably a real 500 exception
    except json.decoder.JSONDecodeError:
        raise BlissRESTUnhandledException(
            f"Response code: {response.status_code} - {response.text}"
        )
