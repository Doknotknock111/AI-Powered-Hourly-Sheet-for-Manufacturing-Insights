import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import os

from data_manager import (
    load_data, 
    save_data, 
    search_data,
    export_data_csv
)
from grok_assistant import process_ai_query
from prediction_models import predict_downtime
from anomaly_detection import detect_anomalies
from utils import get_shift_from_time
from import_data import import_hourly_sheet_data

# Set page configuration
st.set_page_config(
    page_title="Manufacturing Hourly Sheet Tracker",
    page_icon="🏭",
    layout="wide"
)

# Initialize session state
if "df" not in st.session_state:
    st.session_state.df = load_data()

# Title and description
st.title("🏭 Manufacturing Hourly Sheet Tracker")
st.subheader("AI-Enhanced Production Monitoring System")

# Main navigation
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📝 Data Entry", 
    "🔍 Search Records", 
    "🤖 AI Assistant", 
    "⚠️ Predictions & Anomalies",
    "📊 Export Data",
    "📥 Import Data"
])

# Tab 1: Data Entry
with tab1:
    st.header("Hourly Sheet Data Entry")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Current date and time for default values
        current_date = datetime.now().date()
        current_time = datetime.now().time()
        default_shift = get_shift_from_time(current_time)
        
        entry_date = st.date_input("Date", value=current_date)
        shift = st.selectbox("Shift", ["Morning", "Afternoon", "Night"], index=["Morning", "Afternoon", "Night"].index(default_shift))
        
        machine_id = st.text_input("Machine/Workstation ID")
        operator_name = st.text_input("Operator Name")
        product_name = st.text_input("Product Name / Part Number")
    
    with col2:
        target_output = st.number_input("Target Output (Planned Production per Hour)", min_value=0, step=1)
        actual_output = st.number_input("Actual Output (Produced Units per Hour)", min_value=0, step=1)
        cumulative_output = st.number_input("Cumulative Output (Total from Shift Start to Current Hour)", min_value=0, step=1)
        defects = st.number_input("Defects/Rework Units", min_value=0, step=1)
        downtime = st.number_input("Downtime (Minutes)", min_value=0, max_value=60, step=1)
        downtime_reason = st.text_input("Reason for Downtime (If Any)")
        remarks = st.text_area("Operator Remarks (Optional)")
    
    # Submit button
    if st.button("Submit Hourly Data"):
        if not machine_id or not operator_name or not product_name:
            st.error("Please fill in all required fields: Machine ID, Operator Name, and Product Name.")
        else:
            # Create new record
            new_record = {
                "Date": entry_date.strftime("%Y-%m-%d"),
                "Shift": shift,
                "Machine_ID": machine_id,
                "Operator_Name": operator_name,
                "Product_Name": product_name,
                "Target_Output": target_output,
                "Actual_Output": actual_output,
                "Cumulative_Output": cumulative_output,
                "Defects": defects,
                "Downtime_Minutes": downtime,
                "Downtime_Reason": downtime_reason,
                "Remarks": remarks,
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Add to dataframe
            st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([new_record])], ignore_index=True)
            
            # Save data
            save_data(st.session_state.df)
            
            st.success("Data submitted successfully!")
            
    # Display recent entries
    if not st.session_state.df.empty:
        st.subheader("Recent Entries")
        st.dataframe(st.session_state.df.sort_values(by="Timestamp", ascending=False).head(5), use_container_width=True)
    else:
        st.info("No data entries yet. Start by adding your first hourly record.")

# Tab 2: Search Records
with tab2:
    st.header("Search Production Records")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        search_date = st.date_input("Date (Optional)", value=None)
    with col2:
        search_shift = st.selectbox("Shift (Optional)", ["All", "Morning", "Afternoon", "Night"], index=0)
    with col3:
        search_machine = st.text_input("Machine ID (Optional)")
    
    search_operator = st.text_input("Operator Name (Optional)")
    
    if st.button("Search Records"):
        date_str = search_date.strftime("%Y-%m-%d") if search_date else None
        shift_value = None if search_shift == "All" else search_shift
        
        search_results = search_data(
            st.session_state.df, 
            date=date_str, 
            shift=shift_value,
            machine_id=search_machine if search_machine else None,
            operator_name=search_operator if search_operator else None
        )
        
        if not search_results.empty:
            st.subheader(f"Search Results: {len(search_results)} records found")
            st.dataframe(search_results, use_container_width=True)
        else:
            st.info("No records found matching your search criteria.")

