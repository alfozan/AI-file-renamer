#!/usr/bin/env python

# Description: Rename a single file using the OpenAI Responses API based on its content.
# Example: python main.py ~/Documents/myfile.pdf

import base64
import mimetypes
import os
import re
import sys
from io import BytesIO
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image

# Load environment variables from .env file
load_dotenv()

# --------------- config ---------------
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEFAULT_REQUESTS_TIMEOUT_SEC = 30
MAX_FILE_BYTES = 3 * 1024 * 1024  # 3MB
# --------------- config ---------------

if not OPENAI_API_KEY:
    print("Error: OPENAI_API_KEY environment variable not set", file=sys.stderr)
    print("Please set it in a .env file or with: export OPENAI_API_KEY='your-api-key'", file=sys.stderr)
    sys.exit(1)

client = OpenAI(api_key=OPENAI_API_KEY)


def image_base64_encode(file_path: str) -> str:
    # Open the image
    image = Image.open(file_path)

    # Get original dimensions
    original_width, original_height = image.size

    # Resize image to reduce file size while maintaining aspect ratio
    # Max dimension of 1024 pixels should keep quality good while reducing size
    max_dimension = 1024
    if original_width > max_dimension or original_height > max_dimension:
        if original_width > original_height:
            new_width = max_dimension
            new_height = int((original_height * max_dimension) / original_width)
        else:
            new_height = max_dimension
            new_width = int((original_width * max_dimension) / original_height)

        image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        print(f"Original image size: {original_width}x{original_height}, resized to: {new_width}x{new_height}")

    # Handle image format and mode
    img_format = "JPEG"
    if image.mode == "RGBA":
        img_format = "PNG"
    elif image.mode != "RGB":
        image = image.convert("RGB")

    # Convert image to base64 with quality optimization for JPEG
    buffered = BytesIO()
    if img_format == "JPEG":
        image.save(buffered, format=img_format, quality=85, optimize=True)
    else:
        image.save(buffered, format=img_format, optimize=True)

    img_str = base64.b64encode(buffered.getvalue())

    return img_str.decode("utf-8")


