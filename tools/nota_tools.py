from crud.nota import crear_nota
from database.session import get_db_session
from schemas.nota import CrearNota


def crear_nota_tool(data: CrearNota) -> dict:
    with get_db_session() as db:
        nota = crear_nota(db, data)

        return {
            "id": nota.id,
            "titulo": nota.titulo,
        }
