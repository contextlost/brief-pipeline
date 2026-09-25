"""Load feeds.yaml + environment settings. Secrets ONLY come from env vars."""
import os
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent

DEFAULTS = {
    "max_items_per_feed": 20,
    "similarity_threshold": 0.35,
}


def _load_dotenv(root):
    """Minimal .env loader (no dependency): KEY=VALUE lines into os.environ."""
    path = root / ".env"
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip("'\""))


def load_config():
    _load_dotenv(ROOT)
    path = ROOT / "feeds.yaml"
    if not path.exists():
        raise FileNotFoundError(
            "feeds.yaml not found. Copy feeds.example.yaml to feeds.yaml "
            "and add your feeds."
        )
    with open(path, encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    settings = {**DEFAULTS, **(data.get("settings") or {})}
    if os.getenv("MAX_ITEMS_PER_FEED"):
        settings["max_items_per_feed"] = int(os.getenv("MAX_ITEMS_PER_FEED"))
    return {
        "feeds": data.get("feeds", []),
        "settings": settings,
        "llm": {
            "api_key": os.getenv("LLM_API_KEY"),
            "base_url": os.getenv("LLM_BASE_URL") or "https://api.openai.com/v1",
            "model": os.getenv("LLM_MODEL") or "gpt-4o-mini",
        },
        # Reserved for later steps (e.g. full-article research). Never in git.
        "secrets": {"news_api_key": os.getenv("NEWS_API_KEY")},
    }
