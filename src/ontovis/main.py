# pyright: strict
from enum import Enum
from typing import Annotated

import typer
from jinja2 import Environment, PackageLoader, select_autoescape
from rich import print as rprint

from .io.read import read_local_or_remote
from .parser import build_groups, parse_pathbuilder

app = typer.Typer(no_args_is_help=True, rich_markup_mode="markdown")


class TemplateChoice(str, Enum):
    no_groups = "no_groups"
    no_fields = "no_fields"
    full = "full"


@app.command(no_args_is_help=True)
def render(
    input: str,
    template: Annotated[
        TemplateChoice, typer.Option(case_sensitive=False)
    ] = TemplateChoice.no_groups,
    template_custom: Annotated[pathlib.Path | None, typer.Option()] = None,
    skip_disabled: Annotated[
        bool, typer.Option("--skip-disabled/--include-disabled")
    ] = True,
    raw: Annotated[bool, typer.Option("--raw", "-r")] = False,
):
    """
    Render a graphical representation of a pathbuilder definition.

    Use `--template` to select a builtin template, or use `--template-custom` to
    pass your own template.


    The builtin templates are:

    * no_groups (default): render only the ontology-classes and omit grouping
      into fields and path-groups.

    * no_fields: group the ontology classes into path-groups, omit fields.

    * full: group classes into fields, and fields into path-groups. **Warning:**
      the resulting representation can become very dense.

    To pass a custom template using `--template-custom`, use
    [jinja2 markup](https://jinja.palletsprojects.com/en/stable/templates/)
    to author a template.

    Your template will have to work with the parser's intermediate
    representation; pass the `--raw` flag to see this.
    """
    root = read_local_or_remote(input)

    env = Environment(
        loader=PackageLoader("ontovis"),
        autoescape=select_autoescape(),
        trim_blocks=True,
        lstrip_blocks=True,
    )

    tmpl = env.get_template(f"{template.value}.dot.jinja2")

    paths = parse_pathbuilder(root)
    if paths == []:
        rprint("[red]Pathbuilder document was empty. [bold]Quitting[/bold][/red]")
        raise typer.Exit()

    groups = build_groups(paths, skip_disabled)

    if raw:
        rprint(groups)
        raise typer.Exit()

    print(tmpl.render(groups=groups))



@app.command()
def stats() -> typer.Exit:
    return typer.Exit()
@app.callback()
def callback():
    """
    Visualize and analyze WissKI pathbuilder definitions
    """
