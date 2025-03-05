
from .memory import MemorySessionImp
from .base import IBaseSession


class Session:

    def __init__(self, app=None, interface: IBaseSession = None):
        self.interface = None
        if app:
            self.init_app(app, interface)

    @property
    def expiry(self):
        """
        session 过期时间
        """
        return self.interface.expiry if self.interface else None

    def init_app(self, app, interface: IBaseSession):
        self.interface = interface or MemorySessionImp()
        if not hasattr(app.ctx, "extensions"):
            app.ctx.extensions = {}

        app.ctx.extensions[self.interface.session_name] = self  # session_name defaults to 'session'

        # @app.middleware('request')
        async def add_session_to_request(request):
            """Before each request initialize a session
            using the client's request."""
            await self.interface.open(request)

        # @app.middleware('response')
        async def save_session(request, response):
            """After each request save the session, pass
            the response to set client cookies.
            """
            await self.interface.save(request, response)

        app.request_middleware.appendleft(add_session_to_request)
        app.response_middleware.append(save_session)
