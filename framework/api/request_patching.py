import functools
import json
import time
import urllib
import uuid
from contextlib import suppress
from pprint import pformat
from urllib.parse import urlparse

import requests
from requests import Request

from framework.consts.consts_common import (ICON_FAILED, ICON_REQUEST,
                                            ICON_RESPONSE, dir_caldav,
                                            dir_carddav)
from framework.core.config import ProjConfig
from framework.utils import datetime_util
from framework.utils.logging_util import logger
from framework.utils.string_util import decode_unicode_escape

hostname_to_service = {}


def handle_service_name(url):
    # Build hostname → service name map từ config
    # Resolve service từ URL hostname
    global hostname_to_service
    if not hostname_to_service:
        base_urls = ProjConfig.get_config("base_url", {})
        hostname_to_service = {
            urlparse(url).hostname: service.capitalize()
            for service, url in base_urls.items()
            if isinstance(url, str) and url.startswith("http") and service not in ["subscriptions"]
        }
    return hostname_to_service.get(url, "Unknown")


def handle_params_string(params):
    params_string = "?"
    for index, item in enumerate(params.items()):
        params_string += f"{item[0]}={item[1]}" if index == 0 else f"&{item[0]}={item[1]}"
    return params_string


def build_curl(*args, **kwargs):
    # Input: Response + Requests **kwargs
    _result, *_ = args if args else (dict(), None)
    _request_headers = dict()

    if args:
        _url = _result.request.url
        _method = _result.request.method
        _request_headers |= dict(_result.request.headers)
    else:
        _params = kwargs.get("params", dict())
        _url = kwargs.get("url", "") + (handle_params_string(_params) if _params else "")
        _method = kwargs.get("method", "").upper()
        _request_headers |= kwargs.get("headers", dict()) or dict()

    if dir_caldav in _url or dir_carddav in _url:
        _request_headers["Content-Type"] = _request_headers.get("Content-Type", "") or "application/davsharing+xml"
    elif not kwargs.get("files", ""):
        _request_headers["Content-Type"] = _request_headers.get("Content-Type", "") or "application/json"

    cond_upload_file = "file" in _url and _method == "POST"

    if not kwargs:
        if dir_caldav in _url or dir_carddav in _url:
            _kwargs = (
                dict(data=_result.request.body) if not isinstance(_result.request.body, (dict, list)) else dict(json=_result.request.body)
            )
        elif cond_upload_file:
            _request_body = dict() if isinstance(_result.request.body, bytes) else _result.request.body
            _kwargs = (
                dict(data={item.split("=")[0]: item.split("=")[1] for item in _request_body.split("&")})
                if isinstance(_request_body, str)
                else dict(data=_request_body)
            )
        else:
            _kwargs = dict(json=("" if not _result.request.body else json.loads(_result.request.body.decode("utf8"))))
    else:
        _kwargs = kwargs

    _data_raw = ""

    # if _kwargs.get("files", "") or cond_upload_file:
    _form_data = _kwargs.get("data", "")
    _form_list = [f"'{k}=\"{v}\"'" for k, v in _form_data.items()] if isinstance(_form_data, dict) else []
    _form_file = ""
    if _kwargs.get("files"):
        _file_items = [item for item in _kwargs["files"]]
        _form_file = ""
        for _file_item in _file_items:
            _form_file += f"\\\n --form '{_file_item[0]}=@\"{str(_file_item[1][1]).split("'")[1]}\"'"
        # _file_dir = str(_kwargs["files"][0][1][1]).split("'")[1]
        # _form_file = f"\\\n --form 'file=@\"{_file_dir}\"'"
    _form_info = "\\\n --form " + "\\\n --form ".join(_form_list)
    _data_raw += _form_file + (_form_info if _form_list else "")

    _request_body = (
        (
            _kwargs.get("data", "")
            if not isinstance(_kwargs.get("data", ""), (dict, list))
            else json.dumps(_kwargs.get("data", ""), indent=2)
        )
        if any([(dav_dir in _url) for dav_dir in (dir_caldav, dir_carddav)]) and _kwargs.get("data", "")
        else json.dumps(_kwargs.get("json", dict()), indent=2)
    )
    _request_body = _request_body.decode("utf8") if isinstance(_request_body, bytes) else _request_body
    _data_raw += "" if _request_body in ("", "{}", "null") else f"\\\n --data-raw '{_request_body}'"

    _curl_format = "curl --location --request {method} '{url}'\\\n --header {headers} {data_raw}"

    _headers_list = [f"'{k}: {v}'" for k, v in _request_headers.items() if k != "Content-Length"]
    _headers = "\\\n --header ".join(_headers_list)
    _curl_result = _curl_format.format(method=_method, url=_url, headers=_headers, data_raw=_data_raw)
    return _curl_result


