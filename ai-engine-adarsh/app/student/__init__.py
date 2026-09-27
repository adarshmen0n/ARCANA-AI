"""Student Model subsystem managing learner profiles, progress, and history."""

from .models import StudentInteractionRecord
from .service import StudentService, student_service

__all__ = ["StudentInteractionRecord", "StudentService", "student_service"]
