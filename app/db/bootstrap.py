from sqlalchemy import text

from app.db.engine import engine
from app.db.models import Base


def init_database() -> None:
    with engine.begin() as connection:
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    Base.metadata.create_all(bind=engine)
