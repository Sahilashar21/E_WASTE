from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from mongo import mongo
from bson import ObjectId
from services.payment_service import PaymentService

payment_bp = Blueprint('payment', __name__)
payment_service = PaymentService()

@payment_bp.route('/payment/initiate/<pickup_id>', methods=['POST'])
def initiate_payment(pickup_id):
    """Create a payment order for a pickup request"""
    if session.get('role') != 'recycler':
        return jsonify({'error': 'Unauthorized'}), 403

    pickup = mongo.db.pickup_requests.find_one({'_id': ObjectId(pickup_id)})
    if not pickup:
        return jsonify({'error': 'Pickup not found'}), 404

    # Determine amount (use engineer_price or calculate fallback)
    amount = pickup.get('engineer_price')
    if not amount:
        # Fallback logic if no price set (e.g. 50 INR per kg)
        weight = pickup.get('final_weight') or pickup.get('approx_weight') or 0
        amount = weight * 0.05 # Assuming weight is in grams, 50 INR/kg = 0.05 INR/g
        if amount < 1: amount = 100 # Minimum amount

    order = payment_service.create_order(amount, pickup_id)
    
    if not order:
        return jsonify({'error': 'Failed to create payment order'}), 500

    return jsonify({
        'order_id': order['id'],
        'amount': order['amount'],
        'key_id': payment_service.key_id,
        'pickup_id': str(pickup_id),
        'user_name': pickup.get('user_name'),
        'email': session.get('email')
    })


@payment_bp.route('/payment/verify', methods=['POST'])
def verify_payment():
    """Handle payment success callback"""
    data = request.json
    
    razorpay_payment_id = data.get('razorpay_payment_id')
    razorpay_order_id = data.get('razorpay_order_id')
    razorpay_signature = data.get('razorpay_signature')
    pickup_id = data.get('pickup_id')

    # Verify Signature
    params_dict = {
        'razorpay_order_id': razorpay_order_id,
        'razorpay_payment_id': razorpay_payment_id,
        'razorpay_signature': razorpay_signature
    }
    
    if payment_service.verify_signature(params_dict):
        # Calculate total amount from order (convert paise to INR)
        # In a real scenario, fetch order details from Razorpay to confirm amount
        # Here we trust the passed amount or re-fetch from DB
        pickup = mongo.db.pickup_requests.find_one({'_id': ObjectId(pickup_id)})
        amount = pickup.get('engineer_price') or 100 # Fallback

        # Distribute Funds & Generate Invoices
        success = payment_service.distribute_and_generate_invoices(
            pickup_id, amount, razorpay_payment_id
        )
        
        if success:
            return jsonify({'success': True})
    
    return jsonify({'error': 'Payment verification failed'}), 400


@payment_bp.route('/invoices')
def my_invoices():
    """View invoices for the logged-in user"""
    if 'user_id' not in session:
        return redirect('/')
    
    user_id = session['user_id']
    role = session['role']
    
    query = {'recipient_id': user_id}
    if role == 'warehouse':
        # Warehouse sees their own + can see all (optional)
        query = {'$or': [{'recipient_id': user_id}, {'recipient_role': 'warehouse'}]}
        
    invoices = list(mongo.db.invoices.find(query).sort('created_at', -1))
    
    return render_template('payment/invoices.html', invoices=invoices)