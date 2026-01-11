# 日志设计文档

## 1. 概述

本项目采用统一的结构化日志系统，结合 Python 标准库 `logging` 模块，旨在提供清晰、可追踪且便于分析的运行时信息。

## 2. 日志层级 (Log Levels)

| 级别 | 对应标准库 | 典型场景 | 是否告警 |
| :--- | :--- | :--- | :--- |
| **DEBUG** | `logging.DEBUG` | 微信消息原始 XML 内容、Redis 交互细节、算法中间状态 | 否 |
| **INFO** | `logging.INFO` | 关键业务事件：房间创建、游戏开始、用户加入、投票结果 | 否 |
| **WARNING** | `logging.WARNING` | 预期内异常：用户输入非法指令、房间已满、校验失败 | 否 |
| **ERROR** | `logging.ERROR` | 系统级故障：Redis 连接失败、微信接口超时、代码未处理的异常 | **是** |
| **CRITICAL** | `logging.CRITICAL` | 导致进程崩溃的错误：配置缺失、核心服务不可用 | **是** |

## 3. 日志格式

生产环境推荐使用 JSON 格式以便于 ELK 等日志系统采集；本地开发使用文本格式。

### 3.1 文本格式 (Dev)
```text
[2024-03-20 10:00:00,123] [INFO] [src.services.game_service] [game_start] Room(1024) game started by User(u_123)
```
格式模板：`[%(asctime)s] [%(levelname)s] [%(name)s] [%(funcName)s] %(message)s`

### 3.2 JSON 格式 (Prod)
```json
{
  "timestamp": "2024-03-20T10:00:00.123Z",
  "level": "INFO",
  "logger": "src.services.game_service",
  "func": "game_start",
  "message": "Room(1024) game started",
  "context": {
    "room_id": "1024",
    "user_id": "u_123",
    "event": "GAME_START"
  },
  "trace_id": "req-123456"
}
```

## 4. 模块设计

日志模块位于 `src/utils/logger.py`。

### 4.1 核心功能
```python
# 获取 logger
def get_logger(name: str) -> logging.Logger: ...

# 配置初始化 (在 app_factory 中调用)
def setup_logging(app_config: dict) -> None: ...
```

### 4.2 关键组件
1. **Correlation ID Filter**: 自动在日志中注入 `request_id` 或 `trace_id`，用于追踪单个请求的全链路日志。
2. **Context Adapter**: 允许在日志调用时方便地传入额外的上下文字段（如 `room_id`, `user_id`）。

## 5. 使用规范

### 5.1 业务代码中打日志

```python
from src.utils.logger import get_logger

logger = get_logger(__name__)

def join_room(room_id, user_id):
    logger.info(f"User {user_id} attempting to join room {room_id}")
    
    try:
        # 业务逻辑...
        logger.info(f"User {user_id} joined room {room_id}", extra={"event": "USER_JOIN", "room_id": room_id})
    except RoomFullError:
        logger.warning(f"Join failed: Room {room_id} full", extra={"user_id": user_id})
        raise
    except Exception as e:
        logger.error(f"Unexpected error during join: {str(e)}", exc_info=True)
        raise
```

### 5.2 敏感信息脱敏
- **绝对禁止**打印用户的 `OpenID` 以外的敏感信息（如 Token、AES Key）。
- 微信消息体如果是加密的，在 DEBUG 模式下解密后打印时需谨慎。

## 6. 配置参数 (Env)

- `LOG_LEVEL`: String (DEBUG, INFO, WARNING, ERROR). Default: INFO.
- `LOG_FORMAT`: String (TEXT, JSON). Default: TEXT.
- `LOG_FILE`: Path. Optional. 如果设置，则同时输出到文件。

## 7. 日志轮转 (Rotation)
- 容器化环境下，标准输出 (Stdout/Stderr) 由 Docker Daemon 或 K8s Log Driver 接管。
- 若输出到文件，使用 `RotatingFileHandler`，限制单文件 10MB，保留 5 个备份。
