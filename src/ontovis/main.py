# pyright: strict
import typer
from jinja2 import Environment, PackageLoader, select_autoescape
from rich import print as rprint

from ontovis.io import read_local_or_remote
from ontovis.parser import build_groups, parse_pathbuilder

app = typer.Typer(no_args_is_help=True)


@app.command()
def render(
    file: str,
    template: str = "graph",
    skip_disabled: bool = True,
    pprint: bool = False,
) -> typer.Exit:
    root = read_local_or_remote(file)

    env = Environment(
        loader=PackageLoader("ontovis"),
        autoescape=select_autoescape(),
    )

    tmpl = env.get_template(f"{template}.dot.jinja2")

    paths = parse_pathbuilder(root)
    if paths == []:
        rprint("[red]Pathbuilder document was empty. [bold]Quitting[/bold][/red]")
        return typer.Exit()

    groups = build_groups(paths, skip_disabled)

    if pprint:
        from pprint import pprint as pp

        pp(groups)
        return typer.Exit()

    print(tmpl.render(groups=groups))

    return typer.Exit()


@app.command()
def stats() -> typer.Exit:
    return typer.Exit()
