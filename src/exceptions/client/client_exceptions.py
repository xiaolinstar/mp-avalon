from ..base import ClientException


class ParamValidationError(ClientException):
    def __init__(self, message: str, details: dict = None, http_status: int = 400):
        super().__init__(
            message=message, 
            error_code="VALIDATION-PARAM-001", 
            details=details,
            http_status=http_status
        )


class InvalidCommandError(ClientException):
    def __init__(self, command: str, http_status: int = 400):
        super().__init__(
            message=f"无效的指令: {command}",
            error_code="VALIDATION-CMD-001",
            details={"command": command},
            http_status=http_status
        )
