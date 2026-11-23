"""Schema contract and drift checks (Section D2)."""
import json
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent


def load_schema(version):
    """Load the source schema contract for a version."""
    return json.loads((ROOT / "schemas" / f"source_order_lines.{version}.json").read_text())


def diff_schemas(old, new):
    """Report added, removed, type-changed, and nullability-changed columns."""
    old_columns = {column["name"]: column for column in old["columns"]}
    new_columns = {column["name"]: column for column in new["columns"]}
    common = old_columns.keys() & new_columns.keys()
    return {
        "added": [name for name in new_columns if name not in old_columns],
        "removed": [name for name in old_columns if name not in new_columns],
        "type_changed": [
            name for name in old_columns if name in common
            and old_columns[name]["type"] != new_columns[name]["type"]
        ],
        "nullability_changed": [
            name for name in old_columns if name in common
            and old_columns[name]["nullable"] != new_columns[name]["nullable"]
        ],
    }


@pytest.mark.parametrize(
    ("version", "filename"),
    [
        ("v1", "source_order_lines.csv"),
        ("v2", "source_order_lines_v2_sample.csv"),
    ],
)
def test_csv_header_matches_schema(version, filename):
    """Verify a source CSV header matches its schema contract."""
    schema = load_schema(version)
    expected = [column["name"] for column in schema["columns"]]
    actual = pd.read_csv(ROOT / "data" / filename, nrows=0).columns.tolist()
    missing = sorted(set(expected) - set(actual))
    extra = sorted(set(actual) - set(expected))
    print(
        f"{filename} header: expected columns={len(expected)}, actual columns={len(actual)}, "
        f"missing={missing}, extra={extra}, order_matches={actual == expected}"
    )
    assert actual == expected, (
        f"{filename} header does not match {version} schema: "
        f"missing={missing}, extra={extra}, expected order={expected}, actual order={actual}"
    )


def test_schema_upgrade_has_no_breaking_changes():
    """Fail if the upgrade removes a column or changes an existing type."""
    changes = diff_schemas(load_schema("v1"), load_schema("v2"))
    breaking = {
        "removed": changes["removed"],
        "type_changed": changes["type_changed"],
    }
    print(
        f"Schema changes: added={len(changes['added'])} {changes['added']}, "
        f"removed={len(changes['removed'])} {changes['removed']}, "
        f"type_changed={len(changes['type_changed'])} {changes['type_changed']}, "
        f"nullability_changed={len(changes['nullability_changed'])} "
        f"{changes['nullability_changed']}"
    )
    assert not breaking["removed"] and not breaking["type_changed"], (
        f"breaking schema changes: removed={breaking['removed']}, "
        f"type_changed={breaking['type_changed']}; additive columns are allowed"
    )
