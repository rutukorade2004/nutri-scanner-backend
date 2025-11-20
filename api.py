# api.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# from fetch_api import fetch_product
# from scoring import calculate_health
# from predict import predict_health_label
from fetch_api import fetch_product
from scoring import calculate_health
from predict import predict_health_label


app = FastAPI(title="Nutrition Scanner API")

# Allow CORS from typical frontends during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def root():
    return {"status": "ok"}

@app.get("/scan/{barcode}")
def scan_product(barcode: str):
    # 1) Fetch product from OpenFood API
    product = fetch_product(barcode)
    if product is None:
        return {"error": "Product not found"}

    nutriments = product.get("nutriments", {})

    # Extract with safe defaults and multiple key names
    sugar = nutriments.get("sugars_100g") or nutriments.get("sugars") or 0
    fat = nutriments.get("fat_100g") or nutriments.get("fat") or 0
    sodium = nutriments.get("sodium_100g") or nutriments.get("sodium") or 0
    protein = nutriments.get("proteins_100g") or nutriments.get("proteins") or nutriments.get("proteins_value") or 0

    # 2) ML prediction from your model (if model files present)
    try:
        ml_prediction = predict_health_label(sugar, fat, sodium, protein)
    except Exception as e:
        ml_prediction = f"Prediction error: {str(e)}"

    # 3) Rule-based health scoring
    scoring = calculate_health(product)

    # 4) Final output to frontend
    return {
        "product_name": product.get("product_name"),
        "brands": product.get("brands"),
        "ingredients": product.get("ingredients_text"),
        "image_url": product.get("image_front_small_url") or product.get("image_url"),
        "nutriments": nutriments,
        "model_prediction": ml_prediction,
        "health_score": scoring["health_score"],
        "warnings": scoring["warnings"],
        "result": scoring["result"]
    }
