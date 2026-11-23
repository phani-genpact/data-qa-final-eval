"""Aggregation and report checks."""
import pandas as pd


def test_agg_one_row_per_date_region(agg):
    """Ensure each date and region has one aggregate row."""
    # raise NotImplementedError("TODO")
    grain = ["order_date", "region"]
    duplicate_rows = agg.loc[agg.duplicated(subset=grain, keep=False)].sort_values(grain)
    duplicate_groups = duplicate_rows[grain].drop_duplicates()
    print(
        f"Aggregate grain check: aggregate rows={len(agg)}, "
        f"duplicate groups={len(duplicate_groups)}, duplicate rows={len(duplicate_rows)}"
    )
    if not duplicate_rows.empty:
        print("Duplicate date/region rows:")
        print(duplicate_rows.to_string(index=False))
    assert duplicate_groups.empty, (
        f"duplicate date/region groups={len(duplicate_groups)}, "
        f"sample={duplicate_groups.head(5).to_dict(orient='records')}"
    )


def test_agg_total_equals_fact_total(agg, fact):
    """Reconcile aggregate order and revenue totals with fact totals."""
    # raise NotImplementedError("TODO")
    aggregate_orders = int(agg["orders"].sum())
    fact_orders = int(fact["order_id"].nunique())
    aggregate_revenue = round(float(agg["revenue"].sum()), 2)
    fact_revenue = round(float(fact["amount"].sum()), 2)
    print(
        f"Aggregate-to-fact totals: aggregate orders={aggregate_orders}, "
        f"fact distinct orders={fact_orders}, aggregate revenue={aggregate_revenue:.2f}, "
        f"fact revenue={fact_revenue:.2f}"
    )
    assert aggregate_orders == fact_orders and aggregate_revenue == fact_revenue, (
        f"orders: aggregate={aggregate_orders}, fact distinct={fact_orders}, "
        f"difference={aggregate_orders - fact_orders}; "
        f"revenue: aggregate={aggregate_revenue:.2f}, fact={fact_revenue:.2f}, "
        f"difference={aggregate_revenue - fact_revenue:.2f}"
    )


def test_agg_recompute_from_curated(curated, dim_customer, agg):
    """Rebuild orders and revenue per (order_date, region) from curated and compare with agg (outer join, flag every difference)."""
    # raise NotImplementedError("TODO")
    active = curated.loc[curated["status"] != "CANCELLED"].copy()
    active["order_date"] = pd.to_datetime(active["order_ts"], utc=True).dt.strftime("%Y-%m-%d")
    current_customers = dim_customer.loc[
        dim_customer["is_current"] == "Y", ["customer_id", "region"]
    ]
    enriched = active.merge(current_customers, on="customer_id", how="left")
    null_customer_rows = enriched["customer_id"].isna()
    enriched.loc[null_customer_rows, "region"] = "Unknown"
    unmapped = enriched.loc[
        ~null_customer_rows & enriched["region"].isna(),
        ["order_id", "line_no", "customer_id"],
    ]
    expected = (
        enriched.groupby(["order_date", "region"], dropna=False)
        .agg(orders=("order_id", "nunique"), revenue=("amount", "sum"))
        .reset_index()
    )
    comparison = expected.merge(
        agg[["order_date", "region", "orders", "revenue"]],
        on=["order_date", "region"],
        how="outer",
        suffixes=("_expected", "_actual"),
        indicator=True,
    )
    order_mismatch = comparison["orders_expected"].ne(comparison["orders_actual"]).fillna(True)
    revenue_mismatch = (
        comparison["revenue_expected"].round(2).ne(comparison["revenue_actual"].round(2)).fillna(True)
    )
    mismatches = comparison.loc[
        comparison["_merge"].ne("both") | order_mismatch | revenue_mismatch
    ]
    print(
        f"Curated-to-aggregate recomputation: expected groups={len(expected)}, "
        f"aggregate groups={len(agg)}, expected orders={int(expected['orders'].sum())}, "
        f"aggregate orders={int(agg['orders'].sum())}, "
        f"expected revenue={expected['revenue'].sum():.2f}, "
        f"aggregate revenue={agg['revenue'].sum():.2f}, "
        f"mismatched groups={len(mismatches)}, unmapped customer lines={len(unmapped)}"
    )
    if not unmapped.empty:
        print("Active curated lines without a current customer-dimension match:")
        print(unmapped.to_string(index=False))
    if not mismatches.empty:
        print("Aggregate groups missing, extra, or with different totals:")
        print(mismatches.to_string(index=False))
    assert mismatches.empty and unmapped.empty, (
        f"mismatched aggregate groups={len(mismatches)}, "
        f"sample={mismatches.head(5).to_dict(orient='records')}; "
        f"unmapped customer lines={len(unmapped)}, "
        f"sample={unmapped.head(5).to_dict(orient='records')}"
    )


