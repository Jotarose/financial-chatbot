# Importar todos los modelos
from database import Base, engine
from models.nota import Nota  # noqa: F401


def init_db():
    Base.metadata.create_all(bind=engine)
