import math
import os
import time
from contextlib import suppress

import requests

from framework.api.models.oauth2_model import payload_auth
from framework.api.url_builder import build_url
from framework.consts.consts_common import InternalGroup
from framework.consts.project import RESOURCES_PEM_DIR
from framework.core.config import ProjConfig
from framework.core.user_registry import UserRegistry
from framework.utils import (datetime_util, encrypt_util, qr_otp_util,
                             random_util)
from framework.utils.logging_util import logger

user_registry = UserRegistry()


def get_public_key(env, url=None):
    """get public_key use for OAuth2"""
    public_key = None  # Default value do not remove
    path = RESOURCES_PEM_DIR / f"{env}.pem"
    _config = ProjConfig.get_config(load_api=True)

    if _config["new_public_key"]:
        os.remove(path)

    with suppress(FileNotFoundError):
        with path.open("r+") as _r:
            public_key = _r.readline()

    if not public_key:
        with path.open("w+") as _f:
            resp = requests.get(
                url=url or build_url('api', 'dynamic_key'),
                headers=dict(device_uid=_config["device_uid"], app_id=_config["app_id"]),
            )
            public_key = resp.json().get("pkey", None)
            _f.writelines(public_key)

    if not public_key:
        raise ValueError(f"Public key is empty in {env}")

    decoded_pk = encrypt_util.decode_base64(public_key)
    logger.debug(f"\n{decoded_pk}")
    return decoded_pk


def headers_app(*, device_uid="", app_id="", user_agent=None, username=None, expires_in=""):
    _config = ProjConfig.get_config(load_api=True)
    app_id = _config["app_ids"].get((app_id or "").lower()) or app_id or _config["app_id"]
    app = [k for k, v in _config["app_ids"].items() if v == app_id][0]
    _username = username.split("@")[0] if username else _config.username
    _headers = {
        "device_uid": device_uid or _config["device_uid"],
        "app_id": app_id,
        "user-agent": user_agent or _config["app_user_agents"][app],
        "auto_request_id": f"{expires_in}-floauto.{_username}",
    }
    # if encoding := _config["encoding"]:
    #     if encoding not in ["gzip", "deflate"]:
    #         raise ValueError(f"Unsupported encoding {encoding}")
    #     _headers |= {"Accept-Encoding": encoding}

    return _headers


def check_user_exist(user="", **kwargs):
    _status = user_registry.is_verified(user) or requests.post(
        url=kwargs.get("url") or build_url('oauth2', 'checkemail'),
        headers=kwargs.get("headers") or headers_app(username=user),
        json=dict(email=user),
    ).json()["data"]["is_exist"]
    user_registry.mark_exists(user, exists=_status)
    return _status


def new_token(user="", password="", internal_group=0, headers=None, **kwargs):
    _headers = headers or headers_app(username=user)
    resp = requests.post(
        url=kwargs.pop("url", None) or build_url('oauth2', 'signup'),
        headers=_headers,
        json=payload_auth(
            username=user,
            password=password,
            **dict(internal_group=internal_group) if internal_group else dict(),
            public_key=kwargs.get("public_key"),
        ),
    )
    _status_code = resp.status_code
    assert _status_code == 200, f"Failed OAuth2!\n" f"User: {user} | Message: {resp['error']['message']!r}"

    token = resp.json()["data"]["access_token"]
    token_type = resp.json()["data"].get("token_type") or "Bearer"
    _headers["authorization"] = f"{token_type} {token}"
    if resp.status_code == 200:
        user_registry.mark_signed_up(user, unused="unused" in user)  # Collect users to clean up after testing
    return _headers


