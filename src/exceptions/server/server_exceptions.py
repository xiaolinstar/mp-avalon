from ..base import ServerException


class RedisConnectionError(ServerException):
    def __init__(self, message: str = "Redis 连接异常", http_status: int = 500):
        super().__init__(
            message=message, 
            error_code="INFRA-REDIS-001",
            http_status=http_status
        )


class DatabaseError(ServerException):
    def __init__(self, message: str = "数据库操作异常", http_status: int = 500):
        super().__init__(
            message=message, 
            error_code="INFRA-DB-001",
            http_status=http_status
        )
