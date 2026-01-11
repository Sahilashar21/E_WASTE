"""
Migration helper: multiply weight fields by 1000 when values appear to be in kilograms (small values).
Usage:
  python migrate_weights_to_grams.py        # dry-run: shows candidate updates
  python migrate_weights_to_grams.py --apply
"""
from pymongo import MongoClient
import os
import argparse

MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/ewaste_db')
client = MongoClient(MONGO_URI)
db = client['ewaste_db']
pickups = db.pickup_requests

parser = argparse.ArgumentParser()
parser.add_argument('--apply', action='store_true', help='Apply changes (otherwise dry-run)')
args = parser.parse_args()

# Fields to consider
weight_fields = ['approx_weight', 'ewaste_weight', 'final_weight']

# Heuristic: if a weight field exists and value is >0 and <1000, assume it's in kg and convert to grams
candidates = []
for wf in weight_fields:
    for doc in pickups.find({wf: {'$exists': True, '$ne': None}}):
        val = doc.get(wf)
        try:
            num = float(val)
        except Exception:
            continue
        if 0 < num < 1000:
            candidates.append((str(doc['_id']), wf, num))

print(f'Found {len(candidates)} candidate weight fields that look like kg-values (0 < val < 1000).')
if not args.apply:
    print('Dry run mode. Use --apply to perform updates.')
    for cid, field, val in candidates[:50]:
        print(f'DOC {cid} {field}={val} -> will become {val*1000}')
else:
    print('Applying updates...')
    updated = 0
    for cid, field, val in candidates:
        pickups.update_one({'_id': cid}, {'$set': {field: val * 1000}})
        updated += 1
    print(f'Updated {updated} fields.')

print('Done.')
