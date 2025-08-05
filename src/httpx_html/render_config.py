"""Configuration dataclass for HTML rendering operations."""

from dataclasses import dataclass
from typing import Optional, Union

from .constants import (
    DEFAULT_RENDER_RETRIES,
    DEFAULT_RENDER_WAIT,
    DEFAULT_RENDER_SLEEP,
    DEFAULT_RENDER_TIMEOUT,
)


@dataclass
class RenderConfig:
    """Configuration for HTML rendering operations.
    
    Consolidates all rendering parameters into a single configuration object
    to improve method signatures and maintainability.
    """
    
    retries: int = DEFAULT_RENDER_RETRIES
    script: Optional[str] = None
    wait: float = DEFAULT_RENDER_WAIT
    scrolldown: Union[bool, int] = False
    sleep: int = DEFAULT_RENDER_SLEEP
    reload: bool = True
    timeout: Union[float, int] = DEFAULT_RENDER_TIMEOUT
    wait_until: Optional[Union[str, list[str]]] = None
    keep_page: bool = False
    cookies: Optional[list[dict]] = None
    send_cookies_session: bool = False
    
    def __post_init__(self):
        """Validate and normalize configuration values."""
        if self.cookies is None:
            self.cookies = [{}]
        
        # Convert scrolldown bool to int for consistency
        if isinstance(self.scrolldown, bool) and self.scrolldown:
            self.scrolldown = 1
        elif isinstance(self.scrolldown, bool) and not self.scrolldown:
            self.scrolldown = 0