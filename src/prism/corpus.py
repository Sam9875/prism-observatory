from __future__ import annotations

from pathlib import Path

from prism.types import SourceDoc


def _parse_frontmatter(raw: str) -> tuple[dict[str, str], str]:
    if not raw.startswith("---"):
        raise ValueError("Corpus file is missing frontmatter")
    end = raw.find("\n---", 3)
    if end < 0:
        raise ValueError("Corpus frontmatter is not closed")
    header = raw[3:end].strip()
    body = raw[end + 4 :].strip()
    meta: dict[str, str] = {}
    for line in header.splitlines():
        if not line.strip() or ":" not in line:
            continue
        key, value = line.split(":", 1)
        meta[key.strip()] = value.strip()
    return meta, body


def load_corpus(root: Path) -> list[SourceDoc]:
    folder = Path(root)
    if not folder.is_dir():
        raise ValueError(f"Corpus directory does not exist: {folder}")
    docs: list[SourceDoc] = []
    for path in sorted(folder.glob("*.md")):
        meta, body = _parse_frontmatter(path.read_text(encoding="utf-8"))
        entities = [part.strip() for part in meta.get("entities", "").split(";") if part.strip()]
        docs.append(
            SourceDoc(
                id=meta.get("id") or path.stem,
                title=meta.get("title") or path.stem,
                archive=meta.get("archive") or "orbital",
                summary=meta.get("summary") or "",
                entities=entities,
                text=body,
                path=str(path),
            )
        )
    if not docs:
        raise ValueError(f"No markdown documents in {folder}")
    return docs
