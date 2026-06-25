from sqlalchemy import Column, DateTime, Integer, String, Text, func

from database import Base


class Nota(Base):
    """Modelo de la tabla notas"""

    __tablename__ = "notas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    titulo = Column(String(255), nullable=False)
    contenido = Column(Text, nullable=False)
    categoria = Column(String(50), nullable=False, default="general")
    fecha_creacion = Column(DateTime, default=func.now())
    fecha_modificacion = Column(DateTime, default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Nota(id={self.id}, titulo='{self.titulo[:30]}...', categoria='{self.categoria}')>"

    def to_dict(self):
        """Convierte la nota a diccionario"""
        return {
            "id": self.id,
            "titulo": self.titulo,
            "contenido": self.contenido,
            "categoria": self.categoria,
            "fecha_creacion": self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            "fecha_modificacion": self.fecha_modificacion.isoformat()
            if self.fecha_modificacion
            else None,
        }
