import random
import re
import string
import uuid
from itertools import combinations
from xml.etree import ElementTree

from framework.utils import DotDict


def remove_space_line(string_with_empty_lines) -> str:
    return "\n".join(line for line in string_with_empty_lines.split("\n") if line.strip())


def convert_string_to_dict(values: str, regex: str) -> dict:
    res = []
    for value in values.split("\n"):
        if regex in value:
            res.append([i.strip() for i in value.split(regex, 1)])
    return dict(res)


def unique_uuid1():
    return str(uuid.uuid1()).split("-")[0]


def get_content_from_xml_by_conditions(content, parent_node_xpath: str, children_node_xpath=None):
    def _cook_path(node, node_xpath):
        return [node.find(_path).text for _path in node_xpath]

    ele_tree = ElementTree.fromstring(content)
    parent_nodes = ele_tree.findall(parent_node_xpath)
    raw_data = [_cook_path(_node, children_node_xpath) for _node in parent_nodes]
    good_data = [data for data in raw_data if all(data)]
    return good_data


def get_content_from_xml(content, tags: str, *, check_text=True):
    ele_tree = ElementTree.fromstring(content)
    if not check_text:
        return [node.text for node in ele_tree.iter() if node.tag == tags]
    return [node.text for node in ele_tree.iter() if node.tag == tags and node.text]


def get_list_from_xml(content, /, *, tags: str):
    ele_tree = ElementTree.fromstring(content)
    return [node.text for node in ele_tree.iter() if node.tag == tags]


def str_random_by_len(len_=10, /) -> str:
    return "".join(random.choices(string.ascii_letters + string.digits, k=len_))


def word_random_by_len() -> str:
    return "auto" + str_random_by_len(4)


def string_sample(special_only=False):
    normal_characters = {"normal": "Testing " + word_random_by_len()} if special_only else {}
    return DotDict(
        {
            "short": str_random_by_len(3),
            "vietnamese": "Thử nghiệm " + word_random_by_len(),
            "japanese": "テスト " + word_random_by_len(),
            "emoji": "✅🥳 " + word_random_by_len(),
            "special": r"[@ut0](~!#$%^&*-+=),{|./} ?: <" + word_random_by_len() + ">;",
        }
        | normal_characters
    )


def generate_samples(value, list_value, pop_single_val=False):
    """
    this function is used to randomly generate a combined sample based on list_value
    EX: value = 0, list_value = [0,1,2] --> 0, 0,2, 0,2,1
    - pop_single_val: remove the input "value" out of the result samples
    """
    _list_value = list_value[:]
    random.shuffle(_list_value)
    all_samples = []

    for r in range(2, len(_list_value) + 1):
        samples = []
        for combination in combinations(_list_value, r):

            if value in combination:
                samples.append(",".join(map(str, combination)))

        all_samples.append(samples)

    # randomly sample the result
    result = [str(value)]
    for sublist in all_samples:
        amount = len(sublist) if len(sublist) == 1 else random.randint(1, 2)
        val = random.sample(sublist, k=amount)
        result.extend(val)

    return result[1 if pop_single_val else None :]


def join_list_as_str(*list_value: any, sep=None) -> str:
    """
    This function is used to join list of values into a string
    :param list_value: input *arg or a list of values
    :param sep: separator string by default is ", "
    :return: a string of values separated by the separator
    """
    list_value = list_value if len(list_value) > 1 else list_value[0]
    if not isinstance(list_value, (list, tuple)):
        return str(list_value)
    sep = sep or ", "
    return sep.join(map(str, list_value))


# Get string between two strings
def get_string_between(text_str: str, start: str, end: str) -> str:
    """
    This function is used to get the string between two strings
    :param text_str: Text string
    :param start: Start string
    :param end: End string
    :return: The string between start and end
    """
    # handle if start and end is not in the string
    if start not in text_str and end not in text_str:
        return text_str

    if start not in text_str:
        return text_str.split(end)[0]

    if end not in text_str:
        return text_str.split(start)[1]

    return text_str.split(start)[1].split(end)[0]


html_codes = (
    ('&', '&amp;'),
    ("'", '&#39;'),
    ('"', '&quot;'),
    ('>', '&gt;'),
    ('<', '&lt;'),
)


def html_encode(s, include_codes=None):
    """
    Returns the ASCII encoded version of the given HTML string.
    """
    include_codes = include_codes or html_codes
    for code in include_codes:
        s = s.replace(code[0], code[1])
    return s


def html_decode(s, include_codes=None):
    """
    Returns the ASCII decoded version of the given HTML string.
    """
    include_codes = include_codes or html_codes
    for code in include_codes:
        s = s.replace(code[1], code[0])
    return s


def dav_title_decode(s, include_codes=None):
    """
    Returns CalDav string decoded version of the given string.
    """
    include_codes = include_codes or [
        (',', r'\,'),
        (';', r'\;'),
    ] + list(html_codes)
    for code in include_codes:
        s = s.replace(code[1], code[0])
    return s


def convert_unicode_to_string(unicode: str) -> str:
    # Remove "U+" from the string
    hex_code = unicode.replace("U+", "")
    # Convert the hexadecimal string to a number
    code_point = int(hex_code, 16)
    # Convert the code point to an emoji
    emoji_str = chr(code_point)

    return emoji_str


def random_case_string(text):
    """ "
    Randomly converts each letter in the input text to either uppercase or lowercase with a 50% chance
    """
    return ''.join(c.upper() if random.random() < 0.5 else (c.lower() if c.isalpha() else c) for c in text)


def random_sub_sentence(sentence):
    """
    Return a randomly sliced sub-part of the given sentence with range of full words

    :param sentence: A complete sentence (not just a word).
    :return: A sub-sentence string randomly sliced from the input.
    """
    sentence = sentence.strip()
    tokens = sentence.split()

    if len(tokens) < 2:
        return sentence

    max_len = len(tokens)
    sub_len = random.randint(1, max_len - 1)  # always less than full
    start = random.randint(0, len(tokens) - sub_len - 1)
    try:
        end = start + random.randint(1, max_len // 2 - 1)
    except ValueError:
        end = start + 1

    result = tokens[start:end]
    return ' '.join(result)


def random_prefix_partial_word(sentence):
    """
    Returns a random beginning partial word from the sentence.

    A partial is a prefix of a word with at least 2 characters,
    but shorter than the full word. If no valid partials are found,
    returns the original sentence.

    Example: "I want a job" → possible partials: "wa", "wan", "jo"
    """
    words = sentence.split()
    partials = set()

    for word in words:
        for i in range(2, len(word)):  # Start from length 2
            partials.add(word[:i])

    return random.choice(sorted(partials)) if partials else sentence


def decode_unicode_escape(s: str) -> str:
    """
    Giải mã các ký tự Unicode escape (vd: \\u00f4, \\u1ecdc) thành chữ có dấu.
    Nếu chuỗi đã bình thường thì giữ nguyên.
    Giữ nguyên các escape như \n, \t, ...
    """
    # Chỉ xử lý nếu có \uXXXX
    if not isinstance(s, str) or '\\u' not in s:
        return s

    # Hàm decode chỉ các phần \uXXXX, không chạm tới \n hay \t
    def decode_match(m):
        try:
            return bytes(m.group(0), "utf-8").decode("unicode_escape")
        except Exception:
            return m.group(0)

    try:
        return re.sub(r'\\u[0-9a-fA-F]{4}', decode_match, s)
    except Exception:
        return s
