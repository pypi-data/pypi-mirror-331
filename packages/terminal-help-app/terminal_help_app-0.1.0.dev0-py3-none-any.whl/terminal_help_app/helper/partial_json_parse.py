from partialjson.json_parser import JSONParser

_partial_json_parser = JSONParser()


def partial_json_parse(code: str):
    return _partial_json_parser.parse(code)
