# UrbanOracle — Urban Crime Pattern Predictor & Hotspot Analyzer

UrbanOracle is a machine learning-based web application that predicts the likelihood of arrests for reported crimes and identifies crime hotspots in Chicago. It serves as a project review submission for Supervised Learning and Neural Networks.

## Features
- **Predictive Modeling**: Uses multiple ML models (Logistic Regression, SVM, Decision Tree, Random Forest, Multivariate Linear Regression) and an MLP Neural Network to predict arrest probability and a synthetic risk score.
- **Hotspot Analysis**: Uses K-Means clustering to identify top 10 crime hotspots based on location coordinates, visualized on an interactive Leaflet.js map.
- **Model Comparison**: Interactive dashboard comparing the accuracy and F1 scores of classical models alongside the MLP training curves.

## Installation

1. Clone the repository or navigate to the project folder.
2. Ensure you have Python installed.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Place the `crimes.csv` dataset inside the `data/` folder. A sample of 50,000 rows is recommended for performance.

## Running the Training Scripts

Before starting the Flask application, you must train the models. The training scripts automatically save the models and generate the required `.json` files for the dashboard.

1. **Train Classical Models**:
   ```bash
   python models/train_classical.py
   ```
2. **Train MLP Neural Network**:
   ```bash
   python models/train_mlp.py
   ```

## Starting the Flask Application

Once the models are trained and saved in `models/saved/`, start the Flask server:
```bash
python app.py
```
Open your browser and navigate to `http://127.0.0.1:5000/`.

## API Routes
- `POST /predict`: Accepts form input (hour, day of week, month, district, crime type, location desc, domestic) and returns predictions from all models.
- `GET /analytics`: Returns the performance metrics (`results.json`) for the dashboard charts.
- `GET /hotspot`: Returns K-Means cluster centers and sizes for map rendering.
- `GET /history`: Returns the MLP training history (`mlp_history.json`) for the loss/accuracy curves.
