def setup_basic_params(name: str = "Ozza App") -> dict:
    return {
        "title": f"{name} public API",
        "description": "{svc_name} public api",
        "version": "0.1.0",
        "docs_url": "/swagger",
        "redoc_url": "/docs",
        "openapi_prefix": "/ozza/"
    }
