"""Runtime configuration; credentials are injected through the environment."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    code_agent_name: str = "code-agent"
    code_agent_env: str = "development"
    knowledge_base_url: str = ""
    llm_api_key: str = ""
    source_control_token: str = ""
    deep_agent_enabled: bool = True
    deep_agent_model_id: str = "anthropic.claude-3-haiku-20240307-v1:0"
    aws_region: str = "us-east-1"
    sandbox_source_root: Path = Path("./repositories")
    sandbox_work_root: Path = Path("./.agent-sandboxes")


settings = Settings()
