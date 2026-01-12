from redis import Redis
from flask import Flask

class RedisExtension:
    def __init__(self, app=None):
        self._client = None
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        redis_url = app.config.get("REDIS_URL")
        # 初始化连接池
        self._client = Redis.from_url(redis_url, decode_responses=True)
        
        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['redis_manager'] = self

    @property
    def client(self) -> Redis:
        return self._client

# 创建单例对象，供外部模块导入
redis_manager = RedisExtension()
