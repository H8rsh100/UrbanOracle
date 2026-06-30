import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
import joblib
import os

def load_and_preprocess_data(data_path="data/crimes.csv", sample_size=50000):
    """
    Loads dataset, preprocesses it, and splits into train/val/test.
    """
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Dataset not found at {data_path}. Please place crimes.csv in the data directory.")

    # Read data
    df = pd.read_csv(data_path)
    
    # Drop rows with nulls in critical columns
    critical_cols = ['Primary Type', 'Arrest', 'Domestic', 'District', 'Latitude', 'Longitude', 'Date', 'Location Description']
    df = df.dropna(subset=critical_cols)

    # Sample dataset
    if len(df) > sample_size:
        df = df.sample(sample_size, random_state=42).reset_index(drop=True)

    # Parse Date
    # Date format usually: 09/05/2015 01:30:00 PM
    df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y %I:%M:%S %p', errors='coerce')
    df = df.dropna(subset=['Date'])
    
    df['Hour'] = df['Date'].dt.hour
    df['DayOfWeek'] = df['Date'].dt.dayofweek
    df['Month'] = df['Date'].dt.month

    # Boolean to int
    df['Arrest'] = df['Arrest'].astype(int)
    df['Domestic'] = df['Domestic'].astype(int)

    # Compute district analytics before label encoding
    district_analytics = {}
    for d in df['District'].unique():
        if pd.isna(d):
            continue
        dist_df = df[df['District'] == d]
        total_crimes = len(dist_df)
        arrest_rate = float(dist_df['Arrest'].mean()) if total_crimes > 0 else 0.0
        peak_hour = int(dist_df['Hour'].mode()[0]) if total_crimes > 0 and not dist_df['Hour'].mode().empty else 0
        top_crimes = dist_df['Primary Type'].value_counts().head(3).index.tolist()
        
        district_analytics[str(d)] = {
            "total_crimes": total_crimes,
            "arrest_rate": arrest_rate,
            "peak_hour": peak_hour,
            "top_crimes": top_crimes
        }

    # Label Encode Categorical Features
    encoders = {}
    categorical_cols = ['Primary Type', 'Location Description', 'District']
    
    for col in categorical_cols:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col].astype(str))
        encoders[col] = le

    # Create synthetic Risk Score for regression target
    # Higher for night hours (18-5), higher for specific crime types
    # We will simulate risk score based on hour, district frequency, and crime type frequency
    crime_freq = df['Primary Type'].value_counts(normalize=True).to_dict()
    district_freq = df['District'].value_counts(normalize=True).to_dict()
    
    df['Crime_Severity'] = df['Primary Type'].map(crime_freq)
    df['District_Risk'] = df['District'].map(district_freq)
    df['Night_Risk'] = df['Hour'].apply(lambda x: 1.5 if x < 6 or x > 18 else 1.0)
    
    df['Risk_Score'] = (df['Crime_Severity'] * 10 + df['District_Risk'] * 10) * df['Night_Risk']
    df['Risk_Score'] = df['Risk_Score'] + np.random.normal(0, 0.1, size=len(df)) # Add some noise

    # Features for modeling
    features = ['Hour', 'DayOfWeek', 'Month', 'District', 'Primary Type', 'Location Description', 'Domestic']
    X = df[features]
    y_class = df['Arrest']
    y_reg = df['Risk_Score']
    coords = df[['Latitude', 'Longitude', 'Hour']] # For clustering later

    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    X_scaled_df = pd.DataFrame(X_scaled, columns=features)

    # Save encoders and scaler
    os.makedirs('models/saved', exist_ok=True)
    joblib.dump(encoders, 'models/saved/encoders.pkl')
    joblib.dump(scaler, 'models/saved/scaler.pkl')

    # Train, Val, Test split
    # First split: Train (70%), Temp (30%)
    X_train, X_temp, y_class_train, y_class_temp, y_reg_train, y_reg_temp, coords_train, coords_temp = train_test_split(
        X_scaled_df, y_class, y_reg, coords, test_size=0.3, random_state=42
    )

    # Second split: Val (15%), Test (15%) -> half of Temp
    X_val, X_test, y_class_val, y_class_test, y_reg_val, y_reg_test, coords_val, coords_test = train_test_split(
        X_temp, y_class_temp, y_reg_temp, coords_temp, test_size=0.5, random_state=42
    )

    return {
        'X_train': X_train, 'y_class_train': y_class_train, 'y_reg_train': y_reg_train, 'coords_train': coords_train,
        'X_val': X_val, 'y_class_val': y_class_val, 'y_reg_val': y_reg_val, 'coords_val': coords_val,
        'X_test': X_test, 'y_class_test': y_class_test, 'y_reg_test': y_reg_test, 'coords_test': coords_test,
        'full_coords': coords,
        'district_analytics': district_analytics
    }

if __name__ == "__main__":
    print("Running preprocessing...")
    data = load_and_preprocess_data()
    print(f"Data shapes:")
    print(f"Train X: {data['X_train'].shape}")
    print(f"Val X: {data['X_val'].shape}")
    print(f"Test X: {data['X_test'].shape}")
    print("Encoders and Scaler saved successfully.")
