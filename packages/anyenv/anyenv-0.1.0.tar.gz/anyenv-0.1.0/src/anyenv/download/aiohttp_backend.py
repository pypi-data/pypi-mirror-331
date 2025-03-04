"""aiohttp backend implementation for anyenv."""

from __future__ import annotations

import os
import pathlib
from typing import Any

import aiohttp
from aiohttp_client_cache import CachedSession, SQLiteBackend

from anyenv.download.base import (
    HttpBackend,
    HttpResponse,
    Method,
    ProgressCallback,
    Session,
)


class AiohttpResponse(HttpResponse):
    """aiohttp implementation of HTTP response."""

    def __init__(self, response: aiohttp.ClientResponse) -> None:
        self._response = response

    @property
    def status_code(self) -> int:
        return self._response.status

    @property
    def headers(self) -> dict[str, str]:
        return dict(self._response.headers)

    async def text(self) -> str:
        return await self._response.text()

    async def json(self) -> Any:
        return await self._response.json()

    async def bytes(self) -> bytes:
        return await self._response.read()


class AiohttpSession(Session):
    """aiohttp implementation of HTTP session."""

    def __init__(
        self,
        session: CachedSession,
        base_url: str | None = None,
    ) -> None:
        self._session = session
        self._base_url = base_url

    async def request(
        self,
        method: Method,
        url: str,
        *,
        params: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
        json: Any = None,
        data: Any = None,
        timeout: float | None = None,
        cache: bool = False,
    ) -> HttpResponse:
        if self._base_url:
            url = f"{self._base_url.rstrip('/')}/{url.lstrip('/')}"

        response = await self._session.request(
            method,
            url,
            params=params,
            headers=headers,
            json=json,
            data=data,
            timeout=aiohttp.ClientTimeout(total=timeout) if timeout else None,
            expire_after=0 if not cache else None,  # Don't cache if cache=False
        )
        return AiohttpResponse(response)

    async def close(self) -> None:
        await self._session.close()


class AiohttpBackend(HttpBackend):
    """aiohttp implementation of HTTP backend."""

    async def _create_session(
        self,
        cache: bool = False,
        base_url: str | None = None,
        headers: dict[str, str] | None = None,
    ) -> CachedSession:
        if cache:
            cache_backend = SQLiteBackend(
                cache_name=os.path.join(self.cache_dir, "http_cache.db"),
                expire_after=self.cache_ttl,
            )
            return CachedSession(
                cache=cache_backend,
                headers=headers,
                base_url=base_url,
            )

        # Even when not caching, we use CachedSession for consistent interface
        return CachedSession(
            expire_after=0,  # Disable caching
            headers=headers,
            base_url=base_url,
        )

    async def request(
        self,
        method: Method,
        url: str,
        *,
        params: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
        json: Any = None,
        data: Any = None,
        timeout: float | None = None,
        cache: bool = False,
    ) -> HttpResponse:
        session = await self._create_session(cache=cache)
        try:
            response = await session.request(
                method,
                url,
                params=params,
                headers=headers,
                json=json,
                data=data,
                timeout=aiohttp.ClientTimeout(total=timeout) if timeout else None,
            )
            return AiohttpResponse(response)
        finally:
            await session.close()

    async def download(
        self,
        url: str,
        path: str | os.PathLike[str],
        *,
        headers: dict[str, str] | None = None,
        progress_callback: ProgressCallback | None = None,
        cache: bool = False,
    ) -> None:
        session = await self._create_session(cache=cache)
        try:
            async with session.get(url, headers=headers) as response:
                response.raise_for_status()

                total = int(response.headers.get("content-length", "0"))
                current = 0

                with pathlib.Path(path).open("wb") as f:
                    async for chunk in response.content.iter_chunked(8192):
                        f.write(chunk)
                        current += len(chunk)
                        if progress_callback:
                            await self._handle_callback(progress_callback, current, total)
        finally:
            await session.close()

    async def create_session(
        self,
        *,
        base_url: str | None = None,
        headers: dict[str, str] | None = None,
        cache: bool = False,
    ) -> Session:
        session = await self._create_session(
            cache=cache,
            base_url=base_url,
            headers=headers,
        )
        return AiohttpSession(session, base_url)
