from pathlib import Path
from time import sleep

import owntwin.builder.utils as utils
import requests
from loguru import logger
from owntwin.builder.tile import TileData

KK_KEIKAI_URL = (
    "https://disaportaldata.gsi.go.jp/raster/05_kyukeishakeikaikuiki/{z}/{x}/{y}.png"
)
KK_HOUKAI_URL = (
    "https://disaportaldata.gsi.go.jp/raster/05_kyukeisyachihoukai/{z}/{x}/{y}.png"
)
HIGHTIDE_URL = "https://disaportaldata.gsi.go.jp/raster/03_hightide_l2_shinsuishin_data/{z}/{x}/{y}.png"


class Downloader(object):
    def __init__(self, cwd, interval=1):
        self.cwd = Path(cwd)
        self.interval = interval

    def _download_base(self, template_url, template_filename, tiles, cache=True):
        tiledata = []

        z_min, z_max = 2, 17

        for i, tile in enumerate(tiles):
            if not z_min <= tile.z <= z_max:
                raise Exception

            url = template_url.format(z=tile.z, x=tile.x, y=tile.y)

            filename = template_filename.format(z=tile.z, x=tile.x, y=tile.y)
            filename = self.cwd.joinpath(filename)

            td = TileData(filename, z=tile.z, x=tile.x, y=tile.y)
            tiledata.append(td)

            logger.info(f"({i + 1}/{len(tiles)}) {url} → {filename}")
            # logger.info(f"({i + 1}/{len(tiles)}) {url} → {str(filename).replace('nolze', 'ozekik')}")
            if cache and filename.exists():
                continue

            resp = requests.get(url)

            if resp.status_code == 404:
                im = utils.make_error_tile((256, 256))
                im.save(filename, "png")
            else:
                with open(filename, "wb") as f:
                    f.write(resp.content)

            if len(tiles) - (i + 1) == 0:
                continue

            sleep(self.interval)

        return tiledata

    def download_kyukeisha_keikai(self, tiles, cache=True):
        return self._download_base(
            KK_KEIKAI_URL, "kk_keikai-{z}_{x}_{y}.png", tiles, cache=cache
        )

    def download_kyukeisha_houkai(self, tiles, cache=True):
        return self._download_base(
            KK_HOUKAI_URL, "kk_houkai-{z}_{x}_{y}.png", tiles, cache=cache
        )

    def download_hightide(self, tiles, cache=True):
        return self._download_base(
            HIGHTIDE_URL, "hightide-{z}_{x}_{y}.png", tiles, cache=cache
        )
