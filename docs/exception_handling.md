# 异常处理规范

项目采用统一的异常处理机制，将领域异常转换为标准响应或友好的微信文本回复。基于**防御性编程、用户友好、可观测性**三大核心理念，将自定义异常细分为**客户端异常、业务异常、服务端异常**三类。

## 异常分类设计

### 1. ClientException (客户端异常)
- **特征**: 错误源于客户端输入或操作
- **适用场景**:
  - 参数校验失败
  - 权限不足
  - 资源不存在（用户请求的资源）
  - 非法操作请求
- **处理原则**:
  - 防御性编程：快速失败，明确错误信息
  - 用户友好：提供清晰的错误说明和解决建议
  - 可观测性：记录统计信息，不记录为错误日志

### 2. BizException (业务异常)
- **特征**: 业务逻辑层面的异常，符合业务规则但不符合当前业务状态
- **适用场景**:
  - 业务状态不符合预期（如：非当前阶段操作）
  - 业务约束违反（如：票数不足）
  - 游戏规则违反
- **处理原则**:
  - 防御性编程：保护业务流程完整性
  - 用户友好：提供业务上下文相关的错误信息
  - 可观测性：记录业务流程异常，用于业务监控

### 3. ServerException (服务端异常)
- **特征**: 服务器内部故障或外部依赖问题
- **适用场景**:
  - 数据库连接失败
  - Redis连接失败
  - 外部服务调用失败
  - 系统资源不足
- **处理原则**:
  - 防御性编程：隔离故障，防止级联失败
  - 用户友好：提供通用错误信息，避免泄露系统细节
  - 可观测性：详细记录错误信息，用于系统监控和告警

## 异常层次结构

```python
class AppException(Exception):
    """应用异常基类，提供统一的异常结构"""
    message: str          # 异常消息
    error_code: str       # 业务错误码
    http_status: int      # HTTP状态码，默认200表示业务逻辑错误而非客户端错误
    details: dict | None = None  # 附加详情
    cause: Exception | None = None  # 原始异常

class ClientException(AppException):
    """客户端异常"""
    http_status: int = 400  # 默认客户端错误状态码

class BizException(AppException):
    """业务异常"""
    http_status: int = 200  # 默认业务逻辑错误，非HTTP错误

class ServerException(AppException):
    """服务端异常"""
    http_status: int = 500  # 默认服务器内部错误状态码
```

## 目录结构

为了便于开发者查找和管理异常，我们将异常按类型组织到不同的目录中：

```
src/exceptions/
├── base.py                 # 定义异常基类
├── __init__.py             # 导出所有异常类
├── client/                 # 客户端异常
│   ├── client_exceptions.py # 客户端相关异常定义
│   └── __init__.py         # 导出客户端异常
├── biz/                    # 业务异常
│   ├── biz_exceptions.py   # 业务相关异常定义
│   ├── room_exceptions.py  # 房间相关异常定义
│   └── __init__.py         # 导出业务异常
└── server/                 # 服务端异常
    ├── server_exceptions.py # 服务端相关异常定义
    └── __init__.py         # 导出服务端异常
```

## 全局错误处理器

在 `src/app_factory.py` 中注册 Error Handler:

1. **API 请求**: 返回 JSON
   ```json
   {
       "status": "error",
       "message": "当前不是投票阶段",
       "code": 200
   }
   ```

2. **微信回调**: 返回 XML 文本
   根据异常类型返回不同前缀的消息：
   - ClientException (400): "请求错误: {message}"
   - BizException (200): "提示: {message}"
   - ServerException (500): "错误: {message}"

   *示例*:
   > 用户: /vote yes
   > 系统回复: 提示: 目前不是投票阶段，请等待队长通过 /pick 指令选择队伍。

## 常见错误码定义 (Code)
- `0`: 成功
- `400`: 客户端请求错误
- `200`: 业务逻辑错误
- `500`: 服务器内部错误
- `1001`: 系统繁忙 (Redis连接失败等)
- `2001`: 房间不存在
- `2002`: 房间已满
- `3001`: 角色校验失败 (你不是刺客)
- `3002`: 阶段校验失败 (当前不能执行此操作)
