from sqlalchemy.exc import SQLAlchemyError  # Importante
from sqlalchemy.orm import Session

from models.nota import Nota
from schemas.nota import CrearNota


def crear_nota(db: Session, data: CrearNota):
    try:
        nueva_nota = Nota(
            titulo=data.titulo,
            contenido=data.contenido,
            categoria=data.categoria,
        )
        db.add(nueva_nota)
        db.commit()
        db.refresh(nueva_nota)
        return nueva_nota
    except SQLAlchemyError as e:
        db.rollback()  # <- CRÍTICO: Limpia la sesión corrupta
        raise e  # <- Pasa el error a la capa superior


def leer_notas(db: Session, limite: int | None = None) -> list[Nota]:
    try:
        query = db.query(Nota).order_by(Nota.fecha_creacion.desc())

        if limite is not None and limite > 0:
            query = query.limit(limite)

        return query.all()
    except SQLAlchemyError as e:
        raise e


def contar_notas(db: Session) -> int:
    try:
        return db.query(Nota).count()
    except SQLAlchemyError as e:
        raise e


def borrar_nota(db: Session, id: int) -> dict:
    """
    Intenta borrar una nota por su ID.
    Retorna True si se borró con éxito, False si no se encontró.
    """
    try:
        # Buscamos la nota primero
        nota = db.query(Nota).filter(Nota.id == id).first()

        if not nota:
            return {"success": False}

        db.delete(nota)
        db.commit()
        return {"success": True, "id": nota.id, "titulo": nota.titulo}

    except SQLAlchemyError as e:
        # Si algo falla en la BBDD (bloqueo, desconexión, etc), revertimos
        db.rollback()
        raise e
