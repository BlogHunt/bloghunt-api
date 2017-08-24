from rest_framework.throttling import ScopedRateThrottle


class ScopedRateWriteThrottle(ScopedRateThrottle):
    """ Like the ScopedRateThrottle but only for POST/PATCH/PUT operations. """
    ALLOWED_METHODS = ('get', 'options', 'head')

    def allow_request(self, request, view):
        if self._is_write_request(request):
            return super().allow_request(request, view)
        return True

    def _is_write_request(self, request):
        return request.method.lower() not in self.ALLOWED_METHODS
