# pyright: strict
import logging
import xml.etree.ElementTree as ET

import requests

logger = logging.getLogger("main")


def read_document(file: str) -> ET.Element:
    if file.startswith("http") or file.startswith("https"):
        logger.info("fetching remote resource")
        response = requests.get(file)
        root = ET.fromstring(response.text)
    else:
        logger.info("loading local document")
        tree = ET.parse(file)
        root = tree.getroot()

    return root
