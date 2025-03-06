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
import logging
import abc
from browserstack_sdk.sdk_cli.bstack111l11l111_opy_ import bstack111l111lll_opy_
class bstack1111111l1l_opy_(abc.ABC):
    bin_session_id: str
    bstack111l11l111_opy_: bstack111l111lll_opy_
    def __init__(self):
        self.bstack11111111l1_opy_ = None
        self.config = None
        self.bin_session_id = None
        self.bstack111l11l111_opy_ = None
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)
    def bstack1lll1ll111l_opy_(self):
        return (self.bstack11111111l1_opy_ != None and self.bin_session_id != None and self.bstack111l11l111_opy_ != None)
    def configure(self, bstack11111111l1_opy_, config, bin_session_id: str, bstack111l11l111_opy_: bstack111l111lll_opy_):
        self.bstack11111111l1_opy_ = bstack11111111l1_opy_
        self.config = config
        self.bin_session_id = bin_session_id
        self.bstack111l11l111_opy_ = bstack111l11l111_opy_
        if self.bin_session_id:
            self.logger.debug(bstack11l1ll1_opy_ (u"ࠦࡠࢁࡩࡥࠪࡶࡩࡱ࡬ࠩࡾ࡟ࠣࡧࡴࡴࡦࡪࡩࡸࡶࡪࡪࠠ࡮ࡱࡧࡹࡱ࡫ࠠࡼࡵࡨࡰ࡫࠴࡟ࡠࡥ࡯ࡥࡸࡹ࡟ࡠ࠰ࡢࡣࡳࡧ࡭ࡦࡡࡢࢁ࠿ࠦࡢࡪࡰࡢࡷࡪࡹࡳࡪࡱࡱࡣ࡮ࡪ࠽ࠣᅓ") + str(self.bin_session_id) + bstack11l1ll1_opy_ (u"ࠧࠨᅔ"))
    def bstack1lll111l1ll_opy_(self):
        if not self.bin_session_id:
            raise ValueError(bstack11l1ll1_opy_ (u"ࠨࡢࡪࡰࡢࡷࡪࡹࡳࡪࡱࡱࡣ࡮ࡪࠠࡤࡣࡱࡲࡴࡺࠠࡣࡧࠣࡒࡴࡴࡥࠣᅕ"))
    @abc.abstractmethod
    def is_enabled(self) -> bool:
        return False