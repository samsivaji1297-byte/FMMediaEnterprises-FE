#!/usr/bin/env python3
"""
publish_draft.py

Reads today's Markdown post from posts/YYYY-MM-DD.md and pushes it to
Substack as an unpublished draft using cookie-based authentication.

This script does NOT publish anything automatically — it only creates a
draft. Publishing is done manually in the Substack app, by design.

Required environment variables (set as GitHub Actions secrets):
    SUBSTACK_SID           -> value of the `substack.sid` cookie
    SUBSTACK_LLI            -> value of the `substack.lli` cookie
    SUBSTACK_PUBLICATION_URL -> e.g. https://yourpub.substack.com
"""

import os
import sys
from datetime import date
from pathlib import Path

from substack import Api

POSTS_DIR = Path(__file__).parent / "posts"


def build_cookie_string() -> str:
    """
    Assembles the raw Cookie header string python-substack expects.
    Format: "name=value; name=value"
    """
    sid = os.environ.get("SUBSTACK_SID")
    lli = os.environ.get("SUBSTACK_LLI")

    if not sid:
        print("ERROR: SUBSTACK_SID environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    parts = [f"substack.sid={sid}"]
    if lli:
        parts.append(f"substack.lli={lli}")

    return "; ".join(parts)


def find_todays_post() -> Path | None:
    """
    Looks for posts/YYYY-MM-DD.md matching today's date.
    Returns None if nothing is queued for today.
    """
    today_str = date.today().isoformat()  # e.g. "2026-08-26"
    candidate = POSTS_DIR / f"{today_str}.md"

    if candidate.exists():
        return candidate
    return None


def parse_frontmatter(md_text: str) -> tuple[dict, str]:
    """
    Very small frontmatter parser. Expects an optional block at the top:

        ---
        title: My Post Title
        subtitle: An optional subtitle
        tags: tag-one, tag-two
        ---

        Rest of the markdown body...

    Returns (metadata_dict, body_markdown).
    """
    metadata = {}
    body = md_text

    if md_text.startswith("---"):
        parts = md_text.split("---", 2)
        if len(parts) >= 3:
            frontmatter_block = parts[1].strip()
            body = parts[2].strip()
            for line in frontmatter_block.splitlines():
                if ":" in line:
                    key, _, value = line.partition(":")
                    metadata[key.strip().lower()] = value.strip()

    return metadata, body


def main() -> None:
    publication_url = os.environ.get("SUBSTACK_PUBLICATION_URL")
    if not publication_url:
        print("ERROR: SUBSTACK_PUBLICATION_URL environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    post_path = find_todays_post()
    if post_path is None:
        print(f"No post found for today ({date.today().isoformat()}) in posts/. Nothing to do.")
        return

    print(f"Found today's post: {post_path.name}")

    raw_text = post_path.read_text(encoding="utf-8")
    metadata, body_markdown = parse_frontmatter(raw_text)

    title = metadata.get("title", post_path.stem)
    subtitle = metadata.get("subtitle", "")
    tags = [t.strip() for t in metadata.get("tags", "").split(",") if t.strip()]

    cookie_string = build_cookie_string()

    api = Api(
        cookies=cookie_string,
        publication_url=publication_url,
    )

    print(f"Creating draft: '{title}'...")

    result = api.create_draft_from_markdown(
        title=title,
        subtitle=subtitle,
        markdown=body_markdown,
        tags=tags if tags else None,
    )

    draft_id = result.get("draft", {}).get("id") or result.get("id")
    print(f"Draft created successfully. Draft ID: {draft_id}")
    print("Review and publish manually in the Substack app.")


if __name__ == "__main__":
    main()
