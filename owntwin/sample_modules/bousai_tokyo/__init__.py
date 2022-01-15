import os
from io import BytesIO
from pathlib import Path
from time import sleep
from urllib.parse import urlparse

import mercantile
import owntwin.builder.utils as utils
import pandas as pd

# from owntwin.builtin_datasources import gsi_disaportal
import requests
from loguru import logger
from owntwin.builder import CACHE_DIR

id = "owntwin.sample_modules.bousai_tokyo"

TOKYO_BM_HINANJO_URL = (
    "https://www.opendata.metro.tokyo.lg.jp/soumu/130001_evacuation_center.csv"
)
TOKYO_BM_HINANBASHO_URL = (
    "https://www.opendata.metro.tokyo.lg.jp/soumu/130001_evacuation_area.csv"
)
TOKYO_BM_FIREHYDRANT_URL = (
    "https://www.opendata.metro.tokyo.lg.jp/shoubou/2021/130001_fire-hydrant.csv"
)
TOKYO_BM_WATERTANK_URL = "https://www.opendata.metro.tokyo.lg.jp/shoubou/2021/130001_fireproof-water-tank.csv"

SUIDOU_WATERSUPPLY_URL = "https://www.opendata.metro.tokyo.lg.jp/suidou/R3/kyoten.csv"

HOKEN_DAREDEMOWC_KOKYO_URL = "https://www.opendata.metro.tokyo.lg.jp/fukushihoken/wc/koukyoshisetsu_barrier-free-wc.csv"
HOKEN_DAREDEMOWC_STATION_URL = "https://www.opendata.metro.tokyo.lg.jp/fukushihoken/wc/tonaitetsudoueki_barrier-free-wc.csv"
HOKEN_SHINRYOUKENSA_URL = "https://www.opendata.metro.tokyo.lg.jp/fukushihoken/130001_shinryoukensa20220112.csv"

