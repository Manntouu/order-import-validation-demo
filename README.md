# Order import validation sample
Synthetic data only. A small Python sample for proposed software support, not a commissioned client deliverable.

Run `python order_import_demo.py --self-test`, then `python order_import_demo.py orders.csv`.
The example returns exit 2 intentionally: DEMO-03 has conflicting quantities and needs review. DEMO-01 is counted once, with CAD 0.30; DEMO-02 has USD 5.00. Currency totals stay separate. No input file or live system is changed.

The eight acceptance checks cover decimal totals, leading-zero SKU preservation, duplicate rows, conflicts, invalid values, malformed headers, CSV parsing and empty input. This is an in-memory, small-file example. It does not implement a database transaction, multi-worker deduplication, ERP integration, tax calculations, XLSX reading or production deployment. Those need the buyer's agreed schema and acceptance criteria.

The code was developed with AI assistance and checked by executing the included tests. No human production review is claimed.

## Fixed-scope paid pilot

For one agreed order CSV schema (up to 1,000 rows), the pilot price is USD 250. You provide a redacted header, representative rows, and the rules for accepting or holding a row. I deliver a runnable validator, a JSON exception report, automated checks for the agreed failure cases, and a short handoff. Target turnaround is two business days after the sample and rules are agreed. No live credentials or production write access are needed.

Email **northharbor5090@proton.me** with the subject **Order CSV preflight** and include the header, five redacted sample rows, and one example of a row you would reject. We will agree the exact scope, acceptance criteria, payment milestone, and deadline in writing before work starts. This repository is a synthetic capability demo, not previous client work.
