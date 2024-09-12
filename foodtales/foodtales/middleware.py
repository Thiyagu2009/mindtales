class AppVersionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Extract app version from headers
        request.app_version = request.headers.get(
            "X-App-Version", "1.0"
        )  # Default to '1.0' if not provided
        return self.get_response(request)
