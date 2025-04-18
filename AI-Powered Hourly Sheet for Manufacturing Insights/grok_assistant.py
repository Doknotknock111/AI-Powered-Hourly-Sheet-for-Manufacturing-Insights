import os
import pandas as pd
import json
from datetime import datetime
# Removed OpenAI import since we're using direct data analysis

def process_ai_query(query, df):
    """
    Process a natural language query about manufacturing data without using external API.
    Simplified version that analyzes the data directly.
    
    Args:
        query (str): The natural language query from the user.
        df (DataFrame): The manufacturing data.
        
    Returns:
        str: The response to the query based on data analysis.
    """
    # Check if dataframe is empty
    if df.empty:
        return "There is no manufacturing data available yet. Please add some hourly records first."
    
    # Standardize query for easier matching
    query_lower = query.lower().strip()
    
    try:
        # BASIC DATA SUMMARY
        if any(keyword in query_lower for keyword in ["summary", "overview", "stats", "statistics"]):
            return generate_data_summary(df)
        
        # MACHINE SPECIFIC QUERIES
        elif "machine" in query_lower and any(machine_id.lower() in query_lower for machine_id in df['Machine_ID'].unique()):
            # Extract machine ID from query
            machine_id = None
            for m_id in df['Machine_ID'].unique():
                if m_id.lower() in query_lower:
                    machine_id = m_id
                    break
                    
            if machine_id:
                # Filter data for this machine
                machine_data = df[df['Machine_ID'] == machine_id]
                
                # Check for defects query
                if "defect" in query_lower:
                    # Check if query is for a specific date
                    if "today" in query_lower:
                        today = datetime.now().strftime("%Y-%m-%d")
                        today_data = machine_data[machine_data['Date'] == today]
                        if not today_data.empty:
                            total_defects = today_data['Defects'].sum()
                            return f"Machine {machine_id} had {total_defects} defects today."
                        else:
                            return f"No data available for Machine {machine_id} today."
                    else:
                        total_defects = machine_data['Defects'].sum()
                        return f"Machine {machine_id} had a total of {total_defects} defects across all recorded periods."
                
                # Check for downtime query
                elif "downtime" in query_lower:
                    total_downtime = machine_data['Downtime_Minutes'].sum()
                    return f"Machine {machine_id} had a total downtime of {total_downtime} minutes across all recorded periods."
                
                # Check for output query
                elif any(word in query_lower for word in ["output", "production", "units"]):
                    total_output = machine_data['Actual_Output'].sum()
                    target_output = machine_data['Target_Output'].sum()
                    efficiency = (total_output / target_output * 100) if target_output > 0 else 0
                    return (f"Machine {machine_id} produced {total_output} units out of {target_output} planned units, "
                            f"with an efficiency of {efficiency:.1f}%.")
                
                # General machine info
                else:
                    return generate_machine_summary(machine_data, machine_id)
        
        # OPERATOR SPECIFIC QUERIES
        elif "operator" in query_lower and any(operator.lower() in query_lower for operator in df['Operator_Name'].unique()):
            # Extract operator name from query
            operator_name = None
            for operator in df['Operator_Name'].unique():
                if operator.lower() in query_lower:
                    operator_name = operator
                    break
                    
            if operator_name:
                # Filter data for this operator
                operator_data = df[df['Operator_Name'] == operator_name]
                
                # Check for productivity query
                if any(word in query_lower for word in ["produce", "output", "units", "production"]):
                    if "last shift" in query_lower or "previous shift" in query_lower:
                        # Get most recent shift
                        recent_date = operator_data['Date'].max()
                        shifts = operator_data[operator_data['Date'] == recent_date]['Shift'].unique()
                        if len(shifts) > 0:
                            last_shift = shifts[-1]
                            shift_data = operator_data[(operator_data['Date'] == recent_date) & (operator_data['Shift'] == last_shift)]
                            total_output = shift_data['Actual_Output'].sum()
                            return f"Operator {operator_name} produced {total_output} units in their last recorded shift ({last_shift})."
                        else:
                            return f"No shift data available for Operator {operator_name}."
                    else:
                        total_output = operator_data['Actual_Output'].sum()
                        return f"Operator {operator_name} produced a total of {total_output} units across all recorded shifts."
                
                # General operator info
                else:
                    return generate_operator_summary(operator_data, operator_name)
        
        # SHIFT SPECIFIC QUERIES
        elif any(shift.lower() in query_lower for shift in ["morning", "afternoon", "night"]):
            # Extract shift from query
            shift = None
            for s in ["Morning", "Afternoon", "Night"]:
                if s.lower() in query_lower:
                    shift = s
                    break
                    
            if shift:
                # Filter data for this shift
                shift_data = df[df['Shift'] == shift]
                
                # Generate shift summary
                return generate_shift_summary(shift_data, shift)
        
        # DATE SPECIFIC QUERIES
        elif "today" in query_lower or "yesterday" in query_lower or "date" in query_lower:
            # Handle date queries
            if "today" in query_lower:
                date = datetime.now().strftime("%Y-%m-%d")
                date_data = df[df['Date'] == date]
                if not date_data.empty:
                    return generate_date_summary(date_data, "today")
                else:
                    return "No data available for today."
            else:
                return "I can only analyze data for specific dates that are in the dataset."
        
        # DEFECT ANALYSIS
        elif "defect" in query_lower or "quality" in query_lower:
            return generate_defect_analysis(df)
        
        # DOWNTIME ANALYSIS
        elif "downtime" in query_lower:
            if "most" in query_lower and "machine" in query_lower:
                # Get machine with most downtime
                machine_downtime = df.groupby('Machine_ID')['Downtime_Minutes'].sum().sort_values(ascending=False)
                if not machine_downtime.empty:
                    worst_machine = machine_downtime.index[0]
                    minutes = machine_downtime.iloc[0]
                    return f"Machine {worst_machine} had the most downtime with {minutes} minutes across all recorded periods."
                else:
                    return "No downtime data available."
            else:
                return generate_downtime_analysis(df)
        
        # GENERAL QUERIES
        else:
            return "I couldn't interpret your specific query. Try asking about machine performance, operator productivity, shift statistics, defects, or downtime."
    
    except Exception as e:
        # Handle errors gracefully
        return f"Error analyzing your query: {str(e)}"

