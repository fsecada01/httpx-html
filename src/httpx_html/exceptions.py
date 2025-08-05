"""Custom exceptions for httpx-html library."""


class HttpxHtmlError(Exception):
    """Base exception for all httpx-html related errors."""
    pass


class RenderError(HttpxHtmlError):
    """Base exception for rendering-related errors."""
    pass


class MaxRetriesExceeded(RenderError):
    """Raised when maximum render retries are exhausted."""
    
    def __init__(self, message: str, retries: int = 0):
        super().__init__(message)
        self.message = message
        self.retries = retries
        
    def __str__(self) -> str:
        return f"{self.message} (after {self.retries} retries)"


class BrowserError(RenderError):
    """Raised when browser operations fail."""
    pass


class BrowserLaunchError(BrowserError):
    """Raised when browser fails to launch."""
    pass


class SessionError(HttpxHtmlError):
    """Base exception for session-related errors."""
    pass


class EventLoopError(SessionError):
    """Raised when there are event loop conflicts."""
    
    def __init__(self, message: str = None):
        default_message = (
            "Cannot use HTMLSession within an existing event loop. "
            "Use AsyncHTMLSession instead."
        )
        super().__init__(message or default_message)


class ParsingError(HttpxHtmlError):
    """Base exception for HTML parsing errors."""
    pass


class EncodingError(ParsingError):
    """Raised when encoding detection or conversion fails."""
    pass