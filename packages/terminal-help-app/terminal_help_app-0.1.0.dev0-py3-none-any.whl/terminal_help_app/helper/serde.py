import json


def json_dumps_consistent(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def json_dumps(obj):
    return json.dumps(obj, sort_keys=False, separators=(",", ":"))
