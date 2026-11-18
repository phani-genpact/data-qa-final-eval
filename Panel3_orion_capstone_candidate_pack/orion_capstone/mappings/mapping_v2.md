# Orion Retail: Daily Regional Sales. Source-to-target mapping v2 (fictional)

Release note: source system release R2 changes order_lines. Changes against v1 are marked.

| Req | Rule | Change vs v1 |
| --- | --- | --- |
| REQ-01 | Reject a source line if qty <= 0 or gross_amount <= 0. | Modified (amount renamed to gross_amount) |
| REQ-02 | Cancelled lines stay in curated but are excluded from fact_sales. | Unchanged |
| REQ-03 | If customer_id is NULL, load with region = 'Unknown'. | Unchanged |
| REQ-04 | Region from dim_customer, is_current = 'Y', one current row per customer. | Unchanged |
| REQ-05 | order_date = UTC date of order_ts. | Unchanged |
| REQ-06 | agg_daily_region_sales: one row per order_date and region. orders = distinct order_id. revenue = SUM(net_revenue). | Modified (revenue is now net) |
| REQ-07 | Every product_id in fact_sales must exist in dim_product. | Unchanged |
| REQ-08 | Monthly AOV = SUM(revenue) / SUM(orders). | Unchanged |
| REQ-09 | Reports read from agg_daily_region_sales only. Every table carries batch_id. | Unchanged |
| REQ-10 | net_revenue = gross_amount - COALESCE(discount_amt, 0). discount_amt must be >= 0 and <= gross_amount, otherwise reject the line. | New |
| REQ-11 | currency must be 'INR'. Any other currency is rejected. | New |

Schema changes in source_order_lines: amount renamed to gross_amount; qty changes from int to decimal(10,3); new nullable column discount_amt; new column currency.
