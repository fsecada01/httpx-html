"""Cookie handling utilities for browser rendering."""

import http.cookiejar
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from collections.abc import MutableMapping


class CookieHandler:
    """Handles cookie conversion between different formats for browser rendering."""
    
    @staticmethod
    def convert_cookiejar_to_render(
        session_cookiejar: http.cookiejar.Cookie,
    ) -> "MutableMapping[str, str]":
        """
        Convert HTMLSession.cookies:cookiejar[] for browser.newPage().setCookie
        
        Args:
            session_cookiejar: Cookie jar from session
            
        Returns:
            Dictionary with cookie fields for browser setCookie
        """
        cookie_render = {}

        def _safe_get_attr(cookiejar, key: str) -> Optional[str]:
            """Safely get attribute from cookiejar, replacing the dangerous eval() approach."""
            try:
                value = getattr(cookiejar, key, None)
                return {key: value} if value else {}
            except Exception:
                return {}

        # Cookie fields expected by pyppeteer setCookie:
        # * name (str): **required**
        # * value (str): **required** 
        # * url (str)
        # * domain (str)
        # * path (str)
        # * expires (number): Unix time in seconds
        # * httpOnly (bool)
        # * secure (bool)
        # * sameSite (str): 'Strict' or 'Lax'
        
        keys = [
            "name",
            "value", 
            "url",
            "domain",
            "path",
            "sameSite",
            "expires",
            "httpOnly", 
            "secure",
        ]
        
        for key in keys:
            cookie_render.update(_safe_get_attr(session_cookiejar, key))
            
        return cookie_render

    @staticmethod
    def convert_session_cookies_to_render(
        session_cookies: http.cookiejar.CookieJar,
    ) -> list["MutableMapping[str, str]"]:
        """Convert HTMLSession.cookies for browser.newPage().setCookie.
        
        Args:
            session_cookies: Session cookie jar
            
        Returns:
            List of cookie dictionaries for browser rendering
        """
        if isinstance(session_cookies, http.cookiejar.CookieJar):
            return [
                CookieHandler.convert_cookiejar_to_render(cookie) 
                for cookie in session_cookies
            ]
        return []