from datetime import datetime
import pytz

def get_ist_datetime_str() -> str:
    """
    Returns current IST date/time as a string.
    """
    ist = pytz.timezone("Asia/Kolkata")
    now_ist = datetime.now(ist)
    return now_ist.strftime("%Y-%m-%d %H:%M:%S")
