"""AIChatService — CRUD for AI conversation history."""
from datetime import datetime
from typing import List, Optional
from ..models.ai_chat import AIConversation, AIMessage


class AIChatService:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def list_conversations(self, user: str, limit: int = 50, offset: int = 0) -> List[dict]:
        with self.db_manager.connection.get_session() as session:
            q = (session.query(AIConversation)
                 .filter(AIConversation.user == user)
                 .order_by(AIConversation.last_message_at.desc())
                 .limit(limit).offset(offset))
            return [c.to_dict() for c in q.all()]

    def get_conversation(self, conversation_id: int, user: str) -> Optional[dict]:
        with self.db_manager.connection.get_session() as session:
            c = (session.query(AIConversation)
                 .filter(AIConversation.id == conversation_id,
                         AIConversation.user == user).first())
            return c.to_dict(include_messages=True) if c else None

    def create_conversation(self, user: str, title: str = None, site_name: str = None,
                            provider: str = None, model: str = None) -> int:
        with self.db_manager.connection.get_session() as session:
            now = datetime.utcnow()
            c = AIConversation(user=user, title=(title or '')[:255] or None,
                               site_name=site_name, provider=provider, model=model,
                               started_at=now, last_message_at=now)
            session.add(c); session.flush()
            return c.id

    def append_message(self, conversation_id: int, role: str, content: str) -> int:
        with self.db_manager.connection.get_session() as session:
            m = AIMessage(conversation_id=conversation_id, role=role,
                          content=content, created_at=datetime.utcnow())
            session.add(m)
            c = session.query(AIConversation).filter(
                AIConversation.id == conversation_id).first()
            if c:
                c.last_message_at = m.created_at
                if not c.title:
                    first = (content or '').strip().splitlines()
                    if first: c.title = first[0][:80]
            session.flush()
            return m.id

    def rename_conversation(self, conversation_id: int, user: str, title: str) -> bool:
        with self.db_manager.connection.get_session() as session:
            c = session.query(AIConversation).filter(
                AIConversation.id == conversation_id,
                AIConversation.user == user).first()
            if not c: return False
            c.title = (title or '').strip()[:255] or None
            return True

    def delete_conversation(self, conversation_id: int, user: str) -> bool:
        with self.db_manager.connection.get_session() as session:
            c = session.query(AIConversation).filter(
                AIConversation.id == conversation_id,
                AIConversation.user == user).first()
            if not c: return False
            session.delete(c)
            return True
