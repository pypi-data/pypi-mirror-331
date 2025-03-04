from dependency_injector.wiring import Provide, inject
from rest_framework.decorators import api_view


def inject_controller(controller_key, methods):
    def decorator(func):
        @api_view(methods)
        @inject
        def wrapper(request, controller=Provide[controller_key], *args, **kwargs):
            return func(request, controller.provider(), *args, **kwargs)

        return wrapper

    return decorator
