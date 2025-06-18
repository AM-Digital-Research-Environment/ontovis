import typer
import pathlib
import xml.etree.ElementTree as ET
import requests
import logging

logging.basicConfig(
    format="%(asctime)-15s %(name)-5s %(levelname)-8s %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("main")
app = typer.Typer()


@app.command()
def print_ontology(file: str):
    if file.startswith("http") or file.startswith("https"):
        logger.info("fetching remote resource")
        response = requests.get(file)
        root = ET.fromstring(response.text)
    else:
        logger.info("loading local document")
        tree = ET.parse(file)
        root = tree.getroot()

    edgelist: list[str] = []

    print("""
digraph G {
   bgcolor=transparent;
    """)
    for path in root:
        wisski_id = path.find("./id")
        assert wisski_id is not None

        is_group = path.find("./is_group")
        assert is_group is not None

        if is_group.text == "1":
            # append this thing into the groups array
            pass

        path_array = path.find("path_array")
        assert path_array is not None

        path_array = [particle.text for particle in path_array]

        # remove the main URL part of the path particle
        path_array = [strip_prefix(particle) for particle in path_array]
        edges = zip(path_array, path_array[1:])
        for h, t in edges:
            print(f'\t "{h}" -> "{t}";')
    print("}")


def strip_prefix(s: str | None) -> str:
    if s is None:
        return "<NO_ID>"

    return pathlib.Path(s).name
