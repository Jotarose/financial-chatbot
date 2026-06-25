# schemas/nota.py

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
