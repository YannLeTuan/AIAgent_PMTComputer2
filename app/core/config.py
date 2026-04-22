from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    GEMINI_API_KEY: str
    GEMINI_MODEL: str = "gemini-2.5-flash"
    DATABASE_URL: str = "sqlite:///./ecommerce.db"
    VECTOR_INDEX_PATH: str = "./data/vector_index/faiss_index"
    EMBEDDING_MODEL: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    TOP_K_RETRIEVAL: int = 4
    TELEGRAM_BOT_TOKEN: str | None = None
    DISCORD_BOT_TOKEN: str | None = None
    FACEBOOK_PAGE_TOKEN: str | None = None
    FACEBOOK_VERIFY_TOKEN: str | None = None
    FACEBOOK_APP_SECRET: str | None = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()