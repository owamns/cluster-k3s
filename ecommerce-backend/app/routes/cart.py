from flask import Blueprint, request, jsonify
from app.services import cart_service

cart_bp = Blueprint('cart_bp', __name__)


@cart_bp.route('/<string:session_id>', methods=['GET'])
def get_cart(session_id):
    try:
        cart_contents = cart_service.get_cart_contents(session_id)
        return jsonify(cart_contents), 200
    except ConnectionError as e:
        return jsonify({"error": str(e)}), 503


@cart_bp.route('/<string:session_id>/items', methods=['POST'])
def add_to_cart(session_id):
    data = request.get_json()
    if not data or 'product_id' not in data or 'quantity' not in data:
        return jsonify({"error": "Faltan 'product_id' y 'quantity'"}), 400

    try:
        updated_cart = cart_service.add_item_to_cart(
            session_id, data['product_id'], data['quantity']
        )
        return jsonify(updated_cart), 201
    except ConnectionError as e:
        return jsonify({"error": str(e)}), 503


@cart_bp.route('/<string:session_id>/items/<int:item_id>', methods=['PUT'])
def update_item_in_cart(session_id, item_id):
    data = request.get_json()
    if not data or 'quantity' not in data:
        return jsonify({"error": "Falta 'quantity'"}), 400

    try:
        updated_cart = cart_service.update_cart_item(
            session_id, item_id, data['quantity']
        )
        return jsonify(updated_cart), 200
    except ConnectionError as e:
        return jsonify({"error": str(e)}), 503


@cart_bp.route('/<string:session_id>/items/<int:item_id>', methods=['DELETE'])
def remove_from_cart(session_id, item_id):
    try:
        updated_cart = cart_service.remove_item_from_cart(session_id, item_id)
        return jsonify(updated_cart), 200
    except ConnectionError as e:
        return jsonify({"error": str(e)}), 503