# Helper functions for data analysis

def generate_data_summary(df):
    """Generate a summary of the manufacturing data."""
    try:
        unique_machines = df['Machine_ID'].nunique()
        unique_operators = df['Operator_Name'].nunique()
        total_production = df['Actual_Output'].sum()
        total_target = df['Target_Output'].sum()
        efficiency = (total_production / total_target * 100) if total_target > 0 else 0
        total_defects = df['Defects'].sum()
        defect_rate = (total_defects / total_production * 100) if total_production > 0 else 0
        total_downtime = df['Downtime_Minutes'].sum()
        
        return f"""
        Manufacturing Data Summary:
        - Total Records: {len(df)}
        - Date Range: {df['Date'].min()} to {df['Date'].max()}
        - Unique Machines: {unique_machines}
        - Unique Operators: {unique_operators}
        - Total Production: {total_production} units
        - Production Efficiency: {efficiency:.1f}%
        - Total Defects: {total_defects} units (Defect Rate: {defect_rate:.2f}%)
        - Total Downtime: {total_downtime} minutes
        """
    except Exception as e:
        return f"Error generating data summary: {str(e)}"

def generate_machine_summary(machine_data, machine_id):
    """Generate a summary for a specific machine."""
    try:
        total_hours = len(machine_data)
        total_production = machine_data['Actual_Output'].sum()
        total_target = machine_data['Target_Output'].sum()
        efficiency = (total_production / total_target * 100) if total_target > 0 else 0
        total_defects = machine_data['Defects'].sum()
        defect_rate = (total_defects / total_production * 100) if total_production > 0 else 0
        total_downtime = machine_data['Downtime_Minutes'].sum()
        operators = machine_data['Operator_Name'].unique()
        
        return f"""
        Machine {machine_id} Summary:
        - Operational Hours: {total_hours}
        - Total Production: {total_production} units
        - Production Efficiency: {efficiency:.1f}%
        - Total Defects: {total_defects} units (Defect Rate: {defect_rate:.2f}%)
        - Total Downtime: {total_downtime} minutes
        - Operators: {', '.join(operators)}
        """
    except Exception as e:
        return f"Error generating machine summary: {str(e)}"

