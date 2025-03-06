def remove_excluded_fields(data, excluded_fields):
    if isinstance(data, dict):
        #* Remove excluded keys at the current level
        for field in excluded_fields:
            data.pop(field, None)
        #* Recursively process nested dictionaries
        for key, value in data.items():
            remove_excluded_fields(value, excluded_fields)
    elif isinstance(data, list):
        #* Recursively process each item in the list
        for item in data:
            remove_excluded_fields(item, excluded_fields)