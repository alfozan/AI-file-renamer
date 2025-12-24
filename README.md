# AI File Renamer

AI-powered file renaming tool with a macOS Finder Quick Action (Automator) for one-click use.

## Quick Action in MacOS Finder

Right-click any file in Finder and use the Quick Action to rename it:

<img width="443" alt="Quick Action in Finder context menu" src="https://github.com/user-attachments/assets/0e553cdf-e11f-480f-abca-b2bf2c45e49d">

**→ [See setup instructions below](#macos-automator-quick-action)**

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
uv run python main.py /path/to/file.pdf
```

## Usage

```bash
uv run python main.py ~/Pictures/IMG_1234.jpg
# → Suggests: "golden_gate_bridge_sunset.jpg"

uv run python main.py ~/Downloads/document.pdf
# → Suggests: "quarterly_sales_report_q4_2023.pdf"
```

**Configuration:** Create a `.env` file with:
```bash
OPENAI_API_KEY=your-key-here
OPENAI_MODEL=gpt-4o  # or gpt-5.2
```

## Development

```bash
make setup              # Install dependencies
make lint               # Check code quality
make tidy               # Format code
make clean              # Clean environment
```

## Supported Files

**Images:** JPG, PNG, GIF, HEIC, WebP, TIFF  
**Text:** TXT, MD, code files, JSON, YAML, CSV  
**Documents:** PDF, Word, Excel, PowerPoint

**Limits:** Max 3MB file size. Images auto-resized to 1024px. Text truncated to 2000 chars.

## macOS Automator (Quick Action)

Easy setup with Automator:

<img width="1009" alt="Automator workflow setup" src="https://github.com/user-attachments/assets/ce230abd-fdc5-4bc5-984f-c5343d2d9e54">

Create a Finder Quick Action to process selected files:
1) Open Automator → new “Quick Action”.
2) Workflow receives current: `files or folders` in `Finder.app`. Pass input: `as arguments`.
3) Add “Run Shell Script”, Shell: `/bin/bash`. Use this script:
   ```bash
   PROJECT="$HOME/AI-file-renamer"
   SCRIPT="$PROJECT/main.py"

   for f in "$@"; do
     /opt/homebrew/bin/uv run --project "$PROJECT" "$SCRIPT" "$f"
   done
   ```
4) Save as “AI File Renamer”.
