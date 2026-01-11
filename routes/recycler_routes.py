from flask import Blueprint, render_template, redirect, session, flash, url_for
from mongo import mongo
from bson import ObjectId

recycler_bp = Blueprint('recycler', __name__, url_prefix='/recycler')

@recycler_bp.route('/dashboard')
def dashboard():
    if session.get('role') != 'recycler':
        return redirect('/')

    # Fetch items that have been collected by engineers (Ready for recycling)
    collected_items = list(mongo.db.pickup_requests.find({'status': 'collected'}).sort('updated_at', -1))
    
    # Fetch history of recycled items
    recycled_items = list(mongo.db.pickup_requests.find({'status': 'recycled'}).sort('updated_at', -1))

    return render_template('recycler/dashboard.html', collected=collected_items, recycled=recycled_items)

@recycler_bp.route('/process/<request_id>')
def process_item(request_id):
    if session.get('role') != 'recycler':
        return redirect('/')
    
    mongo.db.pickup_requests.update_one(
        {'_id': ObjectId(request_id)},
        {'$set': {'status': 'recycled'}}
    )
    
    flash('Item processed and recycled successfully.', 'success')
    return redirect(url_for('recycler.dashboard'))
