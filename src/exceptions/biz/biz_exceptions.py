from ..base import BizException


class GameException(BizException):
    def __init__(
        self,
        message: str = "游戏逻辑错误",
        error_code: str = "GAME-ERROR-001",
        http_status: int = 200,
        details: dict | None = None,
        cause: Exception | None = None,
    ):
        super().__init__(message=message, error_code=error_code, http_status=http_status, details=details, cause=cause)


class NotLeaderError(GameException):
    def __init__(self, http_status: int = 200):
        super().__init__(message="你不是当前队长，无法执行此操作", error_code="GAME-AUTH-001", http_status=http_status)


class InvalidPhaseError(GameException):
    def __init__(self, expected_phase: str, current_phase: str, http_status: int = 200):
        super().__init__(
            message=f"当前阶段为 {current_phase}，无法执行此操作（需求: {expected_phase}）",
            error_code="GAME-STATE-001",
            details={"expected": expected_phase, "current": current_phase},
            http_status=http_status,
        )


class PlayerNotInGameError(GameException):
    def __init__(self, openid: str, http_status: int = 200):
        super().__init__(message="你不在当前游戏中", error_code="GAME-AUTH-002", details={"openid": openid}, http_status=http_status)
