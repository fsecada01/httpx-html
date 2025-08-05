"""Rendering-related exceptions."""


class MaxRetries(Exception):
    """Raised when maximum render retries are exhausted."""

    def __init__(self, message):
        self.message = message