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
from collections import deque
from bstack_utils.constants import *
class bstack1l1l1ll1l1_opy_:
    def __init__(self):
        self._1ll1l11ll1l_opy_ = deque()
        self._1ll1l11lll1_opy_ = {}
        self._1ll1l111lll_opy_ = False
    def bstack1ll1l11l111_opy_(self, test_name, bstack1ll1l11l1l1_opy_):
        bstack1ll1l1l1111_opy_ = self._1ll1l11lll1_opy_.get(test_name, {})
        return bstack1ll1l1l1111_opy_.get(bstack1ll1l11l1l1_opy_, 0)
    def bstack1ll1l11ll11_opy_(self, test_name, bstack1ll1l11l1l1_opy_):
        bstack1ll1l11l11l_opy_ = self.bstack1ll1l11l111_opy_(test_name, bstack1ll1l11l1l1_opy_)
        self.bstack1ll1l111l1l_opy_(test_name, bstack1ll1l11l1l1_opy_)
        return bstack1ll1l11l11l_opy_
    def bstack1ll1l111l1l_opy_(self, test_name, bstack1ll1l11l1l1_opy_):
        if test_name not in self._1ll1l11lll1_opy_:
            self._1ll1l11lll1_opy_[test_name] = {}
        bstack1ll1l1l1111_opy_ = self._1ll1l11lll1_opy_[test_name]
        bstack1ll1l11l11l_opy_ = bstack1ll1l1l1111_opy_.get(bstack1ll1l11l1l1_opy_, 0)
        bstack1ll1l1l1111_opy_[bstack1ll1l11l1l1_opy_] = bstack1ll1l11l11l_opy_ + 1
    def bstack11l1l1111_opy_(self, bstack1ll1l1l111l_opy_, bstack1ll1l11llll_opy_):
        bstack1ll1l11l1ll_opy_ = self.bstack1ll1l11ll11_opy_(bstack1ll1l1l111l_opy_, bstack1ll1l11llll_opy_)
        event_name = bstack11111l1ll1_opy_[bstack1ll1l11llll_opy_]
        bstack1ll1l1l11l1_opy_ = bstack111l11_opy_ (u"ࠣࡽࢀ࠱ࢀࢃ࠭ࡼࡿࠥᚥ").format(bstack1ll1l1l111l_opy_, event_name, bstack1ll1l11l1ll_opy_)
        self._1ll1l11ll1l_opy_.append(bstack1ll1l1l11l1_opy_)
    def bstack111l11ll1_opy_(self):
        return len(self._1ll1l11ll1l_opy_) == 0
    def bstack1ll11l1ll_opy_(self):
        bstack1ll1l111ll1_opy_ = self._1ll1l11ll1l_opy_.popleft()
        return bstack1ll1l111ll1_opy_
    def capturing(self):
        return self._1ll1l111lll_opy_
    def bstack111ll1ll_opy_(self):
        self._1ll1l111lll_opy_ = True
    def bstack1l1111l11_opy_(self):
        self._1ll1l111lll_opy_ = False