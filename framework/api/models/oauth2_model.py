from framework.core.config import ProjConfig
from framework.utils import encrypt_util, random_util


def payload_auth(username="", password="", grant_type="password", **kwargs):
    _password = password or ProjConfig.get_config("password")
    _public_key = kwargs.pop("public_key", None) or ProjConfig.get_config("public_key")
    payload = dict(
        username=username or (ProjConfig.get("signup_prefix") + random_util.random_fake_username() + ProjConfig.get("domain")),
        password=encrypt_util.encrypt_rsa_base64(_password, _public_key),
        grant_type=grant_type
    ) | kwargs
    return payload
