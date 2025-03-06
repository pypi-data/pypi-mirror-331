from pathlib import Path


def mkdir_p(path: Path):
    path.mkdir(parents=True, exist_ok=True)
