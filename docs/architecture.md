# 阿瓦隆 (Avalon) 项目架构提示词

**角色定义**：
你是一位精通 Python 后端开发、领域驱动设计 (DDD) 和云原生架构的资深软件架构师。

**任务目标**：
请为我构建一个名为 **`avalon`** 的多人桌面游戏后端项目，用于微信公众号消息服务端。

**技术栈要求**：
*   **语言**: Python 3.12+
*   **Web 框架**: Flask (使用 Application Factory 模式)
*   **微信SDK**: Wechatpy (用于处理微信消息回调和XML解析)
*   **持久化存储**: MySQL 8.4 (单一事实来源，存储所有用户与游戏状态)
*   **数据缓存**: Redis 7.4 (作为应用层缓存，加速热点数据读取)
*   **容器化**: Docker & Docker Compose
*   **编排**: Kubernetes (K8s)
*   **测试**: Pytest (包含单元测试和集成测试)

**核心架构原则**：
1.  **分层架构 (Layered Architecture)**：严格遵循 `Controller` -> `Service` -> `Repository` 的调用链路。
2.  **状态机驱动 (FSM)**：阿瓦隆游戏包含“组队”、“投票”、“任务”、“刺杀”等多个复杂阶段，必须在 `src/fsm` 中实现健壮的有限状态机来管理状态流转。
3.  **缓存一致性 (Cache Consistency)**：
    *   采用 **Cache-Aside** 或 **Write-Through** 策略。
    *   读取：优先查 Redis，未命中查 MySQL 并回填。
    *   写入：事务更新 MySQL，成功后删除/更新 Redis 缓存。确保数据最终一致性。
4.  **配置分离**：使用 `.env` 管理敏感配置，支持多环境（Dev/Test/Prod）切换。

**目录结构规范**：
请严格按照以下结构生成项目脚手架：

```text
avalon/
├── .github/                 # GitHub Actions CI/CD 配置
├── k8s/                     # Kubernetes 部署清单 (Manifests & Kustomize)
│   ├── base/
│   └── overlays/
├── src/                     # 源代码目录
│   ├── config/              # 配置加载模块
│   ├── controllers/         # Web 路由与 HTTP 处理 (含 WeChat Webhook)
│   │   ├── wechat_ctrl.py   # 微信消息入口 (验证签名, 分发消息)
│   │   └── api_ctrl.py      # 其他管理后台 API (如有)
│   ├── exceptions/          # 自定义异常类型 (按领域拆分)
│   ├── fsm/                 # 游戏状态机核心逻辑 (State Pattern)
│   ├── models/              # 领域模型 (SQLAlchemy ORM + Pydantic DTO)
│   ├── repositories/        # 仓储层 (封装 MySQL 事务与 Redis 缓存逻辑)
│   ├── services/            # 业务逻辑层 (GameService, RoomService)
│   ├── strategies/          # 策略模式 (如不同角色的技能实现)
│   ├── wechat/              # 微信特定逻辑
│   │   ├── parser.py        # 文本指令解析器 (/join, /vote, etc.)
│   │   ├── reply.py         # 消息回复构造器
│   │   └── menu.py          # 自定义菜单管理
│   ├── utils/               # 通用工具函数
│   ├── app_factory.py       # Flask 应用工厂函数
│   └── main.py              # 应用入口
├── tests/                   # 测试用例
│   ├── unit/                # 单元测试
│   └── integration/         # 集成测试 (含 conftest.py Fixtures)
├── .coveragerc              # 测试覆盖率配置
├── .env.example             # 环境变量示例
├── .gitignore               # Git 忽略文件
├── Dockerfile               # 生产环境镜像构建
├── docker-compose.yml       # 本地开发环境编排
├── pytest.ini               # Pytest 配置
└── requirements.txt         # 依赖列表
```

**关键模块实现细节**：

1.  **Repository 层 (`src/repositories`)**：
1.  **Repository 层 (`src/repositories`)**：
    *   **统一入口**: `GameRepository` 同时持有 DB Session 和 Redis Client。
    *   **缓存策略**: 所有的读取操作 (`get_room`) 自动处理缓存命中逻辑；所有的写入操作 (`save_room`) 在数据库提交后更新/失效缓存。
    *   **乐观锁**: 在 MySQL 中使用 `version` 字段处理并发更新，防止脏写。

2.  **Service 层 (`src/services`)**：
    *   `GameService` 将是核心，它调用 Repository 获取数据，通过 FSM 处理状态流转，再存回数据。
    *   阿瓦隆特有逻辑：需处理“五局三胜”制、“梅林/刺客”判定逻辑。

3.  **FSM 模块 (`src/fsm`)**：
    *   定义清晰的阶段枚举（Phase Enum）：`TEAM_SELECTION` (组队), `VOTE` (投票), `QUEST` (任务), `ASSASSINATION` (刺杀), `GAME_OVER` (结束)。
    *   实现状态转移逻辑，验证玩家动作是否符合当前阶段。

4.  **微信交互规范**：
    *   **被动回复**：用户发送特定指令（如 `创建房间`），服务器必须在 5 秒内返回 XML 格式的文本消息。
    *   **指令系统**：前端交互完全基于文本及其指令，需实现一个健壮的 `CommandParser`。
        *   例：`@机器人 建房` -> 创建房间
        *   例：`/join 1234` -> 加入房间
        *   例：`/vote yes` -> 投票同意
    *   **身份识别**：使用微信 OpenID 作为用户的唯一标识5.  **服务端响应规范**：
    *   **WeChat Interface (`POST /`)**: 
        *   **成功/业务反馈**: 返回 XML 文本消息 (`<xml><ToUserName>...</ToUserName><Content>操作成功...</Content></xml>`)。
        *   **业务异常 (`GameRuleError`)**: 捕获异常并将 `error.message` 包装为 XML 文本返回，告知用户不可操作的原因。
    *   **Admin/Monitor Interface (`/health`, `/admin/...`)**: 
        *   返回标准 JSON: `{ "code": 0, "msg": "ok", "data": ... }`。

**交付物**：
请首先生成目录结构和核心配置文件（`requirements.txt`, `Dockerfile`, `src/config/`, `src/app_factory.py`），然后逐步实现核心业务逻辑。
