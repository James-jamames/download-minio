from .api import collections
form .api import download

def created_routes(app):
    
    app.include_router(
        collections.router, 
        prefix='/api/collections', 
        tags=['Collections']
        )

    app.include_router(
        download.router,
        prefix="/api/download",
        tags=['Download']
    )
    
    return app