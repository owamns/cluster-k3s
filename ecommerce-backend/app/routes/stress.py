import random
from flask import Blueprint, request, jsonify
from sqlalchemy.orm import Session
from faker import Faker
from app.utils.database import get_db
from app.services import product_service, cart_service, order_service, cache_service

stress_bp = Blueprint('stress_bp', __name__)
fake = Faker()


@stress_bp.route('/heavy_product_listing', methods=['GET'])
def heavy_product_listing():
    page = request.args.get('page', random.randint(1, 20), type=int)
    limit = request.args.get('limit', 50, type=int)
    category_id = request.args.get('category_id', None, type=int)
    search = request.args.get('search', fake.word(), type=str)

    db: Session = next(get_db())
    result = product_service.get_all_products(db, page, limit, category_id, search)
    return jsonify({"message": "Heavy listing simulation successful", "data_length": len(result['data'])}), 200


@stress_bp.route('/concurrent_cart_additions/<string:session_id>', methods=['POST'])
def concurrent_cart_additions(session_id):
    product_id = random.randint(1, 100)
    quantity = random.randint(1, 3)

    try:
        cart_service.add_item_to_cart(session_id, product_id, quantity)
        return jsonify({"message": f"Added product {product_id} to cart {session_id}"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@stress_bp.route('/mass_order_creation/<string:session_id>', methods=['POST'])
def mass_order_creation(session_id):
    db: Session = next(get_db())
    try:
        new_order = order_service.create_order_from_cart(db, session_id)
        return jsonify({"message": "Mass order creation successful", "order_id": new_order['id']}), 201
    except ValueError as e:
        return jsonify({"error": f"Order creation failed: {str(e)}"}), 400
    except Exception as e:
        print(f"Error inesperado en mass_order_creation: {str(e)}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@stress_bp.route('/cache_miss_simulation/<int:product_id>', methods=['GET'])
def cache_miss_simulation(product_id):
    db: Session = next(get_db())

    cache_service.invalidate_cache(f"product:{product_id}")

    product = product_service.get_product_by_id(db, product_id, use_cache=False)

    if product:
        return jsonify({"message": "Cache miss simulation successful", "product": product}), 200
    return jsonify({"error": "Producto no encontrado"}), 404


@stress_bp.route('/mixed_load_simulation/<int:num_requests>', methods=['GET'])
def mixed_load_simulation(num_requests):

    db: Session = next(get_db())
    session_id = fake.uuid4()
    results = []

    operations = [
        'list_products', 'get_product_details', 'add_to_cart'
    ]

    for i in range(num_requests):
        op = random.choices(operations, weights=[0.5, 0.3, 0.2], k=1)[0]

        try:
            if op == 'list_products':
                product_service.get_all_products(db, 1, 10, None, None)
                results.append(f"Request {i + 1}: List products OK")
            elif op == 'get_product_details':
                product_service.get_product_by_id(db, random.randint(1, 100))
                results.append(f"Request {i + 1}: Get product OK")
            elif op == 'add_to_cart':
                cart_service.add_item_to_cart(session_id, random.randint(1, 100), 1)
                results.append(f"Request {i + 1}: Add to cart OK")
        except Exception as e:
            results.append(f"Request {i + 1}: Operation {op} FAILED - {e}")

    return jsonify(
        {"message": "Mixed load simulation completed", "operations_performed": len(results), "details": results})