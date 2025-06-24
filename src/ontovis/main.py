# pyright: strict
import logging
from pprint import pprint as pp

import typer
from jinja2 import Environment, PackageLoader, select_autoescape

from ontovis.lib.builder import build_groups
from ontovis.lib.parser import parse_pathbuilder
from ontovis.lib.reader import read_document

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
    root = read_document(file)

    env = Environment(
        loader=PackageLoader("ontovis"),
        autoescape=select_autoescape(),
    )

    tmpl = env.get_template(f"{template}.dot.jinja2")

    paths = parse_pathbuilder(root)
    if paths == []:
        logger.info("pathbuilder document was empty. quitting")
        return typer.Exit()

    # try:
    groups = build_groups(paths, skip_disabled)
    # except Exception as e:
    #     logger.error(f"Encountered exception: {e}")
    #     return typer.Exit(1)

    if pprint:
        pp(groups)
        return typer.Exit()

    print(tmpl.render(groups=groups))

    return typer.Exit()
