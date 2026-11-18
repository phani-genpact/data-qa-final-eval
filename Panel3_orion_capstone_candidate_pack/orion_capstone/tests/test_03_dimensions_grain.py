"""Dimension and key checks (star schema)."""
import pandas as pd

from conftest import KEY


def test_dim_customer_one_current_row(dim_customer):
    """Exactly one is_current = 'Y' row per customer."""
    # raise NotImplementedError("TODO")
    customer_ids = dim_customer["customer_id"].dropna().drop_duplicates()
    current_counts = (
        dim_customer.loc[dim_customer["is_current"] == "Y"]
        .groupby("customer_id")
        .size()
        .reindex(customer_ids, fill_value=0)
    )
    invalid = current_counts[current_counts != 1]
    print(
        f"Customer current-row counts: customers={len(customer_ids)}, "
        f"current rows={int((dim_customer['is_current'] == 'Y').sum())}, "
        f"customers without exactly one current row={len(invalid)}"
    )
    if not invalid.empty:
        print("Customers with invalid current-row counts:")
        print(invalid.rename("current_row_count").to_string())
    assert invalid.empty, (
        f"customers without exactly one current row={len(invalid)}, "
        f"sample={invalid.head(5).to_dict()}"
    )


def test_dim_customer_no_overlap_or_gaps(dim_customer):
    """For each customer, valid_from/valid_to ranges must not overlap and must not leave gaps."""
    # raise NotImplementedError("TODO")
    ordered = dim_customer.copy()
    ordered["valid_from"] = pd.to_datetime(ordered["valid_from"])
    ordered["valid_to"] = pd.to_datetime(ordered["valid_to"])
    ordered = ordered.sort_values(["customer_id", "valid_from"])
    ordered["previous_valid_to"] = ordered.groupby("customer_id")["valid_to"].shift()
    transitions = ordered.loc[ordered["previous_valid_to"].notna()].copy()
    overlaps = transitions.loc[transitions["valid_from"] <= transitions["previous_valid_to"]]
    gaps = transitions.loc[
        transitions["valid_from"] > transitions["previous_valid_to"] + pd.Timedelta(days=1)
    ]
    print(
        f"Customer validity ranges: customers={dim_customer['customer_id'].nunique()}, "
        f"transitions={len(transitions)}, overlaps={len(overlaps)}, gaps={len(gaps)}"
    )
    if not overlaps.empty:
        print("Overlapping customer validity ranges:")
        print(
            overlaps[["customer_id", "previous_valid_to", "valid_from"]]
            .to_string(index=False)
        )
    if not gaps.empty:
        print("Customer validity range gaps:")
        print(
            gaps[["customer_id", "previous_valid_to", "valid_from"]]
            .to_string(index=False)
        )
    assert overlaps.empty and gaps.empty, (
        f"overlapping ranges={len(overlaps)}, sample="
        f"{overlaps[['customer_id', 'previous_valid_to', 'valid_from']].head(5).to_dict(orient='records')}; "
        f"gaps={len(gaps)}, sample="
        f"{gaps[['customer_id', 'previous_valid_to', 'valid_from']].head(5).to_dict(orient='records')}"
    )


def test_fact_products_in_dim(fact, dim_product):
    """Every fact product_id exists in dim_product."""
    # raise NotImplementedError("TODO")
    product_ids = dim_product["product_id"].dropna().unique()
    missing_mask = fact["product_id"].isna() | ~fact["product_id"].isin(product_ids)
    missing = fact.loc[missing_mask, KEY + ["product_id"]]
    print(
        f"Fact product check: fact rows={len(fact)}, "
        f"dimension products={len(product_ids)}, missing product rows={len(missing)}"
    )
    if not missing.empty:
        print("Fact rows with missing product IDs:")
        print(missing.to_string(index=False))
    assert missing.empty, (
        f"fact rows with missing product IDs={len(missing)}, "
        f"sample={missing.head(5).to_dict(orient='records')}"
    )


def test_null_customers_map_to_unknown(curated, fact):
    """REQ-03: non-cancelled lines with a NULL customer_id are in fact with region = 'Unknown'."""
    # raise NotImplementedError("TODO")
    eligible = curated.loc[
        (curated["status"] != "CANCELLED") & curated["customer_id"].isna(), KEY
    ].drop_duplicates()
    comparison = eligible.merge(
        fact[KEY + ["region"]], on=KEY, how="left", indicator=True
    )
    missing = comparison.loc[comparison["_merge"] == "left_only", KEY]
    wrong_region = comparison.loc[
        (comparison["_merge"] == "both") & (comparison["region"] != "Unknown"),
        KEY + ["region"],
    ]
    print(
        f"NULL-customer check: eligible lines={len(eligible)}, "
        f"missing fact lines={len(missing)}, lines without Unknown region={len(wrong_region)}"
    )
    if not missing.empty:
        print("NULL-customer lines missing from fact:")
        print(missing.to_string(index=False))
    if not wrong_region.empty:
        print("NULL-customer fact lines with a non-Unknown region:")
        print(wrong_region.to_string(index=False))
    assert missing.empty and wrong_region.empty, (
        f"missing fact lines={len(missing)}, "
        f"sample={missing.head(5).to_dict(orient='records')}; "
        f"wrong-region lines={len(wrong_region)}, "
        f"sample={wrong_region.head(5).to_dict(orient='records')}"
    )
