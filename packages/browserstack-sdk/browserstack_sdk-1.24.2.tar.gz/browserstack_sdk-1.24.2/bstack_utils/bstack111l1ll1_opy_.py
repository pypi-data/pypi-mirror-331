# coding: UTF-8
import sys
bstack1111_opy_ = sys.version_info [0] == 2
bstack111_opy_ = 2048
bstack1lll11_opy_ = 7
def bstack11l1ll1_opy_ (bstack111lll_opy_):
    global bstack11ll_opy_
    bstack1l11lll_opy_ = ord (bstack111lll_opy_ [-1])
    bstack11111_opy_ = bstack111lll_opy_ [:-1]
    bstack111ll11_opy_ = bstack1l11lll_opy_ % len (bstack11111_opy_)
    bstack1l1l11_opy_ = bstack11111_opy_ [:bstack111ll11_opy_] + bstack11111_opy_ [bstack111ll11_opy_:]
    if bstack1111_opy_:
        bstack1ll11ll_opy_ = unicode () .join ([unichr (ord (char) - bstack111_opy_ - (bstack111l1l1_opy_ + bstack1l11lll_opy_) % bstack1lll11_opy_) for bstack111l1l1_opy_, char in enumerate (bstack1l1l11_opy_)])
    else:
        bstack1ll11ll_opy_ = str () .join ([chr (ord (char) - bstack111_opy_ - (bstack111l1l1_opy_ + bstack1l11lll_opy_) % bstack1lll11_opy_) for bstack111l1l1_opy_, char in enumerate (bstack1l1l11_opy_)])
    return eval (bstack1ll11ll_opy_)
from collections import deque
from bstack_utils.constants import *
class bstack1ll1l1ll11_opy_:
    def __init__(self):
        self._11l1ll1l1l1_opy_ = deque()
        self._11l1ll11ll1_opy_ = {}
        self._11l1ll111ll_opy_ = False
    def bstack11l1ll11111_opy_(self, test_name, bstack11l1ll11lll_opy_):
        bstack11l1ll1l11l_opy_ = self._11l1ll11ll1_opy_.get(test_name, {})
        return bstack11l1ll1l11l_opy_.get(bstack11l1ll11lll_opy_, 0)
    def bstack11l1ll1l1ll_opy_(self, test_name, bstack11l1ll11lll_opy_):
        bstack11l1ll11l11_opy_ = self.bstack11l1ll11111_opy_(test_name, bstack11l1ll11lll_opy_)
        self.bstack11l1ll111l1_opy_(test_name, bstack11l1ll11lll_opy_)
        return bstack11l1ll11l11_opy_
    def bstack11l1ll111l1_opy_(self, test_name, bstack11l1ll11lll_opy_):
        if test_name not in self._11l1ll11ll1_opy_:
            self._11l1ll11ll1_opy_[test_name] = {}
        bstack11l1ll1l11l_opy_ = self._11l1ll11ll1_opy_[test_name]
        bstack11l1ll11l11_opy_ = bstack11l1ll1l11l_opy_.get(bstack11l1ll11lll_opy_, 0)
        bstack11l1ll1l11l_opy_[bstack11l1ll11lll_opy_] = bstack11l1ll11l11_opy_ + 1
    def bstack11lllll111_opy_(self, bstack11l1ll1111l_opy_, bstack11l1ll1l111_opy_):
        bstack11l1l1lllll_opy_ = self.bstack11l1ll1l1ll_opy_(bstack11l1ll1111l_opy_, bstack11l1ll1l111_opy_)
        event_name = bstack1l111lllll1_opy_[bstack11l1ll1l111_opy_]
        bstack1ll11l11ll1_opy_ = bstack11l1ll1_opy_ (u"ࠧࢁࡽ࠮ࡽࢀ࠱ࢀࢃࠢ᭝").format(bstack11l1ll1111l_opy_, event_name, bstack11l1l1lllll_opy_)
        self._11l1ll1l1l1_opy_.append(bstack1ll11l11ll1_opy_)
    def bstack1ll1l111_opy_(self):
        return len(self._11l1ll1l1l1_opy_) == 0
    def bstack1ll11llll1_opy_(self):
        bstack11l1ll11l1l_opy_ = self._11l1ll1l1l1_opy_.popleft()
        return bstack11l1ll11l1l_opy_
    def capturing(self):
        return self._11l1ll111ll_opy_
    def bstack11llll111l_opy_(self):
        self._11l1ll111ll_opy_ = True
    def bstack1l1l111111_opy_(self):
        self._11l1ll111ll_opy_ = False