#!/usr/bin/env python3
"""
Main script for the Falla search engine scraper.

This module provides the command-line interface for the Falla search engine scraper.
It demonstrates both synchronous and asynchronous usage of the library.
"""

# this_file: src/twat_search/web/engines/lib_falla/main.py

import argparse
import asyncio
import logging
import sys

from twat_search.web.engines.lib_falla.utils import get_results, get_results_async, list_engines

__version__ = "0.2.0"


async def async_main(args: argparse.Namespace) -> None:
    """
    Run the Falla search engine scraper asynchronously.

    Args:
        args: Command line arguments
    """
    try:
        results = await get_results_async(args.engine, args.query, args.num)

        # Format results
        if args.json:
            pass
        else:
            for _i, _result in enumerate(results, 1):
                pass
    except Exception as e:
        logging.error(f"Error: {e}")
        sys.exit(1)


def main() -> None:
    """Run the Falla search engine scraper from the command line."""
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description="Falla - A multi-search engine scraper",
        epilog="Example: python main.py -e Google -q 'python programming'",
    )
    parser.add_argument("-e", "--engine", help="Search engine to use", required=False)
    parser.add_argument("-q", "--query", help="Search query", required=False)
    parser.add_argument("-n", "--num", help="Number of results to return", type=int, default=10)
    parser.add_argument("-l", "--list", help="List available engines", action="store_true")
    parser.add_argument("-v", "--version", help="Show version", action="store_true")
    parser.add_argument("-j", "--json", help="Output results as JSON", action="store_true")
    parser.add_argument("--async", dest="use_async", help="Use async version", action="store_true")

    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Show version
    if args.version:
        return

    # List available engines
    if args.list:
        for _engine in list_engines():
            pass
        return

    # Validate required args for search
    if not args.engine or not args.query:
        parser.print_help()
        return

    # Run search
    try:
        if args.use_async:
            # Use async version
            asyncio.run(async_main(args))
        else:
            # Use synchronous version
            results = get_results(args.engine, args.query, args.num)

            # Format results
            if args.json:
                pass
            else:
                for _i, _result in enumerate(results, 1):
                    pass
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logging.error(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
