import math

from loguru import logger
import geopandas as gpd
import geopy.distance
import mercantile
from PIL import Image


def meter_to_lat(meter, lat, lng):
    lat_dist = geopy.distance.distance((lat, lng), (lat + 1 / 111111, lng)).m
    approx_degree_per_meter = (1 / 111111) / lat_dist
    return meter * approx_degree_per_meter


def meter_to_lng(meter, lat, lng):
    lat_radians = math.radians(lat)
    lng_dist = geopy.distance.distance(
        (lat, lng), (lat, lng + 1 / (111111 * math.cos(lat_radians)))
    ).m
    approx_degree_per_meter = (1 / (111111 * math.cos(lat_radians))) / lng_dist
    return meter * approx_degree_per_meter


def tiles_bounds(tiles):
    tile_ul = min(tiles, key=lambda t: (t.y, t.x))
    tile_br = max(tiles, key=lambda t: (t.y, t.x))
    ul = [mercantile.bounds(tile_ul).west, mercantile.bounds(tile_ul).north]
    br = [mercantile.bounds(tile_br).east, mercantile.bounds(tile_br).south]
    bbox = [ul[0], br[1], br[0], ul[1]]

    # l = float('inf')
    # b = float('inf')
    # r = 0
    # u = 0
    # for tile in tiles:
    #     l = min(l, mercantile.bounds(tile).west)
    #     b = min(b, mercantile.bounds(tile).south)
    #     r = max(r, mercantile.bounds(tile).east)
    #     u = max(u, mercantile.bounds(tile).north)
    # bbox = [l, b, r, u]

    return bbox


def geojson_merge(geojson_filenames):
    if geojson_filenames:
        gdf = gpd.read_file(geojson_filenames[0])
    else:
        return None
    for filename in geojson_filenames[1:]:
        gdf = gdf.append(gpd.read_file(filename))
    return gdf


def make_error_tile(size):
    # cf. https://github.com/geopandas/contextily/pull/69/files
    im = Image.new(mode="RGBA", size=size, color=(0, 0, 0, 0))
    return im


def stitch_tiles(tiledata, size=(256, 256)):
    # print(tiledata)
    xs = list(map(lambda x: x.x, tiledata))
    ys = list(map(lambda x: x.y, tiledata))
    origin_x = min(xs)
    origin_y = min(ys)
    w = size[0] * (max(xs) - min(xs) + 1)
    h = size[1] * (max(ys) - min(ys) + 1)
    # print(w, h)
    dst = Image.new(mode="RGBA", size=(w, h), color=(0, 0, 0, 0))
    for tile in tiledata:
        im = Image.open(tile.filename)
        # print((tile["x"] - origin_x, tile["y"] - origin_y))
        dst.paste(im, (size[0] * (tile.x - origin_x), size[1] * (tile.y - origin_y)))
    return dst


def crop_img(im, img_bbox, crop_bbox, size=(256, 256)):
    # NOTE: Be aware, larger lat, further north
    # TODO: Fix
    # print(im.size)
    logger.info(img_bbox)
    logger.info(crop_bbox)
    img_ul = (img_bbox[0], img_bbox[3])
    img_br = (img_bbox[2], img_bbox[1])
    px_per_lng = im.size[0] / (img_br[0] - img_ul[0])
    px_per_lat = im.size[1] / (-1 * (img_br[1] - img_ul[1]))
    logger.info((px_per_lng, px_per_lat))

    crop_ul = (crop_bbox[0], crop_bbox[3])
    crop_br = (crop_bbox[2], crop_bbox[1])
    relative_crop_ul = (crop_ul[0] - img_ul[0], -1 * (crop_ul[1] - img_ul[1]))
    relative_crop_br = (crop_br[0] - img_ul[0], -1 * (crop_br[1] - img_ul[1]))
    logger.info((img_ul, crop_ul, crop_br))
    logger.info((relative_crop_ul, relative_crop_br))
    crop_bbox_in_px = (
        relative_crop_ul[0] * px_per_lng,
        relative_crop_ul[1] * px_per_lat,
        relative_crop_br[0] * px_per_lng,
        relative_crop_br[1] * px_per_lat,
    )
    logger.info(
        (
            crop_bbox_in_px,
            crop_bbox_in_px[2] - crop_bbox_in_px[0],
            crop_bbox_in_px[3] - crop_bbox_in_px[1],
        )
    )
    cropped = im.crop(crop_bbox_in_px)
    return cropped
