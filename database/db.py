from config import DATABASE_URL
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Base

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


from sqlalchemy import text


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    
    # Migración automática de columnas para SQLite
    with engine.connect() as conn:
        try:
            result = conn.execute(text("PRAGMA table_info(usuarios)")).fetchall()
            existing_cols = {row[1] for row in result}
            
            if "email" not in existing_cols:
                conn.execute(text("ALTER TABLE usuarios ADD COLUMN email VARCHAR"))
            if "password_hash" not in existing_cols:
                conn.execute(text("ALTER TABLE usuarios ADD COLUMN password_hash VARCHAR"))
            if "salt" not in existing_cols:
                conn.execute(text("ALTER TABLE usuarios ADD COLUMN salt VARCHAR"))
            if "session_token" not in existing_cols:
                conn.execute(text("ALTER TABLE usuarios ADD COLUMN session_token VARCHAR"))
            conn.commit()
        except Exception as e:
            pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()