# app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Definimos las variables y su tipo de dato (Pydantic hará la conversión)
    # Si no le ponemos un valor por defecto (como a SECRET_KEY), será OBLIGATORIA
    DATABASE_URL: str
    DEBUG_MODE: bool = False
    # OpenAI
    OPENAI_API_KEY: str
    OPENAI_BASE_URL: str
    # Azure OpenAI
    AZURE_OPENAI_ENDPOINT: str
    AZURE_OPENAI_API_KEY: str
    AZURE_API_VERSION: str
    # Anthropic
    ANTHROPIC_API_KEY: str
    # Gemini
    GEMINI_API_KEY: str
    # Ollama Local Model
    OLLAMA_API_KEY: str
    OLLAMA_BASE_URL: str

    # Le indicamos a Pydantic que lea automáticamente el archivo .env
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


# Instanciamos la clase una sola vez.
# Al hacer esto, Pydantic lee el .env, valida los datos y los guarda aquí.
settings = Settings()
