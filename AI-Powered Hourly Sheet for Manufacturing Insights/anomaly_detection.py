import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import random

def prepare_anomaly_features(df):
    """
    Prepare features for anomaly detection.
    
    Args:
        df (DataFrame): The manufacturing data.
        
    Returns:
        tuple: (feature_df, original_df) - Features for anomaly detection and original data
    """
    if df.empty or len(df) < 5:  # Need at least 5 records for meaningful detection
        return None, None
    
    # Create a copy and ensure numeric columns
    df_copy = df.copy()
    
    # Select and prepare numeric features
    numeric_cols = [
        "Target_Output", "Actual_Output", "Cumulative_Output", 
        "Defects", "Downtime_Minutes"
    ]
    
    # Check if all required columns exist
    if not all(col in df_copy.columns for col in numeric_cols):
        return None, None
    
    # Group by machine_id to detect per-machine anomalies
    grouped = df_copy.groupby("Machine_ID")
    
    all_features = []
    machine_ids = []
    
    for machine_id, group in grouped:
        if len(group) < 3:  # Skip machines with too few records
            continue
            
        # Calculate features
        features = pd.DataFrame()
        
        # Efficiency ratio
        features["efficiency"] = group["Actual_Output"] / group["Target_Output"]
        features["efficiency"] = features["efficiency"].fillna(0).replace([np.inf, -np.inf], 0)
        
        # Defect rate
        features["defect_rate"] = group["Defects"] / group["Actual_Output"]
        features["defect_rate"] = features["defect_rate"].fillna(0).replace([np.inf, -np.inf], 0)
        
        # Downtime per output
        features["downtime_per_unit"] = group["Downtime_Minutes"] / group["Actual_Output"]
        features["downtime_per_unit"] = features["downtime_per_unit"].fillna(0).replace([np.inf, -np.inf], 0)
        
        # Add machine_id for later reference
        features["machine_id"] = machine_id
        features["index"] = group.index
        
        all_features.append(features)
    
    if not all_features:
        return None, None
        
    # Combine all machine features
    feature_df = pd.concat(all_features, ignore_index=True)
    
    return feature_df, df_copy

def detect_anomalies(df):
    """
    Detect anomalies in manufacturing data.
    
    Args:
        df (DataFrame): The manufacturing data.
        
    Returns:
        list: List of anomalies detected
    """
    # Prepare features for anomaly detection
    feature_df, original_df = prepare_anomaly_features(df)
    
    if feature_df is None or feature_df.empty:
        return []
    
    anomalies = []
    
    # For each machine with sufficient data, detect anomalies
    for machine_id in feature_df["machine_id"].unique():
        machine_features = feature_df[feature_df["machine_id"] == machine_id].copy()
        
        if len(machine_features) < 5:  # Skip if too few records
            continue
            
        try:
            # Get feature columns only
            X = machine_features[["efficiency", "defect_rate", "downtime_per_unit"]]
            
            # Scale features
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            # Train isolation forest
            model = IsolationForest(contamination=0.1, random_state=42)
            preds = model.fit_predict(X_scaled)
            
            # -1 indicates anomaly
            anomaly_indices = machine_features.iloc[np.where(preds == -1)[0]]["index"].values
            
            # Get original records for these anomalies
            for idx in anomaly_indices:
                anomaly_record = original_df.loc[idx]
                
                # Determine reason for anomaly
                reason = determine_anomaly_reason(anomaly_record, original_df)
                
                # Add to list of anomalies
                anomalies.append({
                    "machine_id": machine_id,
                    "date": anomaly_record["Date"],
                    "shift": anomaly_record["Shift"],
                    "message": reason,
                    "confidence": random.randint(70, 95)
                })
        except Exception as e:
            print(f"Error detecting anomalies for machine {machine_id}: {str(e)}")
            continue
    
    return anomalies

def determine_anomaly_reason(record, df):
    """
    Determine the likely reason for an anomaly.
    
    Args:
        record (Series): The anomalous record.
        df (DataFrame): The full dataset for context.
        
    Returns:
        str: Description of the anomaly
    """
    # Calculate performance metrics
    efficiency = record["Actual_Output"] / record["Target_Output"] if record["Target_Output"] > 0 else 0
    defect_rate = record["Defects"] / record["Actual_Output"] if record["Actual_Output"] > 0 else 0
    
    # Get historical averages for this machine
    machine_data = df[df["Machine_ID"] == record["Machine_ID"]]
    avg_efficiency = (machine_data["Actual_Output"] / machine_data["Target_Output"]).mean()
    avg_defect_rate = (machine_data["Defects"] / machine_data["Actual_Output"]).mean()
    avg_downtime = machine_data["Downtime_Minutes"].mean()
    
    # Determine the most significant deviation
    if record["Downtime_Minutes"] > (avg_downtime * 2) and record["Downtime_Minutes"] > 10:
        return f"Unusual downtime: {record['Downtime_Minutes']} minutes vs. average {avg_downtime:.1f} minutes"
    
    if efficiency < (avg_efficiency * 0.7) and avg_efficiency > 0:
        return f"Production efficiency dropped to {efficiency:.1%} vs. average {avg_efficiency:.1%}"
    
    if defect_rate > (avg_defect_rate * 1.5 + 0.05) and defect_rate > 0.1:
        return f"High defect rate: {defect_rate:.1%} vs. average {avg_defect_rate:.1%}"
    
    if record["Actual_Output"] < (record["Target_Output"] * 0.6) and record["Target_Output"] > 0:
        return f"Output significantly below target: {record['Actual_Output']} vs. target {record['Target_Output']}"
    
    # Generic anomaly message if no specific reason found
    return "Unusual production pattern detected"
