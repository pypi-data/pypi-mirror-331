# coding: UTF-8
import sys
bstack1l1l1l_opy_ = sys.version_info [0] == 2
bstack111l111_opy_ = 2048
bstack1lll1l_opy_ = 7
def bstack111l11_opy_ (bstack1ll_opy_):
    global bstack111lll1_opy_
    bstack1l11lll_opy_ = ord (bstack1ll_opy_ [-1])
    bstack111ll1_opy_ = bstack1ll_opy_ [:-1]
    bstack111l11l_opy_ = bstack1l11lll_opy_ % len (bstack111ll1_opy_)
    bstack111l1ll_opy_ = bstack111ll1_opy_ [:bstack111l11l_opy_] + bstack111ll1_opy_ [bstack111l11l_opy_:]
    if bstack1l1l1l_opy_:
        bstack11l1l1_opy_ = unicode () .join ([unichr (ord (char) - bstack111l111_opy_ - (bstack1ll1l_opy_ + bstack1l11lll_opy_) % bstack1lll1l_opy_) for bstack1ll1l_opy_, char in enumerate (bstack111l1ll_opy_)])
    else:
        bstack11l1l1_opy_ = str () .join ([chr (ord (char) - bstack111l111_opy_ - (bstack1ll1l_opy_ + bstack1l11lll_opy_) % bstack1lll1l_opy_) for bstack1ll1l_opy_, char in enumerate (bstack111l1ll_opy_)])
    return eval (bstack11l1l1_opy_)
from filelock import FileLock
import json
import os
import time
import uuid
from typing import Dict, List, Optional
from bstack_utils.constants import bstack11llll11l_opy_, EVENTS
from bstack_utils.helper import bstack11llllll_opy_, get_host_info, bstack1l1ll11l1l_opy_
from datetime import datetime
from bstack_utils.bstack1lll1ll1ll_opy_ import get_logger
logger = get_logger(__name__)
bstack1ll1l11111l_opy_: Dict[str, float] = {}
bstack1ll11llllll_opy_: List = []
bstack1lll11111l_opy_ = os.path.join(os.getcwd(), bstack111l11_opy_ (u"ࠩ࡯ࡳ࡬࠭ᚦ"), bstack111l11_opy_ (u"ࠪ࡯ࡪࡿ࠭࡮ࡧࡷࡶ࡮ࡩࡳ࠯࡬ࡶࡳࡳ࠭ᚧ"))
lock = FileLock(bstack1lll11111l_opy_+bstack111l11_opy_ (u"ࠦ࠳ࡲ࡯ࡤ࡭ࠥᚨ"))
class bstack1ll1l1111l1_opy_:
    duration: float
    name: str
    startTime: float
    worker: int
    status: bool
    failure: str
    details: Optional[str]
    entryType: str
    platform: Optional[int]
    command: Optional[str]
    hookType: Optional[str]
    def __init__(self, duration: float, name: str, start_time: float, bstack1ll1l1111ll_opy_: int, status: bool, failure: str, details: Optional[str] = None, platform: Optional[int] = None, command: Optional[str] = None, test_name: Optional[str] = None, hook_type: Optional[str] = None) -> None:
        self.duration = duration
        self.name = name
        self.startTime = start_time
        self.worker = bstack1ll1l1111ll_opy_
        self.status = status
        self.failure = failure
        self.details = details
        self.entryType = bstack111l11_opy_ (u"ࠧࡳࡥࡢࡵࡸࡶࡪࠨᚩ")
        self.platform = platform
        self.command = command
        self.testName = test_name
        self.hookType = hook_type
