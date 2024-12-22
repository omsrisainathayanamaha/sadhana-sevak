from typing import Any, List, Generator

def extract_floats(input_list: Any) -> List[float]:
    def process_nested(item):
        if isinstance(item, list):
            # Check if it's a list of only floats
            if all(isinstance(x, float) for x in item):
                return item
            else:
                # Process mixed-type lists
                return extract_floats(item)
        elif isinstance(item, Generator):
            # Convert generator to list and process
            return extract_floats(list(item))
        return []

    if isinstance(input_list, list):
        floats_only = []
        for element in input_list:
            if isinstance(element, (list, Generator)):
                nested_result = process_nested(element)
                if nested_result:
                    return nested_result  # Return immediately if list of floats found
            elif isinstance(element, float):
                floats_only.append(element)
        return floats_only
    elif isinstance(input_list, Generator):
        return extract_floats(list(input_list))
    return []
