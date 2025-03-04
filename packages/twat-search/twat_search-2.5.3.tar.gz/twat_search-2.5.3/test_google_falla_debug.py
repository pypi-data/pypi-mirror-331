#!/usr/bin/env python3
# this_file: test_google_falla_debug.py
"""
Debug test script for Google Falla engine.

This script runs a search using the Google Falla engine and prints debug information.
"""

import asyncio
import logging
import os
import sys
import tempfile
import traceback
from pathlib import Path

# Configure verbose logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s:%(funcName)s:%(lineno)d - %(message)s",
    handlers=[logging.StreamHandler()],
)

logger = logging.getLogger("google_falla_debug")

# Add the src directory to the Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

try:
    # Import the search function
    from twat_search.web.engines.lib_falla.core.google import Google
except ImportError as e:
    logger.error(f"Failed to import Google engine: {e}")
    logger.error("Make sure the path is correct and all dependencies are installed.")
    sys.exit(1)


async def main():
    """Run a test search with the Google Falla engine."""
    engine = None
    try:
        # Simple test query
        query = "Python programming language"

        # Initialize Google engine
        engine = Google()

        # Log configuration
        logger.info(f"Testing Google Falla engine with query: {query}")
        logger.info("Engine configuration:")
        logger.info(f"  - Name: {engine.name}")
        logger.info(f"  - Method: {engine.use_method}")
        logger.info(f"  - Container element: {engine.container_element}")
        logger.info(f"  - Wait for selector: {engine.wait_for_selector}")
        logger.info(f"  - Max retries: {engine.max_retries}")

        # Run the search asynchronously
        logger.info("\nRunning search...")
        results = await engine.search_async(query)

        # Print results
        logger.info(f"\nSearch completed. Found {len(results)} results.")

        for i, result in enumerate(results, 1):
            logger.info(f"\nResult {i}:")
            logger.info(f"  Title: {result.get('title', 'N/A')}")
            logger.info(f"  Link: {result.get('link', 'N/A')}")
            snippet = result.get("snippet", "N/A")
            if snippet:
                logger.info(f"  Snippet: {snippet[:100]}...")
            else:
                logger.info("  Snippet: N/A")

        # Check if debug HTML file was created
        temp_dir = tempfile.gettempdir()  # Use tempfile module for secure temp directory
        html_files = [f for f in os.listdir(temp_dir) if f.startswith("google_debug_") and f.endswith(".html")]

        if html_files:
            logger.info("\nDebug HTML files were saved:")
            for html_file in html_files:
                logger.info(f"  - {Path(temp_dir) / html_file}")
        else:
            logger.warning("No debug HTML files were found.")

    except Exception as e:
        logger.error(f"Error during search: {e}")
        logger.error(traceback.format_exc())
        return 1
    finally:
        # Ensure we always clean up resources
        if engine is not None:
            try:
                await engine.close()
                logger.info("Engine resources cleaned up.")
            except Exception as e:
                logger.error(f"Error during cleanup: {e}")

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
