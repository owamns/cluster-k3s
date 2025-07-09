from flask import Blueprint, request, jsonify
from sqlalchemy.orm import Session
from app.utils.database import get_db
from app.services import order_service

orders_bp = Blueprint('orders_bp', __name__)


@orders_bp.route('/', methods=['POST'])
def create_order():
    data = request.get_json()
    if not data or 'session_id' not in data:
        return jsonify({"error": "Falta 'session_id'"}), 400

    db: Session = next(get_db())
    try:
        new_order = order_service.create_order_from_cart(db, data['session_id'])
        return jsonify(new_order), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        # Loggear el error real
        print(f"Error inesperado al crear pedido: {e}")
        return jsonify({"error": "Error interno del servidor al procesar el pedido"}), 500


@orders_bp.route('/<int:order_id>', methods=['GET'])
def get_order(order_id):
    db: Session = next(get_db())
    order = order_service.get_order_by_id(db, order_id)
    if order:
        return jsonify(order), 200
    return jsonify({"error": "Pedido no encontrado"}), 404