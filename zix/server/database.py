import datetime
import uuid

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from zix.server.logging import get_logger

logger = get_logger(logger_name=__name__)


engine = None
SessionLocal = None

def get_engine(database_url, connect_args, engine_kwargs):
    global SessionLocal
    global DBEngine
    DBEngine = create_engine(
        database_url,
        connect_args=connect_args,
        **engine_kwargs,
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=DBEngine)
    return DBEngine


def get_db():
    global SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
