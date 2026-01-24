# Mini-Avalon: 微信公众号阿瓦隆桌游后端

![Game Stage](https://img.shields.io/badge/Stage-Development-orange)
![Python](https://img.shields.io/badge/Python-3.12+-blue)
![Architecture](https://img.shields.io/badge/Architecture-DDD--Layered-green)

## 🌟 项目简介

**Mini-Avalon** 是一个专为微信公众号设计的“阿瓦隆”多人桌面游戏后端。它支持全文本指令交互，完美适配个人订阅号（无自定义菜单环境）。

本项目采用 **MySQL 作为单一事实来源**，并配合 **Redis 缓存异步优化**，确保在微信 5 秒内被动回复的严格限制下，依然能提供稳定、高性能、且具有强数据一致性的游戏体验。

---

## 🚀 部署指南

### Docker Compose (本地/开发)

推荐使用 Docker Compose 一键启动本地开发环境：

```bash
docker-compose up -d --build
```

### Kubernetes (生产环境)

本项目支持基于 Kustomize 的 Kubernetes 部署方案，适用于生产环境。

1. **准备 Secret**:

   ```bash
   cp k8s/overlays/prod/secret.yaml.example k8s/overlays/prod/secret.yaml
   # 编辑 secret.yaml 填入真实配置
   ```

2. **执行部署**:

   ```bash
   kubectl apply -k k8s/overlays/prod
   ```

详细部署说明请参考 [部署文档](docs/deployment.md)。

---

## 📈 开发进度与路线图

### 🟢 已完成 (Done)

- [x] 基于 Application Factory 的 Flask 后端框架。
- [x] 微信消息签名验证及 XML 协议处理。
- [x] 支持多参数的正则表达式指令解析器。
- [x] MySQL 核心模型定义（User, Room, State, History）。
- [x] 集成 Redis 缓存一致性 Repository 层。
- [x] 标准阿瓦隆 FSM 状态机框架（人数分配、阶段校验）。
- [x] 核心游戏流程实现（组队、投票、任务执行、刺杀阶段）。
- [x] **高阶角色支持**: 莫甘娜 (Morgana)、莫德雷德 (Mordred)、奥伯伦 (Oberon) 的视野逻辑与分配。
- [x] **Quest 4 特殊规则**: 7 人及以上局第 4 轮需 2 张失败。
- [x] **个人战绩中心**: 实现 `/profile` 指令，统计胜率及阵营分布。
- [x] **生产级部署**: 基于 Kustomize 的 Kubernetes 部署方案及资源配额优化。
- [x] 单元测试与集成测试（覆盖率 > 50%）。
- [x] 战绩历史统计与归档流程。
- [x] 房间清理机制（命令行指令：`flask cleanup-rooms`）。

### 🟡 进行中 (In Progress)

- [ ] 工程健壮性建设：接入 Sentry 监控与 Flask-Migrate 数据库迁移。
- [ ] 可观测性：引入 TraceID 处理微信 5s 回复限制下的日志追踪。

### 🔴 待办 (Todo)

- [ ] 异步超时处理：当玩家长时间不投票时自动随机执行。
- [ ] HPA (Horizontal Pod Autoscaler) 配置 with 压力测试。

---

## 🧪 测试

```bash
# 运行单元测试
pytest
```

目前指令解析器测试覆盖率已达 100%。

---

## 🛠 配置与环境变量

项目采用 Pydantic-Settings 统一管理配置，遵循 12-Factor App 原则。

详细的最佳实践和加载优先级说明请参考：[环境变量最佳实践](docs/env_best_practices.md)

- **.env.example**: 包含所有必备配置项的模板文件。
- **本地开发**: 复制 `.env.example` 为 `.env` 并根据实际需求修改。
- **生产环境**: 严禁将 `.env` 文件打包进镜像，应通过 Secret 管理工具注入。

---

## 📄 开源协议

本项目遵循 MIT 协议。
