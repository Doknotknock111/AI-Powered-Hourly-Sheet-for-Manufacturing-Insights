import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib
import os
from datetime import datetime, timedelta
import random

# Model file paths
DOWNTIME_MODEL_PATH = "downtime_model.joblib"

def prepare_machine_features(df, machine_id):
    """
    Prepare features for machine downtime prediction.
    
    Args:
        df (DataFrame): The manufacturing data.
        machine_id (str): The machine ID to predict downtime for.
    
    Returns:
        DataFrame: Feature dataframe for prediction.
    """
    # Filter data for this machine
    machine_df = df[df["Machine_ID"] == machine_id].copy()
    
    if machine_df.empty:
        return None
    
    # Add datetime column
    machine_df["DateTime"] = pd.to_datetime(machine_df["Date"] + " " + machine_df["Timestamp"].str.split(" ").str[1])
    
    # Sort by datetime
    machine_df = machine_df.sort_values("DateTime")
    
    # Create features
    features = pd.DataFrame()
    
    # Average downtime in last 24 hours
    features["avg_downtime_24h"] = [machine_df["Downtime_Minutes"].mean()]
    
    # Maximum downtime in last 24 hours
    features["max_downtime_24h"] = [machine_df["Downtime_Minutes"].max()]
    
    # Downtime frequency (count of downtime > 0)
    features["downtime_frequency"] = [(machine_df["Downtime_Minutes"] > 0).sum()]
    
    # Production efficiency (actual/target)
    efficiency = machine_df["Actual_Output"].sum() / machine_df["Target_Output"].sum() if machine_df["Target_Output"].sum() > 0 else 1
    features["production_efficiency"] = [efficiency]
    
    # Defect rate
    defect_rate = machine_df["Defects"].sum() / machine_df["Actual_Output"].sum() if machine_df["Actual_Output"].sum() > 0 else 0
    features["defect_rate"] = [defect_rate]
    
    # Total operation hours
    features["operation_hours"] = [len(machine_df)]
    
    # Has recent downtime (within last 5 records)
    recent_records = min(5, len(machine_df))
    has_recent_downtime = (machine_df.tail(recent_records)["Downtime_Minutes"] > 0).any()
    features["has_recent_downtime"] = [1 if has_recent_downtime else 0]
    
    return features

def train_downtime_model(df):
    """
    Train a model to predict machine downtime.
    This is a simplified version for demonstration - in a real system,
    we would use proper training data and model validation.
    
    Args:
        df (DataFrame): The manufacturing data.
        
    Returns:
        object: Trained model
    """
    # For simplicity in this demo app, we'll create a dummy model
    # In a real system, you would train on historical data
    
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    
    # We would normally split data, train, and evaluate
    # For this demo, we'll just save the untrained model
    # which will make random predictions based on feature importance
    
    joblib.dump(model, DOWNTIME_MODEL_PATH)
    return model

def predict_downtime(df, machine_id):
    """
    Predict the likelihood of downtime for a specific machine.
    
    Args:
        df (DataFrame): The manufacturing data.
        machine_id (str): The machine ID to predict downtime for.
    
    Returns:
        tuple: (risk_score, hours) - The risk score as a percentage and prediction timeframe
    """
    # Prepare features
    features = prepare_machine_features(df, machine_id)
    
    if features is None or features.empty:
        # No data available for this machine
        # Return a random score based on limited information
        return random.randint(10, 90), random.choice([2, 4, 8, 12, 24])
    
    # Check if model exists, otherwise train it
    if not os.path.exists(DOWNTIME_MODEL_PATH):
        model = train_downtime_model(df)
    else:
        try:
            model = joblib.load(DOWNTIME_MODEL_PATH)
        except:
            model = train_downtime_model(df)
    
    # In a real implementation, this would use the trained model
    # For demo purposes, we'll use a heuristic approach
    
    # Calculate risk score based on features
    score = 0
    
    # Higher downtime frequency means higher risk
    downtime_freq = features["downtime_frequency"].values[0]
    score += min(downtime_freq * 10, 30)  # Max 30 points
    
    # Recent downtime is a risk factor
    if features["has_recent_downtime"].values[0] == 1:
        score += 20  # Add 20 points for recent downtime
    
    # Lower efficiency correlates with higher risk
    efficiency = features["production_efficiency"].values[0]
    score += max(0, min(40, int((1 - efficiency) * 100)))  # Max 40 points
    
    # Higher defect rate may indicate issues
    defect_rate = features["defect_rate"].values[0]
    score += min(int(defect_rate * 100), 10)  # Max 10 points
    
    # Cap at 100%
    final_score = min(score, 100)
    
    # Prediction timeframe - more data means longer prediction window
    if len(df[df["Machine_ID"] == machine_id]) > 20:
        hours = 24
    elif len(df[df["Machine_ID"] == machine_id]) > 10:
        hours = 12
    else:
        hours = 4
    
    return final_score, hours

def predict_production_targets(df, machine_id):
    """
    Predict optimal production targets for a machine based on historical performance.
    
    Args:
        df (DataFrame): The manufacturing data.
        machine_id (str): The machine ID to predict targets for.
        
    Returns:
        dict: Predicted optimal targets
    """
    # Filter data for this machine
    machine_df = df[df["Machine_ID"] == machine_id].copy()
    
    if machine_df.empty or len(machine_df) < 3:
        return {
            "optimal_target": None,
            "confidence": 0,
            "message": "Insufficient data for prediction"
        }
    
    # Calculate performance metrics
    avg_efficiency = (machine_df["Actual_Output"] / machine_df["Target_Output"]).mean()
    avg_output = machine_df["Actual_Output"].mean()
    max_output = machine_df["Actual_Output"].max()
    
    # Calculate optimal target
    if avg_efficiency >= 0.95:
        # Machine is meeting targets, can increase slightly
        optimal_target = max(int(max_output * 1.05), int(avg_output * 1.1))
        confidence = 80
        message = "Machine consistently meets targets, can increase production target."
    elif avg_efficiency >= 0.8:
        # Machine is doing well, maintain current targets
        optimal_target = int(avg_output / avg_efficiency)
        confidence = 70
        message = "Machine performs well, maintain current targets."
    else:
        # Machine is struggling, reduce targets
        optimal_target = int(avg_output * 1.1)  # Set target slightly above current output
        confidence = 60
        message = "Machine struggles to meet targets, consider adjustment."
    
    return {
        "optimal_target": optimal_target,
        "confidence": confidence,
        "message": message
    }
