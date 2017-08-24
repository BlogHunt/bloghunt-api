from rest_framework.compat import is_authenticated
from rest_framework.throttling import ScopedRateThrottle


class GlobalScopedDefaultsTrottle(ScopedRateThrottle):
    """ A throttle that uses the User authentication status and request intent
    against a set of predefined rates defined in settings.py

    Throttle Levels are defined by checking against the request method and the
    user's authentication as follows:

    There are 3 levels of access and more specific levels are given
    higher importance.

    - global (all request methods, least specific)
    - action (read or write)
    - method (HTTP verbs, most specific)

    Example:

    An Anonymous user makes a GET request to an endpoint. The following levels
    are checked in order. The first match found in settings.py is used:

    - anon-get
    - anon-read
    - anon
    """
    READ_METHODS = ('get', 'options', 'head')
    ANON_SCOPE = 'anon'
    USER_SCOPE = 'user'

    def allow_request(self, request, view):
        user_level = self.get_user_level(request)
        self.scope = self.get_scope(user_level, request.method.lower())
        if not self.scope:
            return True

        self.rate = self.get_rate()
        self.num_requests, self.duration = self.parse_rate(self.rate)
        return super(ScopedRateThrottle, self).allow_request(request, view)

    def get_scope(self, user_level, method):
        action = 'read' if method in self.READ_METHODS else 'write'
        for intent in [method, action]:
            intent_scope = '%s-%s' % (user_level, intent)
            if self.THROTTLE_RATES.get(intent_scope, False):
                return intent_scope
        if self.THROTTLE_RATES.get(user_level, False):
            return user_level

    def get_user_level(self, request):
        if not is_authenticated(request.user):
            return self.ANON_SCOPE
        return self.USER_SCOPE
