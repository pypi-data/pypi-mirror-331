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
        self.service_name = service_name
        self.project_name = project_name
        self.logger = logger or get_default_logger('RequestMonitor')
        if enabled:
            self.configure()

    def configure(self):
        self._patch_aiohttp()

    def _pre_process_external_request(self, url, method=None, headers=None, data=None):
        url_str = str(url)
        
        if self.analysis_url and self.analysis_url in url_str:
            self.logger.debug(f"跳过监控分析服务请求: {url}")
            return
            
        if "supabase" in url_str.lower():
            self.logger.debug(f"跳过监控 supabase 请求: {url}")
            return
            
        if "one2x" in url_str.lower():
            self.logger.debug(f"跳过监控 one2x 请求: {url}")
            return

        if not self.enabled:
            return

        self.logger.info(
            f"Rre-process Request: {method} {url_str} {headers} {data}")

    def _post_process__external_request(self):
        pass

    def _patch_aiohttp(self):
        try:
            import aiohttp
            original_request = aiohttp.ClientSession._request

            async def patched_request(self_session, method, url, **kwargs):
                if not self.enabled:
                    return await original_request(self_session, method, url, **kwargs)

                headers = kwargs.get('headers', {})
                data = kwargs.get('data', kwargs.get('json', {}))

                self._pre_process_external_request(
                    url=url,
                    method=method,
                    headers=headers,
                    data=data
                )

                response = await original_request(self_session, method, url, **kwargs)
                self._post_process__external_request()
                return response

            aiohttp.ClientSession._request = patched_request
            self.logger.info("RequestMonitor 已对 aiohttp 库进行 AOP 拦截!")
        except ImportError:
            self.logger.info("未找到 aiohttp 库，跳过拦截")
