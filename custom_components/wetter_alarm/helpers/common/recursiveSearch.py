def recursive_search(d, key):
    if key in d:
        return d[key]
    for k, v in d.items():
        if isinstance(v, dict):
            result = recursive_search(v, key)
            if result is not None:
                return result
    return None