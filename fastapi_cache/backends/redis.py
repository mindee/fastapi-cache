from typing import Tuple

from redis.asyncio.client import Redis
from redis.asyncio.sentinel import Sentinel

from fastapi_cache.backends import Backend


class _RedisBackend(Backend):
    def __init__(self, writer: Redis, reader: Redis):
        self.writer = writer
        self.reader = reader

    async def get_with_ttl(self, key: str) -> Tuple[int, str]:
        async with self.reader.pipeline(transaction=True) as pipe:
            return await (pipe.ttl(key).get(key).execute())

    async def get(self, key) -> str:
        return await self.reader.get(key)

    async def set(self, key: str, value: str, expire: int = None):
        return await self.writer.set(key, value, ex=expire)

    async def clear(self, namespace: str = None, key: str = None) -> int:
        if namespace:
            lua = f"for i, name in ipairs(redis.call('KEYS', '{namespace}:*')) do redis.call('DEL', name); end"
            return await self.writer.eval(lua, numkeys=0)
        elif key:
            return await self.writer.delete(key)


class RedisBackend(_RedisBackend):
    def __init__(self, redis: Redis):
        super().__init__(writer=redis, reader=redis)


class RedisSentinelBackend(_RedisBackend):
    def __init__(self, sentinel: Sentinel, service_name: str):
        super().__init__(
            writer=sentinel.master_for(service_name), reader=sentinel.slave_for(service_name)
        )
