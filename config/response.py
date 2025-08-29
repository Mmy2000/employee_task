from rest_framework.response import Response


class CustomResponse(Response):
    def __init__(
        self,
        data=None,
        status=None,
        message=None,
        template_name=None,
        headers=None,
        exception=False,
        content_type=None,
        pagination=None,  # ✅ keep here if you want, but don’t pass to super()
    ):
        non_field_keys = ["non_field_errors", "detail", "details"]

        if status and status < 400:
            message = message if message else "Success"
        else:
            if not message:
                if isinstance(data, dict):
                    for key in data:
                        if key in non_field_keys:
                            message = data[key]
                            if isinstance(message, list):
                                message = message[0]
                            break
                    else:
                        error_key = next(iter(data))
                        error_message = data[error_key]
                        if isinstance(error_message, list):
                            message = error_message[0]
                        elif isinstance(error_message, str):
                            message = error_message
                        else:
                            message = str(error_message)
                elif isinstance(data, list):
                    error_message = data[0]
                    if isinstance(error_message, dict):
                        for key in error_message:
                            if key in non_field_keys:
                                message = error_message[key]
                                if isinstance(message, list):
                                    message = message[0]
                                break
                        else:
                            error_key = next(iter(error_message))
                            message = error_message[error_key]
                            if isinstance(message, list):
                                message = message[0]
                            elif not isinstance(message, str):
                                message = str(message)
                    elif isinstance(error_message, str):
                        message = error_message
                    else:
                        message = str(error_message)
                else:
                    message = str(data)
                data = {}

        custom_data = {
            "status_code": int(status) if status else None,
            "data": data,
            "message": message,
        }

        # ✅ Add pagination info inside response body
        if pagination:
            custom_data["pagination"] = pagination

        super().__init__(
            custom_data,
            status=status,
            template_name=template_name,
            headers=headers,
            exception=exception,
            content_type=content_type,
        )
