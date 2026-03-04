#!/usr/bin/env python3
"""
Book Character Network Generator
=================================
Extracts characters from a book (TXT, EPUB, PDF) using the Claude API
and generates an interactive D3.js HTML visualization of their relationships.

Usage:
    python book_character_network.py <book_file> [--api-key YOUR_KEY] [--output output.html]

Requirements:
    pip install anthropic pdfminer.six
"""

import argparse
import textwrap

from book_analyzer import CharacterNetworkApp


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate an interactive D3.js character network from a book file.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""
        Examples:
          python book_character_network.py my_book.epub
          python book_character_network.py novel.pdf --output network.html
          python book_character_network.py story.txt --api-key sk-ant-...

        API key can also be set via the ANTHROPIC_API_KEY environment variable.
        """),
    )
    parser.add_argument("book", help="Path to book file (.txt, .epub, .pdf)")
    parser.add_argument("--api-key", help="Anthropic API key (or set ANTHROPIC_API_KEY env var)")
    parser.add_argument("--output", default="", help="Output HTML file path (default: <book_name>_network.html)")
    parser.add_argument(
        "--max-chars", type=int, default=80_000,
        help="Max characters to send to Claude (default: 80000)",
    )
    return parser.parse_args()


if __name__ == "__main__":
    CharacterNetworkApp(parse_args()).run()
