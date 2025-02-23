from routes import api_routes,homepage


def register_routes(app):
    """
    Register the API and homepage routes with the FastAPI application.

    Args:
        app (FastAPI): The FastAPI application instance to which routes will be added.

    Includes:
        - API routes prefixed with '/api' to handle various API requests.
        - Homepage routes with no prefix, serving the main application interface.

    Each router includes a default response for 404 errors with a description 'Not found'.
    """

    app.include_router(
        router=api_routes.router,
        prefix='/api',
        responses={404: {'description': 'Not found'}},
    ),
    app.include_router(
    router=homepage.router,
    prefix='',  # No trailing slash here
    responses={404: {'description': 'Not found'}})


