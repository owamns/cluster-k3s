import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'una-clave-secreta-muy-dificil-de-adivinar')

    MYSQL_HOST = os.getenv('MYSQL_HOST', 'mysql-service')
    MYSQL_USER = os.getenv('MYSQL_USER', 'owams')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'owams123')
    MYSQL_DB = os.getenv('MYSQL_DB', 'ecommerce_db')
    SQLALCHEMY_DATABASE_URI = f"mysql+mysqlconnector://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'max_overflow': 20,
        'pool_recycle': 3600,  # Recicla conexiones cada hora
    }

    REDIS_HOST = os.getenv('REDIS_HOST', 'redis-service')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    REDIS_DB = int(os.getenv('REDIS_DB', 0))

    CART_TTL_SECONDS = int(os.getenv('CART_TTL_SECONDS', 259200))

    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() in ('true', '1', 't')
