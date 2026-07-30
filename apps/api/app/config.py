from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origin: str = "http://localhost:5173"

    mcp_server_url: str = "http://localhost:8001"

    azure_ai_endpoint: str = ""
    azure_ai_api_key: str = ""
    azure_chat_deployment: str = ""
    azure_embedding_deployment: str = ""

    azure_search_endpoint: str = ""
    azure_search_index: str = "enterprise-knowledge"
    azure_search_api_key: str = ""

    azure_storage_account: str = ""
    azure_storage_connection_string: str = ""

    applicationinsights_connection_string: str = ""

    azure_ad_tenant_id: str = ""
    azure_ad_client_id: str = ""
    azure_ad_client_secret: str = ""

    dev_auth_enabled: bool = True

    chunk_size: int = 800
    chunk_overlap: int = 120

    data_dir: str = "data"
    prompts_dir: str = "prompts"

    @property
    def azure_openai_configured(self) -> bool:
        return bool(
            self.azure_ai_endpoint
            and self.azure_ai_api_key
            and self.azure_chat_deployment
        )

    @property
    def azure_search_configured(self) -> bool:
        return bool(
            self.azure_search_endpoint
            and self.azure_search_api_key
            and self.azure_search_index
        )

    @property
    def azure_blob_configured(self) -> bool:
        return bool(self.azure_storage_connection_string)

    @property
    def entra_configured(self) -> bool:
        return bool(
            self.azure_ad_tenant_id
            and self.azure_ad_client_id
            and self.azure_ad_client_secret
        )

    @property
    def insights_configured(self) -> bool:
        return bool(self.applicationinsights_connection_string)


settings = Settings()
