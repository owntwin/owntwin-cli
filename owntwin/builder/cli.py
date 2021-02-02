import codecs
import json
import os
import shutil
from collections import namedtuple
from importlib import import_module
from pathlib import Path
from typing import List

# import importlib.resources  # Strangely not working
import importlib_resources  # Should be replaced with importlib.resource
import mercantile
import owntwin.builder.utils as utils
import typer
from geopy.geocoders import Nominatim
from halo import Halo
from InquirerPy import inquirer
from InquirerPy.separator import Separator
from InquirerPy.validator import NumberValidator
from loguru import logger
from owntwin.builder.package import Package
from owntwin.builder.terrain import extract_meshed_level
from owntwin.builtin_datasources import gsi
from xdg import xdg_cache_home

app = typer.Typer()

FILENAME = "twin.json"

if os.name == "nt":
    CACHE_DIR = Path(os.path.expandvars("%APPDATA%/owntwin/cache"))
else:
    CACHE_DIR = xdg_cache_home().joinpath("owntwin/")

if not CACHE_DIR.exists():
    CACHE_DIR.mkdir(parents=True)


def load_config():
    with open(FILENAME, "r") as f:
        twin = json.load(f)
    return twin


def save_config(config, path):
    # NOTE: Use codecs.open for win
    with codecs.open(path, "w", "utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


@app.command("init")
def init(dirname: str = typer.Argument(".")):
    dirname = Path(dirname)

    basemap_zoom = 18  # TODO: Fix

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

        # bbox = [
        #     lng + utils.meter_to_lng(size, lat, lng),  # east
        #     lat - utils.meter_to_lat(size, lat, lng),  # south
        #     lng - utils.meter_to_lng(size, lat, lng),  # west
        #     lat + utils.meter_to_lat(size, lat, lng),  # north
        # ]
        bbox = [
            lng - utils.meter_to_lng(size, lat, lng),  # west
            lat - utils.meter_to_lat(size, lat, lng),  # south
            lng + utils.meter_to_lng(size, lat, lng),  # east
            lat + utils.meter_to_lat(size, lat, lng),  # north
        ]
        tiles = mercantile.tiles(*bbox, basemap_zoom)
        tiles = list(tiles)
        basemap_bbox = utils.tiles_bounds(tiles)
        bbox = basemap_bbox

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
        "canvas": {
            "width": 1024,
            "height": 1024,
        },
        "terrain": {
            "path": "assets/levelmap.json",
        },
        "building": {
            "path": "assets/buildings.json",
        },
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

    dl = gsi.Downloader(CACHE_DIR)  # TODO: Fix

    basemap_zoom = 18
    tiles = mercantile.tiles(*bbox, basemap_zoom)  # left, bottom, right, top
    tiles = list(tiles)

    spinner = Halo(text="", spinner="bouncingBar")
    spinner.start(
        "Installing {}".format(typer.style("terrain", fg=typer.colors.GREEN, bold=True))
    )

    filenames = dl.download_dem5a(tiles)
    merged = utils.geojson_merge(filenames)
    # print(merged.head())

    merged.to_file(package.assets.joinpath("merged_dem5a.geojson"), driver="GeoJSON")

    extract_meshed_level(merged, outfile=package.assets.joinpath("levelmap.json"))

    spinner.succeed()
    spinner.stop()


@app.command("add")
def add(module_names: List[str]):
    # NOTE: a module name can be:
    # local file, PyPI name, git repo/GitHub?

    twin = load_config()

    modules_append = []

    builtin_modules_map = {
        "owntwin.base": "owntwin.builtin_modules.base",
    }

    spinner = Halo(text="", spinner="bouncingBar")
    for module_name in module_names:
        module_name = builtin_modules_map.get(module_name, module_name)
        try:
            module = import_module(module_name)
            spinner.start(
                "Installing {}".format(
                    typer.style(module.id, fg=typer.colors.GREEN, bold=True)
                )
            )
            modules_append.append((module.id, module.module))
            package = Package(".")
            module.add(
                twin["bbox"],
                package,
                CACHE_DIR,
            )
            spinner.succeed()
        except Exception as err:
            logger.error(err)
            spinner.fail()

    spinner.stop()

    if modules_append:
        for (module_name, module) in modules_append:
            twin["modules"][module_name] = module
        save_config(twin, FILENAME)


@app.command("export")
def export(dirname: str = typer.Argument(".")):
    # https://importlib-resources.readthedocs.io/en/latest/migration.html
    path = importlib_resources.files("owntwin.viewer.owntwin")
    spinner = Halo(text="Exporting...", spinner="bouncingBar")
    for entry in path.iterdir():
        logger.info(entry)
        if entry.is_dir():
            shutil.copytree(
                entry,
                Path(dirname).joinpath(entry.name),
                dirs_exist_ok=True,  # TODO: Confirm
                copy_function=shutil.copy,
                ignore=shutil.ignore_patterns(".DS_Store"),
            )
        else:
            if not any(
                [
                    entry.match(exclude)
                    for exclude in ["twin.json", "assets", ".DS_Store"]
                ]
            ):
                shutil.copy(entry, dirname)
    spinner.succeed(text="Done!")
    spinner.stop()


@app.callback()
def main():
    pass


if __name__ == "__main__":
    app()
