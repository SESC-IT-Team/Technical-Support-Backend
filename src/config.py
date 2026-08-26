from pydantic_settings import BaseSettings, SettingsConfigDict
from sesc_auth_sdk.settings import AuthRouterSettings, TokenValidationSettings


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    postgres_host: str
    postgres_port: int
    postgres_user: str
    postgres_password: str
    postgres_db: str

    root_path: str = '/'

    s3_endpoint_url: str
    s3_access_key: str
    s3_secret_key: str
    s3_bucket_name: str
    s3_region_name: str | None = None

    auth_router_settings: AuthRouterSettings = AuthRouterSettings(_env_file='.env')
    token_validation_settings: TokenValidationSettings = TokenValidationSettings(_env_file='.env')

    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

settings = Settings(postgres_host='', postgres_port=0, postgres_user='', postgres_password='', postgres_db='',
                    s3_endpoint_url='', s3_access_key='', s3_secret_key='', s3_bucket_name='')