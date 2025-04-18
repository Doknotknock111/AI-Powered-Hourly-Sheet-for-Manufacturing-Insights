import pandas as pd
import os
import json
import numpy as np
from datetime import datetime
import io

# Define data file path
DATA_FILE = "manufacturing_data.csv"

def load_data():
    """
    Load manufacturing hourly sheet data from CSV file.
    If file doesn't exist, create an empty DataFrame with required columns.
    """
    try:
        if os.path.exists(DATA_FILE):
            df = pd.read_csv(DATA_FILE)
            return df
        else:
            # Create empty DataFrame with required columns
            columns = [
                "Date", "Shift", "Machine_ID", "Operator_Name", "Product_Name",
                "Target_Output", "Actual_Output", "Cumulative_Output", "Defects",
                "Downtime_Minutes", "Downtime_Reason", "Remarks", "Timestamp"
            ]
            return pd.DataFrame(columns=columns)
    except Exception as e:
        print(f"Error loading data: {str(e)}")
        # Return empty DataFrame in case of error
        columns = [
            "Date", "Shift", "Machine_ID", "Operator_Name", "Product_Name",
            "Target_Output", "Actual_Output", "Cumulative_Output", "Defects",
            "Downtime_Minutes", "Downtime_Reason", "Remarks", "Timestamp"
        ]
        return pd.DataFrame(columns=columns)

def save_data(df):
    """
    Save manufacturing data to CSV file.
    """
    try:
        df.to_csv(DATA_FILE, index=False)
        return True
    except Exception as e:
        print(f"Error saving data: {str(e)}")
        return False

def search_data(df, date=None, shift=None, machine_id=None, operator_name=None):
    """
    Search manufacturing data based on provided criteria.
    Returns filtered DataFrame.
    """
    # Create a copy to avoid modifying the original
    result_df = df.copy()
    
    # Apply filters if provided
    if date:
        result_df = result_df[result_df["Date"] == date]
    
    if shift:
        result_df = result_df[result_df["Shift"] == shift]
    
    if machine_id:
        result_df = result_df[result_df["Machine_ID"].str.contains(machine_id, case=False, na=False)]
    
    if operator_name:
        result_df = result_df[result_df["Operator_Name"].str.contains(operator_name, case=False, na=False)]
    
    return result_df

def export_data_csv(df):
    """
    Export data to CSV format.
    Returns CSV data as string.
    """
    output = io.StringIO()
    df.to_csv(output, index=False)
    return output.getvalue()

def get_machine_data(df, machine_id):
    """
    Get all data for a specific machine.
    """
    if machine_id in df["Machine_ID"].values:
        return df[df["Machine_ID"] == machine_id]
    return pd.DataFrame()

def get_operator_data(df, operator_name):
    """
    Get all data for a specific operator.
    """
    if operator_name in df["Operator_Name"].values:
        return df[df["Operator_Name"] == operator_name]
    return pd.DataFrame()

def get_production_stats(df):
    """
    Calculate and return summary statistics for production data.
    """
    if df.empty:
        return {}
    
    stats = {
        "total_production": df["Actual_Output"].sum(),
        "total_defects": df["Defects"].sum(),
        "total_downtime": df["Downtime_Minutes"].sum(),
        "efficiency": (df["Actual_Output"].sum() / df["Target_Output"].sum() * 100) if df["Target_Output"].sum() > 0 else 0,
        "defect_rate": (df["Defects"].sum() / df["Actual_Output"].sum() * 100) if df["Actual_Output"].sum() > 0 else 0,
        "machines": df["Machine_ID"].nunique(),
        "operators": df["Operator_Name"].nunique()
    }
    
    return stats

def get_recent_downtime_reasons(df, limit=5):
    """
    Get most recent downtime reasons from the data.
    """
    if df.empty or "Downtime_Reason" not in df.columns:
        return []
    
    # Filter rows with downtime > 0 and non-empty reason
    downtime_df = df[(df["Downtime_Minutes"] > 0) & (df["Downtime_Reason"].notna()) & (df["Downtime_Reason"] != "")]
    
    if downtime_df.empty:
        return []
    
    # Sort by timestamp (most recent first) and take top 'limit' entries
    recent_reasons = downtime_df.sort_values("Timestamp", ascending=False).head(limit)
    
    return recent_reasons[["Date", "Machine_ID", "Downtime_Minutes", "Downtime_Reason"]].to_dict("records")
