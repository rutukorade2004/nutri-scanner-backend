# scoring.py

def calculate_health(product):
    nutriments = product.get("nutriments", {})

    # try multiple keys gracefully
    sugar = nutriments.get("sugars_100g") if nutriments.get("sugars_100g") is not None else nutriments.get("sugars") or 0
    fat = nutriments.get("fat_100g") if nutriments.get("fat_100g") is not None else nutriments.get("fat") or 0
    calories = nutriments.get("energy-kcal_100g") if nutriments.get("energy-kcal_100g") is not None else nutriments.get("energy-kcal") or nutriments.get("energy") or 0

    try:
        sugar = float(sugar)
    except:
        sugar = 0.0
    try:
        fat = float(fat)
    except:
        fat = 0.0
    try:
        calories = float(calories)
    except:
        calories = 0.0

    warnings = []
    score = 100

    # --- SUGAR ---
    if sugar > 20:
        warnings.append("High sugar")
        score -= 40
    elif sugar > 10:
        warnings.append("Moderate sugar")
        score -= 20

    # --- FAT ---
    if fat > 15:
        warnings.append("High fat")
        score -= 25
    elif fat > 8:
        warnings.append("Moderate fat")
        score -= 10

    # --- CALORIES ---
    if calories > 250:
        warnings.append("High calories")
        score -= 15

    # --- Health Result ---
    if score >= 70:
        result = "Healthy"
    elif score >= 40:
        result = "Moderate"
    else:
        result = "Unhealthy"

    return {
        "health_score": int(score),
        "warnings": warnings,
        "result": result
    }
