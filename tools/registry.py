from openai import pydantic_function_tool

from schemas.nota import ContarNotas, CrearNota, LeerNotas

from .nota_tools import contar_notas_tool, crear_nota_tool, leer_notas_tool

tools = [
    pydantic_function_tool(
        CrearNota,
        name="crear_nota",
        description="Crea una nota en la base de datos.",
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
]


tool_router = {
    "crear_nota": crear_nota_tool,
    "leer_notas": leer_notas_tool,
    "contar_notas": contar_notas_tool,
}
