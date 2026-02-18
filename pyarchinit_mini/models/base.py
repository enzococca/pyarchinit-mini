"""
Base model class for all PyArchInit-Mini models
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import DateTime, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

def _generate_uuid():
    return str(uuid.uuid4())

class BaseModel(Base):
    """
    Base model class with common fields and methods
    """
    __abstract__ = True

    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # Concurrency / sync columns
    entity_uuid = Column(String(36), unique=True, index=True, default=_generate_uuid)
    version_number = Column(Integer, default=1, nullable=False)
    last_modified_by = Column(String(100))
    last_modified_timestamp = Column(DateTime(timezone=True))
    sync_status = Column(String(20), default='new')
    editing_by = Column(String(100))
    editing_since = Column(DateTime(timezone=True))

    def to_dict(self):
        """Convert model instance to dictionary"""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
    
    def update_from_dict(self, data):
        """Update model instance from dictionary"""
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)