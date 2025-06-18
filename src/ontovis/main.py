from collections import defaultdict
import logging
import pathlib
import xml.etree.ElementTree as ET
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Annotated, Self

import requests
import typer
from jinja2 import Environment, PackageLoader, select_autoescape

logging.basicConfig(
    format="%(asctime)-15s %(name)-5s %(levelname)-8s %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("main")
app = typer.Typer()


@app.command()
def print_ontology(
    file: str,
    template: str = "graph",
    skip_disabled: bool = True,
    pprint: bool = False,
):
    if file.startswith("http") or file.startswith("https"):
        logger.info("fetching remote resource")
        response = requests.get(file)
        root = ET.fromstring(response.text)
    else:
        logger.info("loading local document")
        tree = ET.parse(file)
        root = tree.getroot()

    env = Environment(
        loader=PackageLoader("ontovis"),
        autoescape=select_autoescape(),
    )

    template = env.get_template(f"{template}.dot.jinja2")

    # groups: dict[str, Group] = {}
    groups: defaultdict[str, Group] = defaultdict(
        lambda: Group(name="NOT_SET", subgroups=[], path=[], fields=[])
    )

    n_disabled = 0
    for path in root:
        disabled = "0" == safe_get_text_by_xpath(path, "./enabled")
        if skip_disabled and disabled:
            disabled += 1
            continue

        path_id = safe_get_text_by_xpath(path, "./id")
        # true/false is 1/0
        is_group = "1" == safe_get_text_by_xpath(path, "./is_group")
        group_id = safe_get_text_by_xpath(path, "./group_id")

        path_array = path.find("path_array")
        assert path_array is not None

        path_array = [strip_prefix(particle.text) for particle in path_array]

        # remove the main URL part of the path particle
        path_array = [strip_prefix(particle) for particle in path_array]
        # TODO: move this quoting into the template
        path_array = [f'"{x}"' for x in path_array]

        if is_group:
            # the defaultdict will create an empty group we can use
            group = groups[path_id]
            group.name = path_id
            group.path = path_array

            # a top-level group has no group-id, so we're done here
            if group_id == "0":
                continue

            # group has a parent: find it, and append this group to the subgrups
            groups[group_id].subgroups.append(group)
            groups[path_id] = group
            continue

        # the path is a field, so append it to the correct group
        groups[group_id].fields.append(Field(name=path_id, path=path_array))

    if pprint:
        from pprint import pprint as pp

        pp(groups)
        return typer.Exit()

    print(template.render(groups=groups))
    return typer.Exit()


def safe_get_text_by_xpath(path: ET.Element, xpath: str) -> str:
    thing = path.find(xpath)
    assert thing is not None and thing.text is not None

    return thing.text


def strip_prefix(s: str | None) -> str:
    if s is None:
        return "<NO_ID>"

    return pathlib.Path(s).name


@dataclass
class Field:
    name: str
    path: list[str]


@dataclass
class Group:
    name: str
    subgroups: list[Self]
    path: list[str]
    fields: list[Field]
