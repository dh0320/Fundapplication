from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://grantdraft:grantdraft_dev@db:5432/grantdraft"
    JGRANTS_API_BASE_URL: str = "https://api.jgrants-portal.go.jp/exp/v1/public"
    ERAD_BASE_URL: str = "https://www.e-rad.go.jp"

    class Config:
        env_file = ".env"


settings = Settings()
