import functools
import json
import logging
from logging import Logger

import pytest

from framework.consts.project import PYTHON_CONFIG_LOG
from framework.core.config import ProjConfig
from framework.mac.drivers.mac_driver import MacDriver
from framework.mobile.drivers.appium_driver import AppiumDriver
from framework.utils import logging_util, string_util
from framework.web.drivers.web_driver import WebDriver

_logging = None


def pytest_addoption(parser):
    general = parser.getgroup("General")
    api = parser.getgroup("API")
    web = parser.getgroup("Web")
    # General options
    general.addoption(
        "--env",
        action="store",
        default="staging",
        choices=["dev", "qa", "staging"],
        help="Choose test environment: dev, qa, staging",
    )
    general.addoption(
        "--user",
        action="store",
        default="",
        help="Choose test user",
    )
    general.addoption(
        "--user2",
        action="store",
        default="",
        help="Choose test user2",
    )
    general.addoption(
        "--user3",
        action="store",
        default="",
        help="Choose test user3",
    )
    general.addoption(
        "--password",
        action="store",
        default="",
        help="Choose test password",
    )
    general.addoption(
        "--debuglog",
        action="store_true",
        default=False,
        help="Choose test debug log",
    )
    # API options
    general.addoption(
        "--api_app",
        action="store",
        default="web",
        help="Choose test api app",
    )
    general.addoption(
        "--device_uid",
        action="store",
        default=None,
        help="Choose test device uid",
    )
    general.addoption(
        "--new_public_key",
        action="store_true",
        default=False,
        help="Choose test new public key",
    )
    # Web options
    web.addoption(
        "--web_browser",
        action="store",
        default="chromium",
        help="Choose test browser",
    )
    web.addoption(
        "--headless",
        action="store_true",
        default=False,
        help="Choose test headless",
    )


@pytest.fixture(scope="session", autouse=True)
def runtime_profile(request):
    """Runtime Profiles"""
    runtime_options = vars(request.config.option)

    if not runtime_options["env"]:
        pytest.exit(r"Need to '--env=${config}' run tests")
    
    runtime_input = ["env", "user", "password", "debuglog", "headless", "new_public_key", "api_app"]
    for key in runtime_input:
        if runtime_options.get(key) not in [None, ""]:
            ProjConfig.set_runtime(key, runtime_options.get(key))

    return dict(runtime_options)


@pytest.fixture(scope="session", autouse=True, name=f"runtime_session-{string_util.unique_uuid1()}")
def runtime_session(runtime_profile):
    """Runtime session handling"""
    global _logging
    _logging = logging_util.cli_logging_format(runtime_profile["debuglog"])
    

def pytest_runtest_setup(item):
    print("\x00")  # print a non-printable character to break a new line on console
    
    
# @pytest.fixture(scope="session", autouse=True)
# def logger(runtime_profile) -> Logger:
#     """Use log info to commandline"""
#     _logger = logging.getLogger(PYTHON_CONFIG_LOG)
#     if runtime_profile["nolog"]:
#         _logger.disabled = True
#         return _logger

#     _logmsgs_icon = [common_var.ICON_PASSED, common_var.ICON_WARNING, common_var.ICON_FAILED]
#     _logmsgs_checking = ["check response", "check status", "check data"]
#     _logmsgs_verify = ["verify data", "verify response data"]
#     _logmsgs_error = ["error reason", "error curl"]
#     _logmsgs_custom = _logmsgs_icon + _logmsgs_checking + _logmsgs_verify
#     _curl_icon = ""
#     _request_icon = common_var.ICON_REQUEST
#     _response_icon = common_var.ICON_RESPONSE
#     _request_div = '<div class="step__request">'
#     _socket_str = "✓ [SOCKET]"

#     def patchlog(logmsgs_custom, color):
#         def decorator(f):
#             @functools.wraps(f)
#             def wrapper(*args, **kwargs):
#                 *_, _logmsgs = args
#                 _color = color

#                 if _logmsgs is None or _logmsgs == ("-" * 100):
#                     return f(*args, **kwargs)

#                 if _request_icon in str(_logmsgs).lower():
#                     # _loggingmsgs.append(
#                     #     f'{_request_div}{_logmsgs}'
#                     # )
#                     _loggingmsgs.append(allure_util.handle_log_request(_logmsgs, _request_div))
#                     return f(*args, **kwargs)

#                 if _response_icon in str(_logmsgs).lower():
#                     # Find and update the latest item in-place
#                     _div_index_list = [i for i, log in enumerate(_loggingmsgs) if _request_div in log]
#                     for i in _div_index_list:
#                         _desc_div = '<div class="opblock-summary-description">'
#                         # if _loggingmsgs[i].startswith(_request_div) and _loggingmsgs[i].endswith("..."):
#                         #     _loggingmsgs[i] = (
#                         #         f'{_loggingmsgs[i]} {_logmsgs.replace(ICON_RESPONSE, "").strip()}</div>')
#                         #     break
#                         if _loggingmsgs[i].startswith(_request_div) and _desc_div + '</div>' in _loggingmsgs[i]:
#                             _loggingmsgs[i] = _loggingmsgs[i].replace(
#                                 _desc_div + '</div>', f'{_desc_div}{_logmsgs.replace(_response_icon, "").strip()}</div>'
#                             )
#                             break