class bstack111l1l11l1_opy_:
    global bstack1ll1l11111l_opy_
    @staticmethod
    def mark(key: str) -> None:
        try:
            bstack1ll1l11111l_opy_[key] = time.time_ns() / 1000000
        except Exception as e:
            logger.debug(bstack111l11_opy_ (u"ࠨࡅࡳࡴࡲࡶ࠿ࠦࡻࡾࠤᚪ").format(e))
    @staticmethod
    def end(label: str, start: str, end: str, status: bool, failure: Optional[str], hook_type: Optional[str] = None, details: Optional[str] = None, command: Optional[str] = None, test_name: Optional[str] = None) -> None:
        try:
            bstack111l1l11l1_opy_.mark(end)
            bstack111l1l11l1_opy_.measure(label, start, end, status, failure, hook_type, details, command, test_name)
        except Exception as e:
            logger.debug(bstack111l11_opy_ (u"ࠢࡆࡴࡵࡳࡷࡀࠠࡼࡿࠥᚫ").format(e))
    @staticmethod
    def measure(label: str, start: str, end: str, status: bool, failure: Optional[str], hook_type: Optional[str] = None, details: Optional[str] = None, command: Optional[str] = None, test_name: Optional[str] = None) -> None:
        try:
            if start not in bstack1ll1l11111l_opy_ or end not in bstack1ll1l11111l_opy_:
                logger.debug(bstack111l11_opy_ (u"ࠣࡇࡵࡶࡴࡸࠠࡪࡰࠣࡷࡹࡧࡲࡵࠢ࡮ࡩࡾࠦࡷࡪࡶ࡫ࠤࡻࡧ࡬ࡶࡧࠣࡿࢂࠦ࡯ࡳࠢࡨࡲࡩࠦ࡫ࡦࡻࠣࡻ࡮ࡺࡨࠡࡸࡤࡰࡺ࡫ࠠࡼࡿࠥᚬ").format(start,end))
                return
            duration: float = bstack1ll1l11111l_opy_[end] - bstack1ll1l11111l_opy_[start]
            bstack1ll1l111l11_opy_: bstack1ll1l1111l1_opy_ = bstack1ll1l1111l1_opy_(duration, label, bstack1ll1l11111l_opy_[start], os.getpid(), status, failure, details, os.environ.get(bstack111l11_opy_ (u"ࠤࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡒࡏࡅ࡙ࡌࡏࡓࡏࡢࡍࡓࡊࡅ࡙ࠤᚭ"), 0), command, test_name, hook_type)
            del bstack1ll1l11111l_opy_[start]
            del bstack1ll1l11111l_opy_[end]
            bstack111l1l11l1_opy_.bstack1ll1l111111_opy_(bstack1ll1l111l11_opy_)
        except Exception as e:
            logger.debug(bstack111l11_opy_ (u"ࠥࡉࡷࡸ࡯ࡳ࠼ࠣࡿࢂࠨᚮ").format(e))
    @staticmethod
    def bstack1ll1l111111_opy_(bstack1ll1l111l11_opy_):
        os.makedirs(os.path.dirname(bstack1lll11111l_opy_)) if not os.path.exists(os.path.dirname(bstack1lll11111l_opy_)) else None
        try:
            with lock:
                with open(bstack1lll11111l_opy_, bstack111l11_opy_ (u"ࠦࡷ࠱ࠢᚯ"), encoding=bstack111l11_opy_ (u"ࠧࡻࡴࡧ࠯࠻ࠦᚰ")) as file:
                    try:
                        data = json.load(file)
                    except json.JSONDecodeError:
                        data = []
                    data.append(bstack1ll1l111l11_opy_.__dict__)
                    file.seek(0)
                    file.truncate()
                    json.dump(data, file, indent=4)
        except FileNotFoundError:
            with lock:
                with open(bstack1lll11111l_opy_, bstack111l11_opy_ (u"ࠨࡷࠣᚱ"), encoding=bstack111l11_opy_ (u"ࠢࡶࡶࡩ࠱࠽ࠨᚲ")) as file:
                    data = [bstack1ll1l111l11_opy_.__dict__]
                    json.dump(data, file, indent=4)
    @staticmethod
    def bstack111l1ll111_opy_(label: str) -> str:
        try:
            return bstack111l11_opy_ (u"ࠣࡽࢀ࠾ࢀࢃࠢᚳ").format(label,str(uuid.uuid4().hex)[:6])
        except Exception as e:
            logger.debug(bstack111l11_opy_ (u"ࠤࡈࡶࡷࡵࡲ࠻ࠢࡾࢁࠧᚴ").format(e))