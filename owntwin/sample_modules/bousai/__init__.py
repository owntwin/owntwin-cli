from loguru import logger
import mercantile
import owntwin.builder.utils as utils
from owntwin.builtin_datasources import gsi_disaportal

id = "owntwin/sample_modules/bousai"

module = {
    "name": "防災・災害対応",
    "description": "レイヤーは国土地理院ハザードマップポータルサイト「重ねるハザードマップ」のオープンデータです。凡例は <https://disaportal.gsi.go.jp/hazardmap/copyright/opendata.html> を参照してください。",
    "license": "ハザードマップポータルサイト <https://disaportal.gsi.go.jp/hazardmap/copyright/opendata.html>",
    "actions": [
        {
            "type": "link",
            "text": "この場所の防災マニュアルを見る",
            "href": None,
            "params": [],
        },
        {
            "type": "link",
            "text": "この場所から安否状況を登録（発災時のみ）",
            "href": None,
            "params": [],
        },
    ],
    "layers": [
        {
            "id": "kk_keikai",
            "name": "土砂災害警戒区域（急傾斜地の崩壊）",
            "path": "assets/kk_keikai.png",
            "format": "png",
            "enabled": True,
        },
        {
            "id": "kk_houkai",
            "name": "急傾斜地崩壊危険箇所",
            "path": "assets/kk_houkai.png",
            "format": "png",
            "enabled": True,
        },
        {
            "id": "hightide",
            "name": "高潮浸水想定区域",
            "path": "assets/hightide.png",
            "format": "png",
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

    zoom = 16
    tiles = mercantile.tiles(*basemap_bbox, zoom)  # left, bottom, right, top
    # print(list(tiles))
    # tiles = mercantile.simplify(tiles)
    tiles = list(tiles)
    # print(tiles)
    layer_bbox = utils.tiles_bounds(tiles)
    logger.info(("layer_bbox", layer_bbox))

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