def generate_operator_summary(operator_data, operator_name):
    """Generate a summary for a specific operator."""
    try:
        total_hours = len(operator_data)
        total_production = operator_data['Actual_Output'].sum()
        total_target = operator_data['Target_Output'].sum()
        efficiency = (total_production / total_target * 100) if total_target > 0 else 0
        total_defects = operator_data['Defects'].sum()
        defect_rate = (total_defects / total_production * 100) if total_production > 0 else 0
        machines = operator_data['Machine_ID'].unique()
        
        return f"""
        Operator {operator_name} Summary:
        - Work Hours: {total_hours}
        - Total Production: {total_production} units
        - Production Efficiency: {efficiency:.1f}%
        - Total Defects: {total_defects} units (Defect Rate: {defect_rate:.2f}%)
        - Machines Operated: {', '.join(machines)}
        """
    except Exception as e:
        return f"Error generating operator summary: {str(e)}"

def generate_shift_summary(shift_data, shift):
    """Generate a summary for a specific shift."""
    try:
        total_days = shift_data['Date'].nunique()
        total_production = shift_data['Actual_Output'].sum()
        total_target = shift_data['Target_Output'].sum()
        efficiency = (total_production / total_target * 100) if total_target > 0 else 0
        total_defects = shift_data['Defects'].sum()
        total_downtime = shift_data['Downtime_Minutes'].sum()
        
        return f"""
        {shift} Shift Summary:
        - Total Days: {total_days}
        - Total Production: {total_production} units
        - Production Efficiency: {efficiency:.1f}%
        - Total Defects: {total_defects} units
        - Total Downtime: {total_downtime} minutes
        """
    except Exception as e:
        return f"Error generating shift summary: {str(e)}"

def generate_date_summary(date_data, date_desc):
    """Generate a summary for a specific date."""
    try:
        total_production = date_data['Actual_Output'].sum()
        total_target = date_data['Target_Output'].sum()
        efficiency = (total_production / total_target * 100) if total_target > 0 else 0
        total_defects = date_data['Defects'].sum()
        total_downtime = date_data['Downtime_Minutes'].sum()
        machines = date_data['Machine_ID'].unique()
        operators = date_data['Operator_Name'].unique()
        
        return f"""
        Production Summary for {date_desc}:
        - Total Production: {total_production} units
        - Production Efficiency: {efficiency:.1f}%
        - Total Defects: {total_defects} units
        - Total Downtime: {total_downtime} minutes
        - Active Machines: {', '.join(machines)}
        - Active Operators: {', '.join(operators)}
        """
    except Exception as e:
        return f"Error generating date summary: {str(e)}"

def generate_defect_analysis(df):
    """Generate an analysis of defects across the manufacturing data."""
    try:
        if df['Defects'].sum() == 0:
            return "No defects have been recorded in the manufacturing data."
        
        # Calculate defect rates by machine
        machine_defects = df.groupby('Machine_ID').agg({
            'Defects': 'sum',
            'Actual_Output': 'sum'
        })
        machine_defects['Defect_Rate'] = machine_defects['Defects'] / machine_defects['Actual_Output'] * 100
        worst_machine = machine_defects.sort_values('Defect_Rate', ascending=False).iloc[0]
        
        # Calculate defect rates by operator
        operator_defects = df.groupby('Operator_Name').agg({
            'Defects': 'sum',
            'Actual_Output': 'sum'
        })
        operator_defects['Defect_Rate'] = operator_defects['Defects'] / operator_defects['Actual_Output'] * 100
        
        # Calculate defect rates by product
        product_defects = df.groupby('Product_Name').agg({
            'Defects': 'sum',
            'Actual_Output': 'sum'
        })
        product_defects['Defect_Rate'] = product_defects['Defects'] / product_defects['Actual_Output'] * 100
        
        return f"""
        Defect Analysis:
        - Total Defects: {df['Defects'].sum()} units
        - Overall Defect Rate: {df['Defects'].sum() / df['Actual_Output'].sum() * 100:.2f}%
        
        Machine with Highest Defect Rate:
        - Machine {worst_machine.name}: {worst_machine['Defect_Rate']:.2f}% ({worst_machine['Defects']} defects out of {worst_machine['Actual_Output']} units)
        
        Defect Distribution by Shift:
        - Morning: {df[df['Shift'] == 'Morning']['Defects'].sum()} defects
        - Afternoon: {df[df['Shift'] == 'Afternoon']['Defects'].sum()} defects
        - Night: {df[df['Shift'] == 'Night']['Defects'].sum()} defects
        """
    except Exception as e:
        return f"Error analyzing defects: {str(e)}"

