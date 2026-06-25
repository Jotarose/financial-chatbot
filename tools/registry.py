from openai import pydantic_function_tool

from schemas.nota import CrearNota

from .nota_tools import crear_nota_tool

tools = [
    pydantic_function_tool(
        CrearNota,
        name="crear_nota",
        description="Crea una nota en la base de datos.",
    )
]


tool_router = {
    "crear_nota": crear_nota_tool,
}
