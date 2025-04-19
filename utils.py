import datetime

def format_currency(value):
    """Format a value as currency (IDR)."""
    if value is None:
        return 'Rp 0'
    return f"Rp {float(value):,.2f}"

def format_percentage(value):
    """Format a value as percentage."""
    if value is None:
        return '0%'
    return f"{float(value):.2f}%"

def format_date(date_str):
    """Format a date string to a more readable format."""
    try:
        date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d')
        return date_obj.strftime('%d %b %Y')
    except:
        return date_str

def calculate_growth(current, previous):
    """Calculate growth percentage between two values."""
    if previous == 0:
        return 100 if current > 0 else 0
    return ((current - previous) / previous) * 100
