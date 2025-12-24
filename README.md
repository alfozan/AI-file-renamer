# AI File Renamer

A single-file script that uses OpenAI's API to analyze file content and suggest descriptive filenames.

## Features

- Analyzes images, text files, PDFs, and Office documents
- Interactive confirmation before renaming
- Safe operations with duplicate checks
- Automatic image optimization to reduce API costs

## Quick Start

```bash
# 1. Install dependencies (requires uv: https://docs.astral.sh/uv/)
make setup

# 2. Set your API key in .env file
echo 'OPENAI_API_KEY=your-key-here' > .env

# 3. Run it
python main.py /path/to/file.pdf
```

## Usage

```bash
python main.py ~/Pictures/IMG_1234.jpg
# → Suggests: "golden_gate_bridge_sunset.jpg"

python main.py ~/Downloads/document.pdf
# → Suggests: "quarterly_sales_report_q4_2023.pdf"
```

**Configuration:** Create a `.env` file with:
```bash
OPENAI_API_KEY=your-key-here
OPENAI_MODEL=gpt-4o  # optional
```

## Development

```bash
make setup   # Install dependencies
make run     # Run script (pass file with --)
make lint    # Check code quality
make tidy    # Format code
make clean   # Clean environment
```

## Supported Files

**Images:** JPG, PNG, GIF, HEIC, WebP, TIFF  
**Text:** TXT, MD, code files, JSON, YAML, CSV  
**Documents:** PDF, Word, Excel, PowerPoint

**Limits:** Max 3MB file size. Images auto-resized to 1024px. Text truncated to 2000 chars.
