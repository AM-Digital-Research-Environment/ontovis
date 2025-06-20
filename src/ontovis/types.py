from dataclasses import dataclass


@dataclass
class Path:
    enabled: bool
    path_id: str
    is_group: bool
    group_id: str | None
    path_array: list[str]
