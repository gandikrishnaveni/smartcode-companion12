from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "Smart Code Companion"
    API_V1_STR: str = "/api/v1"

    # IBM WatsonX credentials
    WATSONX_APIKEY: str
    WATSONX_PROJECT_ID: str
    WATSONX_URL: str

    # new speech-to-text fields
    IBM_STT_API_KEY: str | None = None
    IBM_STT_URL: str | None = None

    # AI Provider to decide which client to use
    AI_PROVIDER: str = "ibm"  # default can be 'ibm', or 'openai'

    # Pydantic v2 way to load env + ignore extras
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


def get_settings() -> Settings:
    return Settings()
