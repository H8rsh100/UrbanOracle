import os
import sys
import json
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

# Add parent directory to path so we can import preprocessing
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from preprocessing.preprocess import load_and_preprocess_data

def train_mlp():
    print("Loading data for MLP...")
    data = load_and_preprocess_data()
    X_train, y_train = data['X_train'], data['y_class_train']
    X_val, y_val = data['X_val'], data['y_class_val']
    X_test, y_test = data['X_test'], data['y_class_test']

    input_dim = X_train.shape[1]

    # Build Model
    model = Sequential([
        Dense(128, activation='relu', input_shape=(input_dim,)),
        Dense(64, activation='relu'),
        Dropout(0.3),
        Dense(1, activation='sigmoid')
    ])

    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

    print("Training MLP...")
    history = model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=20,
        batch_size=32,
        verbose=1
    )

    # Save History
    history_dict = {
        'loss': history.history['loss'],
        'accuracy': history.history['accuracy'],
        'val_loss': history.history['val_loss'],
        'val_accuracy': history.history['val_accuracy']
    }
    
    # Convert np.float32 to float for JSON serialization
    history_dict = {k: [float(i) for i in v] for k, v in history_dict.items()}
    
    with open('mlp_history.json', 'w') as f:
        json.dump(history_dict, f, indent=4)

    # Save Model
    os.makedirs('models/saved', exist_ok=True)
    model.save('models/saved/mlp_model.h5')

    # Evaluate on Test Set
    print("Evaluating MLP on test set...")
    y_pred_prob = model.predict(X_test)
    y_pred = (y_pred_prob > 0.5).astype(int).flatten()

    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, zero_division=0)
    rec = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    cm = confusion_matrix(y_test, y_pred).tolist()

    print(f"MLP - Acc: {acc:.4f}, F1: {f1:.4f}")

    # Append to results.json
    results_path = 'results.json'
    if os.path.exists(results_path):
        with open(results_path, 'r') as f:
            results = json.load(f)
    else:
        results = {}

    results['MLP Neural Network'] = {
        "Accuracy": float(acc),
        "Precision": float(prec),
        "Recall": float(rec),
        "F1-Score": float(f1),
        "Confusion Matrix": cm
    }

    with open(results_path, 'w') as f:
        json.dump(results, f, indent=4)
        
    print("MLP trained and results saved successfully.")

if __name__ == "__main__":
    train_mlp()