def generate_downtime_analysis(df):
    """Generate an analysis of downtime across the manufacturing data."""
    try:
        if df['Downtime_Minutes'].sum() == 0:
            return "No downtime has been recorded in the manufacturing data."
        
        # Calculate downtime by machine
        machine_downtime = df.groupby('Machine_ID')['Downtime_Minutes'].sum().sort_values(ascending=False)
        
        # Calculate downtime by reason (if available)
        reason_downtime = df[df['Downtime_Reason'].notna() & (df['Downtime_Reason'] != '')]
        if not reason_downtime.empty:
            reason_data = reason_downtime.groupby('Downtime_Reason')['Downtime_Minutes'].sum().sort_values(ascending=False)
            top_reasons = reason_data.head(3)
            reasons_text = "\n".join([f"- {reason}: {minutes} minutes" for reason, minutes in top_reasons.items()])
        else:
            reasons_text = "- No downtime reasons provided in the data"
        
        return f"""
        Downtime Analysis:
        - Total Downtime: {df['Downtime_Minutes'].sum()} minutes
        
        Machines with Most Downtime:
        - {machine_downtime.index[0]}: {machine_downtime.iloc[0]} minutes
        {f"- {machine_downtime.index[1]}: {machine_downtime.iloc[1]} minutes" if len(machine_downtime) > 1 else ""}
        {f"- {machine_downtime.index[2]}: {machine_downtime.iloc[2]} minutes" if len(machine_downtime) > 2 else ""}
        
        Top Downtime Reasons:
        {reasons_text}
        
        Downtime Distribution by Shift:
        - Morning: {df[df['Shift'] == 'Morning']['Downtime_Minutes'].sum()} minutes
        - Afternoon: {df[df['Shift'] == 'Afternoon']['Downtime_Minutes'].sum()} minutes
        - Night: {df[df['Shift'] == 'Night']['Downtime_Minutes'].sum()} minutes
        """
    except Exception as e:
        return f"Error analyzing downtime: {str(e)}"

