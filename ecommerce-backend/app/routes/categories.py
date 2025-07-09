from flask import Blueprint, jsonify
from sqlalchemy.orm import Session
from app.utils.database import get_db
from app.services import product_service

categories_bp = Blueprint('categories_bp', __name__)

@categories_bp.route('/', methods=['GET'])
def get_categories():
    db: Session = next(get_db())
    categories = product_service.get_all_categories(db)
    return jsonify(categories), 200