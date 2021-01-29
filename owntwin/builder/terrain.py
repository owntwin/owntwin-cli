import json
from collections import defaultdict

from loguru import logger


def extract_meshed_level(gdf, outfile="levelmap.json"):
    nx_seg = 100
    ny_seg = 100

    logger.info(gdf.crs)
    gdf = gdf.to_crs(epsg=3857)  # 3395

    logger.info(gdf.head())

    minx, miny, maxx, maxy = gdf.geometry.total_bounds
    gdf.geometry = gdf.geometry.translate(-minx, -miny)
    minx, miny, maxx, maxy = gdf.geometry.total_bounds

    bx = maxx / nx_seg
    by = maxy / ny_seg
    logger.info(minx, miny, maxx, maxy, bx, by)

    res = []
    m = defaultdict(lambda: 0)
    mc = defaultdict(lambda: 0)

    for i, row in gdf.iterrows():
        p = row["geometry"]
        alti = row["alti"]
        if alti > 0:
            x = p.x // bx  # - nx_seg // 2
            y = p.y // by  # - ny_seg // 2
            m[(x, y)] += alti
            mc[(x, y)] += 1

    for x in range(nx_seg):
        for y in range(ny_seg):
            if (x, y) in m:
                alti = m[(x, y)]
                res.append([x, y, alti / mc[(x, y)]])
            else:
                res.append([x, y, -1])

    with open(outfile, "w") as f:
        json.dump(res, f)
