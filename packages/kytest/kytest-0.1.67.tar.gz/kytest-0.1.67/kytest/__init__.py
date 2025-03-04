from .running.runner import main
from .running.conf import App
from .utils.config import kconfig
from .utils.pytest_util import *
from .utils.allure_util import *
from .utils.log import logger
from .api import HttpReq, TC
from .adr import AdrTC
from .ios import IosTC
from .web import WebTC
from .hm import HmTC

__version__ = "0.1.67"
__description__ = "API/安卓/IOS/WEB/鸿蒙Next平台自动化测试框架"
