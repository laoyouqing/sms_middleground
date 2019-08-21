from rest_framework.throttling import SimpleRateThrottle

class WhiteListRateThrottle(SimpleRateThrottle):
    """
    白名单教案
    Limits the rate of API calls that may be made by a given user.

    The user id will be used as a unique cache key if the user is
    authenticated.  For anonymous requests, the IP address of the request will
    be used.
    """
    scope = 'white'

    def get_cache_key(self, request, view):
        if request.user.is_authenticated:
            ident = request.user.pk
        else:
            ident = self.get_ident(request)

        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }

    def allow_request(self, request, view):
        """
        自定义频率限制60秒内只能访问三次
        """
        # 获取用户IP
        ip = request.META.get("REMOTE_ADDR")
        # print('-'*10, ip, self.get_ident(request))
        if ip not in {}:
            return False
        else:
            return True

    def wait(self):
        """
        限制
        """
        return 999