def handle_debug_log(resp, *args, **kwargs):
    """
    Handle debug log
    """
    _path = kwargs.get("url", args[2] if len(args) > 2 else "")
    _skip_url = ["client-report-error", "https://floware.atlassian.net"]
    is_skipped_path = any(item in _path for item in _skip_url)
    if is_skipped_path:
        return

    url = resp.request.url
    if resp.history and dir_caldav not in url and dir_carddav not in url:
        _path = kwargs.get("url", args[2] if len(args) > 2 else "")
        resp.request.prepare_url(_path, kwargs.get("params", ""))
        resp.request.headers.update(kwargs["headers"])
    # path_url = result.request.path_url

    # request_payload = kwargs.get("json", dict()) or kwargs.get("data", dict())

    try:
        # request_payload = json.dumps(request_payload, indent=2) if kwargs.get("json", dict()) else request_payload
        # request_payload = pformat(request_payload, width=200) if kwargs.get("json", dict()) else request_payload
        response_payload = (
            pformat(resp.json(), width=200).replace("None", "null").replace("True", "true").replace("False", "false")
        )
        # response_payload = pformat(result.json(), width=200)
    except json.decoder.JSONDecodeError:
        response_payload = ""
        with suppress(UnicodeDecodeError):
            response_payload = resp.content.decode("UTF-8")
        if not response_payload:
            response_payload = "Empty payload"
    except AttributeError:
        response_payload = "Empty payload"

    curl_result = build_curl(resp, **kwargs)
    curl_result_decode = decode_unicode_escape(curl_result)
    response_payload = decode_unicode_escape(response_payload)
    _response_time = int(round(resp.elapsed.total_seconds(), ndigits=3) * 1000)
    _response_time_msg = f" - {_response_time}ms" if _response_time else ""
    _response_msg = f"[{resp.status_code} ({resp.reason}){_response_time_msg}]"

    logger.debug(f"{"-" * 20}\n--- Request cURL ---\n{curl_result_decode}\n--- Response {_response_msg} ---\n{response_payload}")


def patched_request(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        """
        Monkey-patch requests.Session.request
        Auto log mọi API request/response - không cần sửa code khác.

        Log format:
            Before: [username - API client] [Service] [METHOD /path?params] [timestamp_ms]
            After:  [200 (OK) - 1522ms]
        """
        retries = 4
        polling = 3
        resp = None

        timeout = kwargs.get("timeout", 300)
        stream = kwargs.get("stream", False)
        check_code = kwargs.get("check_code", 0) or 0
        check_code = check_code if isinstance(check_code, list) else [check_code]
        
        method = kwargs.get("method", args[1] if len(args) > 1 else "")
        path = kwargs.get("url", args[2] if len(args) > 2 else "")
        
        hostname = urlparse(path).hostname or ""
        service = handle_service_name(hostname)
        
        kwargs["headers"] = kwargs.get("headers", args[0].headers if len(args) > 0 else {})
        old_auto_request_id = kwargs["headers"].get("auto_request_id", "")
        old_auto_request_id_split = old_auto_request_id.split("-")

        username_headers = (
            ("-" + old_auto_request_id_split[-2] + "-" + old_auto_request_id_split[-1])
            if "-floauto." in old_auto_request_id
            else ""
        )

        username = username_headers.split("-floauto.")[-1] or "Unknown"
        params = kwargs.get("params", {})
        params_str = handle_params_string(params) if params else ""
        endpoint = urllib.parse.urlparse(path).path
        api_url = f"[{method.upper()} {endpoint}{params_str}]"
        api_info = f"[{username} - API client] [{service}] {api_url}"

        # Resolve path
        for retry in range(retries):
            _uuid = str(uuid.uuid1()).split("-")[0]
            _request_time = datetime_util.timestamp(3)
            _timestamp = str(int(_request_time * 1000))  # Time in millisecond
            kwargs["headers"]["auto_request_id"] = f"{_uuid}-{_timestamp}{username_headers}"
            try:
                logger.info(f"{ICON_REQUEST} {api_info} [{_timestamp}] ...")
                # start_time = time.time()
                # - before
                resp = f(*args, **kwargs, timeout=timeout, stream=stream)
                # - after
                # elapsed_ms = int((time.time() - start_time) * 1000)

                _status_code = resp.status_code
                _response_time = int(round(resp.elapsed.total_seconds(), ndigits=3) * 1000)
                _response_time_msg = f" - {_response_time}ms" if _response_time else ""
                _response_msg = f"[{_status_code} ({resp.reason}){_response_time_msg}]"
                logger.info(f" {ICON_RESPONSE} {_response_msg}")
                handle_debug_log(resp, **kwargs)

                if _status_code == 429:
                    _wait_time = int(resp.headers.get("RateLimit-Reset", polling))
                    logger.debug(f"... Waiting for {_wait_time} seconds until RateLimit reset")
                    time.sleep(_wait_time)
                    continue

                if resp is False:
                    continue
                if retry < 2 and check_code != [0] and _status_code not in check_code:
                    time.sleep(polling)
                    continue
                return resp
            except (requests.exceptions.ConnectionError,) as e:
                logger.critical(f"{ICON_FAILED} {api_info} [{_request_time}] " f"Check status : {e}")
                time.sleep(polling)
            except (
                requests.exceptions.ConnectTimeout,
                requests.exceptions.ReadTimeout,
            ) as e:
                logger.critical(f"{ICON_FAILED} {api_info} [{_request_time}] " f"Check status : {e}")
                assert False, "Timed out error!"

        return resp
    
    return wrapper
