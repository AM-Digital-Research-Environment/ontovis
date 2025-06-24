import pathlib
from xml.etree.ElementTree import Element
from ontovis.types import Path


def strip_prefix(s: str | None) -> str:
    if s is None:
        return "<NO_ID>"

    return pathlib.Path(s).name


def safe_get_text(path: Element, xpath: str) -> str:
    thing = path.find(xpath)
    assert thing is not None and thing.text is not None

    return thing.text


def safe_get_bool(path: Element, xpath: str) -> bool:
    thing = path.find(xpath)
    assert thing is not None and thing.text is not None

    return thing.text == "1"


def get_path_array(path: Element) -> list[str]:
    path_array = path.find("./path_array")
    assert path_array is not None
    path_array = [strip_prefix(particle.text) for particle in path_array]

    # remove the main URL part of the path particle
    path_array = [strip_prefix(particle) for particle in path_array]
    # TODO: move this quoting into the template
    path_array = [f'"{x}"' for x in path_array]

    return path_array


def parse(document: Element) -> list[Path]:
    out: list[Path] = []
    paths = document.findall("path")
    if paths == []:
        return []

    for path in paths:
        enabled = safe_get_bool(path, "./enabled")
        path_id = safe_get_text(path, "./id")
        is_group = safe_get_bool(path, "./is_group")
        group_id = safe_get_text(path, "./group_id")
        if group_id == "0":
            group_id = None

        path_array = get_path_array(path)

        out.append(Path(enabled, path_id, is_group, group_id, path_array))

    return out
