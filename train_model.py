import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
import joblib
import os

# Ensure model directory exists
if not os.path.exists('model'):
    os.makedirs('model')

def generate_synthetic_data(n_samples=1000):
    """
    Generates synthetic network traffic data.
    Features:
    - packet_size: Size of the packet in bytes.
    - duration: Duration of the connection in seconds.
    - request_rate: Requests per second.
    - protocol_type: Encoded protocol (0=TCP, 1=UDP, 2=ICMP).
    """
    np.random.seed(42)
    
    # Normal traffic patterns
    normal_data = {
        'packet_size': np.random.normal(loc=500, scale=100, size=n_samples),
        'duration': np.random.exponential(scale=2, size=n_samples),
        'request_rate': np.random.poisson(lam=10, size=n_samples),
        'protocol_type': np.random.choice([0, 1], size=n_samples, p=[0.8, 0.2]) # Mostly TCP/UDP
    }
    
    # Anomaly traffic patterns (e.g., DDOS, large payloads)
    n_anomalies = int(n_samples * 0.1)
    anomaly_data = {
        'packet_size': np.random.normal(loc=2000, scale=500, size=n_anomalies), # Large packets
        'duration': np.random.exponential(scale=10, size=n_anomalies), # Long duration
        'request_rate': np.random.poisson(lam=100, size=n_anomalies), # High rate (DDOS)
        'protocol_type': np.random.choice([0, 1, 2], size=n_anomalies) 
    }
    
    df_normal = pd.DataFrame(normal_data)
    df_anomaly = pd.DataFrame(anomaly_data)
    
    # Combine
    df = pd.concat([df_normal, df_anomaly], ignore_index=True)
    
    # Shuffle
    df = df.sample(frac=1).reset_index(drop=True)
    
    return df

print("Generating synthetic data...")
data = generate_synthetic_data()
print(f"Data shape: {data.shape}")

# Train Isolation Forest
# Contamination is the expected proportion of outliers (anomalies) in the data set
print("Training Isolation Forest model...")
clf = IsolationForest(contamination=0.1, random_state=42)
clf.fit(data)

# Save the model
model_path = 'model/isolation_forest.pkl'
joblib.dump(clf, model_path)
print(f"Model saved to {model_path}")

# Test prediction
test_normal = [[500, 2, 10, 0]]
test_anomaly = [[2500, 15, 120, 2]]

pred_normal = clf.predict(test_normal)
pred_anomaly = clf.predict(test_anomaly)

print(f"Test Normal (1=normal, -1=anomaly): {pred_normal[0]}")
print(f"Test Anomaly (1=normal, -1=anomaly): {pred_anomaly[0]}")
