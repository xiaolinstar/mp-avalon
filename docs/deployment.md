# 部署文档

## 环境要求
- Docker Engine 24+
- Docker Compose v2.0+
- Python 3.12+ (本地开发)

## 快速启动 (Docker Compose)

1. **配置环境变量**
   ```bash
   cp .env.example .env
   # 编辑 .env 填入微信 Token 和 AES Key
   ```

2. **构建并启动**
   ```bash
   docker-compose up -d --build
   ```

3. **验证服务**
   ```bash
   curl http://localhost:8000/health
   # 应返回 {"status": "ok"}
   ```

## Kubernetes 部署

1. **构建镜像**
   ```bash
   docker build -t your-registry/avalon-server:latest .
   docker push your-registry/avalon-server:latest
   ```

2. **应用配置 (Kustomize)**
   ```bash
   kubectl apply -k k8s/overlays/prod
   ```

## 生产环境注意事项
1. **Redis 持久化**: 确保 Redis 开启 AOF 或 RDB，防止容器重启丢失游戏进度。
2. **WeChat Whitelist**: 确保服务器 IP 已加入微信公众号后台的白名单。
3. **HTTPS**: 微信强制要求 Webhook URL 为 HTTPS，需配置 Nginx + Let's Encrypt 或 Cloud Load Balancer。
