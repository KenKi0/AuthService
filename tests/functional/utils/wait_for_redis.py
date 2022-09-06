import asyncio
import os

from aioredis import ConnectionError, Redis
from backoff import backoff


@backoff()
async def main():
    redis = Redis(host=os.environ.get('REDIS_HOST'))

    if not await redis.ping():
        raise ConnectionError('Нет связи с сервером Redis')


if __name__ == '__main__':
    asyncio.run(main())
