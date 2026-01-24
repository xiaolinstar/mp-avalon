# 环境变量与配置管理最佳实践

本项目遵循 [12-Factor App](https://12factor.net/config) 原则，将配置与代码严格分离。

## 1. 核心原则

- **不提交敏感配置**：`.env` 文件严禁提交至版本控制系统。必须在 `.gitignore` 中忽略。
- **配置与镜像分离**：不要将 `.env` 打包进 Docker 镜像。镜像应保持环境无关性指标。
- **Fail-Fast**：程序启动时必须校验核心配置，若缺失则立即报错退出。

## 2. 环境变量加载优先级

加载顺序（由低到高，高优先级覆盖低优先级）：

1. 代码中的声明式默认值（`src/config/settings.py`）
2. `.env` 文件
3. Shell 环境变量（如 `export APP_ENV=prod`）
4. Docker Compose 中的 `environment` 块
5. Kubernetes Secrets / ConfigMaps

## 3. 开发实践

### 3.1 配置文件（Settings）

使用 `pydantic-settings` 统一管理。

```python
from pydantic import SecretStr
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: SecretStr  # 使用 SecretStr 防止日志泄露
    
    model_config = SettingsConfigDict(env_file=".env")
```

### 3.2 敏感信息处理

对于密码、Token 等敏感信息，在 `Settings` 类中使用 `SecretStr` 类型。这能确保在打印对象或记录日志时，敏感内容被自动屏蔽为 `*******`。

### 3.3 生产环境校验

在 `Settings` 的 `__init__` 中增加生产环境校验逻辑：

- 校验 `APP_ENV=prod` 时，`SECRET_KEY` 是否仍为默认值。
- 校验微信开发密钥等必填项是否存在。

## 4. Docker 实践

### 4.1 .dockerignore

确保 `.dockerignore` 包含以下项，防止本地配置泄露到生产镜像：

```text
.env
.env.*
.git
```

### 4.2 Docker Compose

在 `docker-compose.yml` 中：

- 使用 `env_file` 加载基础变量。
- 使用 `environment` 覆盖服务间通信地址（使用服务名而非容器名）。
- 使用 `healthcheck` 确保依赖服务（MySQL/Redis）就绪后再启动应用。

## 5. 部署流程

1. 复制 `.env.example` 为 `.env`。
2. 根据具体环境修改 `.env` 中的变量。
3. 容器化部署时，通过编排工具注入环境变量，不依赖本地文件。
