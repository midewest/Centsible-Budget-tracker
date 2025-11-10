"""Utility functions and template filters."""

def hex_to_rgb(hex_color):
    """Convert hex color to RGB components string.
    
    Args:
        hex_color (str): Hex color code with or without #
        
    Returns:
        str: RGB components as 'R, G, B'
    """
    # Remove hash if present
    hex_color = hex_color.lstrip('#')
    
    # Handle both short (#RGB) and long (#RRGGBB) hex formats
    if len(hex_color) == 3:
        hex_color = ''.join(c * 2 for c in hex_color)
    
    # Convert hex to RGB components
    try:
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return f"{r}, {g}, {b}"
    except (ValueError, IndexError):
        # Return primary color RGB if conversion fails
        return "16, 185, 129"  # Primary green color

def month_name(month_number):
    """Convert month number to month name.
    
    Args:
        month_number (int): Month number (1-12)
        
    Returns:
        str: Month name
    """
    months = [
        'January', 'February', 'March', 'April',
        'May', 'June', 'July', 'August',
        'September', 'October', 'November', 'December'
    ]
    try:
        return months[int(month_number) - 1]
    except (ValueError, IndexError):
        return 'Unknown'