def read_text_file(file_path: str) -> str:
    """Read text content from various text file types."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
            # Limit content to avoid token limits (first 2000 characters)
            return content[:2000] if len(content) > 2000 else content
    except UnicodeDecodeError:
        # Try with different encoding
        try:
            with open(file_path, "r", encoding="latin1") as file:
                content = file.read()
                return content[:2000] if len(content) > 2000 else content
        except Exception:
            return "[Could not read file content - encoding issue]"
    except Exception as e:
        return f"[Error reading file: {str(e)}]"


def get_file_category(
    file_path: str, mime: str
) -> Literal["image", "text", "pdf", "document", "spreadsheet", "presentation", "binary"]:
    """Determine the type of file based on extension and MIME type."""
    extension = Path(file_path).suffix.lower()

    if extension in IMAGE_EXTENSIONS or (mime.startswith("image/")):
        return "image"
    if extension in TEXT_EXTENSIONS or mime.startswith(("text/", "application/json")):
        return "text"
    if extension in PDF_EXTENSIONS or mime == "application/pdf":
        return "pdf"
    if extension in DOCUMENT_EXTENSIONS:
        return "document"
    if extension in SPREADSHEET_EXTENSIONS:
        return "spreadsheet"
    if extension in PRESENTATION_EXTENSIONS:
        return "presentation"

    return "binary"


def suggest_filename(file_path: str, current_filename: str, mime: str, category: str) -> str:
    """Suggest a filename based on file content analysis."""
    if category == "image":
        return suggest_image_filename(file_path, current_filename)
    if category == "text":
        return suggest_text_filename(file_path, current_filename)

    # Everything else goes through the generic file pipeline (pdfs included)
    return suggest_generic_filename(file_path, current_filename, mime, category)


def suggest_image_filename(file_path: str, current_filename: str) -> str:
    # Prepare a resized/optimized preview via base64 for the model
    b64_encoded_img = image_base64_encode(file_path)
    file_extension = Path(current_filename).suffix

    prompt = (
        "Suggest a concise, descriptive base filename for this image. "
        "Return only the base filename (no extension). "
        "Limit to 100 characters. "
    )

    payload = [
        {
            "role": "user",
            "content": [
                {"type": "input_text", "text": prompt},
                {"type": "input_image", "image_url": f"data:image/jpeg;base64,{b64_encoded_img}"},
                {
                    "type": "input_text",
                    "text": f"Current extension: {file_extension or '[none]'}",
                },
            ],
        }
    ]

    response = client.responses.create(
        model=OPENAI_MODEL,
        input=payload,  # type: ignore[arg-type]
        max_output_tokens=200,
        top_p=1,
        timeout=DEFAULT_REQUESTS_TIMEOUT_SEC,
    )
    content = getattr(response, "output_text", None)
    if not content or not content.strip():
        print(f"[debug] empty model output for image. Raw response: {response}")
        raise RuntimeError("Model returned no filename")
    base_name = content.strip()
    return ensure_extension(base_name, file_extension)


def suggest_text_filename(file_path: str, current_filename: str) -> str:
    file_content = read_text_file(file_path)
    file_extension = Path(current_filename).suffix

    prompt = (
        "Analyze the provided text content and propose a concise, descriptive base filename. "
        "Return only the base filename (no extension). Limit to 100 characters. "
    )

    payload = [
        {
            "role": "user",
            "content": [
                {"type": "input_text", "text": prompt},
                {
                    "type": "input_text",
                    "text": (
                        f"Current extension: {file_extension or '[none]'}\n"
                        f"File content preview (truncated to 2000 chars):\n{file_content}"
                    ),
                },
            ],
        }
    ]

    response = client.responses.create(
        model=OPENAI_MODEL,
        input=payload,  # type: ignore[arg-type]
        max_output_tokens=200,
        top_p=1,
        timeout=DEFAULT_REQUESTS_TIMEOUT_SEC,
    )
    content = getattr(response, "output_text", None)
    if not content or not content.strip():
        print(f"[debug] empty model output for text. Raw response: {response}")
        raise RuntimeError("Model returned no filename")
    base_name = content.strip()
    return ensure_extension(base_name, file_extension)


def suggest_generic_filename(file_path: str, current_filename: str, mime: str, category: str) -> str:
    """Send any binary file (including PDFs/Office/media) via input_file."""
    file_extension = Path(current_filename).suffix

    with open(file_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")

    prompt = (
        "Suggest a concise, descriptive base filename for the uploaded file. "
        "Return only the base filename (no extension). "
        "Prefer human-friendly, specific names. "
        "Limit to 100 characters. "
    )

    payload = [
        {
            "role": "user",
            "content": [
                {
                    "type": "input_file",
                    "filename": Path(current_filename).name or "file",
                    "file_data": f"data:{mime};base64,{b64}",
                },
                {
                    "type": "input_text",
                    "text": (
                        f"{prompt}\n"
                        f"Current extension: {file_extension or '[none]'}\n"
                        f"Detected category: {category}\n"
                        f"MIME type: {mime}"
                    ),
                },
            ],
        }
    ]

    response = client.responses.create(
        model=OPENAI_MODEL,
        input=payload,  # type: ignore[arg-type]
        max_output_tokens=200,
        top_p=1,
        timeout=DEFAULT_REQUESTS_TIMEOUT_SEC,
    )
    content = getattr(response, "output_text", None)
    if not content or not content.strip():
        print(f"[debug] empty model output for generic file. Raw response: {response}")
        raise RuntimeError("Model returned no filename")
    base_name = content.strip()
    return ensure_extension(base_name, file_extension)


# --------------- main ---------------


# Supported file extensions (we'll still attempt unknown types via generic flow)
IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp", ".heic"]
TEXT_EXTENSIONS = [
    ".txt",
    ".md",
    ".rst",
    ".log",
    ".py",
    ".js",
    ".ts",
    ".html",
    ".css",
    ".json",
    ".xml",
    ".yml",
    ".yaml",
    ".csv",
    ".toml",
    ".ini",
    ".cfg",
    ".sql",
]
PDF_EXTENSIONS = [".pdf"]
DOCUMENT_EXTENSIONS = [".doc", ".docx", ".rtf", ".odt", ".pages"]
SPREADSHEET_EXTENSIONS = [".xls", ".xlsx", ".ods", ".numbers", ".csv"]
PRESENTATION_EXTENSIONS = [".ppt", ".pptx", ".odp", ".key"]


def get_user_confirmation(suggested_name: str) -> bool:
    """Ask user for confirmation to rename the file."""
    # Auto-accept when running non-interactively (e.g., Automator)
    if not sys.stdin.isatty():
        return True

    print(f"Suggested filename: {suggested_name}")
    try:
        response = input("Press Enter to accept: ")
    except KeyboardInterrupt:
        return False
    return not response.strip()


def rename_single_file(file_path: str) -> bool:
    """Rename a single file based on its content analysis."""
    target = Path(file_path)
    if not target.is_file():
        print(f"Not a file: {file_path}", file=sys.stderr)
        return False

    if target.stat().st_size > MAX_FILE_BYTES:
        print(f"File too large: {target.name} (max {MAX_FILE_BYTES // (1024 * 1024)}MB)", file=sys.stderr)
        return False

    file_name = target.name
    folder_path = str(target.parent)

    mime = mimetypes.guess_type(str(target))[0] or "application/octet-stream"
    category = get_file_category(file_path, mime)

    try:
        # print(f"Analyzing {file_name}...")
        new_filename = suggest_filename(file_path, file_name, mime=mime, category=category)

        # Ensure the new filename is different and valid
        if new_filename and new_filename != file_name:
            # Clean the filename to avoid filesystem issues
            new_filename = clean_filename(new_filename)
            new_file_path = os.path.join(folder_path, new_filename)

            # Check if target file already exists
            if os.path.exists(new_file_path):
                print(f"Error: Target file {new_filename} already exists")
                return False

            # Ask for user confirmation
            if get_user_confirmation(new_filename):
                os.rename(file_path, new_file_path)
                print(f"✓ Successfully renamed to: {new_filename}")
                return True
            else:
                return True
        else:
            print(f"AI suggests keeping original filename: {file_name}")
            return True
    except Exception as e:
        print(f"Error processing {file_name}: {e}", file=sys.stderr)
        return False


def clean_filename(filename: str) -> str:
    """Clean filename to ensure it's filesystem-safe."""
    # Split name and extension
    name, ext = os.path.splitext(filename)

    # Remove forbidden characters, allow spaces (collapse multiple to single)
    name = re.sub(r'[<>:"/\\|?*]', "", name)
    name = " ".join(name.split())

    # Ensure we don't end with a dot or space
    name = name.rstrip(". ")

    return f"{name}{ext}" if name else f"renamed_file{ext}"


def ensure_extension(base_name: str, ext: str) -> str:
    """Append ext if base_name does not already end with it (case-insensitive)."""
    bn = base_name.strip()
    if not bn:
        return f"renamed_file{ext}"
    if ext and not bn.lower().endswith(ext.lower()):
        return f"{bn}{ext}"
    return bn


if __name__ == "__main__":
    # get path from arguments
    if len(sys.argv) > 1 and sys.argv[1]:
        TARGET_PATH = sys.argv[1]
    else:
        print("Usage:")
        print("  python rename_file.py /path/to/your/file.ext")
        sys.exit(1)

    print(f"Processing: {TARGET_PATH}")
    if not rename_single_file(file_path=TARGET_PATH):
        sys.exit(1)