def get_token(user="", password="", is_2fa=False, headers=None, is_web=False, **kwargs):
    _headers = headers or headers_app(username=user)
    if is_web:
        return access_token_web(user=user, password=password, headers=_headers)

    if is_2fa:
        header_2fa_login = access_token_2fa_login(user, password, headers=_headers)
        put_2fa = requests.put(
            url=build_url('admin', 'users_2fa_enable'), 
            headers=header_2fa_login
        )
        qr_base64 = put_2fa["data"]["qr_code"]
        otp = qr_otp_util.get_otp_from_qr_code(qr_base64)
        resp = requests.post(
            url=build_url('admin', 'users_2fa_verification'),
            headers=header_2fa_login,
            json=dict(totp_token=otp),
        )
    else:
        resp = requests.post(
            url=kwargs.pop("url", None) or build_url('oauth2', 'token'),
            headers=_headers,
            json=payload_auth(username=user, password=password, public_key=kwargs.get("public_key")),
        )

    token = resp.json()["data"]["access_token"]
    token_type = resp.json()["data"].get("token_type") or "Bearer"
    _headers["authorization"] = f"{token_type} {token}"

    return _headers


def access_token(
    *, user="", device_uid="", app_id="", fake=False, internal_group=None, password="", is_2fa=None, is_existed=None, is_web=False, **kwargs
) -> tuple:
    """
    Signup and sign in user account and return access_token
    """
    _config = ProjConfig.get_config(load_api=True)
    internal_group = internal_group or InternalGroup.AUTO.id

    url = kwargs.get("url", build_url('oauth2', ''))
    public_key = kwargs.get("public_key") or _config.get("public_key") or get_public_key(_config["env"])
    ProjConfig.set_config("public_key", public_key)
    username = (user or _config["user"]) if not fake else random_util.fake_user()
    username = username if "@" in username else f"{username}{_config['domain']}"
    is_2fa = is_2fa if is_2fa is not None else (_config.get("login_2fa") if username in [_config.get("user_po"), _config.get("user_dev")] else is_2fa)

    if is_web:
        app_id = "web"
    headers = headers_app(device_uid=device_uid, app_id=app_id, username=username, expires_in=str(int(datetime_util.timestamp() + 14400)))
    
    user_exist = is_existed if is_existed is not None else check_user_exist(username, url=url + "/checkemail", headers=headers)
    
    new_headers = (
        new_token(username, password, internal_group, url=url + "/signup", public_key=public_key, headers=headers)
        if not user_exist
        else get_token(username, password, is_2fa=is_2fa, url=url + "/token", public_key=public_key, headers=headers, is_web=is_web)
    )

    user_registry.mark_exists(username)

    return new_headers, username


def access_token_web(
    user="",
    password="",
    headers=None,
):
    _config = ProjConfig.get_config()
    _username = user or _config.user
    _username = _username if "@" in _username else f"{_username}{_config['domain']}"
    _headers = headers or headers_app(username=_username)
    _request = requests.Session()
    resp_key = _request.get(
        url=build_url('web', 'dynamic_key'),
        headers=_headers,
        check_code=200,
    )["response_json"]
    pkey = resp_key["pkey"]
    csrf_token = resp_key["csrfToken"]
    resp_login = _request.post(
        url=_config.url.web.login,
        headers=_headers,
        json=dict(
            email=_username,
            sig=encrypt_util.encrypt_rsa_base64(password or _config["password"], pkey),
            _csrf=csrf_token,
            isRemember=True,
        ),
    )
    cookies = resp_login.cookies.get_dict()
    token = cookies.get("authorization", "")
    token_type = "Bearer"
    _headers["authorization"] = f"{token_type} {token}"
    _headers["cookie"] = "; ".join([f"{k}={v}" for k, v in cookies.items()])
    return _headers


def access_token_2fa_login(
    user="",
    password="",
    headers=None,
):
    _config = ProjConfig.get_config(load_api=True)
    _username = user or _config.user_po
    _username = _username if "@" in _username else f"{_username}{_config['domain']}"
    _headers = headers or headers_app(username=_username)
    payload = dict(
        username=_username,
        password=encrypt_util.encrypt_rsa_base64(password or _config["password"], _config["public_key"]),
        grant_type="password",
    )
    resp = requests.post(
        url=build_url('admin', 'users_2fa_login'), 
        headers=_headers, 
        json=payload
    )
    token = resp["data"]["access_token"]
    token_type = "Bearer"
    _headers["authorization"] = f"{token_type} {token}"
    return _headers
