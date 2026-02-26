import os
import random
import shutil
from pathlib import Path

# Toggle this: if True, used files get moved to archive folders
ARCHIVE_USED_FILES = False

# Base paths (adjust if your repo layout differs)
BASE_DIR = Path(__file__).resolve().parent.parent  # repo root (assuming scripts/ is one level down)
SHORT_FORM_DIR = BASE_DIR / "1_SHORT_FORM"
LONG_FORM_DIR = BASE_DIR / "2_LONG_FORM"
OUTPUT_TEXT_DIR = BASE_DIR / "input" / "text"
ARCHIVE_DIR = BASE_DIR / "archive"


def list_all_files(folder: Path):
    """Return a flat list of all files in a folder (non-recursive)."""
    return [f for f in folder.iterdir() if f.is_file()]


def pick_random_file(folder: Path):
    """Pick a random file from a folder. Raise if none exist."""
    files = list_all_files(folder)
    if not files:
        raise FileNotFoundError(f"No files found in {folder}")
    return random.choice(files)


def read_file(path: Path) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()


def ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)


def archive_file(src: Path, category: str):
    """
    Move a used file into archive/<category>/ preserving filename.
    category examples: 'identity_triggers', 'reel_scripts', 'captions'
    """
    dest_dir = ARCHIVE_DIR / category
    ensure_dir(dest_dir)
    dest = dest_dir / src.name
    shutil.move(str(src), str(dest))


def main():
    # Define source folders
    identity_triggers_dir = SHORT_FORM_DIR / "identity_triggers"
    reel_scripts_dir = SHORT_FORM_DIR / "reel_scripts"
    captions_dir = LONG_FORM_DIR / "captions"

    # Pick random files
    identity_file = pick_random_file(identity_triggers_dir)
    reel_script_file = pick_random_file(reel_scripts_dir)
    caption_file = pick_random_file(captions_dir)

    # Read contents
    identity_text = read_file(identity_file)
    reel_script_text = read_file(reel_script_file)
    caption_text = read_file(caption_file)

    # Assemble final script
    final_script = f"{identity_text}\n\n{reel_script_text}\n\n{caption_text}\n"

    # Ensure output dir exists
    ensure_dir(OUTPUT_TEXT_DIR)

    # Write to input/text/test.txt
    output_path = OUTPUT_TEXT_DIR / "test.txt"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(final_script)

    print("=== Reel Input Built ===")
    print(f"Identity trigger file: {identity_file}")
    print(f"Reel script file:      {reel_script_file}")
    print(f"Caption file:          {caption_file}")
    print(f"Output written to:     {output_path}")

    # Optionally archive used files
    if ARCHIVE_USED_FILES:
        archive_file(identity_file, "identity_triggers")
        archive_file(reel_script_file, "reel_scripts")
        archive_file(caption_file, "captions")
        print("Used files archived.")


if __name__ == "__main__":
    main()