def test_report_equals_agg(agg, rpt_daily):
    """Compare every daily report group with its aggregate group."""
    # raise NotImplementedError("TODO")
    report = rpt_daily.rename(columns={"report_date": "order_date"})
    comparison = agg[["order_date", "region", "orders", "revenue"]].merge(
        report[["order_date", "region", "orders", "revenue"]],
        on=["order_date", "region"],
        how="outer",
        suffixes=("_aggregate", "_report"),
        indicator=True,
    )
    orders_mismatch = comparison["orders_aggregate"].ne(comparison["orders_report"]).fillna(True)
    revenue_mismatch = (
        comparison["revenue_aggregate"].round(2).ne(comparison["revenue_report"].round(2)).fillna(True)
    )
    mismatches = comparison.loc[
        comparison["_merge"].ne("both") | orders_mismatch | revenue_mismatch
    ]
    print(
        f"Daily report reconciliation: aggregate rows={len(agg)}, report rows={len(rpt_daily)}, "
        f"aggregate orders={int(agg['orders'].sum())}, report orders={int(rpt_daily['orders'].sum())}, "
        f"aggregate revenue={agg['revenue'].sum():.2f}, "
        f"report revenue={rpt_daily['revenue'].sum():.2f}, "
        f"missing/extra/different groups={len(mismatches)}"
    )
    if not mismatches.empty:
        print("Daily report groups missing, extra, or with different totals:")
        print(mismatches.to_string(index=False))
    assert mismatches.empty, (
        f"report/aggregate mismatches={len(mismatches)}, "
        f"sample={mismatches.head(5).to_dict(orient='records')}"
    )


def test_monthly_aov_recompute(rpt_daily, rpt_monthly):
    """REQ-08: monthly AOV = SUM(revenue) / SUM(orders) from the daily report rows."""
    # raise NotImplementedError("TODO")
    daily = rpt_daily.copy()
    daily["month"] = pd.to_datetime(daily["report_date"]).dt.strftime("%Y-%m")
    expected = daily.groupby("month").agg(
        orders=("orders", "sum"),
        revenue=("revenue", "sum"),
    )
    expected["avg_order_value"] = (expected["revenue"] / expected["orders"]).round(2)
    expected = expected.reset_index()
    comparison = expected[["month", "avg_order_value"]].merge(
        rpt_monthly[["month", "avg_order_value"]],
        on="month",
        how="outer",
        suffixes=("_expected", "_actual"),
        indicator=True,
    )
    aov_mismatch = comparison["avg_order_value_expected"].round(2).ne(
        comparison["avg_order_value_actual"].round(2)
    ).fillna(True)
    mismatches = comparison.loc[comparison["_merge"].ne("both") | aov_mismatch]
    print(
        f"Monthly AOV reconciliation: recomputed months={len(expected)}, "
        f"reported months={len(rpt_monthly)}, "
        f"expected values={expected[['month', 'orders', 'revenue', 'avg_order_value']].to_dict(orient='records')}, "
        f"reported values={rpt_monthly[['month', 'orders', 'revenue', 'avg_order_value']].to_dict(orient='records')}, "
        f"missing/extra/different months={len(mismatches)}"
    )
    if not mismatches.empty:
        print("Monthly AOV mismatches:")
        print(mismatches.to_string(index=False))
    assert mismatches.empty, (
        f"monthly AOV mismatches={len(mismatches)}, "
        f"sample={mismatches.head(5).to_dict(orient='records')}"
    )
