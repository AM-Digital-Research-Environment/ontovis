from collections.abc import Iterable

from ontovis.lib.types import Group, Path

def build_groups(
    paths: Iterable[Path], skip_disabled: bool = ...
) -> dict[str, Group]: ...
