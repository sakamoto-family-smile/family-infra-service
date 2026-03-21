from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    ENV: str = "dev"
    DEBUG: bool = False

    # GCP
    GCP_PROJECT_ID: str = "youyaku-ai-dev"
    GCP_REGION: str = "asia-northeast1"

    # Cloud SQL
    CLOUD_SQL_INSTANCE: str = ""
    DB_NAME: str = "family_app"
    DB_USER: str = "family_app"
    DB_PASSWORD: str = ""

    # Firebase
    FIREBASE_PROJECT_ID: str = ""

    # Cloud Storage
    GCS_BUCKET: str = "family-app-media-dev"

    # Cloud Tasks
    CLOUD_TASKS_QUEUE: str = "family-app-tasks"
    CLOUD_TASKS_LOCATION: str = "asia-northeast1"
    CLOUD_RUN_SERVICE_URL: str = ""

    @property
    def is_production(self) -> bool:
        return self.ENV == "prod"


settings = Settings()
