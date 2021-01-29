import io

from loguru import logger
import svgwrite
from scour import scour


def render(gdf, outfile, filter=None, optimize=True):
    logger.info(gdf.crs)
    gdf = gdf.to_crs(epsg=3857)  # 3395

    logger.info(gdf.head())

    minx, miny, maxx, maxy = gdf.geometry.total_bounds
    gdf.geometry = gdf.geometry.translate(-minx, -miny)
    minx, miny, maxx, maxy = gdf.geometry.total_bounds
    logger.info((minx, miny, maxx, maxy))

    # gdf = gdf.scale(100000, 100000, origin=(0, 0))

    viewbox = " ".join(map(str, gdf.total_bounds))
    dwg = svgwrite.Drawing(outfile, height="100%", width="100%", viewBox=(viewbox))

    white = "#FFFFFF"
    grey = "#969696"
    dwg.fill(color=white)
    dwg.stroke(color=grey, width=1)
    extras = {}

    if filter:
        filtered_gdf = gdf[filter]
    else:
        filtered_gdf = gdf

    for g in filtered_gdf.geometry:
        mp = [(x, maxy - y) for x, y in zip(*g.coords.xy)]

        # gr = svgwrite.container.Group(**extras)
        dp = dwg.polyline(points=mp)
        # gr.add(dp)
        dwg.add(dp)

    if optimize:

        class ScourOptions:
            quiet = True

        buf1 = io.StringIO()
        dwg.write(buf1)
        buf1.seek(0)
        buf1 = io.BytesIO(buf1.getvalue().encode())
        buf1.seek(0)
        buf1.name = outfile
        with open(outfile, "wb") as f:
            scour.start(ScourOptions, buf1, f)
    else:
        with open(outfile, "w", encoding="utf-8") as f:
            dwg.write(f)


def render_full(gdf, outfile="full.svg"):
    render(gdf, outfile)


def render_contour(gdf, outfile="contour.svg"):
    render(gdf, outfile, filter=(gdf["class"] == "Cntr"))
