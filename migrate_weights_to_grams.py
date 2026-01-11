"""
Migration helper: multiply weight fields by 1000 when values appear to be in kilograms (small values).
Usage:
  python migrate_weights_to_grams.py        # dry-run
  python migrate_weights_to_grams.py --apply
"""

from pymongo import MongoClient
import argparse

# 🔥 Explicit DB name + timeout
MONGO_URI = (
    "mongodb+srv://darpanmeher1346_db_user:E8kreTF6Z8G5mFbn"
    "@cluster0.mhkyevr.mongodb.net/ewaste_db"
    "?retryWrites=true&w=majority"
)

client = MongoClient(
    MONGO_URI,
    serverSelectionTimeoutMS=5000
)

# 🔥 Fail fast if Mongo is unreachable
client.admin.command("ping")

db = client["ewaste_db"]
pickups = db.pickup_requests

parser = argparse.ArgumentParser()
parser.add_argument('--apply', action='store_true', help='Apply changes (otherwise dry-run)')
args = parser.parse_args()

# Fields to consider
weight_fields = ['approx_weight', 'ewaste_weight', 'final_weight']

# Collect updates per document
updates = {}

for doc in pickups.find():
    doc_updates = {}
    for wf in weight_fields:
        val = doc.get(wf)
        try:
            num = float(val)
        except Exception:
            continue

        # Heuristic: kg → grams
        if 0 < num < 1000:
            doc_updates[wf] = num * 1000

    if doc_updates:
        updates[doc['_id']] = doc_updates

print(f'Found {sum(len(v) for v in updates.values())} candidate fields across {len(updates)} documents.')

if not args.apply:
    print('Dry run mode. Use --apply to perform updates.')
    shown = 0
    for _id, fields in updates.items():
        for f, v in fields.items():
            print(f'DOC {_id} {f} -> {v}')
            shown += 1
            if shown >= 50:
                break
        if shown >= 50:
            break
else:
    print('Applying updates...')
    updated = 0
    for _id, fields in updates.items():
        pickups.update_one({'_id': _id}, {'$set': fields})
        updated += len(fields)

    print(f'Updated {updated} fields.')

print('Done.')
