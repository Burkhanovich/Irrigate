import os
from .base import *

DEBUG = False

_use_https = os.environ.get('SECURE_SSL_REDIRECT', 'False') == 'True'

SECURE_SSL_REDIRECT = _use_https
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = _use_https
CSRF_COOKIE_SECURE = _use_https
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

if _use_https:
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# Django 4.x CSRF origin check
_hosts = os.environ.get('ALLOWED_HOSTS', '').split(',')
CSRF_TRUSTED_ORIGINS = [
    f"{'https' if _use_https else 'http'}://{h.strip()}"
    for h in _hosts if h.strip()
]
