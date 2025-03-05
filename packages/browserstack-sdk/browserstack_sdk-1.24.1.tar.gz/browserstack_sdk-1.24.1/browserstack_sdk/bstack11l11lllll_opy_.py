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
import os
class RobotHandler():
    def __init__(self, args, logger, bstack111ll1111l_opy_, bstack111l1llll1_opy_):
        self.args = args
        self.logger = logger
        self.bstack111ll1111l_opy_ = bstack111ll1111l_opy_
        self.bstack111l1llll1_opy_ = bstack111l1llll1_opy_
    @staticmethod
    def version():
        import robot
        return robot.__version__
    @staticmethod
    def bstack111llll1ll_opy_(bstack111l1ll1l1_opy_):
        bstack111l1ll1ll_opy_ = []
        if bstack111l1ll1l1_opy_:
            tokens = str(os.path.basename(bstack111l1ll1l1_opy_)).split(bstack111l11_opy_ (u"ࠤࡢࠦྭ"))
            camelcase_name = bstack111l11_opy_ (u"ࠥࠤࠧྮ").join(t.title() for t in tokens)
            suite_name, bstack111l1ll11l_opy_ = os.path.splitext(camelcase_name)
            bstack111l1ll1ll_opy_.append(suite_name)
        return bstack111l1ll1ll_opy_
    @staticmethod
    def bstack111l1lll11_opy_(typename):
        if bstack111l11_opy_ (u"ࠦࡆࡹࡳࡦࡴࡷ࡭ࡴࡴࠢྯ") in typename:
            return bstack111l11_opy_ (u"ࠧࡇࡳࡴࡧࡵࡸ࡮ࡵ࡮ࡆࡴࡵࡳࡷࠨྰ")
        return bstack111l11_opy_ (u"ࠨࡕ࡯ࡪࡤࡲࡩࡲࡥࡥࡇࡵࡶࡴࡸࠢྱ")