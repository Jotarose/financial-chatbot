from sqlalchemy.orm import Session

from models.nota import Nota
from schemas.nota import CrearNota


def crear_nota(db: Session, data: CrearNota):

    nueva_nota = Nota(
        titulo=data.titulo,
        contenido=data.contenido,
        categoria=data.categoria,
    )

    db.add(nueva_nota)
    db.commit()  # Lo añado y commiteo el cambio en la bbdd
    db.refresh(nueva_nota)  # Actualizo el objeto con los campos autorrellenados

    return nueva_nota
