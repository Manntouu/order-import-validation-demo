# Order import validation sample
Synthetic data only. A small Python sample for proposed software support, not a commissioned client deliverable.

Run `python order_import_demo.py --self-test`, then `python order_import_demo.py orders.csv`.
The example returns exit 2 intentionally: DEMO-03 has conflicting quantities and needs review. DEMO-01 is counted once, with CAD 0.30; DEMO-02 has USD 5.00. Currency totals stay separate. No input file or live system is changed.

The eight acceptance checks cover decimal totals, leading-zero SKU preservation, duplicate rows, conflicts, invalid values, malformed headers, CSV parsing and empty input. This is an in-memory, small-file example. It does not implement a database transaction, multi-worker deduplication, ERP integration, tax calculations, XLSX reading or production deployment. Those need the buyer's agreed schema and acceptance criteria.

The code was developed with AI assistance and checked by executing the included tests. No human production review is claimed.
