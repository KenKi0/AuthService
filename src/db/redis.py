from redis import StrictRedis

from core import settings

redis = StrictRedis.from_url(settings.redis.url, decode_responses=True)
