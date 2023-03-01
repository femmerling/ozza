import logging
from fastapi import FastAPI
from app.api import resource

logger = logging.getLogger(__name__)

app_parameters = {
    'title': "Ozza Web API",
    'description': "Web interface to Ozza datastore",
    'version': '0.1.0',
    'docs_url': '/swagger',
    'redoc_url': '/docs'
}


app = FastAPI(**app_parameters)


@app.get('/healthcheck')
def health_check():
    return {"status": "OK"}


app.include_router(resource.router, tags=['resource'], prefix='/resource')
