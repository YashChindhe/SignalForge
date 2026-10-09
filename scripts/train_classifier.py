import h5py
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib
import sys
import os

# Add src to python path to import our feature extractor
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from src.core.features import extract_features

# -- Configuration --
DATASET_PATH = "../data/radioml/2018.01/GOLD_XYZ_OSC.0001_1024.hdf5"
MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
MODEL_OUTPUT = os.path.join(MODEL_DIR, "rf_classifier.pkl")
SCALER_OUTPUT = os.path.join(MODEL_DIR, "scaler.pkl")
ENCODER_OUTPUT = os.path.join(MODEL_DIR, "label_encoder.pkl")

# Target modulation types we support for the demo
TARGET_MODS = ['BPSK', 'QPSK', '8PSK', '2FSK', '4FSK', 'AM-DSB', 'FM']
MIN_SNR = 0  # Only train on SNR >= 0 dB for better reliability on clean signals

def load_radioml_dataset(path):
    """Load RadioML 2018.01A HDF5 and filter to target modulations + SNR."""
    print(f"[1/5] Loading dataset from {path}...")
    if not os.path.exists(path):
        print(f"Error: RadioML dataset not found at {path}")
        print("Please download it from https://www.deepsig.ai/datasets and place it there.")
        sys.exit(1)
        
    with h5py.File(path, 'r') as f:
        X = f['X'][:]         # (N, 1024, 2) - IQ samples
        Y = f['Y'][:]         # (N, 24) - one-hot modulation labels
        Z = f['Z'][:]         # (N, 1) - SNR values
    
    Z = Z.flatten()
    
    # 24 Modulation classes in RadioML 2018.01A
    mod_names = [
        'OOK', '4ASK', '8ASK', 'BPSK', 'QPSK', '8PSK', '16PSK', '32PSK',
        '16APSK', '32APSK', '16QAM', '32QAM', '64QAM', '128QAM', '256QAM',
        'AM-SSB-WC', 'AM-SSB-SC', 'AM-DSB-WC', 'AM-DSB-SC', 'FM', 'GMSK',
        'OQPSK', '2FSK', '4FSK'
    ]
    
    labels = np.array([mod_names[np.argmax(y)] for y in Y])
    
    # Filter
    mask = np.array([l in TARGET_MODS for l in labels]) & (Z >= MIN_SNR)
    X_filtered = X[mask]
    labels_filtered = labels[mask]
    
    print(f"      Filtered: {len(X_filtered)} samples "
          f"({len(TARGET_MODS)} modulation types, SNR >= {MIN_SNR} dB)")
    
    return X_filtered, labels_filtered

def extract_all_features(X):
    """Extract 6 features from each IQ sample."""
    print("[2/5] Extracting statistical features...")
    features = []
    total = len(X)
    for i, sample in enumerate(X):
        # RadioML format is (1024, 2) where 0 is I and 1 is Q
        iq = sample[:, 0] + 1j * sample[:, 1]
        feat = extract_features(iq.astype(np.complex64))
        features.append(feat)
        if (i + 1) % 10000 == 0:
            print(f"      Progress: {i+1}/{total}")
    return np.array(features)

def train_and_save():
    """Full training pipeline."""
    os.makedirs(MODEL_DIR, exist_ok=True)
    
    X_raw, labels = load_radioml_dataset(DATASET_PATH)
    features = extract_all_features(X_raw)
    
    print("[3/5] Encoding labels and splitting data...")
    le = LabelEncoder()
    y = le.fit_transform(labels)
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(features)
    
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print("[4/5] Training Random Forest (100 trees, max_depth=20)...")
    clf = RandomForestClassifier(
        n_estimators=100,
        max_depth=20,
        random_state=42,
        n_jobs=-1,          # Use all CPU cores
        class_weight='balanced'
    )
    clf.fit(X_train, y_train)
    
    print("[5/5] Evaluating accuracy...")
    y_pred = clf.predict(X_test)
    print("\n" + classification_report(y_test, y_pred, target_names=le.classes_))
    
    joblib.dump(clf, MODEL_OUTPUT)
    joblib.dump(scaler, SCALER_OUTPUT)
    joblib.dump(le, ENCODER_OUTPUT)
    print(f"\n✓ Models saved successfully to {MODEL_DIR}/")

if __name__ == "__main__":
    train_and_save()
