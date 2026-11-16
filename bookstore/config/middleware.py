import logging
from time import perf_counter

logger = logging.getLogger("bookstore.requests")


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = perf_counter()
        response = self.get_response(request)
        match = request.resolver_match
        logger.info(
            "%s %s status=%s duration_ms=%.1f",
            request.method,
            match.view_name if match else "<unresolved>",
            response.status_code,
            (perf_counter() - start) * 1000,
        )
        return response
