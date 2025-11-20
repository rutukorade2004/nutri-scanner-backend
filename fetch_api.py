# fetch_api.py
import requests

def fetch_product(barcode):
    """Fetch product data from OpenFoodFacts API by barcode.
    Returns product dict if found, else None.
    """
    if not barcode or len(str(barcode)) < 5:
        return None

    url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print("API Fetch Error:", e)
        return None

    if data.get("status") == 1:
        return data["product"]
    return None
