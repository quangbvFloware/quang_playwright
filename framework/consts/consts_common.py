from enum import Enum

dir_caldav = "/calendarserver.php/calendars/"
dir_carddav = "/addressbookserver.php/addressbooks/"

ICON_REQUEST = "📨"
ICON_RESPONSE = "⮑"
ICON_PASSED = "✓"
ICON_FAILED = "✘"
ICON_WARNING = "⚠"

class ClientType(Enum):
    """Client types"""
    API = "api"
    WEB = "web"
    MAC = "mac"
    IPHONE = "iphone"
    IPAD = "ipad"
    

class APIServiceType(Enum):
    """Service types"""
    API = 1
    WEB = 2
    ADMIN = 3
    

class WebBrowserType(Enum):
    """Web browser types"""
    CHROMIUM = "chromium"
    FIREFOX = "firefox"
    WEBKIT = "webkit"
    EDGE = "edge"
    SAFARI = "safari"
    OPERA = "opera"
    BRAVE = "brave"
    YANDEX = "yandex"
    UC = "uc"
    MAXTHON = "maxthon"
    IE = "ie"
    EDGE_CHROMIUM = "edge-chromium"
    EDGE_LEGACY = "edge-legacy"
    EDGE_CHROMIUM_DEV = "edge-chromium-dev"
    

class UserRoles(Enum):
    """User roles"""
    OWNER = "owner"
    MEMBER = "member"
    ADMIN = "admin"
    
    
class InternalGroup(Enum):
    """
    Internal groups with ID and prefix
    
    Usage:
        >>> InternalGroup.WEB.value      # 1
        >>> InternalGroup.WEB.prefix     # "web763e90"
        >>> InternalGroup.WEB.id         # 1 (alias for value)
    """
    # (id, prefix)
    WEB = (1, "web763e90")
    MAC = (2, "mac763e90")
    IPHONE = (3, "ios763e90")
    IPAD = (4, "ipad763e90")
    QA = (5, "qa763e90")
    AUTO = (6, "auto763e90")
    
    def __init__(self, id, prefix):
        self._id = id
        self._prefix = prefix
    
    @property
    def id(self):
        """Get group ID"""
        return self._id
    
    @property
    def prefix(self):
        """Get group prefix"""
        return self._prefix
