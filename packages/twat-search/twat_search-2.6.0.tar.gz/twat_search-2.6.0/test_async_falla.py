#!/usr/bin/env python3
import asyncio
import sys

from twat_search.web.engines.lib_falla.core.duckduckgo import DuckDuckGo


async def test_async():
    d = DuckDuckGo()
    try:
        return await d.search_async("FontLab")
    except Exception:
        return None


if __name__ == "__main__":
    try:
        results = asyncio.run(test_async())
        if results:
            pass
        else:
            pass
    except Exception:
        pass
