from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import Config

engine = create_engine(
    Config.SQLALCHEMY_DATABASE_URI,
    pool_size=Config.SQLALCHEMY_ENGINE_OPTIONS['pool_size'],
    max_overflow=Config.SQLALCHEMY_ENGINE_OPTIONS['max_overflow'],
    pool_recycle=Config.SQLALCHEMY_ENGINE_OPTIONS['pool_recycle'],
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_db_tables():
    print("Creando tablas en la base de datos si no existen...")
    Base.metadata.create_all(bind=engine)
    print("Tablas verificadas/creadas.")
