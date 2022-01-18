from loguru import logger
import mercantile
import owntwin.builder.utils as utils
from owntwin.builtin_datasources import gsi_disaportal

id = "owntwin.sample_modules.bousai"

definition = {
    "version": "0.1.0",
    "name": "防災・災害対応（全国）",
    "description": "レイヤーは国土地理院ハザードマップポータルサイト「重ねるハザードマップ」のオープンデータです。凡例は <https://disaportal.gsi.go.jp/hazardmap/copyright/opendata.html> を参照してください。",
    "license": "ハザードマップポータルサイト <https://disaportal.gsi.go.jp/hazardmap/copyright/opendata.html>",
    "actions": [
        {
            "id": "manual",
            "type": "link",
            "text": "この場所の防災マニュアルを見る",
            "href": None,
            "fields": [],
        },
        {
            "id": "anpi",
            "type": "link",
            "text": "この場所から安否状況を登録（発災時のみ）",
            "href": None,
            "fields": ["name", "iri"],
        },
    ],
    "layers": [
        {
            "id": "kk_keikai",
            "name": "土砂災害警戒区域（急傾斜地の崩壊）",
            "path": "assets/kk_keikai.png",
            "format": "png",
        },
        {
            "id": "kk_houkai",
            "name": "急傾斜地崩壊危険箇所",
            "path": "assets/kk_houkai.png",
            "format": "png",
        },
        {
            "id": "hightide",
            "name": "高潮浸水想定区域",
            "path": "assets/hightide.png",
            "format": "png",
        },
    ],
}

default_properties = {
    "actions.manual.href": None,
    "actions.anpi.href": None,
    "actions.anpi.fields.assign_to": {
        "name": None,
        "iri": None,
    },
    "layers.kk_keikai.enabled": True,
    "layers.kk_houkai.enabled": True,
    "layers.hightide.enabled": True,
}


def add(bbox, package, cache_dir):
    ZOOM = 18
    tiles = mercantile.tiles(*bbox, ZOOM)  # left, bottom, right, top
    tiles = list(tiles)
    # print(tiles)
    # ul = mercantile.ul(tiles[0])
    # br = [mercantile.bounds(tiles[-1]).east, mercantile.bounds(tiles[-1]).south]
    # basemap_bbox = [*ul, *br]
    basemap_bbox = utils.tiles_bounds(tiles)
    logger.debug(("basemap_bbox", basemap_bbox))

    ZOOM = 16
    tiles = mercantile.tiles(*basemap_bbox, ZOOM)  # left, bottom, right, top
    # print(list(tiles))
    # tiles = mercantile.simplify(tiles)
    tiles = list(tiles)
    # print(tiles)
    layer_bbox = utils.tiles_bounds(tiles)
    logger.debug(("layer_bbox", layer_bbox))

    dl = gsi_disaportal.Downloader(cache_dir)

    tiledata = dl.download_kyukeisha_keikai(tiles)
    merged = utils.stitch_tiles(tiledata)
    cropped = utils.crop_img(merged, layer_bbox, basemap_bbox)
    cropped.save(package.assets.joinpath("kk_keikai.png"), "png")

    tiledata = dl.download_kyukeisha_houkai(tiles)
    merged = utils.stitch_tiles(tiledata)
    cropped = utils.crop_img(merged, layer_bbox, basemap_bbox)
    cropped.save(package.assets.joinpath("kk_houkai.png"), "png")

    tiledata = dl.download_hightide(tiles)
    merged = utils.stitch_tiles(tiledata)
    cropped = utils.crop_img(merged, layer_bbox, basemap_bbox)
    cropped.save(package.assets.joinpath("hightide.png"), "png")
