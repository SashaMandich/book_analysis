"""
network.app
===========
Orchestrates the full pipeline: extract → sample → analyse → render → write.
"""

import os
import sys

from .extractor import TextExtractor
from .sampler import TextSampler
from .analyzer import ClaudeAnalyzer
from .config import NetworkConfig
from .html_builder import HTMLBuilder


class CharacterNetworkApp:
    """Wires all components together and runs the end-to-end pipeline."""

    def __init__(self, args):
        self.args        = args
        self.api_key     = args.api_key or os.environ.get("ANTHROPIC_API_KEY", "")
        self.output_path = self._resolve_output_path()
        self.extractor   = TextExtractor()
        self.sampler     = TextSampler(max_chars=args.max_chars)
        self.analyzer    = ClaudeAnalyzer(api_key=self.api_key)
        self.builder     = HTMLBuilder(config=NetworkConfig())

    def _resolve_output_path(self) -> str:
        if self.args.output:
            return self.args.output
        base = os.path.splitext(os.path.basename(self.args.book))[0]
        return f"{base}_network.html"

    def _validate_api_key(self) -> None:
        if not self.api_key:
            print("ERROR: No API key provided.")
            print("  Pass --api-key YOUR_KEY  or  set ANTHROPIC_API_KEY environment variable.")
            sys.exit(1)

    def run(self) -> None:
        self._validate_api_key()

        print(f"\n📚  Book Character Network Generator")
        print(f"{'─' * 40}")
        print(f"  Input : {self.args.book}")
        print(f"  Output: {self.output_path}\n")

        # Step 1: Extract text
        try:
            full_text = self.extractor.extract(self.args.book)
            print(f"  Extracted {len(full_text):,} characters of text.")
        except Exception as e:
            print(f"ERROR extracting text: {e}")
            sys.exit(1)

        # Step 2: Sample
        sample = self.sampler.sample(full_text)
        print(f"  Using {len(sample):,} characters as input to Claude.")

        # Step 3: Analyse with Claude
        try:
            data = self.analyzer.analyze(sample)
        except Exception as e:
            print(f"ERROR calling Claude API: {e}")
            sys.exit(1)

        n_chars = len(data.get("characters", []))
        n_rels  = len(data.get("relationships", []))
        print(f"  Extracted {n_chars} characters, {n_rels} relationships.")
        print(f"  Book: {data.get('book_title', '?')} by {data.get('author', '?')}")

        # Step 4: Build HTML
        html = self.builder.build(data)

        # Step 5: Write output
        with open(self.output_path, "w", encoding="utf-8") as f:
            f.write(html)

        print(f"\n✅  Done! Open in your browser:")
        print(f"   {os.path.abspath(self.output_path)}\n")
