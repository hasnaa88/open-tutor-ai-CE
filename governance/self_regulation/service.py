"""Self-regulation feedback service."""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from data.models import Feedback
from governance.self_regulation.repository import FeedbackRepository


class SelfRegulationService:
    """Service for self-regulation and feedback operations."""

    def __init__(self, session: Session):
        self.repo = FeedbackRepository(session, Feedback)

    def submit(
        self,
        user_id: str,
        feedback_type: str,
        response_id: Optional[str] = None,
        content: Optional[str] = None,
        rating: Optional[float] = None,
    ) -> Feedback:
        return self.repo.create(
            id=str(uuid.uuid4()),
            user_id=user_id,
            response_id=response_id,
            feedback_type=feedback_type,
            content=content,
            rating=rating,
            created_at=datetime.utcnow(),
        )

    def get(self, feedback_id: str) -> Optional[Feedback]:
        return self.repo.get_by_id(feedback_id)

    def get_all(self) -> List[Feedback]:
        return self.repo.get_all(limit=10000)

    def get_by_user(self, user_id: str) -> List[Feedback]:
        return self.repo.get_by_user(user_id)

    def get_by_response(self, response_id: str) -> List[Feedback]:
        return self.repo.get_by_response(response_id)

    def get_by_type(self, feedback_type: str) -> List[Feedback]:
        return self.repo.get_by_type(feedback_type)

    def update(self, feedback_id: str, data: Dict[str, Any]) -> Optional[Feedback]:
        return self.repo.update(feedback_id, **data)

    def delete(self, feedback_id: str) -> bool:
        return self.repo.delete(feedback_id)
