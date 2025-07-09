# app/__init__.py

import time
from flask import Flask, jsonify, request

from app.config import Config
from app.utils.database import create_db_tables
from app.routes.products import products_bp
from app.routes.categories import categories_bp
from app.routes.cart import cart_bp
from app.routes.orders import orders_bp
from app.routes.stress import stress_bp

# Métricas simples en memoria (para demostración)
request_count = 0
error_count = 0
total_response_time = 0


def create_app():
    """Crea y configura una instancia de la aplicación Flask."""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Hook para medir el tiempo de respuesta
    @app.before_request
    def before_request():
        global request_count
        request_count += 1
        request.start_time = time.time()

    @app.after_request
    def after_request(response):
        global total_response_time, error_count
        resp_time = (time.time() - request.start_time) * 1000  # en ms
        total_response_time += resp_time
        if response.status_code >= 400:
            error_count += 1
        return response

    # Crear tablas de la base de datos si no existen
    # En un entorno de producción real, esto se manejaría con migraciones (ej. Alembic)
    with app.app_context():
        create_db_tables()

    # Registrar Blueprints
    app.register_blueprint(products_bp, url_prefix='/api/products')
    app.register_blueprint(categories_bp, url_prefix='/api/categories')
    app.register_blueprint(cart_bp, url_prefix='/api/cart')
    app.register_blueprint(orders_bp, url_prefix='/api/orders')
    app.register_blueprint(stress_bp, url_prefix='/api/stress')

    # Endpoint de Health Check
    @app.route('/api/health')
    def health_check():
        return jsonify({"status": "ok", "message": "Service is healthy"}), 200

    # Endpoint de Métricas
    @app.route('/api/metrics')
    def metrics():
        avg_response_time = (total_response_time / request_count) if request_count > 0 else 0
        error_rate = (error_count / request_count) if request_count > 0 else 0

        return jsonify({
            "request_count": request_count,
            "error_count": error_count,
            "average_response_time_ms": round(avg_response_time, 2),
            "error_rate": round(error_rate, 4)
        }), 200

    return app


# Exponer la instancia de la app para Gunicorn/WSGI
app = create_app()