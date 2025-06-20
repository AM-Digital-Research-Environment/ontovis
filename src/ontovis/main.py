import logging
import xml.etree.ElementTree as ET
from collections import defaultdict
from dataclasses import dataclass
from pprint import pprint as pp
from typing import Self

import requests
import typer
from jinja2 import Environment, PackageLoader, select_autoescape

from ontovis.parser import parse

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

    tmpl = env.get_template(f"{template}.dot.jinja2")

    # groups: dict[str, Group] = {}
    groups: defaultdict[str, Group] = defaultdict(
        lambda: Group(name="NOT_SET", subgroups=[], path=[], fields=[])
    )

    paths = parse(root)
    pp(paths)
    n_disabled = len([p for p in paths if not p.enabled])

    for path in paths:
        if skip_disabled and not path.enabled:
            continue

        if path.is_group:
            # the defaultdict will create an empty group we can use
            group = groups[path.path_id]
            group.name = path.path_id
            group.path = path.path_array

            # a top-level group has no group-id, so we're done here
            if path.group_id == "0":
                continue

            # group has a parent: find it, and append this group to the subgrups
            groups[path.group_id].subgroups.append(group)
            groups[path.path_id] = group
            continue

        # the path is a field, so append it to the correct group
        groups[path.group_id].fields.append(
            Field(name=path.path_id, path=path.path_array)
        )

    if pprint:
        pp(groups)
        return typer.Exit()

    print(tmpl.render(groups=groups))
    return typer.Exit()


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
