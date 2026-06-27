# Financial Agent

Financial Agent es un chatbot financiero modular construido como un agente con herramientas (`tools`) y persistencia en base de datos. El proyecto aprovecha proveedores de IA como Azure OpenAI y permite que el agente decida cuándo responder directamente o cuándo invocar una herramienta para operar sobre datos reales.

## Qué hace este proyecto

- Permite conversar con un asistente financiero profesional.
- Soporta múltiples proveedores de IA con selección de proveedor principal y fallback.
- Integra un sistema de herramientas que pueden ejecutar operaciones con persistencia.
- Almacena notas financieras en una base de datos SQL mediante SQLAlchemy.
- Evalúa si el asistente debe usar una herramienta para tareas como crear, listar, contar o borrar notas.

## Arquitectura

El proyecto está organizado en capas claras:

- `database/`: conexión al motor SQL, definición de `SessionLocal`, y creación de esquemas.
- `models/`: modelos ORM de SQLAlchemy. Actualmente contiene el modelo `Nota`.
- `schemas/`: validación y serialización de datos con Pydantic para las herramientas y el dominio.
- `crud/`: operaciones de acceso a datos y reglas de persistencia (crear, leer, contar, borrar notas).
- `tools/`: implementación de herramientas ejecutables por el agente y registro de herramientas disponibles.
- `providers/`: adaptadores de proveedores de IA, incluido Azure OpenAI y otros posibles backend.
- `core/`: lógica del agente, administración de conversación y fallback entre proveedores.
- `config/`: configuración centralizada con `pydantic-settings`.

### Flujo principal

```text
Usuario -> Chatbot / agente -> decide usar tool o responder
                                        │
                                        ├──> si usa tool -> tools/ -> crud/ -> database/
                                        │
                                        └──> si no usa tool -> responde con IA directamente
```

## Estructura del proyecto

```text
financial-agent/
├── config/
│   └── settings.py         # Configuración de entorno y lectura de variables .env
├── core/
│   ├── chatbot.py          # Lógica del agente, flujo de tools y fallback
│   ├── conversation.py     # Historial de conversación con ventana deslizante
│   └── prompts.py          # Inicialización de la base de datos
├── crud/
│   └── nota.py             # Acceso a datos de notas
├── database/
│   ├── database.py         # Motor SQLAlchemy y base declarativa
│   ├── init_db.py          # Inicializa las tablas en la base de datos
│   └── session.py          # Context manager para sesiones de base de datos
├── models/
│   └── nota.py             # Modelo ORM de la tabla notas
├── providers/
│   ├── azureopenai_provider.py
│   ├── factory.py          # Crea proveedores configurados desde settings
│   ├── gemini_provider.py
│   ├── generic_provider.py
│   └── ollama_provider.py
├── schemas/
│   ├── nota.py             # Esquemas Pydantic para las herramientas de notas
│   ├── provider_response.py
│   └── usage_metadata.py
├── tools/
│   ├── nota_tools.py       # Implementación de herramientas de notas con validación y DB
│   └── registry.py         # Registro de tools y mapeo a funciones ejecutoras
├── main.py                 # Punto de entrada de la aplicación
├── pyproject.toml          # Dependencias y metadatos de paquete
└── README.md               # Documentación del proyecto
```

## Concepto de Tools

Las tools son funciones que el agente puede invocar cuando una petición necesita lógica adicional o acceso a datos. En este proyecto, las tools se utilizan para:

- `crear_nota`: guardar una nueva nota financiera en la base de datos.
- `leer_notas`: listar notas existentes.
- `contar_notas`: retornar la cantidad total de notas.
- `borrar_nota`: eliminar una nota por ID.

El agente decide automáticamente si debe usar una tool o generar una respuesta convencional. Esta decisión se toma antes de la generación final de la respuesta.

### Cómo funciona el sistema de tools

1. El usuario envía un mensaje al chatbot.
2. El agente envía el historial al proveedor de IA.
3. El modelo determina si debe invocar una tool.
4. Si hay una tool, el agente registra la llamada y ejecuta la función correspondiente.
5. La herramienta opera sobre la base de datos y devuelve un resultado estructurado.
6. El agente incluye el resultado de la tool en el contexto y genera la respuesta final.

