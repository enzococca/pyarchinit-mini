"""AI Chat history models — persistent conversations with the AI assistant."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base


class AIConversation(Base):
    __tablename__ = 'ai_conversations'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user = Column(String(150), nullable=False, index=True)
    title = Column(String(255))
    site_name = Column(String(255), index=True)
    provider = Column(String(50))
    model = Column(String(100))
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    last_message_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    messages = relationship('AIMessage', back_populates='conversation',
                            cascade='all, delete-orphan', order_by='AIMessage.id')

    def to_dict(self, include_messages: bool = False):
        d = {
            'id': self.id, 'user': self.user,
            'title': self.title or '(senza titolo)',
            'site_name': self.site_name, 'provider': self.provider, 'model': self.model,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'last_message_at': self.last_message_at.isoformat() if self.last_message_at else None,
            'message_count': len(self.messages) if self.messages is not None else 0,
        }
        if include_messages:
            d['messages'] = [m.to_dict() for m in self.messages]
        return d


class AIMessage(Base):
    __tablename__ = 'ai_messages'
    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(Integer,
        ForeignKey('ai_conversations.id', ondelete='CASCADE'),
        nullable=False, index=True)
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    conversation = relationship('AIConversation', back_populates='messages')

    def to_dict(self):
        return {
            'id': self.id, 'role': self.role, 'content': self.content,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


__all__ = ['AIConversation', 'AIMessage']
