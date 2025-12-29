"""
Compatibility shim for Cloud Tasks routes.
Delegates to infrastructure.tasks.router to match README layout.
"""
from infrastructure.tasks.router import router

__all__ = ["router"]
