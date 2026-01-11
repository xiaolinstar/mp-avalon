# 异常处理规范

项目采用统一的异常处理机制，将领域异常转换为标准响应或友好的微信文本回复。

## 异常层次结构

```python
class AvalonError(Exception):
    """基类异常"""
    pass

class GameRuleError(AvalonError):
    """违反游戏规则 (如: 非当前阶段操作, 票数不对)"""
    pass

class RoomNotFoundError(AvalonError):
    """房间不存在"""
    pass

class PlayerNotJoinedError(AvalonError):
    """玩家未加入房间"""
    pass

class WechatSignatureError(AvalonError):
    """微信签名验证失败"""
    pass
```

## 全局错误处理器

在 `src/app_factory.py` 中注册 Error Handler:

1. **API 请求**: 返回 JSON
   ```json
   {
       "code": 4001,
       "msg": "当前不是投票阶段",
       "data": null
   }
   ```

2. **微信回调**: 返回 XML 文本
   如果是通过微信交互触发的异常（如指令错误），应捕获 `GameRuleError` 并将其 message 直接包装为 XML 文本消息回复给用户，告知错误原因。

   *示例*:
   > 用户: /vote yes
   > 系统回复: 目前不是投票阶段，请等待队长通过 /pick 指令选择队伍。

## 常见错误码定义 (Code)
- `0`: 成功
- `1001`: 系统繁忙 (Redis连接失败等)
- `2001`: 房间不存在
- `2002`: 房间已满
- `3001`: 角色校验失败 (你不是刺客)
- `3002`: 阶段校验失败 (当前不能执行此操作)
