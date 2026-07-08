# 🔍 UrbanOracle
### Urban Crime Pattern Predictor & Hotspot Analyzer

> *"The city has patterns. We make them visible."*

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.0+-000000?style=flat&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.0+-FF6F00?style=flat&logo=tensorflow&logoColor=white)](https://www.tensorflow.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

UrbanOracle is a full-stack machine learning web application that predicts 
the likelihood of an arrest for any reported crime incident and maps the 
highest-risk zones across Chicago - all in real time, through a sleek 
interactive dashboard.

Built with Python, Flask, scikit-learn, TensorFlow, and Leaflet.js on top 
of 50,000+ real Chicago crime records.

---

## ⚡ What It Does

- **Runs 5 ML models simultaneously** on any crime incident and shows you 
  every prediction side by side - Logistic Regression, SVM, Decision Tree, 
  Random Forest, and a Keras MLP Neural Network
- **Computes a Risk Score** using Multivariate Linear Regression - a 
  continuous measure of incident severity beyond binary classification
- **Identifies 10 crime hotspots** across Chicago using K-Means geographic 
  clustering, rendered live on an interactive Leaflet.js map
- **Visualizes model performance** with Chart.js - accuracy, F1, precision, 
  recall, and MLP training curves all in one place

---

## 🧠 ML Concepts Covered

| Concept | Implementation |
|---|---|
| Logistic Regression | Arrest classification baseline |
| Support Vector Machine | RBF kernel binary classifier |
| Decision Tree | Gini impurity split, feature importances |
| Random Forest | 100-estimator ensemble classifier |
| Multivariate Linear Regression | Risk score prediction |
| MLP Neural Network | Keras 128→64→32→1, Adam, Dropout |
| K-Means Clustering | Geographic hotspot detection |
| PCA / Feature Engineering | TF-IDF encoding, StandardScaler, datetime parsing |

---

## 🛠️ Tech Stack

Backend   →  Python 3.8+, Flask, scikit-learn, TensorFlow/Keras
Frontend  →  Vanilla JS, Chart.js, Leaflet.js, Lottie
Dataset   →  Chicago Crimes Dataset (Kaggle, 50k rows)

---

## 🚀 Getting Started

### 1. Clone the repo
```bash
git clone https://github.com/H8rsh100/UrbanOracle.git
cd UrbanOracle
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Drop in the dataset
Place `crimes.csv` inside the `data/` folder.
Get it here → [Chicago Crimes Dataset on Kaggle](https://www.kaggle.com/datasets/chicago/chicago-crime)

### 4. Train the models
```bash
# Train all classical models (LR, SVM, DT, RF, Linear Reg)
python models/train_classical.py

# Train the MLP Neural Network
python models/train_mlp.py
```
This generates `results.json` and `mlp_history.json` automatically.

### 5. Launch the app
```bash
python app.py
```
Open → `http://127.0.0.1:5000`

---

## 📡 API Reference

| Method | Route | Description |
|---|---|---|
| POST | `/api/predict` | Run all 5 models on incident input |
| GET | `/api/analytics` | Model performance metrics (results.json) |
| GET | `/api/hotspot` | K-Means cluster centers for map |
| GET | `/api/history` | MLP training history (loss + accuracy curves) |

---

## 📁 Project Structure

UrbanOracle/
├── data/
│   └── crimes.csv
├── models/
│   ├── train_classical.py
│   ├── train_mlp.py
│   └── saved/              ← .pkl and .h5 files go here after training
├── preprocessing/
│   └── preprocess.py
├── routes/
│   ├── predict.py
│   └── hotspot.py
├── static/
│   ├── css/style.css
│   └── js/main.js
├── templates/
│   └── index.html
├── app.py
├── requirements.txt
└── README.md


---

## ⚙️ GitHub Repository Configuration

To optimize your repository index card on GitHub, consider updating the following fields in your repo settings:

* **About Section**:
  > Urban Crime Pattern Predictor & Hotspot Analyzer running 5 ML models simultaneously (including Keras Neural Network and K-Means Clustering) built on 50k+ Chicago crime records.
* **Topics/Keywords**:
  `machine-learning`, `crime-prediction`, `flask`, `tensorflow`, `scikit-learn`, `data-science`, `python`

---

## 🔮 Future Scope

- Elbow Method for optimal K selection in clustering
- Live data feed via Chicago Data Portal API
- SHAP explainability for individual predictions
- LSTM-based temporal crime pattern forecasting
- Docker + cloud deployment on AWS/GCP

---

*Made with 🧠 and way too much caffeine.*

---

## License

MIT - see LICENSE.
