from app.utils.redis_client import redis_client
from app.config import Config


def get_cart_key(session_id: str):
    return f"cart:{session_id}"


def add_item_to_cart(session_id: str, product_id: int, quantity: int):
    if not redis_client:
        raise ConnectionError("Redis no está disponible.")

    cart_key = get_cart_key(session_id)
    redis_client.hset(cart_key, str(product_id), quantity)
    redis_client.expire(cart_key, Config.CART_TTL_SECONDS)
    return get_cart_contents(session_id)


def update_cart_item(session_id: str, product_id: int, quantity: int):
    return add_item_to_cart(session_id, product_id, quantity)


def remove_item_from_cart(session_id: str, product_id: int):
    if not redis_client:
        raise ConnectionError("Redis no está disponible.")

    cart_key = get_cart_key(session_id)
    redis_client.hdel(cart_key, str(product_id))
    return get_cart_contents(session_id)


def get_cart_contents(session_id: str):
    if not redis_client:
        raise ConnectionError("Redis no está disponible.")

    cart_key = get_cart_key(session_id)
    cart_items = redis_client.hgetall(cart_key)

    return {int(pid): int(qty) for pid, qty in cart_items.items()}


def clear_cart(session_id: str):
    if not redis_client:
        return
    cart_key = get_cart_key(session_id)
    redis_client.delete(cart_key)