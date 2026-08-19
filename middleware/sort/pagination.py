def pagination(page: int, limit: int = 10) -> dict:
    skip = (page - 1) * limit
    return {
        "skip": skip,
        "limit": limit
    }