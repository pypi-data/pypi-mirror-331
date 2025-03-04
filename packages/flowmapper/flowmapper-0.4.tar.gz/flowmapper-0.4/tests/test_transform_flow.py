import json
from pathlib import Path

from flowmapper.flow import Flow
from flowmapper.flowmap import Flowmap
from flowmapper.transformation_mapping import prepare_transformations

DATA_DIR = Path(__file__).parent / "data"


def test_transform_flow_without_default_transformations():
    transformations = prepare_transformations(
        [json.load(open(DATA_DIR / "transformations.json"))]
    )
    source_flows = json.load(open(DATA_DIR / "sp.json"))
    source_flows = [Flow(flow, transformations) for flow in source_flows]
    target_flows = json.load(open(DATA_DIR / "ei-3.7.json"))
    target_flows = [Flow(flow, transformations) for flow in target_flows]

    flowmap = Flowmap(source_flows, target_flows)
    actual = flowmap.to_randonneur()

    expected = [
        {
            "source": {
                "name": "1,4-Butanediol",
                "unit": "kg",
                "context": "air",
                "CAS number": "110-63-4",
            },
            "target": {
                "name": "1,4-Butanediol",
                "unit": "kg",
                "identifier": "09db39be-d9a6-4fc3-8d25-1f80b23e9131",
                "context": ["air", "unspecified"],
                "CAS number": "110-63-4",
            },
            "conversion_factor": 1.0,
            "comment": "Identical names",
        },
        {
            "source": {
                "name": "1,4-Butanediol",
                "unit": "kg",
                "context": "air/high. pop.",
                "CAS number": "110-63-4",
            },
            "target": {
                "name": "1,4-Butanediol",
                "unit": "kg",
                "identifier": "09db39be-d9a6-4fc3-8d25-1f80b23e9131",
                "context": ["air", "unspecified"],
                "CAS number": "110-63-4",
            },
            "conversion_factor": 1.0,
            "comment": "Identical names",
        },
    ]
    assert actual == expected


def test_transform_flow_with_default_transformations(transformations):
    all_transformations = transformations + prepare_transformations(
        [json.load(open(DATA_DIR / "transformations.json"))]
    )
    source_flows = json.load(open(DATA_DIR / "sp.json"))
    source_flows = [Flow(flow, all_transformations) for flow in source_flows]
    target_flows = json.load(open(DATA_DIR / "ei-3.7.json"))
    target_flows = [Flow(flow, all_transformations) for flow in target_flows]

    flowmap = Flowmap(source_flows, target_flows)
    actual = flowmap.to_randonneur()

    expected = [
        {
            "comment": "Identical names",
            "conversion_factor": 1.0,
            "source": {
                "CAS number": "110-63-4",
                "context": "air",
                "name": "1,4-Butanediol",
                "unit": "kg",
            },
            "target": {
                "CAS number": "110-63-4",
                "context": ["air", "unspecified"],
                "identifier": "09db39be-d9a6-4fc3-8d25-1f80b23e9131",
                "name": "1,4-Butanediol",
                "unit": "kg",
            },
        },
        {
            "comment": "Identical names",
            "conversion_factor": 1.2142857142857142,
            "source": {
                "context": "air/low. pop.",
                "name": "Ammonia, as N",
                "unit": "kg",
            },
            "target": {
                "CAS number": "7664-41-7",
                "context": ["air", "non-urban air or from high stacks"],
                "identifier": "0f440cc0-0f74-446d-99d6-8ff0e97a2444",
                "name": "Ammonia",
                "unit": "kg",
            },
        },
        {
            "comment": "Name matching with location code",
            "conversion_factor": 1.0,
            "source": {"context": "air/low. pop.", "name": "Ammonia, FR", "unit": "kg"},
            "target": {
                "CAS number": "7664-41-7",
                "context": ["air", "non-urban air or from high stacks"],
                "identifier": "0f440cc0-0f74-446d-99d6-8ff0e97a2444",
                "location": "FR",
                "name": "Ammonia",
                "unit": "kg",
            },
        },
    ]

    assert actual == expected
