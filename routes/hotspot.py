from flask import Blueprint, jsonify, request
from sklearn.cluster import KMeans
import sys
import os
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from preprocessing.preprocess import load_and_preprocess_data

hotspot_bp = Blueprint('hotspot', __name__)

print("Pre-loading coordinates data for dynamic hotspots...")
try:
    data = load_and_preprocess_data()
    coords = data['full_coords'].dropna()
    print("Coordinates data pre-loaded successfully.")
except Exception as e:
    print(f"Error pre-loading coords: {e}")
    coords = None

@hotspot_bp.route('/hotspot', methods=['GET'])
def get_hotspots():
    if coords is None:
        return jsonify([])

    # Optional hour range filter
    hour_min = request.args.get('hour_min', type=int)
    hour_max = request.args.get('hour_max', type=int)

    filtered = coords
    if hour_min is not None and hour_max is not None:
        if hour_min <= hour_max:
            filtered = coords[(coords['Hour'] >= hour_min) & (coords['Hour'] <= hour_max)]
        else:
            # Wrap around midnight (e.g. 22 to 4)
            filtered = coords[(coords['Hour'] >= hour_min) | (coords['Hour'] <= hour_max)]

    sample_size = min(5000, len(filtered))
    if sample_size < 10:
        return jsonify([])

    try:
        sample_coords = filtered.sample(sample_size, random_state=42)
        n_clusters = min(10, len(sample_coords))
        
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        kmeans.fit(sample_coords[['Latitude', 'Longitude']])
        
        cluster_centers = kmeans.cluster_centers_.tolist()
        labels = kmeans.labels_
        
        unique, counts = np.unique(labels, return_counts=True)
        # Ensure sizes map correctly to center indexes
        cluster_sizes = {int(u): int(c) for u, c in zip(unique, counts)}
        
        hotspot_data = []
        for i in range(len(cluster_centers)):
            hotspot_data.append({
                "id": i,
                "lat": cluster_centers[i][0],
                "lng": cluster_centers[i][1],
                "size": cluster_sizes.get(i, 0)
            })
            
        return jsonify(hotspot_data)
    except Exception as e:
        print(f"Error calculating hotspots: {e}")
        return jsonify([])