def analyze_production_issue(machine_id, downtime_reason, df):
    """
    Analyze a production issue and suggest solutions based on historical patterns.
    
    Args:
        machine_id (str): The machine ID with the issue.
        downtime_reason (str): The reason for downtime.
        df (DataFrame): The manufacturing data.
        
    Returns:
        str: Suggested solutions for the issue.
    """
    # Check if dataframe is empty
    if df.empty:
        return "There is no manufacturing data available for analysis."
    
    try:
        # Filter data for this machine
        machine_data = df[df['Machine_ID'] == machine_id]
        
        if machine_data.empty:
            return f"No data found for machine {machine_id}."
        
        # Check if we have downtime data
        if machine_data['Downtime_Minutes'].sum() == 0:
            return f"No downtime history available for machine {machine_id}."
        
        # Identify common issues for this machine
        downtime_counts = {}
        for _, row in machine_data.iterrows():
            reason = row.get('Downtime_Reason', '').strip()
            if reason and not pd.isna(reason):
                downtime_counts[reason] = downtime_counts.get(reason, 0) + 1
        
        # Get the most common issues
        common_issues = sorted(downtime_counts.items(), key=lambda x: x[1], reverse=True)
        
        # Check if current issue matches historical patterns
        current_reason = downtime_reason.strip() if downtime_reason else ""
        similar_issues = []
        
        for issue, count in common_issues:
            if current_reason.lower() in issue.lower() or issue.lower() in current_reason.lower():
                similar_issues.append((issue, count))
        
        # Generate solution based on the issue type
        solutions = []
        
        # General maintenance issues
        if any(keyword in current_reason.lower() for keyword in ["maintenance", "breakdown", "failure", "malfunction"]):
            solutions.append("1. Schedule immediate preventive maintenance to check mechanical components, electrical systems, and control units.")
            solutions.append("2. Review maintenance logs to identify recurring patterns and address root causes.")
            solutions.append("3. Consider implementing condition-based monitoring to detect early signs of failure.")
        
        # Tool or part issues
        elif any(keyword in current_reason.lower() for keyword in ["tool", "part", "component", "worn", "broken"]):
            solutions.append("1. Replace the affected tools or parts with new or reconditioned components.")
            solutions.append("2. Check alignment and calibration of all related components.")
            solutions.append("3. Review tool replacement schedule and adjust based on wear patterns.")
        
        # Calibration or quality issues
        elif any(keyword in current_reason.lower() for keyword in ["calibration", "alignment", "quality", "tolerance"]):
            solutions.append("1. Perform full machine calibration according to manufacturer specifications.")
            solutions.append("2. Check and adjust alignment of critical components.")
            solutions.append("3. Implement more frequent quality checks during production runs.")
        
        # Material-related issues
        elif any(keyword in current_reason.lower() for keyword in ["material", "raw", "input", "feed"]):
            solutions.append("1. Inspect material quality and ensure it meets specifications.")
            solutions.append("2. Check material feeding mechanism for obstructions or wear.")
            solutions.append("3. Consider adjusting machine settings to accommodate material variations.")
        
        # Operator-related issues
        elif any(keyword in current_reason.lower() for keyword in ["operator", "human", "setup", "configuration"]):
            solutions.append("1. Provide additional training for operators on proper machine setup and operation.")
            solutions.append("2. Review and update standard operating procedures for clarity.")
            solutions.append("3. Implement checklist system for machine setup and changeover.")
        
        # Software or control issues
        elif any(keyword in current_reason.lower() for keyword in ["software", "control", "program", "plc", "system"]):
            solutions.append("1. Check and update machine control software/firmware to latest version.")
            solutions.append("2. Verify sensor functions and replace any malfunctioning sensors.")
            solutions.append("3. Backup and restore control programs after validating their integrity.")
        
        # Default solutions if no specific category matches
        if not solutions:
            solutions.append("1. Perform general inspection of the machine and its components.")
            solutions.append("2. Review operating conditions and parameters for abnormalities.")
            solutions.append("3. Consult machine manufacturer documentation for troubleshooting guidance.")
            
        # Add historical context if available
        historical_context = ""
        if similar_issues:
            historical_context = f"\nThis issue appears similar to {len(similar_issues)} previous incidents with machine {machine_id}."
            if len(similar_issues) > 0:
                historical_context += f" The most common similar issue was '{similar_issues[0][0]}' which occurred {similar_issues[0][1]} times."
        
        # Build final response
        response = f"""
        Analysis for Machine {machine_id} - {current_reason}:
        
        Suggested Solutions:
        {chr(10).join(solutions)}
        {historical_context}
        
        Machine Efficiency: {calculate_machine_efficiency(machine_data):.1f}%
        Total Downtime: {machine_data['Downtime_Minutes'].sum()} minutes
        """
        
        return response
    
    except Exception as e:
        # Handle errors gracefully
        return f"Error analyzing production issue: {str(e)}"

def calculate_machine_efficiency(machine_data):
    """Calculate the efficiency percentage for a machine."""
    total_output = machine_data['Actual_Output'].sum()
    total_target = machine_data['Target_Output'].sum()
    if total_target > 0:
        return (total_output / total_target) * 100
    return 0
