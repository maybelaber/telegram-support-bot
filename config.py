import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class BotConfig:
    """Bot configuration"""
    token: str
    admin_ids: list[int]


@dataclass
class DatabaseConfig:
    """Database configuration"""
    url: str


@dataclass
class Config:
    """Main configuration"""
    bot: BotConfig
    db: DatabaseConfig


def load_config() -> Config:
    """Load configuration from environment variables"""
    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token:
        raise ValueError("BOT_TOKEN environment variable is not set")
    
    admin_ids_str = os.getenv("ADMIN_IDS", "")
    admin_ids = [int(id.strip()) for id in admin_ids_str.split(",") if id.strip()]
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is not set")
    
    return Config(
        bot=BotConfig(token=bot_token, admin_ids=admin_ids),
        db=DatabaseConfig(url=database_url)
    )
