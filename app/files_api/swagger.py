import uuid


def swagger_create_files_response():
    return {
        200: {
            "description": "An empty file has been created successfully.",
            "content": {
                "application/json": {
                    "example": {
                        "file_path": f"{uuid.uuid4()}.pdf"
                    }
                },
            }
        },
        400: {
            "description": "There is an error in the request (for example, the Upload-Length or file name is missing).",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Upload-Length header is required."
                    }
                }
            }
        }
    }


def swagger_head_uuid_response():
    return {
        200: {
            "description": "Information about the file.",
            "content": None,
            "headers": {
                "Upload-Offset": {
                    "description": "The current size of the file being uploaded.",
                    "type": "string",
                }
            }
        },
        404: {
            "description": "File not found.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "File not found"
                    }
                }
            }
        }
    }


def swagger_post_uuid_response():
    return {
        200: {
            "description": "Uploading a chunk to local storage",
            "content": {
                "application/json": {
                    "example": {
                        "operation": "upload",
                        "current_offset": 10234,
                        "file_id": f"{uuid.uuid4()}.pdf"
                    }
                },
            },
            "headers": {
                "Upload-Offset": {
                    "description": "The current size of the file being uploaded.",
                    "type": "string",
                }
            }
        },
        201: {
            "description": "Uploading a chunk to cloud storage",
            "content": {
                "application/json": {
                    "example": {
                        'uploaded': False,
                        "current_offset": 10234,
                        "file_id": f"{uuid.uuid4()}.pdf"
                    }
                },
            }
        },
        400: {
            "description": "There is an error in the request (for example, the Upload-Length or file name is missing).",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Upload-Offset header is missing."
                    }
                }
            }
        },
        404: {
            "description": "File not found.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "File not found"
                    }
                }
            }
        }
    }


def download_file_response():
    return {
        200: {
            "description": "Redirects to the signed URL to download the file",
            "content": {
                "application/json": {
                    "example": {
                        "id": f"{uuid.uuid4()}",
                        "original_name": "example_file.xlsx",
                        "size": 12345,
                        "format": "xlsx",
                        "uploaded": True,
                        "download_url": "https://your-signed-url.com"
                    }
                }
            }
        },
        400: {
            "description": "Bad Request",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "The file is in the process of being uploaded to cloud storage"
                    }
                }
            }
        },
        404: {
            "description": "File not found",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "File not found in cloud storage"
                    }
                }
            }
        },
    }
