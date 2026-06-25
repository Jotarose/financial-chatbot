from openai import pydantic_function_tool

from schemas.nota import CrearNota

tools = [pydantic_function_tool(CrearNota)]
