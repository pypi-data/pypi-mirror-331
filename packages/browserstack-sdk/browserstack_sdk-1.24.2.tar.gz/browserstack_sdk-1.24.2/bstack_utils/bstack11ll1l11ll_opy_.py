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
class bstack1l111111ll_opy_:
    def __init__(self, handler):
        self._11l11ll11l1_opy_ = None
        self.handler = handler
        self._11l11ll111l_opy_ = self.bstack11l11ll11ll_opy_()
        self.patch()
    def patch(self):
        self._11l11ll11l1_opy_ = self._11l11ll111l_opy_.execute
        self._11l11ll111l_opy_.execute = self.bstack11l11ll1l11_opy_()
    def bstack11l11ll1l11_opy_(self):
        def execute(this, driver_command, *args, **kwargs):
            self.handler(bstack11l1ll1_opy_ (u"ࠨࡢࡦࡨࡲࡶࡪࠨᯕ"), driver_command, None, this, args)
            response = self._11l11ll11l1_opy_(this, driver_command, *args, **kwargs)
            self.handler(bstack11l1ll1_opy_ (u"ࠢࡢࡨࡷࡩࡷࠨᯖ"), driver_command, response)
            return response
        return execute
    def reset(self):
        self._11l11ll111l_opy_.execute = self._11l11ll11l1_opy_
    @staticmethod
    def bstack11l11ll11ll_opy_():
        from selenium.webdriver.remote.webdriver import WebDriver
        return WebDriver