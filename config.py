from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4o"
    system_prompt: str = "You are a helpful assistant."

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
