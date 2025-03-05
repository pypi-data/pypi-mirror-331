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
import json
import logging
logger = logging.getLogger(__name__)
class BrowserStackSdk:
    def get_current_platform():
        bstack1l1lll111l_opy_ = {}
        bstack11l1llll1l_opy_ = os.environ.get(bstack111l11_opy_ (u"ࠫࡈ࡛ࡒࡓࡇࡑࡘࡤࡖࡌࡂࡖࡉࡓࡗࡓ࡟ࡅࡃࡗࡅ๊ࠬ"), bstack111l11_opy_ (u"๋ࠬ࠭"))
        if not bstack11l1llll1l_opy_:
            return bstack1l1lll111l_opy_
        try:
            bstack11l1llll11_opy_ = json.loads(bstack11l1llll1l_opy_)
            if bstack111l11_opy_ (u"ࠨ࡯ࡴࠤ์") in bstack11l1llll11_opy_:
                bstack1l1lll111l_opy_[bstack111l11_opy_ (u"ࠢࡰࡵࠥํ")] = bstack11l1llll11_opy_[bstack111l11_opy_ (u"ࠣࡱࡶࠦ๎")]
            if bstack111l11_opy_ (u"ࠤࡲࡷࡤࡼࡥࡳࡵ࡬ࡳࡳࠨ๏") in bstack11l1llll11_opy_ or bstack111l11_opy_ (u"ࠥࡳࡸ࡜ࡥࡳࡵ࡬ࡳࡳࠨ๐") in bstack11l1llll11_opy_:
                bstack1l1lll111l_opy_[bstack111l11_opy_ (u"ࠦࡴࡹࡖࡦࡴࡶ࡭ࡴࡴࠢ๑")] = bstack11l1llll11_opy_.get(bstack111l11_opy_ (u"ࠧࡵࡳࡠࡸࡨࡶࡸ࡯࡯࡯ࠤ๒"), bstack11l1llll11_opy_.get(bstack111l11_opy_ (u"ࠨ࡯ࡴࡘࡨࡶࡸ࡯࡯࡯ࠤ๓")))
            if bstack111l11_opy_ (u"ࠢࡣࡴࡲࡻࡸ࡫ࡲࠣ๔") in bstack11l1llll11_opy_ or bstack111l11_opy_ (u"ࠣࡤࡵࡳࡼࡹࡥࡳࡐࡤࡱࡪࠨ๕") in bstack11l1llll11_opy_:
                bstack1l1lll111l_opy_[bstack111l11_opy_ (u"ࠤࡥࡶࡴࡽࡳࡦࡴࡑࡥࡲ࡫ࠢ๖")] = bstack11l1llll11_opy_.get(bstack111l11_opy_ (u"ࠥࡦࡷࡵࡷࡴࡧࡵࠦ๗"), bstack11l1llll11_opy_.get(bstack111l11_opy_ (u"ࠦࡧࡸ࡯ࡸࡵࡨࡶࡓࡧ࡭ࡦࠤ๘")))
            if bstack111l11_opy_ (u"ࠧࡨࡲࡰࡹࡶࡩࡷࡥࡶࡦࡴࡶ࡭ࡴࡴࠢ๙") in bstack11l1llll11_opy_ or bstack111l11_opy_ (u"ࠨࡢࡳࡱࡺࡷࡪࡸࡖࡦࡴࡶ࡭ࡴࡴࠢ๚") in bstack11l1llll11_opy_:
                bstack1l1lll111l_opy_[bstack111l11_opy_ (u"ࠢࡣࡴࡲࡻࡸ࡫ࡲࡗࡧࡵࡷ࡮ࡵ࡮ࠣ๛")] = bstack11l1llll11_opy_.get(bstack111l11_opy_ (u"ࠣࡤࡵࡳࡼࡹࡥࡳࡡࡹࡩࡷࡹࡩࡰࡰࠥ๜"), bstack11l1llll11_opy_.get(bstack111l11_opy_ (u"ࠤࡥࡶࡴࡽࡳࡦࡴ࡙ࡩࡷࡹࡩࡰࡰࠥ๝")))
            if bstack111l11_opy_ (u"ࠥࡨࡪࡼࡩࡤࡧࠥ๞") in bstack11l1llll11_opy_ or bstack111l11_opy_ (u"ࠦࡩ࡫ࡶࡪࡥࡨࡒࡦࡳࡥࠣ๟") in bstack11l1llll11_opy_:
                bstack1l1lll111l_opy_[bstack111l11_opy_ (u"ࠧࡪࡥࡷ࡫ࡦࡩࡓࡧ࡭ࡦࠤ๠")] = bstack11l1llll11_opy_.get(bstack111l11_opy_ (u"ࠨࡤࡦࡸ࡬ࡧࡪࠨ๡"), bstack11l1llll11_opy_.get(bstack111l11_opy_ (u"ࠢࡥࡧࡹ࡭ࡨ࡫ࡎࡢ࡯ࡨࠦ๢")))
            if bstack111l11_opy_ (u"ࠣࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࠥ๣") in bstack11l1llll11_opy_ or bstack111l11_opy_ (u"ࠤࡳࡰࡦࡺࡦࡰࡴࡰࡒࡦࡳࡥࠣ๤") in bstack11l1llll11_opy_:
                bstack1l1lll111l_opy_[bstack111l11_opy_ (u"ࠥࡴࡱࡧࡴࡧࡱࡵࡱࡓࡧ࡭ࡦࠤ๥")] = bstack11l1llll11_opy_.get(bstack111l11_opy_ (u"ࠦࡵࡲࡡࡵࡨࡲࡶࡲࠨ๦"), bstack11l1llll11_opy_.get(bstack111l11_opy_ (u"ࠧࡶ࡬ࡢࡶࡩࡳࡷࡳࡎࡢ࡯ࡨࠦ๧")))
            if bstack111l11_opy_ (u"ࠨࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡠࡸࡨࡶࡸ࡯࡯࡯ࠤ๨") in bstack11l1llll11_opy_ or bstack111l11_opy_ (u"ࠢࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡘࡨࡶࡸ࡯࡯࡯ࠤ๩") in bstack11l1llll11_opy_:
                bstack1l1lll111l_opy_[bstack111l11_opy_ (u"ࠣࡲ࡯ࡥࡹ࡬࡯ࡳ࡯࡙ࡩࡷࡹࡩࡰࡰࠥ๪")] = bstack11l1llll11_opy_.get(bstack111l11_opy_ (u"ࠤࡳࡰࡦࡺࡦࡰࡴࡰࡣࡻ࡫ࡲࡴ࡫ࡲࡲࠧ๫"), bstack11l1llll11_opy_.get(bstack111l11_opy_ (u"ࠥࡴࡱࡧࡴࡧࡱࡵࡱ࡛࡫ࡲࡴ࡫ࡲࡲࠧ๬")))
            if bstack111l11_opy_ (u"ࠦࡨࡻࡳࡵࡱࡰ࡚ࡦࡸࡩࡢࡤ࡯ࡩࡸࠨ๭") in bstack11l1llll11_opy_:
                bstack1l1lll111l_opy_[bstack111l11_opy_ (u"ࠧࡩࡵࡴࡶࡲࡱ࡛ࡧࡲࡪࡣࡥࡰࡪࡹࠢ๮")] = bstack11l1llll11_opy_[bstack111l11_opy_ (u"ࠨࡣࡶࡵࡷࡳࡲ࡜ࡡࡳ࡫ࡤࡦࡱ࡫ࡳࠣ๯")]
        except Exception as error:
            logger.error(bstack111l11_opy_ (u"ࠢࡆࡺࡦࡩࡵࡺࡩࡰࡰࠣࡻ࡭࡯࡬ࡦࠢࡪࡩࡹࡺࡩ࡯ࡩࠣࡧࡺࡸࡲࡦࡰࡷࠤࡵࡲࡡࡵࡨࡲࡶࡲࠦࡤࡢࡶࡤ࠾ࠥࠨ๰") +  str(error))
        return bstack1l1lll111l_opy_