from openai import pydantic_function_tool

from schemas.nota import BorrarNota, ContarNotas, CrearNota, LeerNotas

from .nota_tools import borrar_nota_tool, contar_notas_tool, crear_nota_tool, leer_notas_tool


def _to_responses_format(tool: dict) -> dict:
    """Convierte el formato chat.completions al formato aplanado de la Responses API."""
    if "function" in tool:
        return {
            "type": "function",
            **tool["function"],
        }
    return tool  # Ya está en el formato correcto


_raw_tools = [
    pydantic_function_tool(
        CrearNota, name="crear_nota", description="Crea una nota en la base de datos."
    ),
    pydantic_function_tool(
        LeerNotas,
        name="leer_notas",
        description="Activa esta herramienta SIEMPRE que el usuario pida ver, leer, mostrar, listar o buscar sus notas. Asume que todas las notas residen aquí, sin importar si menciona o no una base de datos.",
    ),
    pydantic_function_tool(
        ContarNotas,
        name="contar_notas",
        description="Activa esta herramienta SIEMPRE que el usuario pregunte por la cantidad, el total o cuántas notas tiene guardadas.",
    ),
    pydantic_function_tool(
        BorrarNota,
        name="borrar_nota",
        description="Activa esta herramienta SIEMPRE que el usuario pida eliminar o borrar una nota. IMPORTANTE: Esta acción es permanente. Si el usuario no ha proporcionado un ID explícito, primero usa 'leer_notas' para identificar el ID correcto y solicita confirmación si hay ambigüedad.",
    ),
]

tools = [_to_responses_format(t) for t in _raw_tools]

tool_router = {
    "crear_nota": crear_nota_tool,
    "leer_notas": leer_notas_tool,
    "contar_notas": contar_notas_tool,
    "borrar_nota": borrar_nota_tool,
}
