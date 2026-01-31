from dataclasses import dataclass


@dataclass
class AppException(Exception):
    """应用异常基类，提供统一的异常结构"""
    message: str
    error_code: str  # 业务错误码
    http_status: int = 200  # HTTP状态码，默认200表示业务逻辑错误而非客户端错误
    details: dict | None = None
    cause: Exception | None = None

    def __str__(self):
        return f"[{self.error_code}] {self.message}"


@dataclass
class ClientException(AppException):
    """
    客户端异常 - 由客户端请求导致的异常
    特征：错误源于客户端输入或操作，通常不应该被记录为系统错误
    适用场景：
    - 参数校验失败
    - 权限不足
    - 资源不存在（用户请求的资源）
    - 非法操作请求
    防御性编程：快速失败，明确错误信息
    用户友好：提供清晰的错误说明和解决建议
    可观测性：记录统计信息，不记录为错误日志
    """
    message: str = "客户端请求错误"
    error_code: str = "CLIENT_ERROR"
    http_status: int = 400  # 客户端错误状态码
    details: dict | None = None
    cause: Exception | None = None

    def __str__(self):
        return f"[{self.error_code}] {self.message}"


@dataclass
class BizException(AppException):
    """
    业务异常 - 业务逻辑层面的异常
    特征：符合业务规则但不符合当前业务状态
    适用场景：
    - 业务状态不符合预期（如：非当前阶段操作）
    - 业务约束违反（如：票数不足）
    - 游戏规则违反
    防御性编程：保护业务流程完整性
    用户友好：提供业务上下文相关的错误信息
    可观测性：记录业务流程异常，用于业务监控
    """
    message: str = "业务逻辑错误"
    error_code: str = "BIZ_ERROR"
    http_status: int = 200  # 业务逻辑错误，非HTTP错误
    details: dict | None = None
    cause: Exception | None = None

    def __str__(self):
        return f"[{self.error_code}] {self.message}"


@dataclass
class ServerException(AppException):
    """
    服务端异常 - 服务器内部错误
    特征：服务器内部故障或外部依赖问题
    适用场景：
    - 数据库连接失败
    - Redis连接失败
    - 外部服务调用失败
    - 系统资源不足
    防御性编程：隔离故障，防止级联失败
    用户友好：提供通用错误信息，避免泄露系统细节
    可观测性：详细记录错误信息，用于系统监控和告警
    """
    message: str = "服务器内部错误"
    error_code: str = "SERVER_ERROR"
    http_status: int = 500  # 服务器内部错误状态码
    details: dict | None = None
    cause: Exception | None = None

    def __str__(self):
        return f"[{self.error_code}] {self.message}"
