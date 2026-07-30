from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    mcp_host: str = "0.0.0.0"
    mcp_port: int = 8001
    crm_api_url: str = "http://localhost:8101"
    sales_api_url: str = "http://localhost:8102"
    tickets_api_url: str = "http://localhost:8103"
    contracts_api_url: str = "http://localhost:8104"
    products_api_url: str = "http://localhost:8105"


settings = Settings()
