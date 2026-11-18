"""Levels 3 and 4: key-level and row-hash reconciliation."""
import pandas as pd

from conftest import KEY


def test_L3_no_missing_keys(curated, fact):
    """Every non-cancelled curated key is in fact. Show how many are missing and a sample."""
    # raise NotImplementedError("TODO")
    expected_keys = curated.loc[curated["status"] != "CANCELLED", KEY].drop_duplicates()
    fact_keys = fact[KEY].drop_duplicates()
    comparison = expected_keys.merge(fact_keys, on=KEY, how="left", indicator=True)
    missing = comparison.loc[comparison["_merge"] == "left_only", KEY]
    if not missing.empty:
        print(f"Missing fact keys ({len(missing)}):")
        print(missing.to_string(index=False))
    assert missing.empty, (
        f"missing fact keys={len(missing)}, sample={missing.head(5).to_dict(orient='records')}"
    )


def test_L3_fact_grain_unique(fact):
    """No (order_id, line_no) appears twice in fact."""
    # raise NotImplementedError("TODO")
    duplicate_rows = fact.loc[fact.duplicated(subset=KEY, keep=False), KEY].sort_values(KEY)
    duplicates = duplicate_rows.drop_duplicates()
    if not duplicate_rows.empty:
        print(f"Duplicate fact key rows ({len(duplicate_rows)} rows):")
        print(duplicate_rows.to_string(index=False))
    assert duplicates.empty, (
        f"duplicate fact keys={len(duplicates)}, "
        f"sample={duplicates.head(5).to_dict(orient='records')}"
    )


def test_L4_row_hash(curated, fact):
    """For keys present in both, a hash of (order_id, line_no, order_date, customer_id, product_id, qty, amount)
    must match. Expected order_date is the UTC date of curated order_ts."""
    # raise NotImplementedError("TODO")
    hash_columns = KEY + ["order_date", "customer_id", "product_id", "qty", "amount"]

    expected = curated.loc[
        curated["status"] != "CANCELLED",
        KEY + ["order_ts", "customer_id", "product_id", "qty", "amount"],
    ].copy()
    expected["order_date"] = pd.to_datetime(expected["order_ts"], utc=True).dt.strftime("%Y-%m-%d")
    expected = expected[hash_columns]
    expected["row_hash"] = pd.util.hash_pandas_object(expected[hash_columns], index=False)

    actual = fact[hash_columns].copy()
    actual["row_hash"] = pd.util.hash_pandas_object(actual[hash_columns], index=False)

    comparison = expected[KEY + ["row_hash"]].drop_duplicates(subset=KEY).merge(
        actual[KEY + ["row_hash"]].drop_duplicates(subset=KEY),
        on=KEY,
        how="inner",
        suffixes=("_expected", "_actual"),
    )
    mismatches = comparison.loc[
        comparison["row_hash_expected"] != comparison["row_hash_actual"],
        KEY + ["row_hash_expected", "row_hash_actual"],
    ]
    if not mismatches.empty:
        print(f"Row-hash mismatches ({len(mismatches)}):")
        print(mismatches.to_string(index=False))
    assert mismatches.empty, (
        f"row hash mismatches={len(mismatches)}, "
        f"sample={mismatches[KEY].head(5).to_dict(orient='records')}"
    )
