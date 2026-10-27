"""Runtime configuration; credentials are injected through the environment."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    code_agent_name: str = "code-agent"
    code_agent_env: str = "development"
    knowledge_base_url: str = ""
    llm_api_key: str = ""
    source_control_token: str = ""


settings = Settings()
