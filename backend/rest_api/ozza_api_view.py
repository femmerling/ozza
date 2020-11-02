from sanic.views import HTTPMethodView

class OzzaApiView(HTTPMethodView):

    def dispatch_request(self, request, service=None, *args, **kwargs, ):
        handler = getattr(self, request.method.lower(), None)
        request.ctx.service = service
        return handler(request, *args, **kwargs)

    @classmethod
    def as_view(cls, *class_args, **class_kwargs):

        def view(*args, **kwargs):
            self = view.view_class()
            return self.dispatch_request(service=class_args[0], *args, **kwargs)

        if cls.decorators:
            view.__module__ = cls.__module__
            for decorator in cls.decorators:
                view = decorator(view)

        view.view_class = cls
        view.__doc__ = cls.__doc__
        view.__module__ = cls.__module__
        view.__name__ = cls.__name__
        return view