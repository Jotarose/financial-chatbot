from pydantic import BaseModel, Field


class CrearNota(BaseModel):
    titulo: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Título de la nota",
    )

    contenido: str = Field(
        ...,
        min_length=1,
        description="Contenido de la nota",
    )

    categoria: str = Field(
        default="general",
        max_length=50,
        description="Categoría de la nota (por defecto 'general')",
    )
