# 部署文档

## 环境要求

- Docker Engine 24+
- Docker Compose v2.0+
- Python 3.11+ (本地开发)

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
   curl http://localhost/health
   # 应返回 {"status": "ok"}
   ```

## Kubernetes 部署

本项目采用 Kustomize 管理 Kubernetes 配置。

### 1. 准备工作

1. **构建并推送镜像**
   ```bash
   docker build -t your-registry/avalon-server:latest .
   docker push your-registry/avalon-server:latest
   ```

2. **配置生产环境 Secret**
   复制示例 Secret 文件并填入真实数据：
   ```bash
   cp k8s/overlays/prod/secret.yaml.example k8s/overlays/prod/secret.yaml
   # 编辑 k8s/overlays/prod/secret.yaml
   ```

3. **配置 Ingress**
   编辑 `k8s/overlays/prod/ingress.yaml`，修改域名为你的实际域名。

### 2. 执行部署

使用 Kustomize 应用配置：
```bash
kubectl apply -k k8s/overlays/prod
```

### 3. 验证状态

```bash
kubectl get pods -n default
kubectl get svc -n default
kubectl get ingress -n default
```

## 生产环境注意事项

1. **持久化存储**: 默认配置使用了 PVC，请确保集群中已安装 StorageClass 提供程序（如 `local-path` 或云厂商提供的磁盘）。
2. **微信白名单**: 确保 K8s 出口节点 IP 已加入微信后台 IP 白名单。
3. **安全配置**: 所有 Deployment 均已设置 `automountServiceAccountToken: false` 以降低攻击面。
4. **HTTPS**: Ingress 配置中已集成 `cert-manager` 注解，建议配合 `letsencrypt` 使用。
