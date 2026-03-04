"""
network.analyzer
================
Calls the Claude API to extract characters and relationships from
a book text sample, returning structured JSON data.
"""

import json
import re


class ClaudeAnalyzer:
    """Calls the Claude API to extract characters and relationships from text."""

    MODEL      = "claude-opus-4-6"
    MAX_TOKENS = 4096

    SYSTEM_PROMPT = """\
You are a literary analyst specializing in character mapping.
You must determine language used in book and produce output in the same language.
Your task is to analyze a book excerpt and return structured JSON data about its characters and their relationships.
Return ONLY valid JSON, no markdown fences, no preamble."""

    USER_PROMPT_TEMPLATE = """\
Analyze the following book text and extract:
1. All significant characters (main + important supporting, 8–20 total)
2. One-paragraph description of each character
3. All meaningful relationships between characters

Return ONLY this JSON structure (no markdown, no extra text):

{{
  "book_title": "Title of the book",
  "author": "Author name",
  "book_summary": "4-6 sentence plot summary of the book",
  "characters": [
    {{
      "id": "unique_snake_case_id",
      "name": "Character Name",
      "group": "one of: protagonist | antagonist | family | ally | rival | other",
      "size": 12,
      "description": "One full paragraph describing this character's personality, role, and importance."
    }}
  ],
  "relationships": [
    {{
      "source": "character_id",
      "target": "character_id",
      "type": "one of: love | family | friendship | conflict | rivalry | professional | other",
      "label": "Short label describing the relationship (e.g. 'Husband and wife', 'Bitter enemies')"
    }}
  ]
}}

Rules:
- `size` should be 26-30 for protagonists, 18-22 for major characters, 12-16 for minor ones
- Every character must appear in at least one relationship
- Relationships should be bidirectional (don't duplicate — list each pair once)
- `id` must be lowercase letters/underscores only, no spaces
- Groups: protagonist (main character), antagonist (villain/opposing force), family (relatives), ally (friends/supporters), rival (competitors/enemies), other

Book text:
---
{book_text}
---"""

    def __init__(self, api_key: str):
        self.api_key = api_key

    def analyze(self, text_sample: str) -> dict:
        try:
            import anthropic
        except ImportError:
            raise ImportError(
                "anthropic package required. Install with: pip install anthropic"
            )

        client = anthropic.Anthropic(api_key=self.api_key)

        print("  Sending to Claude API…")
        message = client.messages.create(
            model=self.MODEL,
            max_tokens=self.MAX_TOKENS,
            system=self.SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": self.USER_PROMPT_TEMPLATE.format(book_text=text_sample),
                }
            ],
        )

        raw = message.content[0].text.strip()

        # Strip any accidental markdown fences
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)

        try:
            return json.loads(raw)
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Claude returned invalid JSON: {e}\n\nRaw response:\n{raw[:500]}"
            )
