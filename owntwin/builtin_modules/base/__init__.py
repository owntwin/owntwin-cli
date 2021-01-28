import mercantile
import owntwin.builder.utils as utils
from loguru import logger
from owntwin.builder.render import render_full
from owntwin.builtin_datasources import gsi

id = "owntwin/base"

module = {
    "name": "基本",
    "description": """国土地理院ベクトルタイル提供実験による「基盤地図情報_基本項目」に基づくベースマップを含む基本モジュールです。

<https://github.com/gsi-cyberjapan/vector-tile-experiment>""",
    "license": "https://github.com/gsi-cyberjapan/vector-tile-experiment#%E6%8F%90%E4%BE%9B%E3%81%AE%E4%BD%8D%E7%BD%AE%E3%81%A5%E3%81%91",
    "actions": [
        {
            "type": "link",
            "text": "この場所の情報修正を提案",
            "href": None,
            "default_params": [],
            "params": [],
        }
    ],
    "layers": [
        {
            "id": "basemap",
            "name": "ベースマップ",
            "path": "assets/basemap.svg",
            "format": "svg",
            "levels": [0],
            "enabled": True,
        },
    ],
}


def add(bbox, package, cache_dir):
    basemap_zoom = 18
    tiles = mercantile.tiles(*bbox, basemap_zoom)  # left, bottom, right, top
    tiles = list(tiles)
    # print(tiles)
    # ul = mercantile.ul(tiles[0])
    # br = [mercantile.bounds(tiles[-1]).east, mercantile.bounds(tiles[-1]).south]
    # basemap_bbox = [*ul, *br]
    basemap_bbox = utils.tiles_bounds(tiles)
    logger.info(("basemap_bbox", basemap_bbox))

    dl = gsi.Downloader(cache_dir)
    filenames = dl.download_fgd(tiles)

    # filenames = []
    # for filename in Path(dl.cwd).glob("fgd-18*.geojson"):
    #     filenames.append(filename)

    merged = utils.geojson_merge(filenames)
    logger.info(merged.head())

    merged.to_file(package.assets.joinpath("merged.geojson"), driver="GeoJSON")

    render_full(merged, outfile=package.assets.joinpath("basemap.svg"))
