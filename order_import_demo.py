"""Synthetic order-import validation sample, Mark Zhang, September 2026.
Python standard library only. Not a client deployment or accounting system.
Run: python order_import_demo.py --self-test
     python order_import_demo.py orders.csv
Outputs a JSON validation report. Exit 2 means review is required.
Conflicting order/SKU rows are all excluded; currencies are never added together.
No files are modified, no network requests are made, no orders are submitted.
"""
import csv, io, json, re, sys, unittest
from decimal import Decimal

REQUIRED = ('order_id', 'sku', 'quantity', 'unit_price', 'currency')

def validate(text):
    reader = csv.DictReader(io.StringIO(text.lstrip('\ufeff')), strict=True)
    fields = reader.fieldnames or []
    if set(fields) != set(REQUIRED) or len(fields) != len(REQUIRED):
        raise ValueError('Header must contain each required column exactly once: ' + ', '.join(REQUIRED))
    by_key, conflicts, errors, duplicates = {}, set(), [], []
    for number, raw in enumerate(reader, 2):
        if None in raw or any(raw.get(k) is None for k in REQUIRED):
            errors.append({'row': number, 'reason': 'Incorrect number of fields'})
            continue
        row = {k: raw[k].strip() for k in REQUIRED}
        order, sku = row['order_id'], row['sku']
        key = (order, sku)
        if not all(re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,63}', v) for v in key):
            errors.append({'row': number, 'reason': 'Invalid or empty order_id/sku'})
            continue
        valid = (re.fullmatch(r'[1-9][0-9]{0,6}', row['quantity'])
                 and re.fullmatch(r'[0-9]{1,10}(\.[0-9]{1,2})?', row['unit_price'])
                 and row['currency'] in ('CAD', 'USD', 'CNY'))
        if not valid:
            conflicts.add(key)
            errors.append({'row': number, 'reason': 'Invalid quantity, price or currency; this order/SKU is held'})
            continue
        row['quantity'] = int(row['quantity'])
        row['unit_price'] = format(Decimal(row['unit_price']), '.2f')
        if key in by_key:
            if row == by_key[key]['data']:
                duplicates.append(number)
            else:
                conflicts.add(key)
                errors.append({'row': number, 'reason': 'Conflicting order/SKU; all versions are held'})
        else:
            by_key[key] = {'row': number, 'data': row}
    accepted, totals = [], {}
    for key, item in by_key.items():
        if key in conflicts:
            continue
        row = item['data']
        accepted.append(row)
        cur = row['currency']
        totals[cur] = totals.get(cur, Decimal(0)) + row['quantity'] * Decimal(row['unit_price'])
    return {'ready': not errors, 'accepted_rows': accepted,
            'duplicate_rows_skipped': duplicates, 'held_keys': [list(k) for k in sorted(conflicts)],
            'errors': errors, 'totals_by_currency': {k: format(v, '.2f') for k, v in sorted(totals.items())},
            'scope': 'Line totals only; tax, discounts, freight and live writes are excluded.'}

HEADER = ','.join(REQUIRED) + '\n'
class AcceptanceChecks(unittest.TestCase):
    def check(self, rows):
        return validate(HEADER + rows)
    def test_exact_decimal_and_currency_separation(self):
        r = self.check('A,0007,3,0.10,CAD\nB,0007,2,2.50,USD\n')
        self.assertEqual(r['totals_by_currency'], {'CAD': '0.30', 'USD': '5.00'})
        self.assertEqual(r['accepted_rows'][0]['sku'], '0007')
    def test_duplicate_does_not_double_count(self):
        r = self.check('A,X,2,1.20,CAD\nA,X,2,1.2,CAD\n')
        self.assertEqual(r['totals_by_currency'], {'CAD': '2.40'})
        self.assertEqual(r['duplicate_rows_skipped'], [3])
    def test_conflict_holds_original_and_later_versions(self):
        r = self.check('A,X,2,1,CAD\nA,X,3,1,CAD\nA,X,2,1,CAD\n')
        self.assertFalse(r['ready'])
        self.assertEqual(r['accepted_rows'], [])
        self.assertEqual(r['held_keys'], [['A','X']])
    def test_invalid_later_row_holds_valid_original(self):
        r = self.check('A,X,1,5,CAD\nA,X,NaN,5,CAD\nB,Y,1,4,CAD\n')
        self.assertFalse(r['ready'])
        self.assertEqual(r['totals_by_currency'], {'CAD':'4.00'})
    def test_invalid_values_are_rejected(self):
        for fields in [('A','X','-1','5','CAD'),('A','X','1','NaN','CAD'),
                       ('A','X','1','1.999','CAD'),('A','X','1','5','ZZZ'),
                       ('=SUM(1)','X','1','5','CAD')]:
            with self.subTest(fields=fields):
                r = self.check(','.join(fields)+'\n')
                self.assertFalse(r['ready'])
                self.assertEqual(r['accepted_rows'], [])
    def test_broken_schema_fails(self):
        for s in ['order_id,sku\nA,B\n','order_id,sku,quantity,unit_price,currency,currency\n']:
            with self.assertRaises(ValueError): validate(s)
    def test_multiline_csv_and_bom_are_parsed(self):
        r = validate('\ufeff'+HEADER+'A,"X\nY",1,5,CAD\n')
        self.assertFalse(r['ready'])
        self.assertEqual(len(r['errors']), 1)
    def test_empty_data_is_a_valid_noop(self):
        r = validate(HEADER)
        self.assertTrue(r['ready'])
        self.assertEqual(r['accepted_rows'], [])

if __name__ == '__main__':
    if sys.argv[1:] == ['--self-test']:
        unittest.main(argv=[sys.argv[0]], verbosity=2)
    elif len(sys.argv) == 2:
        try:
            with open(sys.argv[1], encoding='utf-8-sig', newline='') as f:
                report = validate(f.read())
            print(json.dumps(report, indent=2, ensure_ascii=False))
            raise SystemExit(0 if report['ready'] else 2)
        except (OSError, ValueError, csv.Error) as exc:
            print(json.dumps({'ready': False, 'error': str(exc)}))
            raise SystemExit(2)
    else:
        print('Usage: python order_import_demo.py --self-test | orders.csv', file=sys.stderr)
        raise SystemExit(2)
