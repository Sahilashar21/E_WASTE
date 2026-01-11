def calculate_final_price(category, weight, condition, age_years):
    """
    Calculates the estimated value of e-waste.
    
    Args:
        category (str): E-Waste type (Laptop, PC, etc.)
        weight (float): Weight in kg (converted from grams if needed)
        condition (str): working, repairable, scrap
        age_years (int): Age of the device
    """
    # Base prices in INR per kg (Mock Market Values)
    BASE_PRICES = {
        "Laptop": 300,
        "Desktop PC": 250,
        "Mobile Devices": 500,
        "Printer": 100,
        "Office PCs": 250,
        "Server Racks": 400,
        "UPS Batteries": 150,
        "Washing Machine": 50,
        "Fridge": 60,
        "AC": 70
    }
    
    # Condition Multipliers
    CONDITION_FACTORS = {
        "working": 1.5,
        "repairable": 1.0,
        "scrap": 0.5
    }
    
    base_rate = BASE_PRICES.get(category, 100) # Default 100 if unknown
    condition_factor = CONDITION_FACTORS.get(condition, 0.5)
    
    # Depreciation: 10% per year, max 80%
    depreciation = min(age_years * 0.10, 0.80)
    age_factor = 1 - depreciation
    
    # Formula: Rate * Weight * Condition * AgeFactor
    estimated_value = base_rate * weight * condition_factor * age_factor
    
    return {
        "base_rate": base_rate,
        "condition_factor": condition_factor,
        "age_factor": round(age_factor, 2),
        "estimated_value": round(estimated_value, 2),
        "currency": "INR"
    }