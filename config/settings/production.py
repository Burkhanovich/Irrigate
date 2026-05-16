import os
from .base import *

DEBUG = False

# Security settings
SECURE_SSL_REDIRECT = os.environ.get('SECURE_SSL_REDIRECT', 'False') == 'True'
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Logging to file in production
import os
_log_file = os.environ.get('LOG_FILE', '/var/log/irrigate/django.log')
LOGGING['handlers']['file'] = {
    'class': 'logging.FileHandler',
    'filename': _log_file,
    'formatter': 'verbose',
}
LOGGING['root']['handlers'] = ['console', 'file']
