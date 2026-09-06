from rest_framework.authentication import SessionAuthentication

class CsrfExemptSessionAuthentication(SessionAuthentication):
    """
    SessionAuthentication without CSRF enforcement for REST API endpoints.
    """
    def enforce_csrf(self, request):
        return None
