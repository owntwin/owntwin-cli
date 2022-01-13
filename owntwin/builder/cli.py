import json
from collections import namedtuple
from pathlib import Path
from typing import List

import owntwin.builder.utils as utils
import typer
from geopy.geocoders import Nominatim
from halo import Halo
from InquirerPy import inquirer
from InquirerPy.separator import Separator
from InquirerPy.validator import NumberValidator
from loguru import logger
from owntwin.builder import commands
from owntwin.builder.commands import load_config, save_config
from owntwin.builder.package import Package

app = typer.Typer()

FILENAME = commands.FILENAME


@app.command("init")
def init(dirname: str = typer.Argument(".")):
    dirname = Path(dirname)

    basemap_zoom = commands.BASEMAP_ZOOM  # TODO: Fix

    if Path(dirname.joinpath(FILENAME)).exists():
        typer.Abort()

    if not dirname.is_dir():
        typer.Abort()

    shortdirname = dirname.resolve().name

    uid = inquirer.text(message="Twin ID:", default=shortdirname).execute()

    location_keywords = None
    location = None
    bbox = []
    default_name = ""

    while True:
        location_keywords = inquirer.text(
            message="Location keywords (leave blank to skip):",
        ).execute()

        if not location_keywords:
            break

        geolocator = Nominatim(user_agent="owntwin-cli")
        location_candidates = geolocator.geocode(
            location_keywords, exactly_one=False, limit=5
        )

        if not location_candidates:
            typer.echo("Not found. Please Try again.")
            continue

        location = inquirer.select(
            message="Select nearby location:",
            choices=list(
                map(lambda x: {"name": x.address, "value": x}, location_candidates)
            )
            + [Separator(), {"name": "(Back)", "value": False}],
        ).execute()

        if location:
            break

    if not location_keywords:

        def validate(text):
            try:
                return len(tuple(map(lambda x: float(x.strip()), text.split(",")))) == 2
            except:
                return False

        location_coordinate = inquirer.text(
            message="Location coordinate [latitude, longitude] (leave blank to skip):",
            validate=validate,
            filter=lambda text: tuple(map(lambda x: float(x.strip()), text.split(","))),
        ).execute()
        location = namedtuple("location", ["latitude", "longitude", "address"])
        location.latitude, location.longitude = location_coordinate
        location.address = ""

    if location:
        lat, lng = location.latitude, location.longitude
        # print(location, lat, lng)
        size = inquirer.text(
            message="Side length (meter):",
            filter=lambda x: float(x),
            validate=NumberValidator(float_allowed=True),
        ).execute()

        bbox = utils.bbox_from_center(lat, lng, size)
        bbox = utils.align_bbox(bbox, basemap_zoom)

        typer.echo(
            "  Left (lng): {}\n  Bottom (lat): {}\n  Right (lng): {}\n  Top (lat): {}".format(
                *bbox
            )
        )
        typer.confirm("Is this OK?", default=True, abort=True)
        default_name = location.address

    name = inquirer.text(message="Twin name:", default=default_name).execute()
    type = inquirer.text(message="Twin type:", default="").execute()
    iri = inquirer.text(
        message="IRI or URL:", default=f"https://beta.owntwin.com/twin/{uid}"
    ).execute()
    description = inquirer.text(message="Description:", default="").execute()

    twin = {
        "id": uid,
        "name": name,
        "type": type,
        "type_label": type,
        "iri": iri,
        "description": description,
        "bbox": bbox,
        "terrain": {
            "path": "assets/levelmap.json",
        },
        "building": {
            "path": "assets/buildings.json",
        },
        "properties": {},
        "modules": {},
    }

    # twin = {
    #     "name": name,
    #     ...
    #     "terrain": "levelmap.json",
    #     "objects": {
    #       "building": "building.json",
    #     },
    #     "modules": {},
    # }

    typer.echo(f"About to create {FILENAME}:\n")
    typer.echo(json.dumps(twin, ensure_ascii=False, indent=2))
    typer.confirm("Is this OK?", default=True, abort=True)

    if not dirname.exists():
        dirname.mkdir()

    save_config(twin, dirname.joinpath(FILENAME))


@app.command("add-terrain")
def add_terrain():
    twin = load_config()

    bbox = twin["bbox"]
    package = Package(".")

    with Halo(
        text="Installing {}".format(
            typer.style("terrain", fg=typer.colors.GREEN, bold=True)
        ),
        spinner="bouncingBar",
    ) as spinner:
        commands.add_terrain(bbox, package)
        spinner.succeed()


@app.command("add")
def add(module_names: List[str]):
    # NOTE: a module name can be:
    # local file, PyPI name, git repo/GitHub?

    twin = load_config()

    spinner = Halo(text="", spinner="bouncingBar")
    for module_name in module_names:
        module_name = commands.resolve_module_name(module_name)
        try:
            spinner.start(
                "Installing {}".format(
                    typer.style(
                        module_name,
                        fg=typer.colors.GREEN,
                        bold=True,
                    )
                )
            )
            commands.add_module(twin, Package("."), module_name)
            spinner.succeed()
        except Exception as err:
            logger.error(err)
            spinner.fail()

    spinner.stop()


@app.command("export")
def export(dirname: str = typer.Argument(".")):
    with Halo(text="Exporting...", spinner="bouncingBar") as spinner:
        commands.export(dirname)
        spinner.succeed(text="Done!")


@app.callback()
def main():
    pass


if __name__ == "__main__":
    app()
