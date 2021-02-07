id = "owntwin.sample_modules.jpsearch"

definition = {
    "version": "0.1.0",
    "name": "ジャパンサーチ",
    "description": None,
    "license": "https://jpsearch.go.jp/policy",
    "actions": [
        {
            "id": "search_by_name",
            "type": "link",
            "text": "場所名でジャパンサーチを検索",
            "href": "https://jpsearch.go.jp/csearch/jps-cross",
            "default_param": "csid=jps-cross",
            "fields": ["name"],
            "fields.assign_to": {"name": "q-loc"},
        },
        {
            "id": "search_by_location",
            "type": "link",
            "text": "位置情報でジャパンサーチを検索",
            "href": "https://beta.owntwin.com/resolver/jpsearch",
            "fields": ["owntwin:geohash"],
            "fields.assign_to": {"owntwin:geohash": "geohash"},
        },
    ],
    "layers": [],
}

default_properties = {}


def add(bbox, package, cache_dir):
    pass
