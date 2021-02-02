id = "owntwin/sample_modules/jpsearch"

module = {
    "name": "ジャパンサーチ",
    "description": None,
    "license": "https://jpsearch.go.jp/policy",
    "actions": [
        {
            "type": "link",
            "text": "場所名でジャパンサーチを検索",
            "href": "https://jpsearch.go.jp/csearch/jps-cross",
            "default_param": "csid=jps-cross",
            "params": [["q-loc", "name"]],
        },
        {
            "type": "link",
            "text": "位置情報でジャパンサーチを検索",
            "href": "https://beta.owntwin.com/resolver/jpsearch",
            "params": [["geohash", "geohash"]],
        },
    ],
    "layers": [],
}


def add(bbox, package, cache_dir):
    pass
