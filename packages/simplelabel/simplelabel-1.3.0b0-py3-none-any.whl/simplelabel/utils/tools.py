from typing import Dict


# cube.cube_data.Record -> Dict[str, str]
def record_to_dict(data) -> Dict[str, str]:
    if isinstance(data, dict):
        records = data.get('record', {})
        field_mapping = data.get('field_mapping', {})
    elif hasattr(data, 'record') and hasattr(data, 'field_mapping'):
        records = data.record
        field_mapping = data.field_mapping
    else:
        raise ValueError("Unsupported input data structure")

    result = {}
    for field_name, field_identifier in field_mapping.items():
        if field_identifier in records:
            result[field_name] = str(records[field_identifier]).strip()
        else:
            result[field_name] = ""
    return result

