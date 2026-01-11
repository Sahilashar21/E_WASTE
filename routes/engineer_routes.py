from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from bson import ObjectId
from datetime import datetime
from mongo import mongo
try:
    from services.pricing_engine import calculate_final_price
except Exception:
    # Fallback to top-level pricing_engine if services package import fails
    from pricing_engine import calculate_final_price

engineer_bp = Blueprint("engineer", __name__)

# ---------------- DASHBOARD ----------------
@engineer_bp.route("/engineer/dashboard")
def dashboard():
    if session.get("role") != "engineer":
        return redirect("/")

    engineer_id = session["user_id"]
    
    # 1. Find clusters assigned to this engineer
    assigned_clusters = list(mongo.db.collection_clusters.find({
        "engineer_id": engineer_id
    }))
    
    # 2. Get individual pickups from these clusters
    pickup_ids = []
    for c in assigned_clusters:
        for u in c.get("users", []):
            pickup_ids.append(u["user_id"])
            
    # 3. Fetch pickup details grouped by cluster
    clusters_with_pickups = []
    for c in assigned_clusters:
        u_ids = [u['user_id'] for u in c.get('users', [])]
        pickup_docs = []
        if u_ids:
            pickup_docs = list(mongo.db.pickup_requests.find({'_id': {'$in': u_ids}}))

        # Attach driver and doctor info
        driver = None
        doctor = None
        if c.get('driver_id'):
            driver = mongo.db.users.find_one({'_id': ObjectId(c['driver_id'])}) if ObjectId.is_valid(c['driver_id']) else None
        if c.get('doctor_id'):
            doctor = mongo.db.users.find_one({'_id': ObjectId(c['doctor_id'])}) if ObjectId.is_valid(c['doctor_id']) else None

        c['_id_str'] = str(c.get('_id'))
        clusters_with_pickups.append({
            'cluster': c,
            'pickups': pickup_docs,
            'driver': driver,
            'doctor': doctor
        })

    return render_template(
        "engineer/engineer_dashboard.html",
        pickups=[],
        my_jobs=clusters_with_pickups
    )


# ---------------- AVAILABILITY SETTINGS ----------------
@engineer_bp.route("/engineer/availability", methods=["GET", "POST"])
def availability_settings():
    if session.get("role") != "engineer":
        return redirect("/")
    
    engineer_id = session["user_id"]
    
    if request.method == "POST":
        # Update engineer availability
        is_available = request.form.get("available_tomorrow") == "on"
        
        mongo.db.users.update_one(
            {"_id": ObjectId(engineer_id)},
            {"$set": {
                "available_tomorrow": is_available,
                "availability_updated_at": datetime.utcnow()
            }}
        )
        
        return redirect(url_for("engineer.dashboard"))
    
    # Fetch current engineer availability
    engineer = mongo.db.users.find_one({"_id": ObjectId(engineer_id)})
    is_available = engineer.get("available_tomorrow", True) if engineer else True
    
    return render_template("engineer/availability.html", is_available=is_available)


# ---------------- INSPECTION PAGE ----------------
@engineer_bp.route("/engineer/inspect/<pickup_id>")
def inspect_pickup(pickup_id):
    pickup = mongo.db.pickup_requests.find_one({"_id": ObjectId(pickup_id)})
    return render_template(
        "engineer/inspect_new.html",
        pickup=pickup
    )


# ---------------- LIVE PRICE API ----------------
@engineer_bp.route("/engineer/calculate-price", methods=["POST"])
def calculate_price_api():
    data = request.json
    
    # Convert grams to kg for pricing engine
    weight_kg = float(data["weight"]) / 1000 if float(data["weight"]) > 0 else 0

    pricing = calculate_final_price(
        category=data["category"],
        weight=weight_kg,
        condition=data["condition"],
        age_years=int(data["age_years"])
    )

    return jsonify(pricing)


