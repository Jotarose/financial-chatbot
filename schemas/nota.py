from enum import StrEnum

from pydantic import BaseModel, Field


class CategoriaNota(StrEnum):
    FINANZAS = "finanzas"
    PRESUPUESTO = "presupuesto"
    INVERSIONES = "inversiones"
    GASTOS = "gastos"
    INGRESOS = "ingresos"
    OBJETIVOS = "objetivos"
    DEUDAS = "deudas"
    AHORROS = "ahorros"
    GENERAL = "general"


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

    categoria: CategoriaNota = Field(
        default=CategoriaNota.GENERAL,
        description="Categoría de la nota. Restringido a los valores enumerados.",
    )


class LeerNotas(BaseModel):
    limite: int | None = Field(
        default=None,
        description="Número máximo de notas a recuperar. Úsalo si el usuario pide una cantidad específica (ej. 'las 3 últimas').",
    )


class ContarNotas(BaseModel):
    """Esquema vacío. No requiere parámetros de entrada."""

    pass


class BorrarNota(BaseModel):
    id: int = Field(
        ...,
        description="ID único de la nota que se desea eliminar. Debe obtenerse previamente mediante 'leer_notas'.",
    )
