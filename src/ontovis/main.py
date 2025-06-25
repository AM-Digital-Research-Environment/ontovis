# pyright: strict
import os
import pathlib
from enum import Enum
from typing import Annotated

import click
import typer
from jinja2 import Environment, FileSystemLoader, PackageLoader, select_autoescape
from rich import print as rprint
from rich.table import Table

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

    if template_custom is None:
        env = Environment(
            loader=PackageLoader("ontovis"),
            autoescape=select_autoescape(),
            trim_blocks=True,
            lstrip_blocks=True,
        )

        tmpl = env.get_template(f"{template.value}.dot.jinja2")
    else:
        # figure out the parent of the passed template
        env = Environment(
            loader=FileSystemLoader(template_custom.parent),
            autoescape=select_autoescape(),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        tmpl = env.get_template(template_custom.name)

    paths = parse_pathbuilder(root)
    if paths == []:
        rprint("[red]Pathbuilder document was empty. [bold]Quitting[/bold][/red]")
        raise typer.Exit()

    groups = build_groups(paths, skip_disabled)

    if raw:
        rprint(groups)
        raise typer.Exit()

    print(tmpl.render(groups=groups))


@app.command(no_args_is_help=True)
def stats(input: Annotated[pathlib.Path, typer.Argument(allow_dash=True)]):
    """
    Foo.
    """
    import networkx as nx
    import heapq

    top_n = 3

    with click.open_file(os.fsdecode(input)) as f:
        G: nx.Graph[str]
        G = nx.nx_agraph.read_dot(f)  # pyright: ignore[reportArgumentType]

    table = Table("metric", "value", "remark")
    table.add_row("#nodes", str(G.number_of_nodes()), "nodes == classes in ontology")
    table.add_row("#edges", str(G.number_of_edges()), "multigraph, with parallel edges")
    G_simple = nx.Graph(G)
    table.add_row(
        "#edges", str(G_simple.number_of_edges()), "simplified, no parallel edges"
    )
    table.add_row(
        "avg. clustering",
        f"{nx.average_clustering(G_simple):.4f}",
        (
            "ratio of triangles formed; 'a friend of a friend is also my friend'; "
            "typically low, as paths don't tend to go 'back up' the concept hierarchy"
        ),
    )
    indegree_centrality = nx.in_degree_centrality(G)
    l = heapq.nlargest(top_n, indegree_centrality.items(), key=lambda x: x[1])
    table.add_row(
        f"in-degree centrality",
        "\n".join([f"[bold]{x[0]}[/bold] ({x[1]:.3f})" for x in l]),
        "other classes point to these a lot",
    )
    outdegree_centrality = nx.out_degree_centrality(G)
    l = heapq.nlargest(top_n, outdegree_centrality.items(), key=lambda x: x[1])
    table.add_row(
        f"out-degree centrality",
        "\n".join([f"[bold]{x[0]}[/bold] ({x[1]:.3f})" for x in l]),
        "these point to many other classes",
    )
    betweenness = nx.betweenness_centrality(G)
    l = heapq.nlargest(top_n, betweenness.items(), key=lambda x: x[1])
    table.add_row(
        f"betweenness centrality",
        "\n".join([f"[bold]{x[0]}[/bold] ({x[1]:.3f})" for x in l]),
        "many paths between nodes pass through these",
    )
    closeness = nx.closeness_centrality(G)
    l = heapq.nlargest(top_n, closeness.items(), key=lambda x: x[1])
    table.add_row(
        f"closeness centrality",
        "\n".join([f"[bold]{x[0]}[/bold] ({x[1]:.3f})" for x in l]),
        "the more central a node is, the more nodes can be reached from it by shortest paths",
    )

    rprint(table)


@app.callback()
def callback():
    """
    Visualize and analyze WissKI pathbuilder definitions
    """
