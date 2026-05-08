# UrbanOracle — Future Scope & Roadmap

> Ideas to implement when we revisit this project. Organized by effort and impact.

---

## 🔮 ML / Model Improvements

- **Real-time Retraining Pipeline**  
  Auto-retrain models when new crime data arrives (e.g., monthly Chicago Data Portal API pulls) instead of one-time training scripts.

- **LSTM / Time-Series Model**  
  Predict crime *trends over time* (not just single-event probability). Would need temporal sequencing of the dataset.

- **XGBoost / LightGBM Models**  
  Add gradient boosting models to the comparison dashboard — typically outperform Random Forest on tabular crime data.

- **Model Explainability (SHAP)**  
  Use SHAP values to show *why* a prediction was made (e.g., "High risk because: late hour + STREET location + THEFT type").

- **Anomaly Detection**  
  Flag unusual crime spikes in specific areas using Isolation Forest or Autoencoders.

---

## 🗺️ Hotspot & Map Enhancements

- **Dynamic Hotspot Radius**  
  Currently fixed K-Means centers — add a radius slider on the map so users can adjust cluster density visualization.

- **Time-Filtered Hotspots**  
  Show hotspots for a *specific time window* (e.g., "hotspots only between 10PM–2AM on weekends").

- **Heatmap Layer**  
  Add a toggleable density heatmap layer (Leaflet.heat plugin) on top of the cluster markers.

- **Neighborhood Boundaries Overlay**  
  Overlay Chicago neighborhood/district boundary polygons on the map (GeoJSON available from Chicago Data Portal).

- **Historical Hotspot Drift**  
  Visualize how hotspot locations have shifted over years — an animated time-lapse map.

---

## 📊 Dashboard & Analytics

- **Per-District Analytics Page**  
  Drill-down view: click a district on the map → see its top crime types, peak hours, and arrest rate breakdown.

- **Crime Type Trend Charts**  
  Line charts showing month-over-month trends for specific crime categories.

- **Comparative Year Analysis**  
  Side-by-side comparison of crime stats across different years (2019 vs 2022 vs 2024 etc.).

- **Export Reports**  
  Allow users to download a PDF/CSV snapshot of predictions and hotspot data.

---

## 🔗 Data & Integration

- **Live Chicago Data Portal Integration**  
  Connect directly to the [Chicago Data Portal Socrata API](https://data.cityofchicago.org/) to pull fresh crime data on demand.

- **Weather Correlation**  
  Fetch weather data (temperature, rain, etc.) and correlate with crime rates — there's well-documented research linking the two.

- **User-Submitted Reports**  
  A simple form for users to submit observed incidents, stored in a local DB, to supplement model inputs.

---

## ⚙️ Technical / Infrastructure

- **Replace Flask Debug Server**  
  Switch from `debug=True` to a production WSGI server (Gunicorn on Linux / Waitress on Windows) for any demo/deployment.

- **Async Predictions**  
  Move model inference to background tasks (Celery + Redis) so the UI doesn't block on heavy predictions.

- **Dockerize the App**  
  Create a `Dockerfile` so the entire app (models included) runs in one container — no manual setup needed.

- **GPU Support via TF-DirectML**  
  Install `tensorflow-directml` to use the GPU on native Windows instead of CPU-only inference.
  ```
  pip install tensorflow-directml
  ```

- **Model Versioning**  
  Track trained model versions with MLflow or DVC so you can compare runs and roll back.

- **Silence Startup Warnings (Quick Win)**  
  Add to top of `app.py`:
  ```python
  import os
  os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
  os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
  os.environ['LOKY_MAX_CPU_COUNT'] = '8'  # set to your core count
  ```

---

## 🎨 UI / UX

- **Dark Mode Toggle**  
  Currently fixed theme — add a dark/light toggle.

- **Mobile Responsive Layout**  
  Make the map and prediction form usable on phone screens.

- **Prediction History Log**  
  Store past predictions in localStorage or a SQLite DB so users can review what they queried.

---

*Last updated: May 2026 | Project: UrbanOracle*
