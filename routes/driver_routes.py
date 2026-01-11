from flask import Blueprint, render_template, session, redirect, url_for, jsonify, request
from bson import ObjectId
from datetime import timedelta, datetime
from mongo import mongo

driver_bp = Blueprint('driver', __name__)


@driver_bp.route('/driver/dashboard')
def dashboard():
    if session.get('role') != 'driver':
        return redirect('/')

    driver_id = session.get('user_id')

    # Find clusters assigned to this driver
    clusters = list(mongo.db.collection_clusters.find({'driver_id': driver_id}))

    clusters_with_pickups = []
    for c in clusters:
        u_ids = [u['user_id'] for u in c.get('users', [])]
        pickup_docs = []
        if u_ids:
            pickup_docs = list(mongo.db.pickup_requests.find({'_id': {'$in': u_ids}}))

        # compute schedule times
        scheduled_for = c.get('scheduled_for')
        est_minutes = c.get('estimated_duration_minutes', 0)
        est_end = None
        if scheduled_for and est_minutes:
            try:
                est_end = scheduled_for + timedelta(minutes=int(est_minutes))
            except Exception:
                est_end = None

        clusters_with_pickups.append({
            'cluster': c,
            'pickups': pickup_docs,
            'scheduled_for': scheduled_for,
            'est_end': est_end
        })

    return render_template('driver/driver_dashboard.html', jobs=clusters_with_pickups)


@driver_bp.route('/driver/route/<cluster_id>')
def route_view(cluster_id):
    """Display the multi-stop route for a cluster"""
    if session.get('role') != 'driver':
        return redirect('/')

    driver_id = session.get('user_id')
    
    # Fetch the cluster
    cluster = mongo.db.collection_clusters.find_one({
        '_id': ObjectId(cluster_id),
        'driver_id': driver_id
    })
    
    if not cluster:
        return redirect(url_for('driver.dashboard'))
    
    # Get all user pickups in the cluster
    u_ids = [u['user_id'] for u in cluster.get('users', [])]
    pickup_docs = []
    
    if u_ids:
        pickup_docs = list(mongo.db.pickup_requests.find({'_id': {'$in': u_ids}}))
    
    # Prepare waypoints with coordinates
    waypoints = []
    for pickup in pickup_docs:
        waypoints.append({
            'lat': pickup.get('latitude', 19.076),
            'lng': pickup.get('longitude', 72.877),
            'address': pickup.get('address', 'Unknown Location'),
            'user_id': str(pickup.get('_id', '')),
            'contact': pickup.get('phone_number', '')
        })
    
    return render_template('driver/route.html', waypoints=waypoints)


@driver_bp.route('/api/driver/share-route', methods=['POST'])
def share_route():
    """Share current route with assigned engineers"""
    if session.get('role') != 'driver':
        return jsonify({'error': 'Unauthorized'}), 403
    
    driver_id = session.get('user_id')
    data = request.get_json()
    
    try:
        route_data = {
            'driver_id': driver_id,
            'driver_name': mongo.db.users.find_one({'_id': ObjectId(driver_id)}, {'name': 1}).get('name', 'Unknown'),
            'route': data.get('route', {}),
            'timestamp': datetime.fromisoformat(data.get('timestamp', datetime.now().isoformat())),
            'status': 'active'
        }
        
        # Store route in real-time tracking collection
        mongo.db.active_routes.insert_one(route_data)
        
        # Notify engineers assigned to this driver
        engineers = list(mongo.db.users.find(
            {'role': 'engineer', 'assigned_drivers': driver_id},
            {'_id': 1}
        ))
        
        for engineer in engineers:
            mongo.db.notifications.insert_one({
                'engineer_id': engineer['_id'],
                'type': 'route_update',
                'driver_id': driver_id,
                'message': f"Driver {route_data['driver_name']} is at Stop {route_data['route'].get('stopNumber', 0)}",
                'route_data': route_data['route'],
                'timestamp': datetime.now(),
                'read': False
            })
        
        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@driver_bp.route('/api/driver/update-location', methods=['POST'])
def update_location():
    """Update driver's real-time location"""
    if session.get('role') != 'driver':
        return jsonify({'error': 'Unauthorized'}), 403
    
    driver_id = session.get('user_id')
    data = request.get_json()
    
    try:
        # Update driver location in database
        mongo.db.driver_locations.update_one(
            {'driver_id': driver_id},
            {
                '$set': {
                    'lat': data.get('lat'),
                    'lng': data.get('lng'),
                    'stopNumber': data.get('stopNumber', 0),
                    'timestamp': datetime.fromisoformat(data.get('timestamp', datetime.now().isoformat()))
                }
            },
            upsert=True
        )
        
        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@driver_bp.route('/api/driver/trip-complete', methods=['POST'])
def trip_complete():
    """Mark trip as complete and notify engineers"""
    if session.get('role') != 'driver':
        return jsonify({'error': 'Unauthorized'}), 403
    
    driver_id = session.get('user_id')
    data = request.get_json()
    
    try:
        # Update active routes
        mongo.db.active_routes.update_many(
            {'driver_id': driver_id, 'status': 'active'},
            {'$set': {'status': 'completed', 'completed_at': datetime.now()}}
        )
        
        # Get driver name
        driver = mongo.db.users.find_one({'_id': ObjectId(driver_id)}, {'name': 1})
        
        # Notify engineers
        engineers = list(mongo.db.users.find(
            {'role': 'engineer', 'assigned_drivers': driver_id},
            {'_id': 1}
        ))
        
        for engineer in engineers:
            mongo.db.notifications.insert_one({
                'engineer_id': engineer['_id'],
                'type': 'trip_complete',
                'driver_id': driver_id,
                'message': f"Driver {driver.get('name', 'Unknown')} completed all {data.get('completedStops', 0)} stops",
                'timestamp': datetime.now(),
                'read': False
            })
        
        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
