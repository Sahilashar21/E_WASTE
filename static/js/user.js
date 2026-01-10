/* static/js/user.js */

document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('.pickup-form');
    const weightInput = document.querySelector('input[name="weight"]');
    
    if (form) {
        form.addEventListener('submit', function(e) {
            let isValid = true;
            const weight = parseFloat(weightInput.value);

            // 1. Validate Weight
            if (isNaN(weight) || weight <= 0) {
                alert("Please enter a valid positive weight.");
                weightInput.classList.add('error-border'); // You can add this class to CSS if desired
                isValid = false;
            }

            // 2. Prevent double submission
            if (isValid) {
                const btn = form.querySelector('.btn-submit');
                btn.disabled = true;
                btn.textContent = "Submitting...";
            } else {
                e.preventDefault();
            }
        });
    }

    // Optional: Real-time visual feedback for weight
    if (weightInput) {
        weightInput.addEventListener('input', function() {
            if (this.value < 0) this.value = 0;
        });
    }
});