## Persistencia de datos: notas

La funcionalidad principal de persistencia en esta versión está centrada en notas financieras.

- Las notas se representan con el modelo `models/nota.py`.
- Las reglas de negocio y operaciones CRUD están en `crud/nota.py`.
- Las herramientas validan los datos con `schemas/nota.py` antes de escribir en la base de datos.
- La sesión de base de datos se maneja con `database/session.py`.

### Campos de una nota

- `id`: identificador único.
- `titulo`: texto corto descriptivo.
- `contenido`: detalles de la nota.
- `categoria`: categoría financiera (por ejemplo, finanzas, presupuesto, inversiones, gastos, ingresos, objetivos, deudas, ahorros, general).
- `fecha_creacion`: fecha en que se creó la nota.
- `fecha_modificacion`: fecha de la última actualización.

## Configuración

El proyecto utiliza variables de entorno para todas las credenciales y la URL de la base de datos. Estas variables se leen desde un archivo `.env` gracias a `pydantic-settings`.

Ejemplo mínimo de `.env`:

```env
DATABASE_URL=sqlite:///./data.db
OPENAI_API_KEY=tu_clave_openai
OPENAI_BASE_URL=https://tu-endpoint.openai.azure.com
AZURE_OPENAI_ENDPOINT=https://tu-endpoint.openai.azure.com
AZURE_OPENAI_API_KEY=tu_clave_azure
AZURE_API_VERSION=2024-12-01
ANTHROPIC_API_KEY=tu_clave_anthropic
GEMINI_API_KEY=tu_clave_gemini
OLLAMA_API_KEY=tu_clave_ollama
OLLAMA_BASE_URL=http://localhost:11434
DEBUG_MODE=True
```

> Para un despliegue sencillo, `DATABASE_URL` puede apuntar a un archivo SQLite local. En producción se recomienda usar una base de datos gestionada.

## Ejecución

1. Crear y activar un entorno virtual:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

2. Instalar dependencias:

```powershell
pip install -e .
```

3. Crear el archivo `.env` con la configuración de tu proveedor y la base de datos.

4. Iniciar la base de datos y ejecutar el chatbot:

```powershell
python main.py
```

Al iniciar, el agente crea las tablas necesarias con `database/init_db.py` y carga los proveedores definidos en `providers/factory.py`.

## Uso

Una vez en el chatbot, puedes usar comandos especiales:

- `/salir`: salir del programa.
- `/limpiar`: limpiar el historial de conversación.
- `/cambiar`: cambiar el proveedor de IA principal y el fallback.
- `/estadisticas`: mostrar estadísticas de uso e tokens.
- `/ayuda`: ver comandos disponibles.

### Ejemplos de interacción

- `Crea una nota sobre mi presupuesto mensual con categoría gastos.`
- `Muéstrame las últimas notas financieras.`
- `¿Cuántas notas tengo guardadas?`
- `Borra la nota con id 3.`

## Mejora del proveedor Azure OpenAI

El proveedor Azure OpenAI es uno de los adaptadores soportados y funciona junto a una capa de fallback que evita que la sesión falle si el proveedor principal no responde. El agente puede:

- evaluar llamadas a tools con el modelo,
- generar respuestas por streaming,
- manejar errores entre proveedor principal y fallback.

## Por qué usar este proyecto

- Arquitectura modular preparada para añadir nuevas herramientas y proveedores.
- Persistencia real con SQLAlchemy para mantener memoria contextual útil entre sesiones.
- Diseño de agente moderno que separa la lógica de decisión (usar tool o no) de la ejecución operativa.
- Base sólida para prototipos de asistentes financieros con soporte de notas y consultas administrables.

## Contribuir

1. Abre un issue describiendo tu mejora.
2. Añade un nuevo proveedor en `providers/` o una nueva tool en `tools/`.
3. Añade los esquemas de validación necesarios en `schemas/`.
4. Actualiza la documentación y los tests si corresponde.

---

Financial Agent está diseñado como un proyecto de portafolio profesional para demostrar una aplicación real de agentes de IA con herramientas y persistencia en base de datos.
