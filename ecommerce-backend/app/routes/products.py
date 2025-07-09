from flask import Blueprint, request, jsonify
from sqlalchemy.orm import Session
from app.utils.database import get_db
from app.services import product_service

products_bp = Blueprint('products_bp', __name__)

@products_bp.route('/', methods=['GET'])
def get_products():
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    category_id = request.args.get('category_id', None, type=int)
    search = request.args.get('search', None, type=str)

    db: Session = next(get_db())
    result = product_service.get_all_products(db, page, limit, category_id, search)
    return jsonify(result), 200

@products_bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id: int):
    db: Session = next(get_db())
    product = product_service.get_product_by_id(db, product_id)
    if product:
        return jsonify(product), 200
    return jsonify({"error": "Producto no encontrado"}), 404