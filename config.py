"""General configuration.
Config: Bot Config
"""
# ruff: noqa: ARG003
import logging
import sys
from pathlib import Path
from typing import Annotated
from pydantic import ValidationError, field_validator
from pydantic.networks import UrlConstraints
from pydantic_core import MultiHostUrl
from pydantic_settings import (
    BaseSettings,
    DotEnvSettingsSource,
    EnvSettingsSource,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)
from pydantic_settings.sources import SettingsError
from typing_extensions import TypedDict

logger = logging.getLogger(__name__)
MongoSRVDsn = Annotated[MultiHostUrl, UrlConstraints(allowed_schemes=["mongodb+srv"])]
BASE_PATH = Path(__file__).parent.parent

class ChannelInfo(TypedDict):
    is_private: bool
    invite_link: str
    channel_id: int

class Config(BaseSettings):
    """A general configuration setup to read either .env or environment keys."""

    # --- সরাসরি আপনার তথ্য এখানে বসিয়ে দেওয়া হয়েছে ---
    PORT: int = 8080
    HOSTNAME: str = "0.0.0.0"  
    HTTP_SERVER: bool = True

    API_ID: int = 20726200
    API_HASH: str = "5e927fe061c2f988a843053b67f47da9"
    BOT_TOKEN: str = "8445895843:AAH_mWI4tBRsTs0fGbWIeqg80uNPEfyK3QQ"
    BOT_WORKER: int = 8
    BOT_SESSION: str = "Zaws-File-Share"
    BOT_MAX_MESSAGE_CACHE_SIZE: int = 100

    # আপনার MongoDB লিঙ্কটি নিচে বসান (পাসওয়ার্ডসহ)
    MONGO_DB_URL: str = "mongodb+srv://anik123:rashni2215@cluster0.vm9te27.mongodb.net/?appName=Cluster0"
    MONGO_DB_NAME: str = "Zaws-File-Share"

    # --- চ্যানেল এবং এডমিন সেটআপ ---
    BACKUP_CHANNEL: int = -100XXXXXXXXXX  # <--- এখানে আপনার ব্যাকআপ চ্যানেল আইডি দিন
    ROOT_ADMINS_ID: list[int] = [XXXXXXXXXX] # <--- এখানে আপনার নিজের আইডি দিন
    FORCE_SUB_CHANNELS: list[int] = [-100XXXXXXXXXX] # <--- এখানে মেইন চ্যানেল আইডি দিন
    
    RATE_LIMITER: bool = True
    PRIVATE_REQUEST: bool = False
    PROTECT_CONTENT: bool = True
    AUTO_GENERATE_LINK: bool = True

    channels_n_invite: dict[str, ChannelInfo] = {}

    model_config = SettingsConfigDict(
        env_file=f"{BASE_PATH}/.env",
    )

    @field_validator("ROOT_ADMINS_ID", "FORCE_SUB_CHANNELS", mode="before")
    @classmethod
    def convert_int_to_list(cls, value: int | list[int]) -> list[int]:
        if isinstance(value, int):
            return [value]
        return value

    @field_validator("channels_n_invite", mode="before")
    @classmethod
    def ignore_keys(cls, value: dict[str, ChannelInfo]) -> dict[str, ChannelInfo]:
        return {}

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            DotEnvSettingsSource(settings_cls),
            EnvSettingsSource(settings_cls),
        )

try:
    config = Config()  
except (ValidationError, SettingsError):
    logger.exception("Configuration Error")
    sys.exit(1)
    
