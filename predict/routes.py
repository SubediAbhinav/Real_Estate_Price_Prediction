import pickle
import pandas as pd
from flask import render_template, redirect, url_for, flash, session, request
from flask_login import login_required
from flask import Blueprint
import os
import joblib

# =======================
# Define Blueprint
# =======================
predict_bp = Blueprint('predict', __name__, template_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates', 'predict'))

# =======================
# Load trained model and preprocessing artifacts
# =======================

model = joblib.load("house_price.pkl")    

with open("encoded_columns.pkl", "rb") as f:
    ENCODED_COLUMNS = pickle.load(f)

with open("neighborhood_map.pkl", "rb") as f:
    NEIGHBORHOOD_FREQ_MAP = pickle.load(f)



NUMERIC_COLUMNS = [
    "Area", "Bathroom", "Bedroom", "Floors", "Road_Width",
    "Property_Age", "Amenities_Count"
]

# =======================
# Step 1: Numerical features
# =======================
@predict_bp.route('/step1', methods=['GET', 'POST'])
@login_required
def step1():
    if request.method == 'POST':
        errors = []

        # Validate numeric inputs
        try:
            area = float(request.form['Area'])
            if area <= 1:
                errors.append("Area must be greater than 1")
        except ValueError:
            errors.append("Invalid value for Area")

        try:
            bathroom = int(request.form['Bathroom'])
            if bathroom < 1:
                errors.append("Bathroom count cannot be less than 1")
        except ValueError:
            errors.append("Invalid value for Bathroom")

        try:
            bedroom = int(request.form['Bedroom'])
            if bedroom < 1:
                errors.append("Bedroom count cannot be less than 1")
        except ValueError:
            errors.append("Invalid value for Bedroom")

        try:
            floors = int(request.form['Floors'])
            if floors <= 1:
                errors.append("Floors must be greater than 1")
        except ValueError:
            errors.append("Invalid value for Floors")

        try:
            road_width = float(request.form['Road_Width'])
            if road_width < 0:
                errors.append("Road Width cannot be less than 1")
        except ValueError:
            errors.append("Invalid value for Road Width")

        try:
            property_age = float(request.form['Property_Age'])
            if property_age < 0:
                errors.append("Property Age cannot be negative")
        except ValueError:
            errors.append("Invalid value for Property Age")

        try:
            amenities_count = int(request.form['Amenities_Count'])
            if amenities_count < 0:
                errors.append("Amenities Count cannot be negative")
        except ValueError:
            errors.append("Invalid value for Amenities Count")

        if errors:
            for err in errors:
                flash(err, "danger")
            return redirect(url_for('predict.step1'))

        # Save validated data to session
        session['step1_data'] = {
            'Area': area,
            'Bathroom': bathroom,
            'Bedroom': bedroom,
            'Floors': floors,
            'Road_Width': road_width,
            'Property_Age': property_age,
            'Amenities_Count': amenities_count
        }

        return redirect(url_for('predict.step2'))

    return render_template('step1.html')

# =======================
# Step 2: Categorical features
# =======================
@predict_bp.route('/step2', methods=['GET', 'POST'])
@login_required
def step2():
    if request.method == 'POST':
        errors = []
        
        neighborhood = request.form.get('Neighborhood', '').strip()
        if not neighborhood:
            errors.append("Neighborhood cannot be empty.")

        step1_data = session.get('step1_data', {})
        step2_data = {
            'City': request.form['City'],
            'Road_Type': request.form['Road_Type'],
            'Neighborhood': request.form['Neighborhood']
        }
        session['features'] = {**step1_data, **step2_data}
        return redirect(url_for('predict.result'))
    return render_template('step2.html')

# =======================
# Result: Predict price
# =======================
@predict_bp.route('/result')
@login_required
def result():
    features = session.get('features')
    if not features:
        flash("Please fill in property details first.", "warning")
        return redirect(url_for('predict.step1'))

    # Convert features to DataFrame
    input_df = pd.DataFrame([features])

    # Convert numeric columns to float/int
    for col in NUMERIC_COLUMNS:
        input_df[col] = pd.to_numeric(input_df[col], errors='coerce').fillna(0)

    # Frequency encode Neighborhood
    if 'Neighborhood' in input_df.columns:
        input_df['Neighborhood_freq'] = input_df['Neighborhood'].map(NEIGHBORHOOD_FREQ_MAP).fillna(0)
        input_df.drop(columns=['Neighborhood'], inplace=True)

    # One-hot encode categorical columns
    input_df = pd.get_dummies(input_df, columns=['City', 'Road_Type'], dtype=int)

    # Reindex columns to match training schema
    final_columns = ENCODED_COLUMNS + NUMERIC_COLUMNS + ['Neighborhood_freq']
    input_df = input_df.reindex(columns=model["feature_names"], fill_value=0)

    # Predict price
    predicted_price = model['model'].predict(input_df)[0]

    # Format price with commas
    formatted_price = f"{predicted_price:,.2f}"

    return render_template('predict/result.html', price=formatted_price, features=features)