# Tab 3: AI Assistant
with tab3:
    st.header("AI Production Assistant")
    st.markdown("""
    Ask questions about your production data using natural language. Examples:
    - "Show today's total defects by machine X"
    - "How many units did Operator Y produce last shift?"
    - "Which machine had the most downtime yesterday?"
    """)
    
    user_query = st.text_input("Enter your question:", key="ai_query")
    
    if st.button("Ask Assistant"):
        if user_query:
            with st.spinner("Processing your query..."):
                try:
                    # Get answer from Grok assistant
                    answer = process_ai_query(user_query, st.session_state.df)
                    
                    # Display answer
                    st.subheader("Answer")
                    st.markdown(answer)
                except Exception as e:
                    st.error(f"Error processing your query: {str(e)}")
        else:
            st.warning("Please enter a question to get started.")

# Tab 4: Predictions & Anomalies
with tab4:
    st.header("Downtime Prediction & Anomaly Detection")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Downtime Prediction")
        
        prediction_machine = st.text_input("Enter Machine ID for prediction")
        
        if st.button("Predict Downtime Risk"):
            if prediction_machine:
                if prediction_machine in st.session_state.df["Machine_ID"].values:
                    with st.spinner("Analyzing downtime patterns..."):
                        risk_score, hours = predict_downtime(st.session_state.df, prediction_machine)
                        
                        # Display prediction
                        st.metric("Downtime Risk", f"{risk_score}%")
                        st.markdown(f"**Machine {prediction_machine}** has a **{risk_score}%** risk of downtime in the next **{hours}** hours.")
                        
                        if risk_score > 70:
                            st.error("High risk of downtime! Consider preventive maintenance.")
                        elif risk_score > 30:
                            st.warning("Moderate risk of downtime. Monitor closely.")
                        else:
                            st.success("Low risk of downtime.")
                else:
                    st.error(f"Machine ID '{prediction_machine}' not found in the dataset.")
            else:
                st.warning("Please enter a Machine ID for prediction.")
    
    with col2:
        st.subheader("Anomaly Detection")
        
        if st.button("Detect Production Anomalies"):
            if not st.session_state.df.empty and len(st.session_state.df) > 5:  # Need some data for anomaly detection
                with st.spinner("Detecting anomalies in production data..."):
                    anomalies = detect_anomalies(st.session_state.df)
                    
                    if anomalies:
                        st.warning(f"Detected {len(anomalies)} anomalies in production data")
                        
                        for anomaly in anomalies:
                            st.markdown(f"**{anomaly['machine_id']}**: {anomaly['message']}")
                            st.markdown(f"*Confidence: {anomaly['confidence']}%*")
                    else:
                        st.success("No anomalies detected in the current production data.")
            else:
                st.info("Not enough data for anomaly detection. Please add more production records.")

# Tab 5: Export Data
with tab5:
    st.header("Export Production Data")
    
    if not st.session_state.df.empty:
        export_format = st.selectbox("Export Format", ["CSV"])
        
        if st.button("Export Data"):
            with st.spinner("Preparing data for export..."):
                export_file = export_data_csv(st.session_state.df)
                
                # Create download button
                st.download_button(
                    label="Download Data",
                    data=export_file,
                    file_name=f"manufacturing_data_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
    else:
        st.info("No data available to export. Please add production records first.")

# Tab 6: Import Data
with tab6:
    st.header("Import Production Data")
    
    st.markdown("""
    Import hourly sheet data from the CSV file in the attached_assets folder.
    
    The CSV file should have the following columns:
    - Date
    - Shift
    - Hour
    - Machine_ID
    - Operator_Name
    - Product_Name
    - Target_Output
    - Actual_Output
    - Cumulative_Output
    - Defects_Rework
    - Downtime_Minutes
    - Reason_for_Downtime
    - Operator_Remarks
    """)
    
    if st.button("Import Hourly Sheet Data"):
        with st.spinner("Importing data..."):
            success, message = import_hourly_sheet_data()
            
            if success:
                st.success(message)
                # Reload the data
                st.session_state.df = load_data()
                st.info("Data has been loaded. You can now use it in all other tabs.")
            else:
                st.error(message)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center'>
        <p>Manufacturing Hourly Sheet Tracking System | AI-Enhanced Production Monitor</p>
    </div>
    """, 
    unsafe_allow_html=True
)
