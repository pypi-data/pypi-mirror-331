from .base import IBaseSession
from co6co.storage.Dict import ExpiringDict


class MemorySessionImp(IBaseSession):
    def __init__(
        self,
        expiry: int = 2592000,
        head_name: str = "session",
        prefix: str = "session:",
        samesite: str = None,
        session_name="Session",
        secure: bool = False,
    ):

        super().__init__(
            expiry=expiry,
            prefix=prefix,
            head_name=head_name,
            samesite=samesite,
            session_name=session_name,
            secure=secure,
        )
        self.session_store = ExpiringDict()

    async def _get_value(self, prefix, sid):
        return self.session_store.get(self.prefix + sid)

    async def _delete_key(self, key):
        if key in self.session_store:
            self.session_store.delete(key)

    async def _set_value(self, key, data):
        self.session_store.set(key, data, self.expiry)
