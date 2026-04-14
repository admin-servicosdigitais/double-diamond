from dataclasses import dataclass


@dataclass
class BaseAgent:
    name: str

    def run(self) -> None:
        raise NotImplementedError
