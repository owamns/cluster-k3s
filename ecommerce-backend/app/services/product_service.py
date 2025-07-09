from sqlalchemy.orm import Session, joinedload
from app.models.product import Product
from app.models.category import Category
from app.services import cache_service


def get_product_by_id(db: Session, product_id: int, use_cache=True):
    cache_key = f"product:{product_id}"
    if use_cache:
        cached_product = cache_service.get_cache(cache_key)
        if cached_product:
            return cached_product

    product = db.query(Product).options(joinedload(Product.category)).filter(Product.id == product_id).first()
    if product:
        product_dict = product.to_dict()
        cache_service.set_cache(cache_key, product_dict)
        return product_dict
    return None


def get_all_products(db: Session, page: int, limit: int, category_id: int, search: str):
    query = db.query(Product).options(joinedload(Product.category))

    if category_id:
        query = query.filter(Product.category_id == category_id)

    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))

    total = query.count()
    products = query.offset((page - 1) * limit).limit(limit).all()

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "data": [p.to_dict() for p in products]
    }


def get_all_categories(db: Session):
    cache_key = "all_categories"
    cached_categories = cache_service.get_cache(cache_key)
    if cached_categories:
        return cached_categories

    categories = db.query(Category).all()
    categories_list = [c.to_dict() for c in categories]
    cache_service.set_cache(cache_key, categories_list)
    return categories_list