import codecs
import json
import shutil
from importlib import import_module
from pathlib import Path
from typing import List

# import importlib.resources  # Strangely not working
import importlib_resources  # Should be replaced with importlib.resource
import mercantile
import owntwin.builder.utils as utils
from loguru import logger
from owntwin.builder import CACHE_DIR
from owntwin.builder.terrain import extract_meshed_level
from owntwin.builtin_datasources import gsi

FILENAME = "twin.json"
BASEMAP_ZOOM = 18  # TODO: Fix
DEM5A_ZOOM = 18

def load_config():
    with open(FILENAME, "r") as f:
        twin = json.load(f)
    return twin


def save_config(config, path):
    # NOTE: Use codecs.open for win
    with codecs.open(path, "w", "utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def add_terrain(bbox: List[float], package):
    dl = gsi.Downloader(CACHE_DIR)  # TODO: Fix

    tiles = mercantile.tiles(*bbox, DEM5A_ZOOM)  # left, bottom, right, top
    tiles = list(tiles)

    filenames = dl.download_dem5a(tiles)
    merged = utils.geojson_merge(filenames)
    # print(merged.head())

    merged.to_file(package.assets.joinpath("merged_dem5a.geojson"), driver="GeoJSON")

    extract_meshed_level(merged, outfile=package.assets.joinpath("levelmap.json"))


def resolve_module_name(module_name: str):
    builtin_modules_map = {
        "owntwin.base": "owntwin.builtin_modules.base",
    }

    module_name = builtin_modules_map.get(module_name, module_name)
    return module_name


def add_module(twin, package, module_name: str):
    module = import_module(module_name)  # NOTE: module_name must be resolved

    module_append = (module.id, module.definition, module.default_properties)
    module.add(twin["bbox"], package, CACHE_DIR)

    (module_name, definition, default_properties) = module_append

    if not twin["modules"].get(module_name, None):
        twin["modules"][module_name] = {}

    twin["modules"][module_name]["version"] = "^{}".format(
        definition["version"]
    )  # TODO: Fix

    if not twin.get("properties", None):
        twin["properties"] = {}

    for key, value in default_properties.items():
        ns_key = "{}:{}".format(module_name, key)
        if not twin["properties"].get(ns_key, None):
            twin["properties"][ns_key] = value

    twin["modules"][module_name]["definition"] = definition

    save_config(twin, package.cwd.joinpath(FILENAME))  # TODO: Do not save every time

    return twin


def export(dirname: str):
    # https://importlib-resources.readthedocs.io/en/latest/migration.html
    path = importlib_resources.files("owntwin.viewer.owntwin")
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
