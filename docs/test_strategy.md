# 测试策略文档 (Test Strategy)

## 1. 测试目标
确保 Avalon 游戏后端的核心逻辑正确性、状态流转的严谨性以及微信接口的稳定性。鉴于游戏逻辑的复杂性（特别是 FSM 和 角色技能），测试将遵循“测试金字塔”原则，重点覆盖单元测试。

## 2. 测试范围
*   **单元测试 (Unit Tests)**: 覆盖 FSM 状态转移、角色分配算法、胜负判定逻辑、指令解析器。
*   **集成测试 (Integration Tests)**: 覆盖 Room Service 与 MySQL/Redis 的交互、完整游戏局的流程模拟、并发一致性验证。
*   **端到端测试 (E2E Tests)**: (可选) 模拟微信 Webhook 请求，验证 XML 响应格式。

## 3. 测试工具栈
*   **框架**: `pytest`
*   **Mocking**: `pytest-mock` (用于 mock Redis, WechatClient)
*   **Fixtures**: `pytest-flask` (用于 app context), `factory_boy` (用于生成测试数据)
*   **Coverage**: `pytest-cov`

## 4. 测试目录结构
```text
tests/
├── conftest.py             # 全局共享 Fixtures (App, DB Session, Redis Mock)
├── unit/
│   ├── test_fsm.py         # 状态机逻辑测试 (重中之重)
│   ├── test_parser.py      # 指令解析测试
│   └── test_rules.py       # 游戏规则/角色判定测试
└── integration/
    ├── test_room_service.py # 房间管理集成测试
    └── test_flow_full.py    # 完整 5 人局标准流程模拟
```

## 5. 关键测试场景

### 5.1 FSM 状态机测试
必须覆盖所有合法与非法的状态转移：
*   Waiting -> Valid Start -> Team Selection (OK)
*   Waiting -> Invalid Start (Not Owner) -> Error
*   Team Vote -> Vote Fail (Track < 5) -> Team Selection
*   Team Vote -> Vote Fail (Track = 5) -> Game Over (Evil Win)

### 5.2 角色逻辑
*   梅林应该看到所有坏人（除了莫德雷德）。
*   派西维尔应该看到梅林和莫甘娜（但不区分）。
*   刺客刺杀梅林成功 -> 坏人胜。

### 5.3 并发安全性
*   模拟多个玩家同时发送 `/vote` 指令，验证票数统计准确无误，不会重复计票。

## 6. 运行方式
```bash
# 运行所有测试
pytest

# 运行特定模块
pytest tests/unit/test_fsm.py

# 生成覆盖率报告
pytest --cov=src tests/
```
