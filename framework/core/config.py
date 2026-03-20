import json
import os
import uuid
from pathlib import Path

import pytest
import yaml

from framework.consts.project import (CONFIG_DIR, RESOURCES_CAPABILITIES_DIR,
                                      RESOURCES_YAML_DIR)
from framework.utils import DotDict, encrypt_util


class ProjConfig:
    _runtime = {}
    _config = {}
    _caps = {}
    _config_loaded = False
    _api_loaded = False
    API_BASE_URL = ""
    WEB_BASE_URL = ""
    APPIUM_SERVER = None
    
    @classmethod
    def set_runtime(cls, key, value):
        cls._runtime[key] = value
        
    @classmethod
    def get_runtime(cls, key=None, default=None):
        if key:
            return cls._runtime.get(key, default)
        else:
            return DotDict(cls._runtime)
    
    @classmethod
    def load_config(cls, env='staging') -> dict:
        """Load configuration from yaml file"""
        if not cls._config_loaded:
            config_file = CONFIG_DIR / f'{env}.yaml'
            
            if config_file.exists():
                with open(config_file, 'r') as f:
                    cls._config = (yaml.safe_load(f) or {})
                
                cls.API_BASE_URL = cls._config["base_url"]["api"]
                cls.WEB_BASE_URL = cls._config["web"]
                
                cls._config["web_domain"] = f"{cls._config['user'].partition('@')[-1]}"
                cls._config["domain"] = f"@{cls._config['user'].partition('@')[-1]}"
                
                cls._config = cls._config | cls._runtime
                envs = [item for item in ["dev", "qa", "staging", "prod"] if item in cls._runtime["env"]] or ["qa"]
                cls._config["env"] = envs[0]
                
                cls._config["user"] = (
                    (f"{cls._config['user']}{cls._config['domain']}" if "@" not in cls._runtime["user"] else cls._config["user"])
                    if "user" in cls._runtime
                    else cls._config["user"]
                )
                
                if cls._config["domain"] not in cls._config["user"]:
                    __tracebackhide__ = True
                    pytest.fail(f"Wrong domain {cls._config['user'].partition('@')[-1]!r} in user")
                
                cls._config["username"] = cls._config["user"].partition("@")[0]
                cls._config["member_prefix"] = cls._config["username"] + "_mem"
                cls._config["user2"] = (
                    (f"{cls._config['user2']}{cls._config['domain']}" if "@" not in cls._runtime["user2"] else cls._config["user2"])
                    if "user2" in cls._runtime
                    else cls._config["user2"]
                )
                cls._config["user2_username"] = cls._config["user2"].partition("@")[0]
                cls._config["user3"] = (
                    (f"{cls._config['user3']}{cls._config['domain']}" if "@" not in cls._runtime["user3"] else cls._config["user3"])
                    if "user3" in cls._runtime
                    else cls._config["user3"]
                )
                cls._config["user3_username"] = cls._config["user3"].partition("@")[0]
                
                cls._config["password"] = cls._config["password"] if "password" in cls._runtime else encrypt_util.decode_base64(cls._config["password"])
                cls._config_loaded = True
            else:
                raise FileNotFoundError(f"Config file not found: {config_file}")
        return DotDict(cls._config)
    
    @classmethod
    def load_api_config(cls):
        """Load API configuration from api yaml file"""
        if not cls._api_loaded:
            api_files = ('app_ids.yaml', 'app_user_agents.yaml')
            api_config = {}
            for api_file in api_files:
                api_file = RESOURCES_YAML_DIR / api_file
                if api_file.exists():
                    with open(api_file, 'r') as f:
                        api_config[api_file.name.split(".")[0]] = yaml.safe_load(f) or {}
            
            cls._config["app_ids"] = {k: encrypt_util.decode_base64(v) for k, v in api_config["app_ids"].items()}
            cls._config["app_user_agents"] = api_config["app_user_agents"]
            cls._config["app_id"] = cls._config["app_ids"][cls._config.get("api_app").lower()]
            cls._config["device_uid"] = cls._config.get("device_uid") or str(uuid.uuid4())
            cls._api_loaded = True
        return DotDict(cls._config)
    
    @classmethod
    def get_config(cls, key=None, default=None, load_api=False):
        """Get a config value by key"""
        if not cls._config_loaded:
            cls.load_config()
        if load_api and not cls._api_loaded:
            cls.load_api_config()
        if key:
            return cls._config.get(key, default)
        else:
            return DotDict(cls._config)
    
    @classmethod
    def set_config(cls, key, value):
        """Set a config value by key"""
        cls._config[key] = value
    
    @classmethod
    def load_caps(cls, name: str):
        if not cls._caps.get(name):
            p = RESOURCES_CAPABILITIES_DIR / name
            with open(p) as f:
                cls._caps[name] = json.load(f)
        return DotDict(cls._caps[name])
    
    @classmethod
    def get_caps(cls, name: str):
        if not cls._caps.get(name):
            cls.load_caps(name)
        return DotDict(cls._caps[name])