# ---------------- FINAL SUBMISSION ----------------
@engineer_bp.route("/engineer/submit/<pickup_id>", methods=["POST"])
def submit_inspection(pickup_id):
    if session.get("role") != "engineer":
        return jsonify({"error": "Unauthorized"}), 401

    payload = request.json
    final_price = payload.get("total_price")

    # Update pickup request with final price and status
    mongo.db.pickup_requests.update_one(
        {"_id": ObjectId(pickup_id)},
        {"$set": {
            "status": "collected", # Mark as collected after inspection
            "engineer_price": final_price,
            "inspected_at": datetime.utcnow()
        }}
    )

    return jsonify({"success": True})

# ---------------- COMPLETE CLUSTER (Legacy Support) ----------------
@engineer_bp.route('/engineer/complete-cluster/<cluster_id>')
def complete_job(cluster_id):
    # Mark entire route as completed
    mongo.db.collection_clusters.update_one(
        {'_id': ObjectId(cluster_id)},
        {'$set': {'status': 'completed'}}
    )
    return redirect(url_for('engineer.dashboard'))


# ============= INSPECTION ACCEPT/REJECT WORKFLOW =============
@engineer_bp.route('/engineer/inspection/<pickup_id>/accept', methods=['POST'])
def accept_inspection(pickup_id):
    """Engineer accepts the estimated price and inspection"""
    if session.get('role') != 'engineer':
        return {'error': 'Unauthorized'}, 401
    
    engineer_id = session['user_id']
    estimated_price = request.json.get('price', 0)
    
    # Update pickup with acceptance
    mongo.db.pickup_requests.update_one(
        {'_id': ObjectId(pickup_id)},
        {'$set': {
            'inspection_status': 'accepted',
            'engineer_price': estimated_price,
            'engineer_id': engineer_id,
            'accepted_at': datetime.utcnow()
        }}
    )
    
    # Fetch user and notify them
    pickup = mongo.db.pickup_requests.find_one({'_id': ObjectId(pickup_id)})
    if pickup:
        from routes.notification_routes import create_notification
        create_notification(
            recipient_id=str(pickup.get('user_id')),
            title='Inspection Accepted',
            message=f'Your e-waste has been inspected and accepted! Price: ₹{estimated_price}. Engineer will now collect and deliver to drop-off point.',
            notification_type='inspection_accepted',
            related_data={'pickup_id': str(pickup_id), 'price': estimated_price}
        )
    
    return {'success': True}


@engineer_bp.route('/engineer/inspection/<pickup_id>/reject', methods=['POST'])
def reject_inspection(pickup_id):
    """Engineer rejects the pickup"""
    if session.get('role') != 'engineer':
        return {'error': 'Unauthorized'}, 401
    
    engineer_id = session['user_id']
    reason = request.json.get('reason', 'Item does not meet recycling standards')
    
    # Update pickup with rejection
    mongo.db.pickup_requests.update_one(
        {'_id': ObjectId(pickup_id)},
        {'$set': {
            'inspection_status': 'rejected',
            'engineer_id': engineer_id,
            'rejection_reason': reason,
            'rejected_at': datetime.utcnow()
        }}
    )
    
    # Fetch user and notify them
    pickup = mongo.db.pickup_requests.find_one({'_id': ObjectId(pickup_id)})
    if pickup:
        from routes.notification_routes import create_notification
        create_notification(
            recipient_id=str(pickup.get('user_id')),
            title='Inspection Rejected',
            message=f'Your e-waste was inspected but could not be accepted. Reason: {reason}',
            notification_type='inspection_rejected',
            related_data={'pickup_id': str(pickup_id), 'reason': reason}
        )
    
    return {'success': True}


