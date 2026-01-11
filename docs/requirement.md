# 阿瓦隆 (Avalon) 游戏需求文档

> 微信公众号个人账户不支持自定义菜单、获取用户信息、发送客服消息等，全文本指令交互；后期认证后，可支持自定义菜单、获取用户信息、发送客服消息等。

## 项目概述

实现一个基于微信公众号的"阿瓦隆"游戏服务端，使用 Flask 技术栈。这是一个纯逻辑后端，通过文本指令驱动游戏进程，支持标准阿瓦隆规则（含梅林、刺客等角色）。

## 功能需求

### 核心功能

1. **房间管理**
   - 创建房间（`@机器人 建房`）
   - 加入房间（`/join <房间号>`）
   - 房间状态管理（准备中、游戏中、已结束）
   - 房间超时清理（超过2小时未活动自动销毁）

2. **用户管理**
   - 用户身份识别（微信OpenID）
   - 昵称设置（`/nick <新昵称>`）
   - 查看当前状态（`/status`）

3. **游戏流程 (标准版)**
   - **人数限制**: 5-10 人。
   - **角色分配**: 
     - 好人阵营: 梅林 (Merlin), 派西维尔 (Percival), 忠臣 (Loyal Servant)。
     - 坏人阵营: 莫甘娜 (Morgana), 刺客 (Assassin), 莫德雷德 (Mordred), 爪牙 (Minion)。
   - **核心阶段**:
     - **组队阶段 (Team Selection)**: 队长选择出任务的队员。
     - **投票阶段 (Team Vote)**: 全体玩家对组队方案进行投票（公开，Yes/No）。
     - **任务阶段 (Quest)**: 被选中的队员进行任务投票（秘密，Success/Fail）。
     - **刺杀阶段 (Assassination)**: 若好人率先获得3次任务成功，刺客可刺杀梅林，猜对则坏人反败为胜。
   - **胜负判定**:
     - 好人胜: 3次任务成功 且 梅林未被刺杀。
     - 坏人胜: 3次任务失败 或 连续5次组队被否决 或 刺杀梅林成功。

### 微信公众号集成

1. **消息处理**
   - 解析特定前缀或格式的文本指令。
   - 5秒内快速响应（被动回复）。
   - 复杂长耗时操作需优化异步处理或简化逻辑。

2. **指令设计 (示例)**
   - **房主**: `/start` (开始游戏), `/kick <id>` (踢人)
   - **队长**: `/pick 1 3 5` (选择 1,3,5 号玩家出任务)
   - **全员**: `/vote yes/no` (同意/拒绝组队)
   - **队员**: `/quest success/fail` (任务执行)
   - **刺客**: `/shoot <id>` (刺杀玩家)

## 技术方案

### 后端技术栈
- **Web框架**: Flask (App Factory 模式)
- **微信SDK**: Wechatpy
- **数据库**: 
  - **Redis 7.4**: 活跃游戏状态、房间信息、会话缓存 (Hot Data)。
  - **MySQL 8.4**: 用户档案、历史战绩、游戏回放 (Cold Data)。
- **容器化**: Docker + Kubernetes

### 数据库设计 (MySQL + Redis Cache)

所有数据持久化存储于 MySQL，热点数据 (Room, GameState) 缓存在 Redis。

#### 房间表 (rooms)
```sql
CREATE TABLE rooms (
    id INT PRIMARY KEY AUTO_INCREMENT,
    room_number VARCHAR(10) UNIQUE, -- 4位房间号
    owner_id VARCHAR(64),           -- 房主 OpenID
    status VARCHAR(20),             -- WAITING, PLAYING, ENDED
    created_at DATETIME,
    updated_at DATETIME,
    version INT DEFAULT 1           -- 乐观锁版本号
);
```

#### 游戏状态表 (game_states)
```sql
CREATE TABLE game_states (
    id INT PRIMARY KEY AUTO_INCREMENT,
    room_id INT UNIQUE,            
    phase VARCHAR(20),              -- TEAM_SELECTION, VOTE...
    round_num INT,                  -- 当前第几轮任务 (1-5)
    vote_track INT,                 -- 连续投票失败次数
    leader_idx INT,                 -- 队长索引
    current_team JSON,              -- 当前提名列表
    quest_results JSON,             -- 任务结果记录
    roles_config JSON,              -- 角色分配信息
    FOREIGN KEY (room_id) REFERENCES rooms(id)
);
```
#### 游戏战绩 (GameHistory - MySQL)
```sql
CREATE TABLE game_history (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    room_id VARCHAR(32),
    start_time DATETIME,
    end_time DATETIME,
    winner_team VARCHAR(10), -- 'GOOD' or 'EVIL'
    players JSON,            -- 参与玩家列表及身份
    replay_data JSON         -- 游戏全过程复盘数据
);
```

#### 用户档案 (User - MySQL)
```sql
CREATE TABLE users (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    openid VARCHAR(64) UNIQUE,
    nickname VARCHAR(64),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    total_games INT DEFAULT 0,
    wins_good INT DEFAULT 0,
    wins_evil INT DEFAULT 0
);
```

### 角色配置表 (按人数)
| 人数 | 好人 | 坏人 | 特殊配置建议 |
| :--- | :--- | :--- | :--- |
| 5    | 3    | 2    | 梅林,派西维尔,忠臣 vs 莫甘娜,刺客 |
| 6    | 4    | 2    | +忠臣 |
| 7    | 4    | 3    | +部分坏人 |
| 8    | 5    | 3    | +忠臣 |
| 9    | 6    | 3    | +忠臣 |
| 10   | 6    | 4    | +莫德雷德 |

## 接口与交互设计

由于微信公众号的被动回复机制，系统**不暴露**传统的 RESTful URL (如 `/room/create`, `/game/vote`) 给最终用户。所有用户交互均通过唯一的微信 Webhook 接口进行。

### 1. 微信 Webhook (单一入口)
- **URL**: `https://your-domain.com/`
- **Method**: 
  - `GET`: 用于微信服务器的 Token 验证 (`check_signature`)。
  - `POST`: 接收用户发送的 XML 消息推送。
- **内部路由机制 (Message Dispatcher)**:
  系统不通过 URL 区分业务，而是解析 XML 中的 `<Content>` 文本：
  - **指令匹配**: 使用正则匹配前缀（如 `/join` 匹配 `JoinCommand`）。
  - **会话上下文**: 根据 `<FromUserName>` (OpenID) 查找当前用户所在的 `Room` 和 `State`。
  - **业务分发**: 将请求分发至 `src/services/` 下的具体方法。

### 2. 辅助接口 (运维/监控)
- **健康检查**: `GET /health` (返回 JSON `{"status": "ok"}`, 用于 K8s Probe)
- **数据面板** (可选): `GET /metrics` (Prometheus 监控指标)

## 验收标准
1. 5人局基本流程跑通（组队->投票->任务->结算）。
2. 梅林/刺客机制生效。
3. 连续5次投票失败导致坏人胜利逻辑正确。
4. 能够正确处理并发请求（利用 Redis 原子性）。
