from typing import final

from django.core.cache import cache
from django.conf import settings
from django_utility_suite.api.mixins.utils import seconds_until

from rest_framework.generics import GenericAPIView
from rest_framework.response import Response



class ReadOnlyViewSetMixin(GenericAPIView):
    CACHE_KEY_PREFIX = settings.CACHE_MIXIN_PREFIX
    ONE_MINUTE = 60  # one minute in seconds
    DEFAULT_15_MINUTES = ONE_MINUTE * 15
    FALLBACK_30_MINUTES = ONE_MINUTE * 30

    DEFAULT = "default"
    FALLBACK = "fallback"
    DEPLOY = "deploy"

    force_deploy_cache_update = False

    @property
    def app_name(self):
        raise Exception("app_name not defined")

    @property
    def cache_prefix(self):
        raise NotImplementedError("cache_prefix not defined")

    @property
    def cache_timeout(self):
        return self.DEFAULT_15_MINUTES

    @property
    def fallback_cache_timeout(self):
        return self.FALLBACK_30_MINUTES

    @property
    def deploy_cache_timeout(self):
        """
        By default, it will be invalidated at 20:00:00 PM.
        Deploy cache keys will be progressively updated as customers browse the frontend
        """
        return seconds_until(target_hour=20, target_minute=0, target_second=0)

    def get_cache_key(self):
        raise NotImplementedError("get_cache_key() is not implemented.")

    def get_cache_fallback_key(self):
        return self.get_cache_key()

    @final
    def __get_cache_key(self):
        # DON'T OVERRIDE. Customize key using get_cache_key method
        return f"{self.cache_prefix}:{self.get_cache_key()}:{self.cache_timeout}secs:{self.DEFAULT}"

    @final
    def __get_fallback_key(self):
        # DON'T OVERRIDE. Customize key using get_cache_fallback_key method
        return f"{self.cache_prefix}:{self.get_cache_fallback_key()}:{self.fallback_cache_timeout}secs:{self.FALLBACK}"

    @final
    def __get_deploy_cache_key(self):
        # DON'T OVERRIDE. Customize key using get_cache_key method
        return f"{self.cache_prefix}:{self.get_cache_key()}:{self.DEPLOY}"

    def get_cache(self):
        use_deploy_cache = self.request.headers.get(
            settings.USE_DEPLOY_CACHE_HEADER, False
        )
        if bool(use_deploy_cache):
            key = self.__get_deploy_cache_key()
            data = cache.get(key)
            data_source = self.DEPLOY
            if data is None:
                self.force_deploy_cache_update = True
            return data, data_source

        key = self.__get_cache_key()

        data = cache.get(key)
        data_source = self.DEFAULT
        if data is None:
            data_source = self.FALLBACK
            fallback_key = self.__get_fallback_key()
            data = cache.get(fallback_key)
        if data is None:
            data_source = self.DEPLOY
            deploy_key = self.__get_deploy_cache_key()
            data = cache.get(deploy_key)
            if data is None:
                self.force_deploy_cache_update = True
        return data, data_source

    def set_cache(self, data, timeout):
        if hasattr(data, "data"):
            if data.data is None or (
                isinstance(data.data, (list, dict)) and not data.data
            ):
                return
        if self.force_deploy_cache_update:
            deploy_key = self.__get_deploy_cache_key()
            cache.set(deploy_key, data, self.deploy_cache_timeout)
            if self.request.headers.get(settings.USE_DEPLOY_CACHE_HEADER, False):
                return

        key = self.__get_cache_key()
        fallback_key = self.__get_fallback_key()
        cache.set(key, data, timeout)
        cache.set(fallback_key, data, self.fallback_cache_timeout)

    def invalidate_cache(self, many=False):
        key = self.__get_cache_key()
        if many:
            cache.delete_many(key)
        cache.delete(key)

    def __get_instance_response_and_set_cache(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        response = Response(serializer.data)
        response = self.__finalize_response(args, kwargs, request, response)

        self.set_cache(response, self.cache_timeout)
        return response

    def __finalize_response(self, args, kwargs, request, response):
        response = self.finalize_response(request, response, *args, **kwargs)
        if hasattr(response, "render") and callable(response.render):
            response.render()
        return response

    def retrieve(self, request, *args, **kwargs):
        cached_response, data_source = self.get_cache()
        if cached_response:
            if data_source in (self.FALLBACK, self.DEPLOY):
                self.__get_instance_response_and_set_cache(request, *args, **kwargs)
            return cached_response
        response = self.__get_instance_response_and_set_cache(request, *args, **kwargs)
        return response

    def __get_list_response_and_set_cache(self, request, *args, **kwargs) -> Response:
        qs = self.get_queryset()
        queryset = self.filter_queryset(qs)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            response = self.__finalize_response(args, kwargs, request, response)

            self.set_cache(response, self.cache_timeout)
            return response

        serializer = self.get_serializer(queryset, many=True)
        response = Response(serializer.data)
        response = self.__finalize_response(args, kwargs, request, response)
        self.set_cache(response, self.cache_timeout)
        return response

    def __get_unique_obj_response_and_set_cache(
        self, request, *args, **kwargs
    ) -> Response:
        obj = self.get_object()
        serializer = self.get_serializer(obj)
        response = Response(serializer.data)
        response = self.__finalize_response(args, kwargs, request, response)
        self.set_cache(response, self.cache_timeout)
        return response

    def list(self, request, *args, **kwargs):
        cached_response, data_source = self.get_cache()
        if cached_response:
            if data_source in (self.FALLBACK, self.DEPLOY):
                self.__get_list_response_and_set_cache(request, *args, **kwargs)
            return cached_response
        response = self.__get_list_response_and_set_cache(request, *args, **kwargs)
        return response

    def unique_object(self, request, *args, **kwargs):
        cached_response, data_source = self.get_cache()
        if cached_response:
            if data_source in (self.FALLBACK, self.DEPLOY):
                self.__get_unique_obj_response_and_set_cache(request, *args, **kwargs)
            return cached_response
        response = self.__get_unique_obj_response_and_set_cache(
            request, *args, **kwargs
        )
        return response

    def get_queryset_from_db_and_save_in_cache(self):
        queryset = super().filter_queryset(self.get_queryset())
        self.set_cache(data=queryset, timeout=self.cache_timeout)
        return queryset

    def get_object_from_db_and_save_in_cache(self):
        instance = self.get_object()
        self.set_cache(data=instance, timeout=self.cache_timeout)
        return instance
