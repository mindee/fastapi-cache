from typing import Tuple

from redis.asyncio.client import Redis
from redis.asyncio.sentinel import Sentinel

from fastapi_cache.backends import Backend


class RedisBackend(Backend):
    def __init__(self, redis: Redis):
        self.redis = redis

    async def get_with_ttl(self, key: str) -> Tuple[int, str]:
        async with self.redis.pipeline(transaction=True) as pipe:
            return await (pipe.ttl(key).get(key).execute())

    async def get(self, key) -> str:
        return await self.redis.get(key)

    async def set(self, key: str, value: str, expire: int = None):
        return await self.redis.set(key, value, ex=expire)

    async def clear(self, namespace: str = None, key: str = None) -> int:
        if namespace:
            lua = f"for i, name in ipairs(redis.call('KEYS', '{namespace}:*')) do redis.call('DEL', name); end"
            return await self.redis.eval(lua, numkeys=0)
        elif key:
            return await self.redis.delete(key)


class RedisSentinelBackend(Backend):
    def __init__(self, sentinel: Sentinel, service_name: str):
        self.sentinel = sentinel
        self.service_name = service_name

        self.master = self.sentinel.master_for(self.service_name)
        self.slave = self.sentinel.slave_for(self.service_name)

    async def get_with_ttl(self, key: str) -> Tuple[int, str]:
        async with self.slave.pipeline(transaction=True) as pipe:
            return await (pipe.ttl(key).get(key).execute())

    async def get(self, key) -> str:
        return await self.slave.get(key)

    async def set(self, key: str, value: str, expire: int = None):
        return await self.master.set(key, value, ex=expire)

    async def clear(self, namespace: str = None, key: str = None) -> int:
        if namespace:
            lua = f"for i, name in ipairs(redis.call('KEYS', '{namespace}:*')) do redis.call('DEL', name); end"
            return await self.master.eval(lua, numkeys=0)
        elif key:
            return await self.master.delete(key)
