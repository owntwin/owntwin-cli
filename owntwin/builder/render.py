import io

from loguru import logger
import svgwrite
from scour import scour
import pyproj

NONE = "none"
WHITE = "#FFFFFF"
GRAY = "#969696"


def render(
    gdf,
    outfile,
    bbox=None,
    filter=None,
    optimize=True,
    fill=NONE,
    stroke=GRAY,
    stroke_width=1,
):
    gdf = gdf.copy()
    logger.debug(gdf.crs)
    gdf = gdf.to_crs(epsg=3857)  # 3395

    logger.debug(gdf.head())

    # logger.debug(gdf.columns)
    # for v in gdf[['class', 'type', 'name']].iterrows():
    #     logger.debug(v)
    # exit()

    if bbox is None:
        bbox = gdf.geometry.total_bounds
    else:
        transformer = pyproj.Transformer.from_crs(
            "epsg:4326", "epsg:3857", always_xy=True
        )
        ul = transformer.transform(bbox[0], bbox[1])
        br = transformer.transform(bbox[2], bbox[3])
        bbox = [*ul, *br]
        # logger.debug(f"\n{bbox}\n{gdf.geometry.total_bounds}")

    minx, miny, maxx, maxy = bbox
    gdf.geometry = gdf.geometry.translate(-minx, -miny)
    maxx, maxy = maxx - minx, maxy - miny

    # gdf = gdf.scale(100000, 100000, origin=(0, 0))

    viewbox = " ".join(map(str, [0, 0, maxx, maxy]))
    dwg = svgwrite.Drawing(outfile, height="100%", width="100%", viewBox=(viewbox))

    # NOTE: Not used in SVGMeshLayer (path only)
    dwg.fill(color=fill)
    dwg.stroke(color=stroke, width=stroke_width)
    extras = {}

    if filter is not None:
        filtered_gdf = gdf[filter]
    else:
        filtered_gdf = gdf

    for g in filtered_gdf.geometry:
        # TODO: Reconsider precision
        mp = [(round(x, 5), round(maxy - y, 5)) for x, y in zip(*g.coords.xy)]

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


def render_full(gdf, bbox=None, outfile="full.svg", **kwargs):
    render(gdf, outfile, bbox=bbox, **kwargs)


def render_contour(gdf, bbox=None, outfile="contour.svg", **kwargs):
    render(gdf, outfile, bbox=bbox, filter=(gdf["class"] == "Cntr"), **kwargs)
