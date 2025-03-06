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
import threading
import logging
logger = logging.getLogger(__name__)
bstack11l11ll1l1l_opy_ = 1000
bstack11l11llllll_opy_ = 2
class bstack11l11lll1l1_opy_:
    def __init__(self, handler, bstack11l11lllll1_opy_=bstack11l11ll1l1l_opy_, bstack11l11ll1ll1_opy_=bstack11l11llllll_opy_):
        self.queue = []
        self.handler = handler
        self.bstack11l11lllll1_opy_ = bstack11l11lllll1_opy_
        self.bstack11l11ll1ll1_opy_ = bstack11l11ll1ll1_opy_
        self.lock = threading.Lock()
        self.timer = None
        self.bstack111l11l11l_opy_ = None
    def start(self):
        if not (self.timer and self.timer.is_alive()):
            self.bstack11l11lll1ll_opy_()
    def bstack11l11lll1ll_opy_(self):
        self.bstack111l11l11l_opy_ = threading.Event()
        def bstack11l11llll11_opy_():
            self.bstack111l11l11l_opy_.wait(self.bstack11l11ll1ll1_opy_)
            if not self.bstack111l11l11l_opy_.is_set():
                self.bstack11l11llll1l_opy_()
        self.timer = threading.Thread(target=bstack11l11llll11_opy_, daemon=True)
        self.timer.start()
    def bstack11l11lll11l_opy_(self):
        try:
            if self.bstack111l11l11l_opy_ and not self.bstack111l11l11l_opy_.is_set():
                self.bstack111l11l11l_opy_.set()
            if self.timer and self.timer.is_alive() and self.timer != threading.current_thread():
                self.timer.join()
        except Exception as e:
            logger.debug(bstack11l1ll1_opy_ (u"ࠨ࡝ࡶࡸࡴࡶ࡟ࡵ࡫ࡰࡩࡷࡣࠠࡆࡺࡦࡩࡵࡺࡩࡰࡰ࠽ࠤࠬᯐ") + (str(e) or bstack11l1ll1_opy_ (u"ࠤࡈࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥࡩ࡯ࡶ࡮ࡧࠤࡳࡵࡴࠡࡤࡨࠤࡨࡵ࡮ࡷࡧࡵࡸࡪࡪࠠࡵࡱࠣࡷࡹࡸࡩ࡯ࡩࠥᯑ")))
        finally:
            self.timer = None
    def bstack11l11ll1lll_opy_(self):
        if self.timer:
            self.bstack11l11lll11l_opy_()
        self.bstack11l11lll1ll_opy_()
    def add(self, event):
        with self.lock:
            self.queue.append(event)
            if len(self.queue) >= self.bstack11l11lllll1_opy_:
                threading.Thread(target=self.bstack11l11llll1l_opy_).start()
    def bstack11l11llll1l_opy_(self, source = bstack11l1ll1_opy_ (u"ࠪࠫᯒ")):
        with self.lock:
            if not self.queue:
                self.bstack11l11ll1lll_opy_()
                return
            data = self.queue[:self.bstack11l11lllll1_opy_]
            del self.queue[:self.bstack11l11lllll1_opy_]
        self.handler(data)
        if source != bstack11l1ll1_opy_ (u"ࠫࡸ࡮ࡵࡵࡦࡲࡻࡳ࠭ᯓ"):
            self.bstack11l11ll1lll_opy_()
    def shutdown(self):
        self.bstack11l11lll11l_opy_()
        while self.queue:
            self.bstack11l11llll1l_opy_(source=bstack11l1ll1_opy_ (u"ࠬࡹࡨࡶࡶࡧࡳࡼࡴࠧᯔ"))