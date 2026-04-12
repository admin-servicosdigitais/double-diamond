from pathlib import Path


class ConfigLoader:
    def __init__(self, root_path: str | Path = ".") -> None:
        self.root_path = Path(root_path)

    def workflows_path(self) -> Path:
        return self.root_path / "data" / "workflows"
