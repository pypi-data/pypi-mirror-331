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
import builtins
import logging
class bstack11l1l1l11l_opy_:
    def __init__(self, handler):
        self._1l11l1ll1ll_opy_ = builtins.print
        self.handler = handler
        self._started = False
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self._1l11l1ll1l1_opy_ = {
            level: getattr(self.logger, level)
            for level in [bstack11l1ll1_opy_ (u"ࠩ࡬ࡲ࡫ࡵࠧᓦ"), bstack11l1ll1_opy_ (u"ࠪࡨࡪࡨࡵࡨࠩᓧ"), bstack11l1ll1_opy_ (u"ࠫࡼࡧࡲ࡯࡫ࡱ࡫ࠬᓨ"), bstack11l1ll1_opy_ (u"ࠬ࡫ࡲࡳࡱࡵࠫᓩ")]
        }
    def start(self):
        if self._started:
            return
        self._started = True
        builtins.print = self._1l11l1ll11l_opy_
        self._1l11l1l1lll_opy_()
    def _1l11l1ll11l_opy_(self, *args, **kwargs):
        self._1l11l1ll1ll_opy_(*args, **kwargs)
        message = bstack11l1ll1_opy_ (u"࠭ࠠࠨᓪ").join(map(str, args)) + bstack11l1ll1_opy_ (u"ࠧ࡝ࡰࠪᓫ")
        self._log_message(bstack11l1ll1_opy_ (u"ࠨࡋࡑࡊࡔ࠭ᓬ"), message)
    def _log_message(self, level, msg, *args, **kwargs):
        if self.handler:
            self.handler({bstack11l1ll1_opy_ (u"ࠩ࡯ࡩࡻ࡫࡬ࠨᓭ"): level, bstack11l1ll1_opy_ (u"ࠪࡱࡪࡹࡳࡢࡩࡨࠫᓮ"): msg})
    def _1l11l1l1lll_opy_(self):
        for level, bstack1l11l1ll111_opy_ in self._1l11l1ll1l1_opy_.items():
            setattr(logging, level, self._1l11l1l1ll1_opy_(level, bstack1l11l1ll111_opy_))
    def _1l11l1l1ll1_opy_(self, level, bstack1l11l1ll111_opy_):
        def wrapper(msg, *args, **kwargs):
            bstack1l11l1ll111_opy_(msg, *args, **kwargs)
            self._log_message(level.upper(), msg)
        return wrapper
    def reset(self):
        if not self._started:
            return
        self._started = False
        builtins.print = self._1l11l1ll1ll_opy_
        for level, bstack1l11l1ll111_opy_ in self._1l11l1ll1l1_opy_.items():
            setattr(logging, level, bstack1l11l1ll111_opy_)