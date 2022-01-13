# import mercantile
# import owntwin.builder.utils as utils
# from loguru import logger

id = "owntwin.sample_modules.plateau"

definition = {
    "version": "0.1.0",
    "name": "PLATEAU",
    "description": "国土交通省 Project PLATEAUが提供する3D都市モデルデータです。\n\n<https://www.mlit.go.jp/plateau/>",
    "license": "https://www.mlit.go.jp/plateau/site-policy/",
    "actions": [],
    "layers": [
        {
            "id": "citymodel",
            "name": "3D都市モデル",
            "levels": [0],
            "path": "assets/citymodel.plateau.geojson",
            "format": "geojson",
        }
    ],
}

default_properties = {
    "layers.citymodel.enabled": True,
}


def add(bbox, package, cache_dir):
    pass
