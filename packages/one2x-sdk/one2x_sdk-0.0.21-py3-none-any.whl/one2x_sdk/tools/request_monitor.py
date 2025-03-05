import logging
import os
import time


class RequestMonitor:
    def __init__(self, env, analysis_url=None, service_name="director", project_name="medeo", enabled=True):
        print("Initializing request monitor")
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
        if enabled:
            self._patch_requests()

    def _pre_process_request(self, url: str, *args, **kwargs):
        if self.analysis_url in url:
            print(f"检测到对 analysis_url 的自调用，跳过监控: {url}")
            return url, args, kwargs

        if not self.enabled:
            return

        # todo: 修正为打点逻辑
        logging.info(
            f"Rre-process Request: {time.time()} {args[0]} {url} {kwargs.get('headers', {})} {kwargs.get('data', kwargs.get('json', None))}")

    def _post_process_request(self):
        pass

    def _patch_requests(self):
        print("Patching requests")
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
            logging.debug("已对 requests 库进行AOP注入")
        except ImportError:
            logging.debug("未找到 requests 库，跳过拦截")
