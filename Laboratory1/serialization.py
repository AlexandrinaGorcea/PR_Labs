def custom_serialize(data):
    if isinstance(data, dict):
        return 'D:' + ';'.join(f'{custom_serialize(k)}:{custom_serialize(v)}' for k, v in data.items())
    elif isinstance(data, list):
        return 'L:' + ';'.join(map(custom_serialize, data))
    elif isinstance(data, str):
        return f'S:{len(data)}:{data}'
    elif isinstance(data, bool):
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
        if s.startswith('D:', start):
            result = {}
            i = start + 2
            while i < len(s):
                key, i = parse_item(s, i)
                if i < len(s) and s[i] == ':':
                    value, i = parse_item(s, i + 1)
                    result[key] = value
                if i < len(s) and s[i] == ';':
                    i += 1
                else:
                    break
            return result, i
        elif s.startswith('L:', start):
            result = []
            i = start + 2
            while i < len(s):
                item, i = parse_item(s, i)
                result.append(item)
                if i < len(s) and s[i] == ';':
                    i += 1
                else:
                    break
            return result, i
        elif s.startswith('S:', start):
            colon = s.index(':', start + 2)
            length = int(s[start+2:colon])
            end = colon + 1 + length
            return s[colon+1:end], end
        elif s.startswith('I:', start):
            end = s.find(';', start)
            if end == -1:
                end = len(s)
            return int(s[start+2:end]), end
        elif s.startswith('F:', start):
            end = s.find(';', start)
            if end == -1:
                end = len(s)
            return float(s[start+2:end]), end
        elif s.startswith('B:', start):
            return s[start+2] == 'T', start + 3
        elif s.startswith('N', start):
            return None, start + 1
        else:
            raise ValueError(f"Invalid serialized data: {s[start:]}")

    result, _ = parse_item(data)
    return result


#  test cases
test_cases = [
    {"a": 1, "b": [2, 3]},
    [1, "two", [3, 4]],
    [None, True, False, 3.14],
]

for i, case in enumerate(test_cases):
    print(f"\nTest case {i + 1}:")
    serialized = custom_serialize(case)
    print("Serialized:", serialized)
    deserialized = custom_deserialize(serialized)
    print("Deserialized:", deserialized)
    print("Original equals deserialized:", case == deserialized)