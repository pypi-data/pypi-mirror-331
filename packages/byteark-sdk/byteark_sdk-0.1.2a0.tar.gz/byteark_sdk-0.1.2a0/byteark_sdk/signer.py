import base64
import hashlib
import urllib.parse
from collections import OrderedDict
from datetime import datetime, timedelta, timezone

from urllib.parse import urlparse

SIGN_OPTIONS = {
    "client_ip": {
        "include_value": False,
    },
    "client-ip": {
        "include_value": False,
    },
    "origin": {
        "include_value": False,
    },
    "referer": {
        "include_value": False,
    },
    "user_agent": {
        "include_value": False,
    },
    "geo_allow": {
        "include_value": True,
    },
    "geo_block": {
        "include_value": True,
    },
    "max_resolution": {
        "include_value": True,
    },
    "request_tags": {
        "include_value": True,
    },
    "viwer_group": {
        "include_value": True,
    },
}


class MissingOptions(Exception):
    pass


class ExpiredSignedUrlError(Exception):
    pass


class InvalidSignatureError(Exception):
    pass


class InvalidSignConditionError(Exception):
    pass


class ByteArkSigner:
    def __init__(self, **options):
        self.access_key = options.get("access_key")
        self.access_secret = options.get("access_secret")
        self.default_age = options.get("default_age", 900)

        self._check_options()

    def _check_options(self):
        if not self.access_key:
            raise MissingOptions("access_key is required")
        if not self.access_secret:
            raise MissingOptions("access_secret is required")

    def _make_string_to_sign(self, url: str, expire: int, options: dict = {}):
        parsed_url = urlparse(url)
        host = parsed_url.netloc
        method = options.get("method", "GET")

        elements = []
        elements.append(method)
        elements.append(host)

        if "path_prefix" in options:
            elements.append(options["path_prefix"])
        else:
            elements.append(parsed_url.path)

        for k in options:
            if k in SIGN_OPTIONS:
                elements.append(f"{k}:{options[k]}")

        elements.append(str(expire))
        elements.append(self.access_secret)

        return "\n".join(elements)

    def _make_signature(self, string_to_sign: str):
        h = hashlib.md5()
        h.update(string_to_sign.encode("utf-8"))
        hash_str = base64.b64encode(h.digest()).decode("utf-8")

        hash_str = hash_str.replace("+", "-")
        hash_str = hash_str.replace("/", "_")
        hash_str = hash_str.rstrip("=")
        return hash_str

    def _create_default_expire(self) -> int:
        return int(
            (
                datetime.now(timezone.utc) + timedelta(seconds=self.default_age)
            ).timestamp()
        )

    def sign(self, url: str, expires: int = 0, options: dict = {}) -> str:
        if expires == 0:
            expires = self._create_default_expire()

        options_ = {}
        for k in options:
            v = options[k]
            k = k.lower().replace("-", "_")
            options_[k] = v
        options = options_

        params = OrderedDict(
            [
                ("x_ark_access_id", self.access_key),
                ("x_ark_auth_type", "ark-v2"),
                ("x_ark_expires", expires),
                (
                    "x_ark_signature",
                    self._make_signature(
                        self._make_string_to_sign(url, expires, options)
                    ),
                ),
            ]
        )

        if "path_prefix" in options:
            params["x_ark_path_prefix"] = options["path_prefix"]

        for k in options:
            if k in SIGN_OPTIONS:
                if SIGN_OPTIONS[k]["include_value"]:
                    params[f"x_ark_{k}"] = options[k]
                else:
                    params[f"x_ark_{k}"] = "1"

        params = OrderedDict(sorted(params.items()))
        query_string = urllib.parse.urlencode(params)
        signed_url = f"{url}?{query_string}"

        return signed_url

    def verify(self, signed: str) -> bool:
        parsed_url = urlparse(signed)
        query_params = urllib.parse.parse_qs(parsed_url.query)

        expire = query_params["x_ark_expires"]
        if expire:
            expire = expire[0]
            if int(expire) < int(datetime.now(timezone.utc).timestamp()):
                raise ExpiredSignedUrlError("The signed url is expired")
        else:
            raise InvalidSignConditionError("The signed url is invalid")

        path_prefix = query_params.get("x_ark_path_prefix")
        if path_prefix:
            path_prefix = path_prefix[0]
            if path_prefix != parsed_url.path[: len(path_prefix)]:
                raise InvalidSignConditionError("The signed url is invalid")

        signature = query_params["x_ark_signature"][0]
        string_to_sign = self._make_string_to_sign(signed, expire)
        if signature != self._make_signature(string_to_sign):
            raise InvalidSignatureError("The signature of the signed url is invalid")

        return True


__all__ = [
    "ByteArkSigner",
    "ExpiredSignedUrlError",
    "InvalidSignatureError",
    "InvalidSignConditionError",
]
