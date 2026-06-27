from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from crud.nota import borrar_nota, contar_notas, crear_nota, leer_notas
from database.session import get_db_session
from schemas.nota import BorrarNota, CrearNota, LeerNotas


def crear_nota_tool(**kwargs) -> dict:
    try:
        # 1. Validación de Pydantic (Intercepta alucinaciones del LLM)
        data = CrearNota(**kwargs)

        # 2. Transacción de Base de Datos (Intercepta fallos de persistencia)
        with get_db_session() as db:
            nota = crear_nota(db, data)
            return {
                "estado": "exito",
                "id": nota.id,
                "titulo": nota.titulo,
            }

    except ValidationError as validation_error:
        return {
            "estado": "error",
            "motivo": "Los datos generados por el modelo no cumplen el esquema de la herramienta.",
            "detalle_tecnico": str(validation_error),
        }
    except SQLAlchemyError as db_error:
        return {
            "estado": "error",
            "motivo": "Error de ejecución en la base de datos.",
            "detalle_tecnico": str(db_error),
        }
    except Exception as e:
        return {
            "estado": "error",
            "motivo": "Fallo interno del servidor en la capa de la herramienta.",
            "detalle_tecnico": str(e),
        }


def leer_notas_tool(**kwargs) -> list[dict] | dict:
    try:
        data = LeerNotas(**kwargs)  # Extrae el límite si el LLM lo ha enviado

        with get_db_session() as db:
            notas_db = leer_notas(db, limite=data.limite)
            return [
                {
                    "id": n.id,
                    "titulo": n.titulo,
                    "categoria": n.categoria,
                    "contenido": n.contenido,
                }
                for n in notas_db
            ]

    except ValidationError as validation_error:
        return {
            "estado": "error",
            "motivo": "Parámetros inválidos",
            "detalle": str(validation_error),
        }
    except SQLAlchemyError as db_error:
        return {"estado": "error", "motivo": "Fallo de lectura BD", "detalle": str(db_error)}
    except Exception as e:
        return {"estado": "error", "motivo": "Error interno", "detalle": str(e)}


def contar_notas_tool(**kwargs) -> dict:
    try:
        with get_db_session() as db:
            total_notas = contar_notas(db)
            return {
                "estado": "exito",
                "total_notas": total_notas,
            }

    except SQLAlchemyError as db_error:
        return {
            "estado": "error",
            "motivo": "Fallo de conexión o lectura en la base de datos",
            "detalle_tecnico": str(db_error),
        }
    except Exception as e:
        return {
            "estado": "error",
            "motivo": "Fallo interno ejecutando el conteo",
            "detalle_tecnico": str(e),
        }


def borrar_nota_tool(**kwargs) -> dict:
    try:
        with get_db_session() as db:
            data = BorrarNota(**kwargs)
            nota_id = data.id  # No puedo puedo pasarle el objeto BorrarNota

            result = borrar_nota(db, nota_id)

            if result["success"]:
                return {
                    "estado": "exito",
                    "nota_id": result["id"],
                    "nota_titulo": result["titulo"],
                }
            else:
                return {
                    "estado": "error",
                    "motivo": f"No se encontro ninguna nota con el id: {data}",
                }

    except SQLAlchemyError as db_error:
        return {
            "estado": "error",
            "motivo": "Fallo de conexión o lectura en la base de datos",
            "detalle_tecnico": str(db_error),
        }
    except Exception as e:
        return {
            "estado": "error",
            "motivo": "Fallo interno ejecutando la operacion de eliminacion.",
            "detalle_tecnico": str(e),
        }
