"""AppSetting model — generic key/value store for runtime configuration.

Used by:
- AI keys (openai_api_key, anthropic_api_key) — encrypted
- AI provider/model defaults — plain
- Backup scheduler config (backup_frequency, backup_keep_last, backup_enabled)
"""
from sqlalchemy import Boolean, Column, Integer, String, Text

from .base import BaseModel


class AppSetting(BaseModel):
    __tablename__ = "app_settings"

    id_setting = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(100), unique=True, nullable=False, index=True)
    value = Column(Text)
    is_secret = Column(Boolean, default=False, nullable=False)
    description = Column(Text)

    def __repr__(self) -> str:
        masked = "***" if self.is_secret else (self.value or "")
        return f"<AppSetting key={self.key!r} value={masked!r}>"
