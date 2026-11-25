import re
from pathlib import Path
from solana_ai import config
from solana_ai.registry import Risk, registry

SENSITIVE_NAMES = {".env", "id_rsa", "id_ed25519", "known_hosts","credentials.json", "token.json"}
SENSITIVE_PARTS = {".ssh", ".gnupg", ".aws"}

def _resolve_allowed(path: str) -> Path:
    p = Path(path).expanduser().resolve()
    if not any(p.is_relative_to(root) for root in config.allowed_roots()):
        raise PermissionError("That path is outside the folders Solana may read.")
    parts = {part.lower() for part in p.parts}
    if p.name.lower() in SENSITIVE_NAMES or SENSITIVE_PARTS & parts:
        raise PermissionError("That file may contain secrets and is off limits.")
    return p

@registry.register(risk=Risk.AUTO, untrusted_output=True)
def read_file(path: str, max_chars: int = 4000) -> str:
    """Read a text file from the user's allowed folders and return its text. path is the full file path."""
    p = _resolve_allowed(path)
    if not p.is_file():
        return f"Not a file: {path}"
    return p.read_text(encoding="utf-8", errors="replace")[:max_chars]

@registry.register(risk=Risk.AUTO, untrusted_output=True)
def list_dir(path: str) -> str:
    """List the files and folders inside a directory in the user's allowed folders."""
    p = _resolve_allowed(path)
    if not p.is_dir():
        return f"Not a directory: {path}"
    names = sorted(child.name + ("/" if child.is_dir() else "") for child in p.iterdir())
    return "\n".join(names[:200]) or "(empty)"

@registry.register(risk=Risk.CONFIRM)
def save_note(title: str, content: str) -> str:
    """Save a short text note as a file in the user's SolanaNotes folder."""
    folder = config.notes_dir()
    folder.mkdir(parents=True, exist_ok=True)
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-") or "note"
    target = folder / f"{slug}.txt"
    target.write_text(content, encoding="utf-8")
    return f"Saved note to {target}"