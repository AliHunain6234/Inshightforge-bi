import os
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class Settings:
    root: Path
    db_path: Path
    secret: str
    host: str = "127.0.0.1"
    port: int = 8080
    session_ttl: int = 3600
    max_body: int = 2_000_000

    @classmethod
    def load(cls, root=None):
        root = Path(root or Path(__file__).resolve().parents[1])
        db = Path(os.getenv("DB_PATH", "data/insightforge.db"))
        if not db.is_absolute(): db = root / db
        return cls(root, db, os.getenv("APP_SECRET", "change-me-to-a-long-random-secret"),
                   os.getenv("HOST", "127.0.0.1"), int(os.getenv("PORT", "8080")))
