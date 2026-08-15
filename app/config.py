import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    meli_access_token: str | None = os.getenv("MELI_ACCESS_TOKEN") or None
    meli_site_id: str = os.getenv("MELI_SITE_ID", "MLB")
    api_url: str = os.getenv("DEALMIND_API_URL", "http://127.0.0.1:8000")

settings = Settings()
