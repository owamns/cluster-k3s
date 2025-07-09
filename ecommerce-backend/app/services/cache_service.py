import json
from app.utils.redis_client import redis_client

CACHE_TTL = 3600

def get_cache(key):
    if not redis_client:
        return None
    try:
        cached_value = redis_client.get(key)
        return json.loads(cached_value) if cached_value else None
    except Exception as e:
        print(f"Error al obtener de caché ({key}): {e}")
        return None

def set_cache(key, value, ttl=CACHE_TTL):
    if not redis_client:
        return
    try:
        redis_client.setex(key, ttl, json.dumps(value))
    except Exception as e:
        print(f"Error al establecer en caché ({key}): {e}")

def invalidate_cache(key):
    if not redis_client:
        return
    try:
        redis_client.delete(key)
    except Exception as e:
        print(f"Error al invalidar caché ({key}): {e}")