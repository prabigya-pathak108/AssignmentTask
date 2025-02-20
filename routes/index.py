from routes import api_routes,homepage


def register_routes(app):
    app.include_router(
        router=api_routes.router,
        prefix='/api',
        responses={404: {'description': 'Not found'}},
    ),
    app.include_router(
    router=homepage.router,
    prefix='',  # No trailing slash here
    responses={404: {'description': 'Not found'}})


