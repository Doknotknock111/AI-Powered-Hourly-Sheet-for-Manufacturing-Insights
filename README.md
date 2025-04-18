# Manufacturing Hourly Sheet Tracker

An AI-enhanced system for tracking and analyzing manufacturing production data through hourly sheets. This application helps manufacturing facilities monitor machine performance, production efficiency, quality metrics, and detect anomalies without requiring external visualization components.

## Features

- **Hourly Data Entry**: Record production metrics including machine output, downtime, defects, and operator remarks
- **AI-Powered Assistant**: Query your manufacturing data using natural language to get insights and analytics
- **Downtime Prediction**: Machine learning models to predict potential machine failures and downtime
- **Anomaly Detection**: Automatically identify unusual patterns in production data
- **Data Search & Filtering**: Find and analyze production records by date, shift, machine, or operator
- **CSV Import/Export**: Import data from standard hourly sheet formats and export for external analysis

## System Components

### Core Modules

- **Data Management**: Storage and retrieval of production records
- **AI Assistant**: Natural language processing of production queries
- **Prediction Models**: Machine learning for downtime prediction
- **Anomaly Detection**: Statistical analysis to identify unusual production patterns

### Technology Stack

- **Framework**: Streamlit for web interface
- **Data Processing**: Pandas, NumPy
- **Machine Learning**: Scikit-learn, joblib

## Installation

### Prerequisites

- Python 3.8+
- Pip package manager

### Setup

1. Clone or download this repository
2. Install required packages:
   ```
   pip install streamlit pandas numpy scikit-learn joblib
   ```
3. Ensure you have the sample data file `hourly_sheet.csv` in your project directory or in an `attached_assets` subfolder

### Configuration (Optional)

Create a `.streamlit/config.toml` file with the following content for local development:

```toml
[server]
headless = false
address = "localhost"
port = 8501
```

## Running the Application

1. Navigate to the project directory
2. Run the application:
   ```
   streamlit run app.py
   ```
3. Access the web interface at http://localhost:8501 (or the port specified in your config)

## Data Structure

### Input Format

The hourly sheet CSV file should have the following structure:
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

### Database Storage

The application stores all data in a `manufacturing_data.csv` file, which is created automatically when you:
- Submit your first data entry form
- Import data from the hourly sheet CSV

## Usage Guide

### Data Entry

1. Navigate to the "Data Entry" tab
2. Fill in all required fields (Machine ID, Operator Name, Product Name)
3. Enter production metrics for the current hour
4. Click "Submit Hourly Data"

### Importing Data

1. Navigate to the "Import Data" tab
2. Ensure your hourly sheet CSV file is in the correct format and location
3. Click "Import Hourly Sheet Data"

### Querying the AI Assistant

1. Navigate to the "AI Assistant" tab
2. Type natural language questions about your production data:
   - "Show machine summary for Machine X"
   - "What's the total production by shift?"
   - "Which machine had the most downtime?"

### Predicting Downtime

1. Navigate to the "Predictions & Anomalies" tab
2. Enter a Machine ID
3. Click "Predict Downtime Risk" to see the probability of machine failure

### Detecting Anomalies

1. Navigate to the "Predictions & Anomalies" tab
2. Click "Detect Production Anomalies" to find unusual patterns

## Troubleshooting

- **Import File Not Found**: Ensure the `hourly_sheet.csv` file is in the project root or in an `attached_assets` subfolder
- **Empty Production Data**: Ensure you've either imported data or added records through the Data Entry form
- **Prediction/Anomaly Detection Issues**: These features require enough historical data to work properly (at least 5 records)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

*Manufacturing Hourly Sheet Tracking System | AI-Enhanced Production Monitor*
