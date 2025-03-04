import time
import yaml
import json
from .base_http import BaseHTTP
from .dict import DictUtils


class Configuration:
    def __init__(self, **kwargs):
        self.api_url = kwargs.get("apiUrl")
        self.api_key = kwargs.get("apiKey")
        self.post_body = kwargs.get("postBody")
        self.resp = None
        self.http_client = BaseHTTP()

    def fetch(self):
        if not all([self.api_url]):
            raise ValueError("Missing required API url")

        headers = {}
        if self.api_key:
            headers = {"X-APIKEY": "{}".format(self.api_key)}
        response = self.http_client.post(self.api_url, self.post_body, headers)

        if response:
            content_type = response.headers.get("Content-Type", "")
            if "json" in content_type:
                result = response.json()
            elif "yaml" in content_type:
                result = yaml.safe_load(response.text)
            else:
                result = response.text

            self.resp = result
            return result
        return None

    def get_resp(self):
        return self.resp

    def get_value(self, key_path):
        if not self.resp:
            print("[ERROR] Response is set as None, did you call fetch()?")
        return DictUtils.get_by_path(self.resp, key_path)
