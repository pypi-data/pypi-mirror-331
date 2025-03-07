from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

if not hasattr(settings, "CACHE_MIXIN_PREFIX"):
    raise ImproperlyConfigured("CACHE_MIXIN_PREFIX must be set in Django settings")
