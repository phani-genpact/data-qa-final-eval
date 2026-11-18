"""Shared fixtures. Complete the TODOs (Section B1)."""
from pathlib import Path

import pandas as pd
import pytest

DATA = Path(__file__).resolve().parent.parent / "data"
KEY = ["order_id", "line_no"]          # grain of curated and fact


# TODO B1: add one session-scoped fixture per file, returning a DataFrame.
# Names to use: source, rejects, curated, dim_customer, dim_product, fact, agg, rpt_daily, rpt_monthly
# Files: source_order_lines, reject_order_lines, curated_order_lines, dim_customer, dim_product,
#        fact_sales, agg_daily_region_sales, rpt_daily_region_sales, rpt_monthly_kpi  (all .csv)
# Parse order_ts as a datetime in source and curated.


@pytest.fixture(scope="session")
def source():
    """Load source rows and parse order timestamps."""
    return pd.read_csv(DATA / "source_order_lines.csv", parse_dates=["order_ts"])


@pytest.fixture(scope="session")
def rejects():
    """Load source rows rejected during cleaning."""
    return pd.read_csv(DATA / "reject_order_lines.csv")


@pytest.fixture(scope="session")
def curated():
    """Load curated rows and parse order timestamps."""
    return pd.read_csv(DATA / "curated_order_lines.csv", parse_dates=["order_ts"])


@pytest.fixture(scope="session")
def dim_customer():
    """Load customer dimension rows."""
    return pd.read_csv(DATA / "dim_customer.csv")


@pytest.fixture(scope="session")
def dim_product():
    """Load product dimension rows."""
    return pd.read_csv(DATA / "dim_product.csv")


@pytest.fixture(scope="session")
def fact():
    """Load sales fact rows."""
    return pd.read_csv(DATA / "fact_sales.csv")


@pytest.fixture(scope="session")
def agg():
    """Load daily regional aggregate rows."""
    return pd.read_csv(DATA / "agg_daily_region_sales.csv")


@pytest.fixture(scope="session")
def rpt_daily():
    """Load daily regional report rows."""
    return pd.read_csv(DATA / "rpt_daily_region_sales.csv")


@pytest.fixture(scope="session")
def rpt_monthly():
    """Load monthly KPI report rows."""
    return pd.read_csv(DATA / "rpt_monthly_kpi.csv")
