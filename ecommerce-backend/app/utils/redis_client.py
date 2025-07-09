import redis
from app.config import Config

def get_redis_connection():
    try:
        redis_client = redis.Redis(
            host=Config.REDIS_HOST,
            port=Config.REDIS_PORT,
            db=Config.REDIS_DB,
            decode_responses=True
        )
        redis_client.ping()
        print("Conexión a Redis exitosa.")
        return redis_client
    except redis.exceptions.ConnectionError as e:
        print(f"Error al conectar con Redis: {e}")
        return None

redis_client = get_redis_connection()