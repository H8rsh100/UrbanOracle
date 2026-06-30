from flask import Blueprint, jsonify
from sklearn.cluster import KMeans
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from preprocessing.preprocess import load_and_preprocess_data

hotspot_bp = Blueprint('hotspot', __name__)

# We compute this once when the module loads, or we could compute it per request.
# Computing once makes the API faster.
print("Calculating Hotspots using K-Means...")
try:
    data = load_and_preprocess_data()
    coords = data['full_coords'].dropna()
    
    # We take a sample to speed up KMeans if dataset is large, but 50k is fast enough for KMeans usually
    sample_coords = coords.sample(min(10000, len(coords)), random_state=42)
    
    kmeans = KMeans(n_clusters=10, random_state=42, n_init=10)
    kmeans.fit(sample_coords[['Latitude', 'Longitude']])
    
    cluster_centers = kmeans.cluster_centers_.tolist()
    labels = kmeans.labels_
    
    # Count cluster sizes
    import numpy as np
    unique, counts = np.unique(labels, return_counts=True)
    cluster_sizes = counts.tolist()
    
    hotspot_data = []
    for i in range(10):
        hotspot_data.append({
            "id": i,
            "lat": cluster_centers[i][0],
            "lng": cluster_centers[i][1],
            "size": cluster_sizes[i]
        })
        
except Exception as e:
    print(f"Error calculating hotspots: {e}")
    hotspot_data = []

@hotspot_bp.route('/hotspot', methods=['GET'])
def get_hotspots():
    return jsonify(hotspot_data)