definition = {
    "version": "0.1.0",
    "name": "防災・災害対応（東京都）",
    "description": "東京都オープンデータカタログ掲載のオープンデータです。",
    "license": "避難所、避難場所データ オープンデータ (CC-BY-4.0) <https://catalog.data.metro.tokyo.lg.jp/dataset/t000003d0000000093>\n"
    + "東京消防庁 消火栓及び防火水槽等 (CC-BY-4.0) <https://catalog.data.metro.tokyo.lg.jp/dataset/t000017d0000000007>\n"
    + "東京都水道局 給水拠点一覧データ (CC-BY-4.0) <https://catalog.data.metro.tokyo.lg.jp/dataset/t000019d0000000001>\n"
    + "東京都福祉保健局 だれでもトイレのバリアフリー情報 (CC-BY-4.0) <https://catalog.data.metro.tokyo.lg.jp/dataset/t000010d0000000062>\n"
    + "東京都福祉保健局  診療・検査医療機関の一覧  (CC-BY-4.0) <https://catalog.data.metro.tokyo.lg.jp/dataset/t000010d0000000095>",
    "actions": [
        {
            "id": "manual",
            "type": "link",
            "text": "この場所の防災マニュアルを見る",
            "href": None,
            "fields": [],
        },
        # {
        #     "id": "anpi",
        #     "type": "link",
        #     "text": "この場所から安否状況を登録（発災時のみ）",
        #     "href": None,
        #     "fields": ["name", "iri"],
        # },
    ],
    "layers": [
        {
            "id": "tokyo_bm_hinanjo",
            "name": "避難所",
            "path": "assets/tokyo_bm_hinanjo.csv",
            "format": "csv",
            "labelVisibility": "always",
            "keys": {
                "lat": "緯度",
                "lng": "経度",
                "label": "避難所_名称",
            },
        },
        {
            "id": "tokyo_bm_hinanbasho",
            "name": "避難場所",
            "path": "assets/tokyo_bm_hinanbasho.csv",
            "format": "csv",
            "keys": {
                "lat": "緯度",
                "lng": "経度",
                "label": "避難場所_名称",
            },
        },
        {
            "id": "tokyo_bm_firehydrant",
            "name": "消火栓",
            "path": "assets/tokyo_bm_firehydrant.csv",
            "format": "csv",
            "keys": {
                "lat": "緯度",
                "lng": "経度",
                "label": None,
            },
            "color": 0xFA913C,
            "size": {"height": 16},
        },
        {
            "id": "tokyo_bm_watertank",
            "name": "防火水槽等",
            "path": "assets/tokyo_bm_watertank.csv",
            "format": "csv",
            "keys": {
                "lat": "緯度",
                "lng": "経度",
                "label": None,
            },
            "color": 0x6366F1,
            "size": {"height": 16},
        },
        {
            "id": "suidou_watersupply",
            "name": "給水拠点",
            "path": "assets/suidou_watersupply.csv",
            "format": "csv",
            "keys": {
                "lat": "緯度",
                "lng": "経度",
                "label": "施設名",
            },
            "color": 0x6366F1,
            "size": {"height": 16},
        },
        {
            "id": "hoken_daredemowc",
            "name": "だれでもトイレ（バリアフリー）",
            "path": "assets/hoken_daredemowc.csv",
            "format": "csv",
            "keys": {
                "lat": "緯度",
                "lng": "経度",
                "label": "トイレ名",
            },
            "color": 0x06B6D4,
            "size": {"height": 32},
        },
        {
            "id": "hoken_shinryoukensa",
            "name": "診療・検査医療機関",
            "path": "assets/hoken_shinryoukensa.csv",
            "format": "csv",
            "keys": {
                "lat": "緯度",
                "lng": "経度",
                "label": "医療機関名",
            },
            "color": 0xE879F9,
            "size": {"height": 50},
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
    "layers.tokyo_bm_hinanjo.enabled": True,
    "layers.tokyo_bm_hinanbasho.enabled": True,
    "layers.tokyo_bm_firehydrant.enabled": False,
    "layers.tokyo_bm_watertank.enabled": True,
    "layers.suidou_watersupply.enabled": True,
    "layers.hoken_daredemowc.enabled": False,
    "layers.hoken_shinryoukensa.enabled": True,
}


def save_areadata(bbox, url_or_urls, filename, encoding=None, cache=True):
    if not isinstance(url_or_urls, (list, tuple)):
        urls = [url_or_urls]
    else:
        urls = url_or_urls

    area_df = pd.DataFrame()

    for url in urls:
        cachefile = Path(CACHE_DIR) / os.path.basename(urlparse(url).path)
        data = None
        if cache and cachefile.exists():
            with open(cachefile, "rb") as f:
                data = BytesIO(f.read())
        if not cache or not data:
            resp = requests.get(url)
            # if resp.status_code == 404:
            #     raise
            logger.debug(("resp.apparent_encoding", resp.apparent_encoding))
            encoding = encoding or resp.apparent_encoding
            content = resp.content.decode(encoding)
            data = BytesIO(content.encode("utf-8"))
            if cache:
                with open(cachefile, "wb") as f:
                    f.write(data.read())
                data.seek(0)

        df = pd.read_csv(data, sep=",")
        logger.debug(df.columns)
        # NOTE: NaN in bad rows
        df[["緯度", "経度"]] = df[["緯度", "経度"]].apply(pd.to_numeric, errors="coerce")
        # df[["緯度", "経度"]] = df[["緯度", "経度"]].astype("float")
        area_df = area_df.append(
            df.query("@bbox[1] <= 緯度 <= @bbox[3] and @bbox[0] <= 経度 <= @bbox[2]")
        )
        logger.debug(("area_df", area_df))

    area_df.to_csv(filename, encoding="utf-8", sep=",")

    sleep(1)


def add(bbox, package, cache_dir):
    basemap_zoom = 18
    tiles = mercantile.tiles(*bbox, basemap_zoom)  # left, bottom, right, top
    tiles = list(tiles)
    basemap_bbox = utils.tiles_bounds(tiles)
    logger.debug(("basemap_bbox", basemap_bbox))

    save_areadata(
        basemap_bbox,
        TOKYO_BM_HINANJO_URL,
        package.assets.joinpath("tokyo_bm_hinanjo.csv"),
    )
    save_areadata(
        basemap_bbox,
        TOKYO_BM_HINANBASHO_URL,
        package.assets.joinpath("tokyo_bm_hinanbasho.csv"),
    )
    save_areadata(
        basemap_bbox,
        TOKYO_BM_FIREHYDRANT_URL,
        package.assets.joinpath("tokyo_bm_firehydrant.csv"),
    )
    save_areadata(
        basemap_bbox,
        TOKYO_BM_WATERTANK_URL,
        package.assets.joinpath("tokyo_bm_watertank.csv"),
    )

    save_areadata(
        basemap_bbox,
        SUIDOU_WATERSUPPLY_URL,
        package.assets.joinpath("suidou_watersupply.csv"),
    )

    save_areadata(
        basemap_bbox,
        [HOKEN_DAREDEMOWC_KOKYO_URL, HOKEN_DAREDEMOWC_STATION_URL],
        package.assets.joinpath("hoken_daredemowc.csv"),
        encoding="cp932",
    )

    save_areadata(
        basemap_bbox,
        [HOKEN_SHINRYOUKENSA_URL],
        package.assets.joinpath("hoken_shinryoukensa.csv"),
    )
