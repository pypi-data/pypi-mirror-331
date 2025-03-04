from irawatch.trace_pb2 import KeyValue, AnyValue, ArrayValue, KeyValueList


def convert_to_any_value(value):
    if isinstance(value, str):
        return AnyValue(string_value=value)
    elif isinstance(value, int):
        return AnyValue(int_value=value)
    elif isinstance(value, bool):
        return AnyValue(bool_value=value)
    elif isinstance(value, float):
        return AnyValue(double_value=value)
    elif isinstance(value, bytes):
        return AnyValue(bytes_value=value)
    elif isinstance(value, list):
        return AnyValue(array_value=ArrayValue(values=[convert_to_any_value(v) for v in value]))
    elif isinstance(value, dict):
        return AnyValue(kvlist_value=KeyValueList(values=convert_dict_to_key_values(value)))
    else:
        raise ValueError(f"Unsupported type for value: {value}")


def convert_dict_to_key_values(attributes_dict):
    key_value_list = []
    for key, value in attributes_dict.items():
        key_value_list.append(KeyValue(key=key, value=convert_to_any_value(value)))
    return key_value_list
