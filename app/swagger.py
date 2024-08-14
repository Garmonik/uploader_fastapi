def root_swagger():
    return {
        200: {
            "description": "Root URL",
            "content": {
                "application/json": {
                    "example": {
                        "message": "This is root url"
                    }
                }
            }
        }
    }