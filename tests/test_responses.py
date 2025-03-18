import glob
import os
import pytest
from pathlib import Path
from typing import Dict, Any

# These will be imported from the schemas repository
from schemas.python.can_frame import CANIDFormat
from schemas.python.json_formatter import format_file
from schemas.python.signals_testing import obd_testrunner_by_year

REPO_ROOT = Path(__file__).parent.parent.absolute()

TEST_CASES = [
    {
        "model_year": 2020,
        "tests": [
            # Tire pressures
            ("72E056228130300", {"TRANSITC_TP_FL": 38.4}),
            ("72E0562281303EF", {"TRANSITC_TP_FL": 50.35}),
            ("72E056228140308", {"TRANSITC_TP_FR": 38.8}),
            ("72E0562281403D4", {"TRANSITC_TP_FR": 49}),
            ("72E056228150308", {"TRANSITC_TP_RR": 38.8}),
            ("72E0562281503DB", {"TRANSITC_TP_RR": 49.35}),
            ("72E056228160300", {"TRANSITC_TP_RL": 38.4}),
            ("72E0562281603CF", {"TRANSITC_TP_RL": 48.75}),

            # Gear
            ("7E804621E1201", {"TRANSITC_GEAR": "1"}),
            ("7E804621E1202", {"TRANSITC_GEAR": "2"}),
            ("7E804621E1203", {"TRANSITC_GEAR": "3"}),
            ("7E804621E1204", {"TRANSITC_GEAR": "4"}),
            ("7E804621E1205", {"TRANSITC_GEAR": "5"}),
            ("7E804621E1206", {"TRANSITC_GEAR": "6"}),
            ("7E804621E1207", {"TRANSITC_GEAR": "7"}),
            ("7E804621E1208", {"TRANSITC_GEAR": "8"}),
            ("7E804621E123C", {"TRANSITC_GEAR": None}),  # TODO: What gear is this?
            ("7E804621E1246", {"TRANSITC_GEAR": None}),  # TODO: What gear is this?
        ]
    },
]

@pytest.mark.parametrize(
    "test_group",
    TEST_CASES,
    ids=lambda test_case: f"MY{test_case['model_year']}"
)
def test_signals(test_group: Dict[str, Any]):
    """Test signal decoding against known responses."""
    # Run each test case in the group
    for response_hex, expected_values in test_group["tests"]:
        try:
            obd_testrunner_by_year(
                test_group['model_year'],
                response_hex,
                expected_values,
                can_id_format=CANIDFormat.ELEVEN_BIT
            )
        except Exception as e:
            pytest.fail(
                f"Failed on response {response_hex} "
                f"(Model Year: {test_group['model_year']}: {e}"
            )

def get_json_files():
    """Get all JSON files from the signalsets/v3 directory."""
    signalsets_path = os.path.join(REPO_ROOT, 'signalsets', 'v3')
    json_files = glob.glob(os.path.join(signalsets_path, '*.json'))
    # Convert full paths to relative filenames
    return [os.path.basename(f) for f in json_files]

@pytest.mark.parametrize("test_file",
    get_json_files(),
    ids=lambda x: x.split('.')[0].replace('-', '_')  # Create readable test IDs
)
def test_formatting(test_file):
    """Test signal set formatting for all vehicle models in signalsets/v3/."""
    signalset_path = os.path.join(REPO_ROOT, 'signalsets', 'v3', test_file)

    formatted = format_file(signalset_path)

    with open(signalset_path) as f:
        assert f.read() == formatted

if __name__ == '__main__':
    pytest.main([__file__])
