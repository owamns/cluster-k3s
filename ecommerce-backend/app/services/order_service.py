from sqlalchemy.orm import Session
from app.models.product import Product
from app.models.order import Order, OrderItem, OrderStatus
from app.services import cart_service


def create_order_from_cart(db: Session, session_id: str):
    cart_items = cart_service.get_cart_contents(session_id)
    if not cart_items:
        raise ValueError("El carrito está vacío.")

    try:
        with db.begin_nested():
            product_ids = list(cart_items.keys())
            products_in_db = db.query(Product).filter(Product.id.in_(product_ids)).with_for_update().all()
            product_map = {p.id: p for p in products_in_db}
            total_amount = 0
            order_items_to_create = []

            for product_id, quantity in cart_items.items():
                product = product_map.get(product_id)
                if not product:
                    raise ValueError(f"Producto con ID {product_id} no encontrado.")
                if product.stock < quantity:
                    raise ValueError(
                        f"Stock insuficiente para el producto '{product.name}'. Disponible: {product.stock}, Solicitado: {quantity}")
                product.stock -= quantity
                item_total = product.price * quantity
                total_amount += item_total
                order_items_to_create.append(
                    OrderItem(
                        product_id=product_id,
                        quantity=quantity,
                        price_per_unit=product.price
                    )
                )

            if not order_items_to_create:
                raise ValueError("No se pudieron procesar los ítems del carrito.")

            new_order = Order(
                user_id=session_id,
                total_amount=total_amount,
                status=OrderStatus.pending
            )
            new_order.items = order_items_to_create
            db.add(new_order)

        db.commit()

    except Exception as e:
        print(f"Error en create_order_from_cart: {str(e)}")
        db.rollback()
        raise e

    cart_service.clear_cart(session_id)
    return new_order.to_dict()


def get_order_by_id(db: Session, order_id: int):
    order = db.query(Order).filter(Order.id == order_id).first()
    return order.to_dict() if order else None