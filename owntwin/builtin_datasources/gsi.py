from pathlib import Path
from time import sleep

import requests
from loguru import logger

RDCL_URL = "https://cyberjapandata.gsi.go.jp/xyz/experimental_rdcl/{z}/{x}/{y}.geojson"
RAILCL_URL = (
    "https://cyberjapandata.gsi.go.jp/xyz/experimental_railcl/{z}/{x}/{y}.geojson"
)
RVCL_URL = "https://cyberjapandata.gsi.go.jp/xyz/experimental_rvrcl/{z}/{x}/{y}.geojson"
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

    def download_rdcl(self, tiles, cache=True):
        filenames = []

        for i, tile in enumerate(tiles):
            url = RDCL_URL.format(z=tile.z, x=tile.x, y=tile.y)

            filename = "rdcl-{z}_{x}_{y}.geojson".format(z=tile.z, x=tile.x, y=tile.y)
            filename = self.cwd.joinpath(filename)
            filenames.append(filename)

            logger.info(f"({i + 1}/{len(tiles)}) {url} → {filename}")
            if cache and filename.exists():
                continue

            resp = requests.get(url)

            if resp.status_code == 404:
                data = bytes('{"type":"FeatureCollection","features":[]}', "utf-8")
            else:
                data = resp.content

            with open(filename, "wb") as f:
                f.write(data)

            if len(tiles) - (i + 1) == 0:
                continue

            sleep(self.interval)

        return filenames

    def download_railcl(self, tiles, cache=True):
        filenames = []

        for i, tile in enumerate(tiles):
            url = RAILCL_URL.format(z=tile.z, x=tile.x, y=tile.y)

            filename = "railcl-{z}_{x}_{y}.geojson".format(z=tile.z, x=tile.x, y=tile.y)
            filename = self.cwd.joinpath(filename)
            filenames.append(filename)

            logger.info(f"({i + 1}/{len(tiles)}) {url} → {filename}")
            if cache and filename.exists():
                continue

            resp = requests.get(url)

            if resp.status_code == 404:
                data = bytes('{"type":"FeatureCollection","features":[]}', "utf-8")
            else:
                data = resp.content

            with open(filename, "wb") as f:
                f.write(data)

            if len(tiles) - (i + 1) == 0:
                continue

            sleep(self.interval)

        return filenames

    def download_rvcl(self, tiles, cache=True):
        filenames = []

        for i, tile in enumerate(tiles):
            url = RVCL_URL.format(z=tile.z, x=tile.x, y=tile.y)

            filename = "rvcl-{z}_{x}_{y}.geojson".format(z=tile.z, x=tile.x, y=tile.y)
            filename = self.cwd.joinpath(filename)
            filenames.append(filename)

            logger.info(f"({i + 1}/{len(tiles)}) {url} → {filename}")
            if cache and filename.exists():
                continue

            resp = requests.get(url)

            if resp.status_code == 404:
                data = bytes('{"type":"FeatureCollection","features":[]}', "utf-8")
            else:
                data = resp.content

            with open(filename, "wb") as f:
                f.write(data)

            if len(tiles) - (i + 1) == 0:
                continue

            sleep(self.interval)

        return filenames

    def download_fgd(self, tiles, cache=True):
        filenames = []

        for i, tile in enumerate(tiles):
            url = FGD_URL.format(z=tile.z, x=tile.x, y=tile.y)

            filename = "fgd-{z}_{x}_{y}.geojson".format(z=tile.z, x=tile.x, y=tile.y)
            filename = self.cwd.joinpath(filename)
            filenames.append(filename)

            logger.info(f"({i + 1}/{len(tiles)}) {url} → {filename}")
            if cache and filename.exists():
                continue

            resp = requests.get(url)

            if resp.status_code == 404:
                data = bytes('{"type":"FeatureCollection","features":[]}', "utf-8")
            else:
                data = resp.content

            with open(filename, "wb") as f:
                f.write(data)

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
            if cache and filename.exists():
                continue

            resp = requests.get(url)

            if resp.status_code == 404:
                data = bytes('{"type":"FeatureCollection","features":[]}', "utf-8")
            else:
                data = resp.content

            with open(filename, "wb") as f:
                f.write(data)

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
            logger.debug((url, filename))
            if cache and filename.exists():
                continue

            resp = requests.get(url)

            with open(filename, "wb") as f:
                f.write(resp.content)

            if len(tiles) - (i + 1) == 0:
                continue

            sleep(self.interval)
