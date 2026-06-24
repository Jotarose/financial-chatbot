from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from core import settings

engine = create_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


class Base(declarative_base()):
    pass
