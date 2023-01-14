import mercantile
import owntwin.builder.utils as utils
from loguru import logger
from owntwin.builder.render import render_full
from owntwin.builtin_datasources import gsi

id = "owntwin.base"

definition = {
    "version": "0.1.0",
    "name": "基本",
    "description": """国土地理院ベクトルタイル提供実験による「基盤地図情報_基本項目」に基づくベースマップ等を含む基本モジュールです。

<https://github.com/gsi-cyberjapan/vector-tile-experiment>""",
    "license": "https://github.com/gsi-cyberjapan/vector-tile-experiment#%E6%8F%90%E4%BE%9B%E3%81%AE%E4%BD%8D%E7%BD%AE%E3%81%A5%E3%81%91",
    "actions": [
        {
            "id": "suggestion",
            "type": "link",
            "text": "この場所の情報修正を提案",
            "fields": ["name", "iri"],
        }
    ],
    "layers": [
        {
            "id": "basemap",
            "name": "ベースマップ",
            "levels": [0],
            "path": "assets/basemap.svg",
            "format": "svg",
            "color": "rgb(229, 231, 235)",
        },
        {
            "id": "rdcl",
            "name": "道路",
            "levels": [0],
            "path": "assets/rdcl.svg",
            "format": "svg",
            "color": "rgb(209, 213, 219)",
        },
        # {
        #     "id": "rdcl",
        #     "name": "道路",
        #     "levels": [0],
        #     "path": "assets/rdcl.geojson",
        #     "format": "geojson",
        #     "colors": {"default": "rgb(255, 255, 255)"},
        # },
        {
            "id": "railcl",
            "name": "鉄道",
            "levels": [0],
            "path": "assets/railcl.svg",
            "format": "svg",
            "color": "rgb(14, 116, 144)",
        },
        {
            "id": "rvcl",
            "name": "河川",
            "levels": [0],
            "path": "assets/rvcl.svg",
            "format": "svg",
            "color": "rgb(59, 130, 246)",
        },
    ],
}

default_properties = {
    "actions.suggestion.href": None,
    "actions.suggestion.fields.assign_to": {
        "name": None,
        "iri": None,
    },
    "layers.basemap.enabled": True,
    "layers.rdcl.enabled": True,
    "layers.railcl.enabled": True,
    "layers.rvcl.enabled": True,
}


def bbox_to_tiles(bbox, zoom):
    tiles = mercantile.tiles(*bbox, zoom)  # left, bottom, right, top
    tiles = list(tiles)
    # print(tiles)
    # ul = mercantile.ul(tiles[0])
    # br = [mercantile.bounds(tiles[-1]).east, mercantile.bounds(tiles[-1]).south]
    # basemap_bbox = [*ul, *br]
    return tiles


def add(bbox, package, cache_dir):
    dl = gsi.Downloader(cache_dir)

    ### basemap (fgd)
    BASEMAP_ZOOM = 18
    tiles = bbox_to_tiles(bbox, BASEMAP_ZOOM)
    basemap_bbox = utils.tiles_bounds(tiles)
    logger.debug(("basemap_bbox", basemap_bbox))

    filenames = dl.download_fgd(tiles)

    # filenames = []
    # for filename in Path(dl.cwd).glob("fgd-18*.geojson"):
    #     filenames.append(filename)

    merged = utils.geojson_merge(filenames)
    logger.debug(merged.head())

    if not merged.empty:  # TODO: Handle empty DataFrame
        merged.to_file(package.assets.joinpath("fgd.geojson"), driver="GeoJSON")
    render_full(
        merged, bbox=basemap_bbox, outfile=package.assets.joinpath("basemap.svg")
    )

    ### roadmap (rdcl)
    RDCL_ZOOM = 16  # TODO: Must be consistent with BASEMAP_ZOOM
    tiles = bbox_to_tiles(bbox, RDCL_ZOOM)
    filenames = dl.download_rdcl(tiles)

    merged = utils.geojson_merge(filenames)
    logger.debug(merged.head())

    if not merged.empty:
        merged.to_file(package.assets.joinpath("rdcl.geojson"), driver="GeoJSON")
    # TODO: basemap_bbox or else
    render_full(merged, bbox=basemap_bbox, outfile=package.assets.joinpath("rdcl.svg"))

    ### railmap (railcl)
    RAILCL_ZOOM = 16  # TODO: Must be consistent with BASEMAP_ZOOM
    tiles = bbox_to_tiles(bbox, RAILCL_ZOOM)
    filenames = dl.download_railcl(tiles)

    merged = utils.geojson_merge(filenames)
    logger.debug(merged.head())

    if not merged.empty:
        merged.to_file(package.assets.joinpath("railcl.geojson"), driver="GeoJSON")
    # TODO: basemap_bbox or else
    render_full(
        merged, bbox=basemap_bbox, outfile=package.assets.joinpath("railcl.svg")
    )

    ### rivermap (rvcl)
    RVCL_ZOOM = 16
    tiles = bbox_to_tiles(bbox, RVCL_ZOOM)
    filenames = dl.download_rvcl(tiles)

    merged = utils.geojson_merge(filenames)
    logger.debug(merged.head())

    if not merged.empty:
        merged.to_file(package.assets.joinpath("rvcl.geojson"), driver="GeoJSON")
    render_full(merged, bbox=basemap_bbox, outfile=package.assets.joinpath("rvcl.svg"))
