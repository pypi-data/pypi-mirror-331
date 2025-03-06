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
import os
class RobotHandler():
    def __init__(self, args, logger, bstack111l1lll1l_opy_, bstack111l1l1l11_opy_):
        self.args = args
        self.logger = logger
        self.bstack111l1lll1l_opy_ = bstack111l1lll1l_opy_
        self.bstack111l1l1l11_opy_ = bstack111l1l1l11_opy_
    @staticmethod
    def version():
        import robot
        return robot.__version__
    @staticmethod
    def bstack111ll1l1ll_opy_(bstack111l11ll1l_opy_):
        bstack111l11lll1_opy_ = []
        if bstack111l11ll1l_opy_:
            tokens = str(os.path.basename(bstack111l11ll1l_opy_)).split(bstack11l1ll1_opy_ (u"ࠢࡠࠤ࿇"))
            camelcase_name = bstack11l1ll1_opy_ (u"ࠣࠢࠥ࿈").join(t.title() for t in tokens)
            suite_name, bstack111l11llll_opy_ = os.path.splitext(camelcase_name)
            bstack111l11lll1_opy_.append(suite_name)
        return bstack111l11lll1_opy_
    @staticmethod
    def bstack111l1l1111_opy_(typename):
        if bstack11l1ll1_opy_ (u"ࠤࡄࡷࡸ࡫ࡲࡵ࡫ࡲࡲࠧ࿉") in typename:
            return bstack11l1ll1_opy_ (u"ࠥࡅࡸࡹࡥࡳࡶ࡬ࡳࡳࡋࡲࡳࡱࡵࠦ࿊")
        return bstack11l1ll1_opy_ (u"࡚ࠦࡴࡨࡢࡰࡧࡰࡪࡪࡅࡳࡴࡲࡶࠧ࿋")