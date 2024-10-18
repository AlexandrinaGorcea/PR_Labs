def custom_serialize(data):
    if isinstance(data, dict):
        return 'D:' + ';'.join(f'{custom_serialize(k)}:{custom_serialize(v)}' for k, v in data.items())
    elif isinstance(data, list):
        return 'L:' + ';'.join(custom_serialize(item) for item in data)
    elif isinstance(data, str):
        return f'S:{len(data)}:{data}'
    elif isinstance(data, bool):  # Check for bool before int
        return f'B:{"T" if data else "F"}'
    elif isinstance(data, int):
        return f'I:{data}'
    elif isinstance(data, float):
        return f'F:{data}'
    elif data is None:
        return 'N'
    else:
        raise TypeError(f"Object of type {type(data)} is not serializable")

def custom_deserialize(data):
    def parse_item(s, start=0):
        print(f"Parsing from index {start}: {s[start:]}")
        if s.startswith('D:', start):  # Parsing dictionary
            print("Parsing dictionary")
            result = {}
            i = start + 2
            while i < len(s) and s[i] != ';':
                key, i = parse_item(s, i)
                if i < len(s) and s[i] == ':':
                    value, i = parse_item(s, i + 1)
                    result[key] = value
                    print(f"Added key-value pair: {key}: {value}")
                if i < len(s) and s[i] == ';':
                    i += 1
            print(f"Finished dictionary: {result}")
            return result, i
        elif s.startswith('L:', start):  # Parsing list
            print("Parsing list")
            result = []
            i = start + 2
            while i < len(s) and s[i] != ';':
                item, i = parse_item(s, i)
                result.append(item)
                print(f"Added item to list: {item}")
                if i < len(s) and s[i] == ';':
                    i += 1
            print(f"Finished list: {result}")
            return result, i
        elif s.startswith('S:', start):  # Parsing string
            colon = s.index(':', start + 2)
            length = int(s[start+2:colon])
            result = s[colon+1:colon+1+length]
            print(f"Parsed string: {result}")
            return result, colon+1+length
        elif s.startswith('I:', start):  # Parsing integer
            end = s.find(';', start)
            if end == -1:
                end = len(s)
            result = int(s[start+2:end])
            print(f"Parsed integer: {result}")
            return result, end
        elif s.startswith('F:', start):  # Parsing float
            end = s.find(';', start)
            if end == -1:
                end = len(s)
            result = float(s[start+2:end])
            print(f"Parsed float: {result}")
            return result, end
        elif s.startswith('B:', start):  # Parsing boolean
            result = s[start+2] == 'T'
            print(f"Parsed boolean: {result}")
            return result, start + 3
        elif s.startswith('N', start):  # Parsing None
            print("Parsed None")
            return None, start + 1
        else:
            raise ValueError(f"Invalid serialized data: {s[start:]}")

    result, _ = parse_item(data)
    return result

# Wrapper function to handle top-level list
def custom_deserialize_wrapper(data):
    if data.startswith('L:'):
        result = []
        i = 2
        while i < len(data):
            item, i = custom_deserialize(data[i:])
            result.append(item)
            if i < len(data) and data[i] == ';':
                i += 1
        return result
    else:
        return custom_deserialize(data)

# Test the serialization and deserialization
test_data = [{"key1": "val1"}, {"key2": 2}, [1, 2, 3], None, True, 3.14]
serialized = custom_serialize(test_data)
print("Serialized data:", serialized)
deserialized = custom_deserialize(serialized)
print("Deserialized data:", deserialized)
print("Original data equals deserialized data:", test_data == deserialized)