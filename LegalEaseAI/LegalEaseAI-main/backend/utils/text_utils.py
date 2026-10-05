import html
import re
import unicodedata


def sanitize_text(text: str) -> str:
    """Normalize Unicode typography and remove unsafe control characters."""
    replacements = {
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2013": "-",
        "\u2014": "-",
        "\u00a0": " ",
        "\u2022": "-",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)

    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
    return text.strip()


def escape_html(text: str) -> str:
    return html.escape(sanitize_text(text))


def text_to_html(text: str) -> str:
    """Convert plain text to safe, readable HTML paragraphs/headings."""
    safe = escape_html(text)
    lines = safe.splitlines()
    blocks: list[str] = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if re.match(r"^\d+[\.)]\s+", stripped):
            blocks.append(f"<h3>{stripped}</h3>")
        elif len(stripped) < 100 and stripped.isupper():
            blocks.append(f"<h2>{stripped}</h2>")
        elif stripped.startswith("- "):
            blocks.append(f"<li>{stripped[2:]}</li>")
        else:
            blocks.append(f"<p>{stripped}</p>")

    return "\n".join(blocks)
