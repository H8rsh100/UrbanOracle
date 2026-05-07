import os
import sys
import json
import joblib
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, r2_score, mean_squared_error

# Add parent directory to path so we can import preprocessing
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from preprocessing.preprocess import load_and_preprocess_data

def train_and_evaluate():
    print("Loading data...")
    data = load_and_preprocess_data()
    X_train, y_class_train, y_reg_train = data['X_train'], data['y_class_train'], data['y_reg_train']
    X_test, y_class_test, y_reg_test = data['X_test'], data['y_class_test'], data['y_reg_test']

    results = {}
    os.makedirs('models/saved', exist_ok=True)

    def evaluate_classification(model, name, X_train, y_train, X_test, y_test):
        print(f"Training {name}...")
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        
        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, zero_division=0)
        rec = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        cm = confusion_matrix(y_test, y_pred).tolist()
        
        print(f"{name} - Acc: {acc:.4f}, F1: {f1:.4f}")
        
        # Save model
        model_path = f"models/saved/{name.lower().replace(' ', '_')}.pkl"
        joblib.dump(model, model_path)
        
        results[name] = {
            "Accuracy": acc,
            "Precision": prec,
            "Recall": rec,
            "F1-Score": f1,
            "Confusion Matrix": cm
        }
        return model

    # 1. Logistic Regression
    lr = LogisticRegression(max_iter=1000)
    evaluate_classification(lr, "Logistic Regression", X_train, y_class_train, X_test, y_class_test)

    # 2. SVM (SVC with RBF kernel) - use a subset for training if it's too slow, but 35k should be manageable
    # For performance on local execution, we might want to cap SVM training size if it's taking too long
    svm = SVC(kernel='rbf', probability=True)
    # Using a 10k sample for SVM to ensure reasonable training time
    sample_size = min(10000, len(X_train))
    evaluate_classification(svm, "SVM", X_train[:sample_size], y_class_train[:sample_size], X_test, y_class_test)

    # 3. Decision Tree Classifier
    dt = DecisionTreeClassifier(max_depth=5, min_samples_leaf=50, random_state=42)
    dt_model = evaluate_classification(dt, "Decision Tree", X_train, y_class_train, X_test, y_class_test)
    joblib.dump(dt_model.feature_importances_.tolist(), 'models/saved/dt_feature_importances.pkl')

    # 4. Random Forest Classifier
    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    rf_model = evaluate_classification(rf, "Random Forest", X_train, y_class_train, X_test, y_class_test)
    joblib.dump(rf_model.feature_importances_.tolist(), 'models/saved/rf_feature_importances.pkl')

    # 5. Multivariate Linear Regression (Regression Task)
    print("Training Multivariate Linear Regression...")
    mlr = LinearRegression()
    mlr.fit(X_train, y_reg_train)
    y_reg_pred = mlr.predict(X_test)
    
    r2 = r2_score(y_reg_test, y_reg_pred)
    mse = mean_squared_error(y_reg_test, y_reg_pred)
    print(f"MLR - R2: {r2:.4f}, MSE: {mse:.4f}")
    
    joblib.dump(mlr, 'models/saved/multivariate_linear_regression.pkl')
    results["Multivariate Linear Regression"] = {
        "R2-Score": r2,
        "MSE": mse
    }

    # Save results to JSON
    with open('results.json', 'w') as f:
        json.dump(results, f, indent=4)
        
    print("Classical models trained and results saved successfully.")

if __name__ == "__main__":
    train_and_evaluate()
