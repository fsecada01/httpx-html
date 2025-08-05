"""Rendering-related exceptions."""

# Re-export from main exceptions module for backward compatibility
from ..exceptions import MaxRetriesExceeded as MaxRetries

__all__ = ["MaxRetries"]