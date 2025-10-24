import json

def check_filters(filepath, user_filters):
    """
    Load dietary analysis from JSON and print results for selected filters.
    
    Args:
        filepath (str): Path to the JSON file containing dietary analysis
        user_filters (list): List of filter numbers (1-8) to display
    
    Returns:
        dict: Complete dietary analysis dictionary
    """
    # Load JSON file into dictionary
    try:
        with open(filepath, 'r') as file:
            data_dict = json.load(file)
        print(f"JSON data successfully loaded from '{filepath}'.\n")
    except Exception as e:
        print(f"Error loading file: {e}")
        raise
    
    # Filter mapping
    filters = {
        1: "Anti-Inflammatory",
        2: "Low-Sugar",
        3: "Nut Allergy",
        4: "Halal",
        5: "Gluten-Free",
        6: "Lactose Intolerant",
        7: "Vegan",
        8: "Vegetarian"
    }
    
    # Print selected filters
    print(f"There are {len(user_filters)} filters:")
    for index, filter_num in enumerate(user_filters, start=1):
        filter_name = filters[filter_num]
        filter_data = data_dict['dietary_analysis'][filter_name]
        print(f"{index}. {filter_name}")
        print(filter_data)
        print()
    
    return data_dict