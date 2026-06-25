# schemas/provider_response.py

from typing import Any

from pydantic import BaseModel, Field


class ToolCall(BaseModel):
    id: str = Field(
        ...,
        description="Identificador único de la llamada a la herramienta proporcionado por la API.",
    )
    nombre: str = Field(..., description="Nombre de la función a ejecutar.")
    argumentos: dict[str, Any] = Field(
        ..., description="Argumentos parseados en formato diccionario listos para inyección."
    )


class ProviderResponse(BaseModel):
    content: str | None = Field(
        default=None, description="Contenido en lenguaje natural generado en la Fase 1, si existe."
    )
    tool_calls: list[ToolCall] = Field(
        default_factory=list,
        description="Lista estandarizada de herramientas solicitadas por el modelo.",
    )
    raw_tool_calls_data: Any = Field(
        default=None,
        description="Objeto nativo de la API requerido para la reconstrucción del estado transaccional en el historial.",
    )

    def ha_pedido_usar_tools(self) -> bool:
        return len(self.tool_calls) > 0
