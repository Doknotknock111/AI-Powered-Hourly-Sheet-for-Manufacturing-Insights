from datetime import datetime, time

def get_shift_from_time(current_time):
    """
    Determine the shift (Morning, Afternoon, Night) based on the current time.
    
    Args:
        current_time: A datetime.time object or a datetime.datetime object
        
    Returns:
        str: The shift name (Morning, Afternoon, or Night)
    """
    # If it's a datetime object, extract the time
    if isinstance(current_time, datetime):
        current_time = current_time.time()
    
    # Define shift times
    morning_start = time(6, 0)
    afternoon_start = time(14, 0)
    night_start = time(22, 0)
    
    # Determine the shift
    if morning_start <= current_time < afternoon_start:
        return "Morning"
    elif afternoon_start <= current_time < night_start:
        return "Afternoon"
    else:
        return "Night"

def calculate_efficiency(actual, target):
    """
    Calculate production efficiency as a percentage.
    
    Args:
        actual (float): Actual output
        target (float): Target output
        
    Returns:
        float: Efficiency percentage
    """
    if target == 0:
        return 0
    return (actual / target) * 100

def format_percentage(value, decimal_places=1):
    """
    Format a decimal as a percentage string.
    
    Args:
        value (float): Value to format
        decimal_places (int): Number of decimal places
        
    Returns:
        str: Formatted percentage string
    """
    return f"{value:.{decimal_places}f}%"

def calculate_defect_rate(defects, output):
    """
    Calculate defect rate as a percentage.
    
    Args:
        defects (int): Number of defects
        output (int): Total output
        
    Returns:
        float: Defect rate percentage
    """
    if output == 0:
        return 0
    return (defects / output) * 100

def format_duration(minutes):
    """
    Format minutes as hours and minutes.
    
    Args:
        minutes (int): Duration in minutes
        
    Returns:
        str: Formatted duration string
    """
    hours = minutes // 60
    mins = minutes % 60
    
    if hours > 0:
        return f"{hours}h {mins}m"
    else:
        return f"{mins}m"

def parse_date_string(date_str):
    """
    Parse a date string into a datetime object.
    
    Args:
        date_str (str): Date string in format YYYY-MM-DD
        
    Returns:
        datetime.date: Date object
    """
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except:
        return None
