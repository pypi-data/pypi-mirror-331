def get_object(object_name: str):
    """Return a json representation of a beacon `object`"""
    return {"__type__": "object", "name": object_name}