#                     return f(*args, **kwargs)

#                 if _socket_str.lower() in str(_logmsgs).lower():
#                     _data_target = str(_logmsgs).replace(_socket_str, "").strip()
#                     _logmsgs = allure_util.handle_log_custom(_logmsgs, logmsgs_custom, color=_color)
#                     _loggingmsgs.append(
#                         f'<div style="color:{_color};margin-bottom:-12px;" class="opblock-click" data-target="{_data_target}">{_logmsgs}</div>'
#                     )
#                     return f(*args, **kwargs)

#                 if any(_msgs in str(_logmsgs).lower() for _msgs in _logmsgs_error):
#                     _logmsgs = allure_util.handle_log_error(_logmsgs, _logmsgs_error, _color, _curl_icon)
#                     _loggingmsgs.append(f'<div style="color:{_color};margin-bottom:-12px;">{_logmsgs}</div>')
#                     return f(*args, **kwargs)

#                 if any(_msgs in str(_logmsgs).lower() for _msgs in logmsgs_custom):
#                     _logmsgs = allure_util.handle_log_custom(_logmsgs, logmsgs_custom, color=_color)
#                     _loggingmsgs.append(f'<div style="color:{_color};margin-bottom:-12px;">{_logmsgs}</div>')
#                     return f(*args, **kwargs)

#                 if "actual" in str(_logmsgs).lower():
#                     expect_title = ". Expected:"
#                     actual_title = ". Actual:"

#                     # Separate into "Actual" and "Expected"
#                     # Find the index of "Expected:"
#                     expected_index = _logmsgs.find('\t\t\t\tExpected:')
#                     # Extract "Actual" part
#                     actual = _logmsgs[:expected_index].strip()
#                     # Extract "Expected" part
#                     expect = _logmsgs[expected_index:].strip()

#                     expect = (
#                         (
#                             allure_util.custom_log_long_text(
#                                 expect.replace("Expected:", expect_title),
#                                 expect_title,
#                                 "",
#                                 is_expand=False,
#                                 height="250px",
#                                 max_chars=50,
#                                 icon_class="fa-check",
#                                 color="green",
#                             )
#                         )
#                         if expect
#                         else ""
#                     )
#                     actual = allure_util.custom_log_long_text(
#                         actual.replace("Actual:", actual_title),
#                         actual_title,
#                         "",
#                         is_expand=False,
#                         height="250px",
#                         max_chars=50,
#                         icon_class="fa-times",
#                     )
#                     _logmsgs = (
#                         "<div class='textFailed' style='display: flex; flex-direction: row; margin-left: 25px'>"
#                         f"<div style='width: 50%;'>{actual}</div>"
#                         f"<div style='width: 50%;'>{expect}</div>"
#                         "</div>"
#                     )

#                     _logmsgs_resp_time = ["ms", "millisecond"]
#                     if any(_msgs in str(_logmsgs).lower() for _msgs in _logmsgs_resp_time):
#                         _loggingmsgs.append(f'<div style="color:{_color};margin-bottom:-12px;">{_logmsgs}</div>')
#                     else:
#                         _loggingmsgs.append(f'<div class="stepFailed" style="color:{_color};margin-bottom:-12px;">{_logmsgs}</div>')
#                     return f(*args, **kwargs)

#                 _loggingmsgs.append(f'<div style="margin-bottom:-12px;font-weight:700;">{_logmsgs}</div>')
#                 return f(*args, **kwargs)

#             return wrapper

#         return decorator

#     _logger.info = patchlog(_logmsgs_custom, "green")(_logger.info)
#     _logger.warning = patchlog(_logmsgs_custom + _logmsgs_error, "orange")(_logger.warning)
#     _logger.critical = patchlog(_logmsgs_custom + _logmsgs_error, "red")(_logger.critical)

#     return _logger


# @pytest.fixture(scope="session", autouse=True, name=f"allure_step-{string_util.unique_uuid1()}")
# def allure_step():
#     def patch(f):
#         @functools.wraps(f)
#         @contextmanager
#         def wrapper(*args, **kwargs):
#             title = kwargs.get("title") or args[0]
#             _loggingmsgs.append(
#                 f'''
#                 <div class="step descriptionStep">
#                     <div class="step__title step__title_hasContent long-line">
#                         <span class="step__arrow block__arrow">
#                             <span class="fa fa-chevron-right fa-fw text_status_passed"></span>
#                         </span>
#                         <div class="step__name">Step: {title}</div>
#                         <span class="step-row__control">
#                             <span class="fa fa-fw iconStatus fa-check text_status_passed"></span>
#                         </span>
#                     </div>
#                     <div class="step__content">
#                 '''
#             )
#             _logger = logging.getLogger(PYTHON_CONFIG_LOG)
#             _logger.info(f"*** Step: {title} ***")
#             with f(*args, **kwargs):
#                 yield
#             _logger.info("-" * 100)
#             _loggingmsgs.append("</div></div>")

#         return wrapper

#     allure.step = patch(allure.step)
