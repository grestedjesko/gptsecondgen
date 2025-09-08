import redis.asyncio as redis

class RedisCache:
    def __init__(self, url: str):
        self.client = redis.from_url(url, decode_responses=True)

    async def set(self, key: str, value: str, ttl: int = None):
        print(value)
        await self.client.set(key, value, ex=ttl)

    async def get(self, key: str):
        print(key)
        return await self.client.get(key)

    async def delete(self, key: str):
        await self.client.delete(key)

    async def exists(self, key: str) -> bool:
        return await self.client.exists(key) > 0

    async def lpush(self, key: str, value: str):
        await self.client.lpush(key, value)
        await self.client.ltrim(key, 0, 9)  # оставляем только 10 последних

    async def lrange(self, key: str, start=0, stop=9):
        return await self.client.lrange(key, start, stop)

    async def expire(self, key: str, ttl: int):
        await self.client.expire(key, ttl)

    async def ltrim(self, key: str, start: int, stop: int):
        await self.client.ltrim(key, start, stop)