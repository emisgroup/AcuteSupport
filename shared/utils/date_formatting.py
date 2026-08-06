import pandas as pd

def parse_uk_datetime(series):
    """Parse UK format datetimes DD/MM/YYYY HH:MM:SS."""
    return pd.to_datetime(series, format='%d/%m/%Y %H:%M:%S', errors='coerce')

def format_duration_dhms(seconds):
    """Format duration in seconds into '[X days, ][Y hrs, ][Z mins]' format."""
    if pd.isna(seconds) or seconds is None:
        return 'N/A'
    try:
        s = int(round(float(seconds)))
    except (ValueError, TypeError):
        return 'N/A'
    if s < 0:
        return 'N/A'
    
    days, rem = divmod(s, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, _ = divmod(rem, 60)
    
    parts = []
    if days > 0:
        parts.append(f"{days} day" if days == 1 else f"{days} days")
    if hours > 0:
        parts.append(f"{hours} hr" if hours == 1 else f"{hours} hrs")
    if minutes > 0 or not parts:
        parts.append(f"{minutes} min" if minutes == 1 else f"{minutes} mins")
    return ", ".join(parts)

def format_duration(seconds):
    """Alias for format_duration_dhms which is sometimes called format_duration."""
    # Some files use this variant:
    if pd.isna(seconds):
        return ''
    try:
        s = int(round(float(seconds)))
    except (ValueError, TypeError):
        return ''
    if s <= 0:
        return ''
    minutes = s // 60
    days = minutes // (24 * 60)
    minutes_rem = minutes - days * 24 * 60
    hours = minutes_rem // 60
    mins = minutes_rem - hours * 60
    parts = []
    if days > 0:
        parts.append(f"{days} days")
    if hours > 0:
        parts.append(f"{hours} hrs")
    if mins > 0:
        parts.append(f"{mins} mins")
    return ', '.join(parts)
