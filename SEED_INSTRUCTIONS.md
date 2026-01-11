# Seed Data Instructions for E-WASTE Database

All seed scripts now use **`ewaste_db`** database (changed from `e_waste`).

## Available Seed Scripts

### 1. **seed.py** (Original seed - basic demo)
Creates base users, pickup requests, clusters, and pricing data.

```bash
python seed.py
```

**Inserts:**
- 8 users (1 warehouse, 2 engineers, 2 drivers, 1 recycler, 1 regular user, 1 doctor)
- 10 pickup requests (status: pending, collected)
- 2 collection clusters
- Category prices and metal prices

---

### 2. **seed_more_demo.py** (Extended seed - advanced analytics)
Adds 3 more engineers, 5 recyclers, ~30 pickup requests, and multiple clusters.
All weights are in **grams**.

```bash
python seed_more_demo.py
```

**Inserts:**
- 3 additional engineers (engineer3, engineer4, engineer5)
- 5 recyclers (recycler1-5)
- ~30 pickup requests with random statuses (pending, collected, delivered, recycled, scheduled)
- 4 collection clusters with warehouse destinations

---

### 3. **database/create_demo_users.py** (User creation only)
Creates demo users if they don't already exist.

```bash
python database/create_demo_users.py
```

**Inserts:**
- Demo User (user role)
- Demo Admin (admin role)
- Demo Engineer (engineer role)
- Demo Warehouse (warehouse role)

---

### 4. **migrate_weights_to_grams.py** (Weight conversion utility)
Converts existing weight values from kilograms to grams using heuristic detection.

**Dry-run (preview changes):**
```bash
python migrate_weights_to_grams.py
```

**Apply migration:**
```bash
python migrate_weights_to_grams.py --apply
```

Detects values between 0-1000 and multiplies by 1000 to convert kg → grams.

---

## Recommended Workflow

1. **Initial Setup:**
   ```bash
   python seed.py                    # Basic data
   python seed_more_demo.py          # Advanced data
   ```

2. **Optional - Check weight conversion:**
   ```bash
   python migrate_weights_to_grams.py    # Preview
   python migrate_weights_to_grams.py --apply  # Apply if needed
   ```

3. **Run the app:**
   ```bash
   python app.py
   ```

4. **Login with demo credentials:**
   - **Warehouse:** warehouse@example.com / warehousepass
   - **Engineer:** engineer@example.com / password123
   - **Recycler:** recycler@example.com / password123
   - **Driver:** driver@example.com / password123
   - **User:** user@example.com / userpass

---

## Database Connection

All scripts use the environment variable `MONGO_URI`:
```bash
# Default (localhost)
python seed.py

# Custom MongoDB URI
set MONGO_URI=mongodb://your-host:27017/ewaste_db
python seed.py
```

If `MONGO_URI` is not set, scripts default to: `mongodb://localhost:27017/ewaste_db`

---

## Files Updated for ewaste_db

✅ seed.py  
✅ seed_more_demo.py  
✅ migrate_weights_to_grams.py  
✅ database/create_demo_users.py  
✅ database/mongo.py  
✅ app.py (main app.config["MONGO_URI"] already set to ewaste_db)

---

## Notes

- All weights in database are stored in **grams**, not kilograms
- Pickups created by seed_more_demo.py have realistic grams values (200-5000)
- Engineers, drivers, and recyclers can be assigned to clusters
- Hub inventory tracking is available for "delivered" and "completed" statuses
