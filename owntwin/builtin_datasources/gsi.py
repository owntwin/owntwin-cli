from pathlib import Path
from time import sleep

import requests
from loguru import logger

FGD_URL = "https://cyberjapandata.gsi.go.jp/xyz/experimental_fgd/{z}/{x}/{y}.geojson"
DEM5A_URL = (
    "https://cyberjapandata.gsi.go.jp/xyz/experimental_dem5a/{z}/{x}/{y}.geojson"
)
DEM10B_URL = (
    "https://cyberjapandata.gsi.go.jp/xyz/experimental_dem10b/{z}/{x}/{y}.geojson"
)


class Downloader(object):
    def __init__(self, cwd, interval=1):
        self.cwd = Path(cwd)
        self.interval = interval

    def download_fgd(self, tiles, cache=True):
        filenames = []

        for i, tile in enumerate(tiles):
            url = FGD_URL.format(z=tile.z, x=tile.x, y=tile.y)

            filename = "fgd-{z}_{x}_{y}.geojson".format(z=tile.z, x=tile.x, y=tile.y)
            filename = self.cwd.joinpath(filename)
            filenames.append(filename)

            logger.info(f"({i + 1}/{len(tiles)}) {url} → {filename}")
            # print(f"({i + 1}/{len(tiles)}) {url} → {str(filename).replace('nolze', 'ozekik')}")
            if cache and filename.exists():
                continue

            resp = requests.get(url)

            with open(filename, "wb") as f:
                f.write(resp.content)

            if len(tiles) - (i + 1) == 0:
                continue

            sleep(self.interval)

        return filenames

    def download_dem5a(self, tiles, cache=True):
        filenames = []

        for i, tile in enumerate(tiles):
            url = DEM5A_URL.format(z=tile.z, x=tile.x, y=tile.y)

            filename = "dem5a-{z}_{x}_{y}.geojson".format(z=tile.z, x=tile.x, y=tile.y)
            filename = self.cwd.joinpath(filename)
            filenames.append(filename)
            logger.info(f"({i + 1}/{len(tiles)}) {url} → {filename}")
            # print(f"({i + 1}/{len(tiles)}) {url} → {str(filename).replace('nolze', 'ozekik')}")
            if cache and filename.exists():
                continue

            resp = requests.get(url)

            with open(filename, "wb") as f:
                f.write(resp.content)

            if len(tiles) - (i + 1) == 0:
                continue

            sleep(self.interval)

        return filenames

    def download_dem10b(self, tiles, cache=True):
        for i, tile in enumerate(tiles):
            url = DEM10B_URL.format(z=tile.z, x=tile.x, y=tile.y)

            filename = "./dem10b-{z}_{x}_{y}.geojson".format(
                z=tile.z, x=tile.x, y=tile.y
            )
            filename = self.cwd.joinpath(filename)
            logger.info((url, filename))
            if cache and filename.exists():
                continue

            resp = requests.get(url)

            with open(filename, "wb") as f:
                f.write(resp.content)

            if len(tiles) - (i + 1) == 0:
                continue

            sleep(self.interval)
