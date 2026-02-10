import random
import string
import uuid
from typing import Any

from framework.core.config import ProjConfig
from framework.utils.logging_util import logger


def random_bool() -> bool:
    return random.choice((True, False))


def random_bool_int() -> int:
    return random.choice((1, 0))


def random_int_min_max(min_, max_, /) -> int:
    return random.randint(min_, max_)


def random_float_min_max(min_, max_, /, ndigits_=3) -> float:
    return round(random.uniform(min_, max_), ndigits=ndigits_)


def random_ascii_letters_by_len(len_=10, /) -> str:
    return "".join(random.choices(string.ascii_letters, k=len_))


def random_str_by_len(len_=10, /) -> str:
    return "".join(random.choices(string.ascii_letters + string.digits, k=len_))


def random_int_by_len(len_=1, /) -> int:
    random_int = 0
    while random_int == 0:
        random_int = int("".join(random.choices(string.digits, k=len_)))
    return random_int


def random_fake_username() -> str:
    return "auto" + str(uuid.uuid1()).split('-')[0] + random_str_by_len(2).lower()


def random_word() -> str:
    return "auto" + random_str_by_len(4)


def random_title() -> str:
    return "Auto title " + str(uuid.uuid1()).split('-')[0]


def random_sentence(prefix="Auto sentence ") -> str:
    return prefix + str(uuid.uuid1()).replace('-', ' ')


def random_hex_color() -> str:
    r = lambda: random.randint(0, 255)
    hex_color = '#%02X%02X%02X' % (r(), r(), r())
    return hex_color.lower()


def random_base64_string(length: int = 32) -> str:
    """Generate a randomized base64 string.
    Parameters
    ----------
    length : int
        Desired character length of the returned token.
    Returns
    -------
    str
        Randomly generated token with length of `length`.
    """
    length = length if length >= 4 else 4
    characters = string.ascii_letters + string.digits + "+/"
    return f"{''.join(random.choice(characters) for _ in range(length - 2))}=="


def generate_user_email(api_domain: str = None, amount: int = 1) -> list[str]:
    """
    Generate a list of fake emails based on specified API domain.
    :param api_domain: The API domain which usually has '@' prefix (for example: @flouat.net, flouat.net)
    :param amount: Number of user emails to be generated
    """
    emails_list: list = list()
    fake_username = random_fake_username()
    if not api_domain:
        api_domain = random.choice(
            [
                "@gmail.com",
                "@yahoo.com",
                "@zoho.com",
                "@caldav.com",
                "@icloud.com",
                "@hcm.edu.vn",
                "@outlook.com",
            ]
        )

    use_api_domain = api_domain if api_domain.startswith("@") else f"@{api_domain}"
    for counter in range(amount):
        emails_list.append(f"{fake_username}_{counter + 1}{use_api_domain}")

    return emails_list


def pick_random_item(from_list: list[Any], /, excl_list: list[Any] = None) -> Any:
    """
    Pick a random item from the list, which (optionally) not occurring in another one.

    :param from_list: The input list for data to pick from.
    :param excl_list: The list of items should not be taken. Defaults to None.

    :return: The output list having same type as inputs
    """
    total_list = from_list or []
    if excl_list:
        total_list = list(set(total_list) - set(excl_list))
    return_item = random.choice(total_list)
    return return_item


def generate_random_platform():
    version_ranges = {'iOS': (10, 17), 'macOS': (9, 14)}
    platform = random.choice(list(version_ranges.keys()))

    version_min, version_max = version_ranges.get(platform, (1, 1))
    version_major = random.randint(version_min, version_max)
    version_minor = random.randint(0, 9)  # Minor version is from 0 to 9
    version = f"{platform}{version_major}.{version_minor}"

    return version


def generate_phone_number():
    # Randomly choose a country code between 1 (USA) and 84 (Vietnam)
    country_code = random.choice([1, 84])

    # Generate a 3 digit area code
    area_code = random.randint(100, 999)

    # Generate a 3 digit local number part
    local_number_part1 = random.randint(100, 999)

    # Generate a 4 digit local number part
    local_number_part2 = random.randint(1000, 9999)

    # Combine all parts into a phone number
    phone_number = f"+{country_code}{area_code}{local_number_part1}{local_number_part2}"

    return phone_number


def fake_user(*, prefix="", suffix="", domain=""):
    """
    Generate fake user and avoid banned words
    """
    _config = ProjConfig.get_config()
    prefix = prefix if prefix else _config["signup_prefix"]
    domain = domain if domain else _config["domain"]
    bw = _config["banned_words"]
    bw_partial = list(map(str.lower, bw["partial"]))

    randomuser = (prefix + suffix + str(uuid.uuid1()).split('-')[0]).lower()
    if any(_w in randomuser for _w in bw_partial):
        logger.info(f"Username {randomuser!r} contains partial banned words. Removing ...")
        invalid_words = [_w for _w in bw_partial if _w in randomuser]
        for word in invalid_words:
            randomuser = randomuser.replace(word, "")
    if randomuser[0].isdigit() or randomuser[0] in "_.-":
        logger.info(f"Username {randomuser!r} starts with invalid character. Removing ...")
        randomuser = randomuser.replace(randomuser[0], "", 1)
    randomuser = randomuser[:32]
    if randomuser[-1] == "_":
        logger.info(f"Username {randomuser!r} ends with invalid character. Removing ...")
        randomuser = randomuser[:-1]

    return f"{randomuser[:32]}{domain}"


def random_url():
    _config = ProjConfig.get_config()
    if _config:
        domain = _config["domain"].lstrip("@")
    else:
        domain = random.choice(["example.com", "test.com", "demo.com"])

    return (
        f"https://flo.k8s.{domain}/#/flo?type=3&id={random_int_by_len(8)}&uid={str(uuid.uuid4())}&colid={random_int_by_len(8)}&category=1"
    )
