import datetime
from .base import get_request_container

# 只做一些备份 没作用


def _delete_cookie(self, request, response):
    req = get_request_container(request)
    response.cookies[self.cookie_name] = req[self.session_name].sid

    # We set expires/max-age even for session cookies to force expiration
    response.cookies[self.cookie_name]["expires"] = datetime.datetime.utcnow()
    response.cookies[self.cookie_name]["max-age"] = 0


def getSid(self, request):
    return request.cookies.get(self.cookie_name)
