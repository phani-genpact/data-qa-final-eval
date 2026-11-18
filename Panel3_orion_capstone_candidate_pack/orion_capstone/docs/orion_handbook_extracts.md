# Orion Data Platform Operations Handbook: extracts (fictional)

## S1 Nightly load
The nightly batch load of the sales mart starts at 01:00 UTC and must complete by 05:00 UTC. If the load has not completed by 05:00 UTC, the on-call engineer is paged and the 06:00 UTC dashboard refresh is postponed until the load succeeds.

## S5 Data quality gates
Every curated table must pass three automated checks before it is published: row-count reconciliation against source (tolerance 0.5%), a null check on primary key columns (no nulls allowed), and a duplicate check on primary keys (no duplicates allowed). A table that fails any check is quarantined and not published.

## S6 Reruns and backfills
A rerun of a failed load must be approved by the on-call lead. A backfill of more than 7 days of data needs a change ticket and must run after 20:00 UTC.

## S7 Test environments
Non-production environments must use masked data. Customer names, email addresses and phone numbers are replaced with tokens during the copy to non-production. Unmasked production data must never be loaded into a test environment.

## S8 Releases
Schema changes are released on Tuesdays and Thursdays only, after peer review by two engineers. Emergency changes need approval from the platform lead.
