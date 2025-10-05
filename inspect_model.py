# inspect_model.py
import joblib

# Path to your model
MODEL_PATH = "house_price.pkl"

# Load the model
try:
    model = joblib.load(MODEL_PATH)
except Exception as e:
    print(f"Error loading the model: {e}")
    exit()

# Inspect type
print("Type of the loaded object:", type(model))

# If it's a dictionary, print keys
if isinstance(model, dict):
    print("\nKeys in the dictionary:")
    for key in model.keys():
        print("-", key)

# If it has attributes, print them
elif hasattr(model, '__dict__'):
    print("\nAttributes of the object:")
    for attr in dir(model):
        if not attr.startswith("_"):
            print("-", attr)

# Otherwise, just print the object
else:
    print("\nLoaded object contents:")
    print(model)
