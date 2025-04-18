import pandas as pd
import os
from datetime import datetime
from data_manager import save_data

# Define file paths
DATA_FILE = "manufacturing_data.csv"
IMPORT_FILE = "hourly_sheet.csv"

def import_hourly_sheet_data():
    """
    Import data from the hourly sheet CSV and convert it to the format expected by the application.
    """
    try:
        # Check if import file exists
        if not os.path.exists(IMPORT_FILE):
            return False, "Import file not found"
            
        # Read the CSV file
        import_df = pd.read_csv(IMPORT_FILE)
        
        # Create a new DataFrame with the application's expected structure
        records = []
        
        for _, row in import_df.iterrows():
            # Format the timestamp
            date_str = row['Date']
            timestamp = f"{date_str} 00:00:00"  # Add placeholder time
            
            # Create a record in the application's format
            new_record = {
                "Date": date_str,
                "Shift": row['Shift'],
                "Machine_ID": row['Machine_ID'],
                "Operator_Name": row['Operator_Name'],
                "Product_Name": row['Product_Name'],
                "Target_Output": row['Target_Output'],
                "Actual_Output": row['Actual_Output'],
                "Cumulative_Output": row['Cumulative_Output'],
                "Defects": row['Defects_Rework'],
                "Downtime_Minutes": row['Downtime_Minutes'],
                "Downtime_Reason": row['Reason_for_Downtime'] if pd.notna(row['Reason_for_Downtime']) else "",
                "Remarks": row['Operator_Remarks'] if pd.notna(row['Operator_Remarks']) else "",
                "Timestamp": timestamp
            }
            records.append(new_record)
        
        # Create a DataFrame with the records
        df = pd.DataFrame(records)
        
        # Save the data to the application's data file
        save_data(df)
        
        return True, f"Successfully imported {len(records)} records"
    
    except Exception as e:
        return False, f"Error importing data: {str(e)}"

if __name__ == "__main__":
    success, message = import_hourly_sheet_data()
    print(message)