def helper_function(data):
    """Helper function to process data"""
    if isinstance(data, list):
        return [x * 2 for x in data]
    elif isinstance(data, str):
        return data.upper()
    else:
        return data