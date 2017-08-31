from rest_framework.compat import is_authenticated
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.settings import api_settings


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

    Partial Overrides
    ----------------------

    Views can override and add throttle rates by adding the `throttle_rates`
    property whose value is a dictionary of scopes and rates. If a required rate
    is not found in the view's rates, then the global settings are used instead.

    If you wish to remove rates found in the global config, set the scope's
    rate value to None

    Example
    -------

    An Anonymous user makes a GET request to an endpoint. The following levels
    are checked in order. The first match found in settings.py is used:

    - anon-get
    - anon-read
    - anon
    """
    READ_METHODS = ('get', 'options', 'head')
    ANON_SCOPE = 'anon'
    USER_SCOPE = 'user'
    PREMIUM_SCOPE = 'premium'

    throttle_rates_attr = 'throttle_rates'

    def allow_request(self, request, view):
        user_level = self.get_user_level(request)
        rates = {
            **api_settings.DEFAULT_THROTTLE_RATES,
            **getattr(view, self.throttle_rates_attr, {})
        }
        self.scope = self.get_scope(user_level, request.method.lower(), rates)
        if not self.scope:
            return True

        self.THROTTLE_RATES = rates
        self.rate = self.get_rate()
        self.num_requests, self.duration = self.parse_rate(self.rate)
        return super(ScopedRateThrottle, self).allow_request(request, view)

    def get_scope(self, user_level, method, rates):
        action = 'read' if method in self.READ_METHODS else 'write'
        for intent in [method, action]:
            intent_scope = '%s-%s' % (user_level, intent)
            if rates.get(intent_scope, None):
                return intent_scope
        return user_level if rates.get(user_level, None) else None

    def get_user_level(self, request):
        try:
            if is_authenticated(request.user):
                return self.USER_SCOPE
        except AttributeError:
            pass
        try:
            if request.auth.is_valid():
                return self.PREMIUM_SCOPE
        except AttributeError:
            pass
        return self.ANON_SCOPE

    def get_cache_key(self, request, view):
        ident = None

        try:
            if is_authenticated(request.user):
                ident = request.user.pk
        except AttributeError:
            pass

        try:
            if request.auth.is_valid():
                ident = request.auth.user_id
        except AttributeError:
            pass

        if ident is None:
            ident = self.get_ident(request)

        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }
