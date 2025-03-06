import json
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KURAL_FILE = os.path.join(BASE_DIR, "kural.json")


with open(KURAL_FILE, "r", encoding="utf-8") as f:
    kural_data = json.load(f)

def get_kural(number):
    """Fetch a specific Kural by number."""
    return next((k for k in kural_data if k["number"] == number), None)
