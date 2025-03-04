#!/usr/bin/env python3
import sys

from twat_search.web.engines.lib_falla.core.duckduckgo import DuckDuckGo


def test_sync():
    d = DuckDuckGo()
    try:
        return d.search("FontLab")
    except Exception:
        return None


if __name__ == "__main__":
    results = test_sync()
    if results:
        pass
    else:
        pass
