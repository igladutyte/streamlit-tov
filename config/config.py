import os
from pathlib import Path
from typing import Optional
from pydantic import BaseModel
from dotenv import load_dotenv

# Load .env from project root if present
PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")


class AppConfig(BaseModel):
    app_name: str = "Decodo TOV Copywriter"
    data_dir: Path = PROJECT_ROOT / "data"
    db_file: Path = PROJECT_ROOT / "data" / "app_state.json"

    # OpenAI
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    # Generation defaults
    max_tokens_short: int = 200
    max_tokens_medium: int = 400
    max_tokens_long: int = 800
    temperature_subtle: float = 0.4
    temperature_balanced: float = 0.7
    temperature_strong: float = 0.95


def get_config() -> AppConfig:
    cfg = AppConfig()
    cfg.data_dir.mkdir(parents=True, exist_ok=True)
    return cfg
