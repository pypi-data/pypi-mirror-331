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
import threading
from bstack_utils.helper import bstack111l1l111_opy_
from bstack_utils.constants import bstack1l111lll111_opy_, EVENTS, STAGE
from bstack_utils.bstack1ll1ll111_opy_ import get_logger
logger = get_logger(__name__)
class bstack11ll1ll1_opy_:
    bstack11l11lll111_opy_ = None
    @classmethod
    def bstack1l1l1llll1_opy_(cls):
        if cls.on() and os.getenv(bstack11l1ll1_opy_ (u"ࠤࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡖࡈࡗ࡙ࡎࡕࡃࡡࡘ࡙ࡎࡊࠢᵄ")):
            logger.info(
                bstack11l1ll1_opy_ (u"࡚ࠪ࡮ࡹࡩࡵࠢ࡫ࡸࡹࡶࡳ࠻࠱࠲ࡳࡧࡹࡥࡳࡸࡤࡦ࡮ࡲࡩࡵࡻ࠱ࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡦࡳࡲ࠵ࡢࡶ࡫࡯ࡨࡸ࠵ࡻࡾࠢࡷࡳࠥࡼࡩࡦࡹࠣࡦࡺ࡯࡬ࡥࠢࡵࡩࡵࡵࡲࡵ࠮ࠣ࡭ࡳࡹࡩࡨࡪࡷࡷ࠱ࠦࡡ࡯ࡦࠣࡱࡦࡴࡹࠡ࡯ࡲࡶࡪࠦࡤࡦࡤࡸ࡫࡬࡯࡮ࡨࠢ࡬ࡲ࡫ࡵࡲ࡮ࡣࡷ࡭ࡴࡴࠠࡢ࡮࡯ࠤࡦࡺࠠࡰࡰࡨࠤࡵࡲࡡࡤࡧࠤࡠࡳ࠭ᵅ").format(os.getenv(bstack11l1ll1_opy_ (u"ࠦࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡘࡊ࡙ࡔࡉࡗࡅࡣ࡚࡛ࡉࡅࠤᵆ"))))
    @classmethod
    def on(cls):
        if os.environ.get(bstack11l1ll1_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣ࡙ࡋࡓࡕࡊࡘࡆࡤࡐࡗࡕࠩᵇ"), None) is None or os.environ[bstack11l1ll1_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡚ࡅࡔࡖࡋ࡙ࡇࡥࡊࡘࡖࠪᵈ")] == bstack11l1ll1_opy_ (u"ࠢ࡯ࡷ࡯ࡰࠧᵉ"):
            return False
        return True
    @classmethod
    def bstack1l1l11111ll_opy_(cls, bs_config, framework=bstack11l1ll1_opy_ (u"ࠣࠤᵊ")):
        bstack1l11l1l11ll_opy_ = False
        for fw in bstack1l111lll111_opy_:
            if fw in framework:
                bstack1l11l1l11ll_opy_ = True
        return bstack111l1l111_opy_(bs_config.get(bstack11l1ll1_opy_ (u"ࠩࡷࡩࡸࡺࡏࡣࡵࡨࡶࡻࡧࡢࡪ࡮࡬ࡸࡾ࠭ᵋ"), bstack1l11l1l11ll_opy_))
    @classmethod
    def bstack11l1111111l_opy_(cls, framework):
        return framework in bstack1l111lll111_opy_
    @classmethod
    def bstack11l1111l111_opy_(cls, bs_config, framework):
        return cls.bstack1l1l11111ll_opy_(bs_config, framework) is True and cls.bstack11l1111111l_opy_(framework)
    @staticmethod
    def current_hook_uuid():
        return getattr(threading.current_thread(), bstack11l1ll1_opy_ (u"ࠪࡧࡺࡸࡲࡦࡰࡷࡣ࡭ࡵ࡯࡬ࡡࡸࡹ࡮ࡪࠧᵌ"), None)
    @staticmethod
    def bstack11l1l11l1l_opy_():
        if getattr(threading.current_thread(), bstack11l1ll1_opy_ (u"ࠫࡨࡻࡲࡳࡧࡱࡸࡤࡺࡥࡴࡶࡢࡹࡺ࡯ࡤࠨᵍ"), None):
            return {
                bstack11l1ll1_opy_ (u"ࠬࡺࡹࡱࡧࠪᵎ"): bstack11l1ll1_opy_ (u"࠭ࡴࡦࡵࡷࠫᵏ"),
                bstack11l1ll1_opy_ (u"ࠧࡵࡧࡶࡸࡤࡸࡵ࡯ࡡࡸࡹ࡮ࡪࠧᵐ"): getattr(threading.current_thread(), bstack11l1ll1_opy_ (u"ࠨࡥࡸࡶࡷ࡫࡮ࡵࡡࡷࡩࡸࡺ࡟ࡶࡷ࡬ࡨࠬᵑ"), None)
            }
        if getattr(threading.current_thread(), bstack11l1ll1_opy_ (u"ࠩࡦࡹࡷࡸࡥ࡯ࡶࡢ࡬ࡴࡵ࡫ࡠࡷࡸ࡭ࡩ࠭ᵒ"), None):
            return {
                bstack11l1ll1_opy_ (u"ࠪࡸࡾࡶࡥࠨᵓ"): bstack11l1ll1_opy_ (u"ࠫ࡭ࡵ࡯࡬ࠩᵔ"),
                bstack11l1ll1_opy_ (u"ࠬ࡮࡯ࡰ࡭ࡢࡶࡺࡴ࡟ࡶࡷ࡬ࡨࠬᵕ"): getattr(threading.current_thread(), bstack11l1ll1_opy_ (u"࠭ࡣࡶࡴࡵࡩࡳࡺ࡟ࡩࡱࡲ࡯ࡤࡻࡵࡪࡦࠪᵖ"), None)
            }
        return None
    @staticmethod
    def bstack11l11111111_opy_(func):
        def wrap(*args, **kwargs):
            if bstack11ll1ll1_opy_.on():
                return func(*args, **kwargs)
            return
        return wrap
    @staticmethod
    def bstack111ll1l1ll_opy_(test, hook_name=None):
        bstack111lllllll1_opy_ = test.parent
        if hook_name in [bstack11l1ll1_opy_ (u"ࠧࡴࡧࡷࡹࡵࡥࡣ࡭ࡣࡶࡷࠬᵗ"), bstack11l1ll1_opy_ (u"ࠨࡶࡨࡥࡷࡪ࡯ࡸࡰࡢࡧࡱࡧࡳࡴࠩᵘ"), bstack11l1ll1_opy_ (u"ࠩࡶࡩࡹࡻࡰࡠ࡯ࡲࡨࡺࡲࡥࠨᵙ"), bstack11l1ll1_opy_ (u"ࠪࡸࡪࡧࡲࡥࡱࡺࡲࡤࡳ࡯ࡥࡷ࡯ࡩࠬᵚ")]:
            bstack111lllllll1_opy_ = test
        scope = []
        while bstack111lllllll1_opy_ is not None:
            scope.append(bstack111lllllll1_opy_.name)
            bstack111lllllll1_opy_ = bstack111lllllll1_opy_.parent
        scope.reverse()
        return scope[2:]
    @staticmethod
    def bstack11l111111l1_opy_(hook_type):
        if hook_type == bstack11l1ll1_opy_ (u"ࠦࡇࡋࡆࡐࡔࡈࡣࡊࡇࡃࡉࠤᵛ"):
            return bstack11l1ll1_opy_ (u"࡙ࠧࡥࡵࡷࡳࠤ࡭ࡵ࡯࡬ࠤᵜ")
        elif hook_type == bstack11l1ll1_opy_ (u"ࠨࡁࡇࡖࡈࡖࡤࡋࡁࡄࡊࠥᵝ"):
            return bstack11l1ll1_opy_ (u"ࠢࡕࡧࡤࡶࡩࡵࡷ࡯ࠢ࡫ࡳࡴࡱࠢᵞ")
    @staticmethod
    def bstack111llllllll_opy_(bstack1ll11llll_opy_):
        try:
            if not bstack11ll1ll1_opy_.on():
                return bstack1ll11llll_opy_
            if os.environ.get(bstack11l1ll1_opy_ (u"ࠣࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡓࡇࡕ࡙ࡓࠨᵟ"), None) == bstack11l1ll1_opy_ (u"ࠤࡷࡶࡺ࡫ࠢᵠ"):
                tests = os.environ.get(bstack11l1ll1_opy_ (u"ࠥࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡕࡉࡗ࡛ࡎࡠࡖࡈࡗ࡙࡙ࠢᵡ"), None)
                if tests is None or tests == bstack11l1ll1_opy_ (u"ࠦࡳࡻ࡬࡭ࠤᵢ"):
                    return bstack1ll11llll_opy_
                bstack1ll11llll_opy_ = tests.split(bstack11l1ll1_opy_ (u"ࠬ࠲ࠧᵣ"))
                return bstack1ll11llll_opy_
        except Exception as exc:
            logger.debug(bstack11l1ll1_opy_ (u"ࠨࡅࡹࡥࡨࡴࡹ࡯࡯࡯ࠢ࡬ࡲࠥࡸࡥࡳࡷࡱࠤ࡭ࡧ࡮ࡥ࡮ࡨࡶ࠿ࠦࠢᵤ") + str(str(exc)) + bstack11l1ll1_opy_ (u"ࠢࠣᵥ"))
        return bstack1ll11llll_opy_