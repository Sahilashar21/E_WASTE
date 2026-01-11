async function calculatePrice() {
    const category = document.getElementById('category').value;
    const weight = document.getElementById('weight').value;
    const condition = document.getElementById('condition').value;
    const age = document.getElementById('age').value;

    try {
        const response = await fetch('/engineer/calculate-price', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                category: category,
                weight: weight,
                condition: condition,
                age_years: age
            })
        });

        const data = await response.json();
        document.getElementById('calculated-price').innerText = data.estimated_value;
        return data.estimated_value;
    } catch (error) {
        console.error('Error calculating price:', error);
        return 0;
    }
}

async function submitInspection() {
    const pickupId = document.getElementById('pickup-id').value;
    const price = await calculatePrice(); // Ensure we have latest price

    if (!confirm(`Confirm collection at ₹${price}?`)) return;

    try {
        const response = await fetch(`/engineer/submit/${pickupId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                total_price: price,
                decision: 'approved'
            })
        });

        const result = await response.json();
        if (result.success) {
            alert('Pickup collected successfully!');
            window.location.href = '/engineer/dashboard';
        }
    } catch (error) {
        alert('Error submitting inspection');
    }
}

// Auto-calculate on load
document.addEventListener('DOMContentLoaded', calculatePrice);