@engineer_bp.route('/engineer/inspection/<pickup_id>/mark-collected', methods=['POST'])
def mark_collected(pickup_id):
    """Engineer marks pickup as collected after visiting customer"""
    if session.get('role') != 'engineer':
        return {'error': 'Unauthorized'}, 401
    
    engineer_id = session['user_id']
    final_weight = request.json.get('weight', 0)
    final_quality = request.json.get('quality', 'good')
    
    # Update pickup status to 'collected'
    mongo.db.pickup_requests.update_one(
        {'_id': ObjectId(pickup_id)},
        {'$set': {
            'status': 'collected',
            'engineer_id': engineer_id,
            'final_weight': final_weight,
            'final_quality': final_quality,
            'collected_at': datetime.utcnow()
        }}
    )
    
    # Notify user that collection is complete
    pickup = mongo.db.pickup_requests.find_one({'_id': ObjectId(pickup_id)})
    if pickup:
        from routes.notification_routes import create_notification
        create_notification(
            recipient_id=str(pickup.get('user_id')),
            title='Item Collected',
            message=f'Your e-waste has been successfully collected (Weight: {final_weight}kg). It is now at our warehouse.',
            notification_type='item_collected',
            related_data={'pickup_id': str(pickup_id), 'weight': final_weight}
        )
    
    return {'success': True}


# ========== ROUTE VIEW ==========
@engineer_bp.route('/engineer/route/<cluster_id>')
def route_view(cluster_id):
    """View the route for a specific cluster"""
    if session.get("role") != "engineer":
        return redirect("/")
    
    cluster = mongo.db.collection_clusters.find_one({'_id': ObjectId(cluster_id)})
    if not cluster:
        return redirect(url_for('engineer.dashboard'))
    
    # Get all user pickups in the cluster
    u_ids = [u['user_id'] for u in cluster.get('users', [])]
    pickup_docs = []
    if u_ids:
        pickup_docs = list(mongo.db.pickup_requests.find({'_id': {'$in': u_ids}}))
    
    waypoints = []
    for pickup in pickup_docs:
        waypoints.append({
            'lat': pickup.get('latitude', 19.076),
            'lng': pickup.get('longitude', 72.877),
            'address': pickup.get('address', 'Unknown Location')
        })
    
    return render_template('engineer/route.html', waypoints=waypoints, view_only=True, driver_id=cluster.get('driver_id'))


# ========== DRIVER TRACKING ==========
@engineer_bp.route("/engineer/track-driver/<driver_id>")
def track_driver(driver_id):
    """View real-time driver location and active route"""
    if session.get("role") != "engineer":
        return redirect("/")
    
    engineer_id = session.get("user_id")
    
    # Verify engineer can track this driver
    driver = mongo.db.users.find_one({'_id': ObjectId(driver_id)})
    if not driver or driver.get('role') != 'driver':
        return redirect(url_for('engineer.dashboard'))
    
    # Get active routes for this driver
    active_routes = list(mongo.db.active_routes.find(
        {'driver_id': driver_id, 'status': 'active'}
    ).sort('timestamp', -1).limit(10))
    
    # Get current location
    current_location = mongo.db.driver_locations.find_one(
        {'driver_id': driver_id}
    )
    
    return render_template(
        'engineer/track_driver.html',
        driver=driver,
        active_routes=active_routes,
        current_location=current_location
    )


@engineer_bp.route("/api/engineer/driver-location/<driver_id>")
def get_driver_location(driver_id):
    """Get current driver location (for AJAX updates)"""
    if session.get("role") != "engineer":
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        location = mongo.db.driver_locations.find_one({'driver_id': driver_id})
        if location:
            location['_id'] = str(location['_id'])
        return jsonify(location or {}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@engineer_bp.route("/api/engineer/driver-routes/<driver_id>")
def get_driver_routes(driver_id):
    """Get all routes for a driver"""
    if session.get("role") != "engineer":
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        routes = list(mongo.db.active_routes.find(
            {'driver_id': driver_id}
        ).sort('timestamp', -1).limit(20))
        
        for route in routes:
            route['_id'] = str(route['_id'])
        
        return jsonify(routes), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500