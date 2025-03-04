from pathlib import Path


def get_path() -> Path:
    parent = Path(__file__).parent
    return (parent / "bin" / "changelog").resolve()
