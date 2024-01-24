
class NotLoggedInError(Exception):
    """User not logged in"""

class CsrfTokenNotFoundError(Exception):
    """CSRF Token not found"""
