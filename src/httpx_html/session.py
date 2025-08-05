import asyncio
from collections.abc import Mapping
from concurrent.futures import ThreadPoolExecutor
from functools import partial

import httpx
import pyppeteer
from fake_useragent import UserAgent

from .browser_manager import BrowserManager
from .constants import DEFAULT_ENCODING, DEFAULT_USER_AGENT
from .parse_ import HTML

useragent = None


class HTMLResponse(httpx.Response):
    """An HTML-enabled :class:`httpx.Response <httpx.Response>` object.
    Effectively the same, but with an intelligent ``.html`` property added.
    """

    def __init__(
        self,
        status_code: int,
        session: "BaseSession",
    ) -> None:
        super().__init__(status_code)
        self._html: HTML | None = None
        self.session = session

    @property
    def html(self) -> HTML:
        if not self._html:
            self._html = HTML(
                session=self.session,
                url=self.url,
                html=self.content,
                default_encoding=self.encoding,
            )

        return self._html

    @classmethod
    def _from_response(cls, response, session: "BaseSession") -> "HTMLResponse":
        html_r = cls(status_code=response.status_code, session=session)
        html_r.__dict__.update(response.__dict__)
        return html_r


def user_agent(style: Mapping | None = None) -> str:
    """Returns an apparently legit user-agent, if not requested one of a specific
    style. Defaults to a Chrome-style User-Agent.
    """
    global useragent

    if not useragent and style:
        useragent = UserAgent()

    return useragent[style] if style else DEFAULT_USER_AGENT


class BaseSession(httpx.Client):
    """A consumable session, for cookie persistence and connection pooling,
    amongst other things.
    """

    def __init__(
        self,
        *,
        mock_browser: bool = True,
        verify: bool = True,
        browser_args: list | None = None,
        proxies: Mapping[str, str] | None = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)

        # Initialize browser manager
        browser_args = ["--no-sandbox"] if not browser_args else browser_args
        self._browser_manager = BrowserManager(verify=verify, browser_args=browser_args)
        
        # mock a web browser's user agent
        if mock_browser:
            self.headers["User-Agent"] = user_agent()

        self.verify = verify
        self.follow_redirects = True

        if proxies:
            # fix requests-style proxy declaration
            self.proxies = {(k if ":" in k else f"{k}://"): v for k, v in proxies.items()}
        else:
            self.proxies = {}

    def request(self, *args, **kwargs) -> HTMLResponse:
        response = super().request(*args, **kwargs)
        if not response.encoding:
            response.encoding = DEFAULT_ENCODING
        return HTMLResponse._from_response(response, self)

    def mount(self, pattern: str, transport: httpx._transports.base.BaseTransport) -> None:
        self._mounts.update({httpx._utils.URLPattern(pattern): transport})

    @property
    async def browser(self) -> "pyppeteer.Browser":
        """
        Returns pyppeteer.Browser instance, creating it if necessary.
        """
        return await self._browser_manager.get_browser()


class HTMLSession(BaseSession):
    def __init__(
        self,
        *,
        mock_browser: bool = True,
        verify: bool = True,
        browser_args: list | None = None,
        proxies: Mapping[str, str] | None = None,
        **kwargs,
    ):
        super().__init__(
            mock_browser=mock_browser,
            verify=verify,
            browser_args=browser_args,
            proxies=proxies,
            **kwargs,
        )
        self.loop = None

    @property
    def browser(self) -> "pyppeteer.Browser":
        """
        Property for browser access in synchronous context.
        """
        self.loop = asyncio.get_event_loop()
        return self._browser_manager.get_browser_sync(self.loop)

    def close(self) -> None:
        """If a browser was created close it first."""
        if self._browser_manager.has_browser:
            self._browser_manager.close_browser_sync(self.loop)
        super().close()


class AsyncHTMLSession(BaseSession):
    """An async consumable session."""

    def __init__(
        self,
        loop=None,
        workers=None,
        mock_browser: bool = True,
        *args,
        **kwargs,
    ) -> None:
        """Set or create an event loop and a thread pool.

        :param loop: Asyncio loop to use.
        :param workers: Amount of threads to use for executing async calls.
            If not pass it will default to the number of processors on the
            machine, multiplied by 5.
        """
        super().__init__(*args, **kwargs)

        self.loop = loop or asyncio.get_event_loop()
        self.thread_pool = ThreadPoolExecutor(max_workers=workers)

    async def __aenter__(self) -> "AsyncHTMLSession":
        return self

    async def __aexit__(self, exc_t, exc_v, exc_tb) -> None:
        try:
            await self.close()
        except Exception:
            pass

        if exc_t:
            raise exc_t(exc_v)

    def request(self, *args, **kwargs) -> HTMLResponse:
        """Partial original request func and run it in a thread."""
        func = partial(super().request, *args, **kwargs)
        return self.loop.run_in_executor(self.thread_pool, func)

    async def close(self) -> None:
        """If a browser was created close it first."""
        await self._browser_manager.close_browser()
        super().close()

    def run(self, *coros):
        """Pass in all the coroutines you want to run, it will wrap each one
        in a task, run it and wait for the result. Return a list with all
        results, this is returned in the same order coros are passed in.
        """
        tasks = [asyncio.ensure_future(coro()) for coro in coros]
        done, _ = self.loop.run_until_complete(asyncio.wait(tasks))
        return [t.result() for t in done]
