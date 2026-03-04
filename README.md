# Book Character Network

Extracts characters and relationships from a book (`.txt`, `.epub`, `.pdf`) using the Claude API and generates a self-contained, interactive D3.js HTML visualization.

## Project Structure

```
book_analysis/
├── main.py                  # CLI entry point
├── requirements.txt
├── .gitignore
└── book_analyzer/
    ├── __init__.py
    ├── app.py               # Pipeline orchestrator
    ├── extractor.py         # Text extraction (TXT / EPUB / PDF)
    ├── sampler.py           # Smart text truncation
    ├── analyzer.py          # Claude API call & prompt
    ├── config.py            # Visual style constants (colors, labels)
    └── html_builder.py      # D3.js HTML renderer
```

## Setup

```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
# Basic (API key from environment variable)
export ANTHROPIC_API_KEY=sk-ant-...
python main.py my_book.epub

# With explicit API key and custom output path
python main.py novel.pdf --api-key sk-ant-... --output network.html

# Limit how much text is sent to Claude (default: 80 000 chars)
python main.py story.txt --max-chars 60000
```

The output is a single `.html` file — open it in any browser.

## Requirements

| Package | Purpose |
|---|---|
| `anthropic` | Claude API client |
| `pdfminer.six` | PDF text extraction |

EPUB and TXT support uses only Python's standard library.

## Configuration

To tweak colors, group labels, or link dash patterns, edit [`book_analyzer/config.py`](book_analyzer/config.py) — no other files need to change.
