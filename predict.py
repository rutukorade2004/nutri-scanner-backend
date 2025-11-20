# backend/predict.py

import os
import pickle
from pathlib import Path
import joblib
import numpy as np


# ================================================================
#  CROSS-PLATFORM PATH HANDLING (Windows / Linux / Android / Render)
# ================================================================

BACKEND_DIR = Path(__file__).resolve().parent               # /backend
ROOT_DIR = BACKEND_DIR.parent                               # project root
MODEL_DIR = ROOT_DIR / "model_training"                     # repo folder

MODEL_ENV_PATH  = os.getenv("MODEL_PATH")                   # optional override
ENCODER_ENV_PATH = os.getenv("ENCODER_PATH")                # optional override


def build_path_candidates():
    """Builds a list of model + encoder file paths for ALL platforms."""
    model_candidates = []
    encoder_candidates = []

    # 1) Environment variables (highest priority)
    if MODEL_ENV_PATH:
        model_candidates.append(MODEL_ENV_PATH)
    if ENCODER_ENV_PATH:
        encoder_candidates.append(ENCODER_ENV_PATH)

    # 2) Linux / Android / Render paths (repo-based)
    linux_model_paths = [
        MODEL_DIR / "nutrition_best_model.pkl",
        MODEL_DIR / "nutrition_bundle.joblib",
        MODEL_DIR / "trained_model.pkl",
    ]
    linux_encoder_paths = [MODEL_DIR / "label_encoder.pkl"]

    # 3) Windows local development path (optional)
    if os.name == "nt":   # Windows only
        user_home = Path.home()
        win_model_dir = (
            user_home / "Desktop" / "major-project" /
            "nutrition-scanner" / "backend" / "model_training"
        )

        windows_models = [
            win_model_dir / "nutrition_best_model.pkl",
            win_model_dir / "nutrition_bundle.joblib",
            win_model_dir / "trained_model.pkl",
        ]
        windows_encoders = [win_model_dir / "label_encoder.pkl"]

        model_candidates.extend([str(p) for p in windows_models])
        encoder_candidates.extend([str(p) for p in windows_encoders])

    # Always add Linux/Render paths too (so repo works everywhere)
    model_candidates.extend([str(p) for p in linux_model_paths])
    encoder_candidates.extend([str(p) for p in linux_encoder_paths])

    # Remove duplicates while preserving order
    def unique(items):
        seen = set()
        out = []
        for i in items:
            if i not in seen:
                seen.add(i)
                out.append(i)
        return out

    return unique(model_candidates), unique(encoder_candidates)


MODEL_CANDIDATES, ENCODER_CANDIDATES = build_path_candidates()



# ================================================================
#  MODEL LOADING HELPERS
# ================================================================

def load_model(path_list):
    """Try loading models from several candidates."""
    tried = []

    for p in path_list:
        p = Path(p)
        tried.append(str(p))

        if not p.exists():
            continue

        try:
            if p.suffix.lower() in [".joblib", ".jl", ".jb"]:
                return joblib.load(p), p

            # Default: try pickle
            with open(p, "rb") as f:
                return pickle.load(f), p

        except ModuleNotFoundError as e:
            missing = str(e).split("'")[1]
            raise RuntimeError(
                f"Model requires missing dependency '{missing}'. "
                f"Add it to backend/requirements.txt"
            ) from e

        except Exception as e:
            raise RuntimeError(f"Failed loading model from {p}: {e}") from e

    raise FileNotFoundError(
        "Model not found.\nTried:\n" + "\n".join(tried) +
        "\n\nPlace model in model_training/ or set MODEL_PATH env variable."
    )


def load_encoder(path_list):
    """Load label encoder."""
    tried = []

    for p in path_list:
        p = Path(p)
        tried.append(str(p))

        if not p.exists():
            continue

        try:
            with open(p, "rb") as f:
                return pickle.load(f), p
        except Exception as e:
            raise RuntimeError(f"Failed loading encoder from {p}: {e}") from e

    raise FileNotFoundError(
        "Label encoder not found.\nTried:\n" + "\n".join(tried)
    )



# ================================================================
#  LOAD MODEL + ENCODER (done at import — startup fails fast)
# ================================================================

model, model_path = load_model(MODEL_CANDIDATES)
label_encoder, encoder_path = load_encoder(ENCODER_CANDIDATES)

print(f"[predict.py] Loaded model from: {model_path}")
print(f"[predict.py] Loaded label encoder from: {encoder_path}")



# ================================================================
#  PREDICTION LOGIC
# ================================================================

def predict_health_label(sugar, fat, sodium, protein):
    """Runs prediction and returns the decoded label."""

    # Validate numeric input
    try:
        values = np.array([[float(sugar), float(fat), float(sodium), float(protein)]])
    except ValueError:
        raise ValueError("Inputs must be numeric: sugar, fat, sodium, protein.")

    pred = model.predict(values)

    # If model returns encoded integers → decode
    try:
        decoded = label_encoder.inverse_transform(pred)[0]
        return decoded
    except Exception:
        # Model may return strings directly
        if isinstance(pred, (list, tuple, np.ndarray)):
            return pred[0]
        return pred



# ================================================================
#  QUICK LOCAL TEST
# ================================================================

if __name__ == "__main__":
    print("=== Testing model with sample inputs ===")
    try:
        result = predict_health_label(5, 3, 200, 6)
        print("Prediction:", result)
    except Exception as e:
        print("Test failed:", e)
