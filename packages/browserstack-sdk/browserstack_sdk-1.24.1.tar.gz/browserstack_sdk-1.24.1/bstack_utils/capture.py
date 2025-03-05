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
import builtins
import logging
class bstack11l1ll11ll_opy_:
    def __init__(self, handler):
        self._1111l1l1l1_opy_ = builtins.print
        self.handler = handler
        self._started = False
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self._1111l1ll11_opy_ = {
            level: getattr(self.logger, level)
            for level in [bstack111l11_opy_ (u"ࠩ࡬ࡲ࡫ࡵࠧႆ"), bstack111l11_opy_ (u"ࠪࡨࡪࡨࡵࡨࠩႇ"), bstack111l11_opy_ (u"ࠫࡼࡧࡲ࡯࡫ࡱ࡫ࠬႈ"), bstack111l11_opy_ (u"ࠬ࡫ࡲࡳࡱࡵࠫႉ")]
        }
    def start(self):
        if self._started:
            return
        self._started = True
        builtins.print = self._1111l1l11l_opy_
        self._1111l1lll1_opy_()
    def _1111l1l11l_opy_(self, *args, **kwargs):
        self._1111l1l1l1_opy_(*args, **kwargs)
        message = bstack111l11_opy_ (u"࠭ࠠࠨႊ").join(map(str, args)) + bstack111l11_opy_ (u"ࠧ࡝ࡰࠪႋ")
        self._log_message(bstack111l11_opy_ (u"ࠨࡋࡑࡊࡔ࠭ႌ"), message)
    def _log_message(self, level, msg, *args, **kwargs):
        if self.handler:
            self.handler({bstack111l11_opy_ (u"ࠩ࡯ࡩࡻ࡫࡬ࠨႍ"): level, bstack111l11_opy_ (u"ࠪࡱࡪࡹࡳࡢࡩࡨࠫႎ"): msg})
    def _1111l1lll1_opy_(self):
        for level, bstack1111l1ll1l_opy_ in self._1111l1ll11_opy_.items():
            setattr(logging, level, self._1111l1l1ll_opy_(level, bstack1111l1ll1l_opy_))
    def _1111l1l1ll_opy_(self, level, bstack1111l1ll1l_opy_):
        def wrapper(msg, *args, **kwargs):
            bstack1111l1ll1l_opy_(msg, *args, **kwargs)
            self._log_message(level.upper(), msg)
        return wrapper
    def reset(self):
        if not self._started:
            return
        self._started = False
        builtins.print = self._1111l1l1l1_opy_
        for level, bstack1111l1ll1l_opy_ in self._1111l1ll11_opy_.items():
            setattr(logging, level, bstack1111l1ll1l_opy_)