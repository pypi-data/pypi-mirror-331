import time
import datetime
import abc
import uuid
from co6co.utils import log
from co6co.storage.Dict import CallbackDict
try:
    import ujson
except ImportError:
    import json as ujson


def get_request_container(request):
    """
    用于获取请求的容器对象
    """
    return request.ctx.__dict__ if hasattr(request, "ctx") else request


class SessionDict(CallbackDict):
    def __init__(self, initial=None, sid=None):
        def on_update(self):
            self.modified = True

        super().__init__(initial, on_update)

        self.sid = sid
        self.modified = False


class IBaseSession(metaclass=abc.ABCMeta):
    # this flag show does this Interface need request/response middleware hooks

    def __init__(
        # 会话的过期时间，单位为秒
        self, expiry: int,
        # 存储会话数据时使用的键前缀
        prefix: str,
        # 头部名称，可能用于自定义请求头或响应头
        head_name: str,
        # 用于设置 Cookie 的 SameSite 属性
        samesite,
        # 会话对象在请求容器中的名称
        session_name,
        # 是否使用安全的 Cookie（仅通过 HTTPS 传输）
        secure,
    ):

        self.expiry = expiry
        self.prefix = prefix
        self.head_name = head_name
        self.samesite = samesite
        self.session_name = session_name
        self.secure = secure

    @staticmethod
    def _calculate_expires(expiry):
        expires = time.time() + expiry
        return datetime.datetime.fromtimestamp(expires)

    @abc.abstractmethod
    async def _get_value(self, prefix: str, sid: str):
        """
        Get value from datastore. Specific implementation for each datastore.

        Args:
            prefix:
                A prefix for the key, useful to namespace keys.
            sid:
                a uuid in hex string
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def _delete_key(self, key: str):
        """Delete key from datastore"""
        raise NotImplementedError

    @abc.abstractmethod
    async def _set_value(self, key: str, data: SessionDict):
        """Set value for datastore"""
        raise NotImplementedError

    def getSid(self, request):
        sid = request.headers.get(self.head_name)
        return sid

    async def open(self, request) -> SessionDict:
        """
        Opens a session onto the request. Restores the client's session
        from the datastore if one exists.The session data will be available on
        `request.session`. 
        Args:
            request (sanic.request.Request):
                The request, which a sessionwill be opened onto.

        Returns:
            SessionDict:
                the client's session data,
                attached as well to `request.session`.
        """

        sid = self. getSid(request)
        if not sid:
            sid = uuid.uuid4().hex
            session_dict = SessionDict(sid=sid)
        else:
            val = await self._get_value(self.prefix, sid)

            if val is not None:
                data = ujson.loads(val)
                session_dict = SessionDict(data, sid=sid)
            else:
                session_dict = SessionDict(sid=sid)

        # attach the session data to the request, return it for convenience
        req = get_request_container(request)
        req[self.session_name] = session_dict
        return session_dict

    async def save(self, request, response) -> None:
        """Saves the session to the datastore.

        Args:
            request (sanic.request.Request):
                The sanic request which has an attached session.
            response (sanic.response.Response):
                The Sanic response. Cookies with the appropriate expiration
                will be added onto this response.

        Returns:
            None
        """
        req = get_request_container(request)
        if self.session_name not in req:
            return

        key = self.prefix + req[self.session_name].sid
        if not req[self.session_name]:
            await self._delete_key(key)

        val = ujson.dumps(dict(req[self.session_name]))
        await self._set_value(key, val)
