"""Configuration constants for httpx-html library."""

# Default encoding and URL settings
DEFAULT_ENCODING = "utf-8"
DEFAULT_URL = "https://example.org/"

# Default user agent string
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) "
    "AppleWebKit/603.3.8 (KHTML, like Gecko) "
    "Version/10.1.2 Safari/603.3.8"
)

# Default pagination symbols
DEFAULT_NEXT_SYMBOL = ["next", "more", "older"]

# Render configuration defaults
DEFAULT_RENDER_RETRIES = 8
DEFAULT_RENDER_WAIT = 0.2
DEFAULT_RENDER_TIMEOUT = 8.0
DEFAULT_RENDER_SLEEP = 0