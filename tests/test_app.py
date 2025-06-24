import pytest
from typer.testing import CliRunner

from ontovis.lib.parser import parse_pathbuilder
from ontovis.lib.reader import read_document
from ontovis.lib.types import Field, Group
from ontovis.main import app, build_groups

runner = CliRunner()


def test_entrypoint_local_file():
    result = runner.invoke(app, ["./tests/fixtures/fixture.xml"])
    assert result.exit_code == 0


def test_pprint():
    result = runner.invoke(app, ["./tests/fixtures/fixture.xml", "--pprint"])
    assert result.exit_code == 0


@pytest.mark.slow
def test_entrypoint_remote_file():
    result = runner.invoke(
        app,
        [
            # an XML-document with only the root element, base64-encoded
            "https://httpbin.org/base64/PD94bWwgdmVyc2lvbj0iMS4wIj8+CjxwYXRoYnVpbGRlcmludGVyZmFjZS8+"
        ],
    )
    assert result.exit_code == 0


def test_entrypoint_local_file_disabled_paths():
    result = runner.invoke(app, ["./tests/fixtures/fixture_disabled-path.xml"])
    assert result.exit_code == 0


def test_group_builder():
    root = read_document("./tests/fixtures/fixture_group-hierarchy.xml")
    paths = parse_pathbuilder(root)
    result = build_groups(paths)

    expected = {
        "g_research_data_item": Group(
            name="g_research_data_item",
            subgroups=[
                Group(
                    name="g_research_data_item_title",
                    subgroups=[],
                    path=[
                        '"information_carrier"',
                        '"P102_has_title"',
                        '"alternative_title"',
                    ],
                    fields=[
                        Field(
                            name="f_research_data_item_title_appel",
                            path=[
                                '"information_carrier"',
                                '"P102_has_title"',
                                '"alternative_title"',
                                '"P1_is_identified_by"',
                                '"E41_Appellation"',
                            ],
                        ),
                        Field(
                            name="f_research_data_item_title_type",
                            path=[
                                '"information_carrier"',
                                '"P102_has_title"',
                                '"alternative_title"',
                                '"P2_has_type"',
                                '"E55_Type"',
                                '"P1_is_identified_by"',
                                '"E41_Appellation"',
                            ],
                        ),
                    ],
                )
            ],
            path=['"information_carrier"'],
            fields=[],
        )
    }
    assert result == expected
