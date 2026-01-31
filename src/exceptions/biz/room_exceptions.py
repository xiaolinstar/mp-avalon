from ..base import BizException


class RoomException(BizException):
    def __init__(
        self,
        message: str = "房间逻辑错误",
        error_code: str = "ROOM-ERROR-001",
        http_status: int = 200,
        details: dict | None = None,
        cause: Exception | None = None,
    ):
        super().__init__(message=message, error_code=error_code, http_status=http_status, details=details, cause=cause)


class RoomNotFoundError(RoomException):
    def __init__(self, room_id: str, http_status: int = 200):
        super().__init__(message=f"未找到房间: {room_id}", error_code="ROOM-NOT_FOUND-001", details={"room_id": room_id}, http_status=http_status)


class RoomFullError(RoomException):
    def __init__(self, room_id: str, http_status: int = 200):
        super().__init__(message="该房间已满", error_code="ROOM-STATE-001", details={"room_id": room_id}, http_status=http_status)


class RoomStateError(RoomException):
    def __init__(self, message: str, http_status: int = 200):
        super().__init__(message=message, error_code="ROOM-STATE-002", http_status=http_status)
