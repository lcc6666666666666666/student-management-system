def success(data=None, message: str = "success", code: int = 0):
    return {"code": code, "message": message, "data": data}
