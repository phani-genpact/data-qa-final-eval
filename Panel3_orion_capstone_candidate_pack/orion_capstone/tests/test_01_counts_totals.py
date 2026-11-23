"""Levels 1 and 2: row counts and control totals."""


def test_L1_source_to_curated_rows(source, rejects, curated):
    """Source rows = curated rows + rejected rows."""
    # raise NotImplementedError("TODO")
    source_rows = len(source)
    loaded_and_rejected_rows = len(curated) + len(rejects)
    print(
        f"Source-to-curated counts: source={source_rows}, curated={len(curated)}, "
        f"rejects={len(rejects)}, curated+rejects={loaded_and_rejected_rows}, "
        f"difference={source_rows - loaded_and_rejected_rows}"
    )
    assert source_rows == loaded_and_rejected_rows, (
        f"source rows={source_rows}, curated rows={len(curated)}, "
        f"rejected rows={len(rejects)}, difference={source_rows - loaded_and_rejected_rows}"
    )


def test_L1_curated_to_fact_rows(curated, fact):
    """Fact rows = curated rows that are not CANCELLED."""
    # raise NotImplementedError("TODO")
    expected_rows = len(curated[curated["status"] != "CANCELLED"])
    actual_rows = len(fact)
    print(
        f"Curated-to-fact counts: expected={expected_rows}, actual={actual_rows}, "
        f"difference={actual_rows - expected_rows}"
    )
    assert actual_rows == expected_rows, (
        f"expected fact rows={expected_rows}, actual fact rows={actual_rows}, "
        f"difference={actual_rows - expected_rows}"
    )


def test_L2_curated_to_fact_revenue(curated, fact):
    """Fact revenue = revenue of the curated rows that are not CANCELLED (2 decimals)."""
    # raise NotImplementedError("TODO")
    active_curated = curated[curated["status"] != "CANCELLED"]
    expected_revenue = round(float(active_curated["amount"].sum()), 2)
    actual_revenue = round(float(fact["amount"].sum()), 2)
    print(
        f"Curated-to-fact revenue: expected={expected_revenue:.2f}, "
        f"actual={actual_revenue:.2f}, difference={actual_revenue - expected_revenue:.2f}"
    )
    assert actual_revenue == expected_revenue, (
        f"expected fact revenue={expected_revenue:.2f}, actual fact revenue={actual_revenue:.2f}, "
        f"difference={actual_revenue - expected_revenue:.2f}"
    )


def test_L2_source_to_report_tie_out(source, rejects, curated, rpt_daily):
    """Source revenue = report revenue + rejected revenue + cancelled revenue."""
    # raise NotImplementedError("TODO")
    source_revenue = round(float(source["amount"].sum()), 2)
    report_revenue = round(float(rpt_daily["revenue"].sum()), 2)
    rejected_revenue = round(float(rejects["amount"].sum()), 2)
    cancelled_revenue = round(
        float(curated.loc[curated["status"] == "CANCELLED", "amount"].sum()), 2
    )
    accounted_revenue = round(report_revenue + rejected_revenue + cancelled_revenue, 2)
    print(
        f"Source-to-report tie-out: source={source_revenue:.2f}, "
        f"report={report_revenue:.2f}, rejects={rejected_revenue:.2f}, "
        f"cancelled={cancelled_revenue:.2f}, accounted={accounted_revenue:.2f}, "
        f"difference={source_revenue - accounted_revenue:.2f}"
    )
    assert source_revenue == accounted_revenue, (
        f"source revenue={source_revenue:.2f}, report revenue={report_revenue:.2f}, "
        f"rejected revenue={rejected_revenue:.2f}, cancelled revenue={cancelled_revenue:.2f}, "
        f"accounted revenue={accounted_revenue:.2f}, "
        f"difference={source_revenue - accounted_revenue:.2f}"
    )
