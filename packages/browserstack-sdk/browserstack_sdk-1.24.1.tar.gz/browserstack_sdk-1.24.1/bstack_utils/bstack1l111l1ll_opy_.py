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
class bstack1l1lll1ll1_opy_:
    def __init__(self, handler):
        self._1ll111lll1l_opy_ = None
        self.handler = handler
        self._1ll111lll11_opy_ = self.bstack1ll111ll1l1_opy_()
        self.patch()
    def patch(self):
        self._1ll111lll1l_opy_ = self._1ll111lll11_opy_.execute
        self._1ll111lll11_opy_.execute = self.bstack1ll111ll1ll_opy_()
    def bstack1ll111ll1ll_opy_(self):
        def execute(this, driver_command, *args, **kwargs):
            self.handler(bstack111l11_opy_ (u"ࠨࡢࡦࡨࡲࡶࡪࠨᜓ"), driver_command, None, this, args)
            response = self._1ll111lll1l_opy_(this, driver_command, *args, **kwargs)
            self.handler(bstack111l11_opy_ (u"ࠢࡢࡨࡷࡩࡷࠨ᜔"), driver_command, response)
            return response
        return execute
    def reset(self):
        self._1ll111lll11_opy_.execute = self._1ll111lll1l_opy_
    @staticmethod
    def bstack1ll111ll1l1_opy_():
        from selenium.webdriver.remote.webdriver import WebDriver
        return WebDriver