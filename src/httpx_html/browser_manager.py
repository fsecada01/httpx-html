"""Browser lifecycle management for httpx-html."""

import asyncio
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    import pyppeteer


class BrowserManager:
    """Manages browser lifecycle and ensures consistent browser handling across sessions."""
    
    def __init__(self, verify: bool = True, browser_args: Optional[list[str]] = None):
        """Initialize browser manager.
        
        Args:
            verify: Whether to verify SSL certificates
            browser_args: Arguments to pass to browser launch
        """
        self._browser: Optional["pyppeteer.Browser"] = None
        self._browser_launching = False
        self.verify = verify
        self.browser_args = browser_args or ["--no-sandbox"]
        
    @property
    def has_browser(self) -> bool:
        """Check if browser instance exists."""
        return self._browser is not None
        
    async def get_browser(self) -> "pyppeteer.Browser":
        """Get browser instance, launching if necessary.
        
        Returns:
            pyppeteer.Browser: The browser instance
        """
        if self._browser is None and not self._browser_launching:
            self._browser_launching = True
            try:
                import pyppeteer
                self._browser = await pyppeteer.launch(
                    ignoreHTTPSErrors=not self.verify,
                    headless=True,
                    args=self.browser_args
                )
            finally:
                self._browser_launching = False
                
        # Wait for browser to be ready if it's launching
        while self._browser_launching:
            await asyncio.sleep(0.1)
            
        return self._browser
        
    def get_browser_sync(self, loop: asyncio.AbstractEventLoop) -> "pyppeteer.Browser":
        """Get browser instance synchronously using provided event loop.
        
        Args:
            loop: Event loop to use for async operations
            
        Returns:
            pyppeteer.Browser: The browser instance
            
        Raises:
            RuntimeError: If called from within a running event loop
        """
        if loop.is_running():
            raise RuntimeError(
                "Cannot use synchronous browser access within an existing event loop. "
                "Use get_browser() instead."
            )
        return loop.run_until_complete(self.get_browser())
        
    async def close_browser(self) -> None:
        """Close the browser if it exists."""
        if self._browser is not None:
            await self._browser.close()
            self._browser = None
            
    def close_browser_sync(self, loop: asyncio.AbstractEventLoop) -> None:
        """Close the browser synchronously using provided event loop."""
        if self._browser is not None:
            loop.run_until_complete(self.close_browser())