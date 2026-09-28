from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from prism.export import export_archive

if __name__ == "__main__":
    payload = export_archive(
        ROOT / "corpus",
        [ROOT / "data" / "archive.json", ROOT / "dashboard" / "archive.json"],
    )
    print(f"Exported {len(payload['documents'])} documents and {len(payload['chunks'])} chunks.")
