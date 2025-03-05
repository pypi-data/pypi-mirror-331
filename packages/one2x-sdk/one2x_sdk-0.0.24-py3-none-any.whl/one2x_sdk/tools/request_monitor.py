import os
import time

from one2x_sdk.utils.logger import get_default_logger


class RequestMonitor:
    def __init__(self, env="dev", analysis_url=None, service_name="director", project_name="medeo", enabled=True,
                 logger=None):
        self.env = env or os.getenv(
            "ENV", "dev"
        )
        self.enabled = enabled
        self.analysis_url = analysis_url or os.getenv(
            "ANALYSIS_SERVICE_URL", "http://localhost:3268"
        )
        self.env = env
        self.service_name = service_name
        self.project_name = project_name
        self.logger = logger or get_default_logger('RequestMonitor')
        if enabled:
            self.configure()

    def configure(self):
        self._patch_requests()
        self._patch_aiohttp()
        
    def _pre_process_request(self, url: str, *args, **kwargs):
        if self.analysis_url in url:
            self.logger.info(f"检测到对 analysis_url 的自调用，跳过监控: {url}")
            return url, args, kwargs

        if not self.enabled:
            return

        # todo: 修正为打点逻辑
        self.logger.info(
            f"Rre-process Request: {time.time()} {args[0]} {url} {kwargs.get('headers', {})} {kwargs.get('data', kwargs.get('json', None))}")

    def _post_process_request(self):
        pass

    def _patch_requests(self):
        try:
            import requests
            original_request = requests.request

            def patched_request(*args, **kwargs):
                if not self.enabled:
                    return original_request(*args, **kwargs)

                method = kwargs.get('method', 'GET')
                url = kwargs.get('url', args[0] if args else '')
                headers = kwargs.get('headers', {})
                data = kwargs.get('data', kwargs.get('json', None))

                self._pre_process_request(
                    url=url,
                    method=method,
                    headers=headers,
                    body=data
                )

                response = original_request(*args, **kwargs)
                self._post_process_request()
                return response

            requests.request = patched_request
            self.logger.info("RequestMonitor 已对 requests 库进行 AOP 拦截!")
        except ImportError:
            self.logger.info("未找到 requests 库，跳过拦截")

    def _patch_aiohttp(self):
        try:
            import aiohttp
            original_request = aiohttp.ClientSession._request

            async def patched_request(self_session, method, url, **kwargs):
                if not self.enabled:
                    return await original_request(self_session, method, url, **kwargs)

                headers = kwargs.get('headers', {})
                data = kwargs.get('data', kwargs.get('json', None))

                self._pre_process_request(
                    url=url,
                    method=method,
                    headers=headers,
                    data=data
                )

                response = await original_request(self_session, method, url, **kwargs)
                self._post_process_request()
                return response

            aiohttp.ClientSession._request = patched_request
            self.logger.info("RequestMonitor 已对 aiohttp 库进行 AOP 拦截!")
        except ImportError:
            self.logger.info("未找到 aiohttp 库，跳过拦截")

