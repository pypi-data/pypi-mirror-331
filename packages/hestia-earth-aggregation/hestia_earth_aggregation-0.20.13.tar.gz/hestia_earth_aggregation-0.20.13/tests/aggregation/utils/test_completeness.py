import json

from tests.utils import fixtures_path
from hestia_earth.aggregation.utils.completeness import aggregate_completeness


def test_aggregate_completeness():
    with open(f"{fixtures_path}/cycle/wheatGrain.jsonld", encoding='utf-8') as f:
        cycles = json.load(f)
    with open(f"{fixtures_path}/cycle/utils/completeness.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    assert aggregate_completeness(cycles) == expected
