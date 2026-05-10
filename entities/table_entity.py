from dataclasses import dataclass


@dataclass
class TableEntity:
    name: str
    id: int | None = None
