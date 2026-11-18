# Orion Retail: Daily Regional Sales. Source-to-target mapping v1 (fictional)

Pipeline: source_order_lines -> curated_order_lines (+ reject_order_lines) -> fact_sales -> agg_daily_region_sales -> reports.
Grain of fact_sales: one row per order line (order_id, line_no).

| Req | Rule |
| --- | --- |
| REQ-01 | Reject a source line if qty <= 0 or amount <= 0. Rejected lines go to reject_order_lines with a reason. All other lines load to curated_order_lines. |
| REQ-02 | Cancelled lines (status = CANCELLED) stay in curated but are excluded from fact_sales. |
| REQ-03 | If customer_id is NULL, load the line with region = 'Unknown'. Do not drop it. |
| REQ-04 | Region comes from dim_customer (SCD Type 2) using the row where is_current = 'Y'. Exactly one current row per customer. |
| REQ-05 | order_date = the UTC date of order_ts. |
| REQ-06 | agg_daily_region_sales: one row per order_date and region. orders = distinct order_id. revenue = SUM(amount). |
| REQ-07 | Every product_id in fact_sales must exist in dim_product. |
| REQ-08 | Monthly average order value (AOV) = SUM(revenue) / SUM(orders) for the month. Never average daily AOVs. |
| REQ-09 | Reports read from agg_daily_region_sales only. Every table carries batch_id. |
