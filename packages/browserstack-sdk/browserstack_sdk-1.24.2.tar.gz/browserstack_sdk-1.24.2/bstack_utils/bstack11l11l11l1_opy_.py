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
import json
import logging
import os
import datetime
import threading
from bstack_utils.constants import EVENTS, STAGE
from bstack_utils.helper import bstack1l11ll11l1l_opy_, bstack1l11llll111_opy_, bstack1l1111l1l_opy_, bstack111llll1ll_opy_, bstack11lll1l1l1l_opy_, bstack11lll11ll1l_opy_, bstack1l1l1111111_opy_, bstack1ll1l1ll_opy_
from bstack_utils.measure import measure
from bstack_utils.bstack11l11lll111_opy_ import bstack11l11lll1l1_opy_
import bstack_utils.bstack1lll1lll1_opy_ as bstack1l1l1lll11_opy_
from bstack_utils.bstack11l11l1lll_opy_ import bstack11ll1ll1_opy_
import bstack_utils.accessibility as bstack11lll11ll1_opy_
from bstack_utils.bstack1l1ll1111l_opy_ import bstack1l1ll1111l_opy_
from bstack_utils.bstack11l11lllll_opy_ import bstack111ll1l1l1_opy_
bstack11l1111llll_opy_ = bstack11l1ll1_opy_ (u"ࠫ࡭ࡺࡴࡱࡵ࠽࠳࠴ࡩ࡯࡭࡮ࡨࡧࡹࡵࡲ࠮ࡱࡥࡷࡪࡸࡶࡢࡤ࡬ࡰ࡮ࡺࡹ࠯ࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡤࡱࡰࠫ᱊")
logger = logging.getLogger(__name__)
class bstack11111l1l1_opy_:
    bstack11l11lll111_opy_ = None
    bs_config = None
    bstack1lll11ll1_opy_ = None
    @classmethod
    @bstack111llll1ll_opy_(class_method=True)
    @measure(event_name=EVENTS.bstack1l11l111l11_opy_, stage=STAGE.bstack1l1ll1llll_opy_)
    def launch(cls, bs_config, bstack1lll11ll1_opy_):
        cls.bs_config = bs_config
        cls.bstack1lll11ll1_opy_ = bstack1lll11ll1_opy_
        try:
            cls.bstack11l111111ll_opy_()
            bstack1l11ll11111_opy_ = bstack1l11ll11l1l_opy_(bs_config)
            bstack1l11lll1l1l_opy_ = bstack1l11llll111_opy_(bs_config)
            data = bstack1l1l1lll11_opy_.bstack1l11llll11l_opy_(bs_config, bstack1lll11ll1_opy_)
            config = {
                bstack11l1ll1_opy_ (u"ࠬࡧࡵࡵࡪࠪ᱋"): (bstack1l11ll11111_opy_, bstack1l11lll1l1l_opy_),
                bstack11l1ll1_opy_ (u"࠭ࡨࡦࡣࡧࡩࡷࡹࠧ᱌"): cls.default_headers()
            }
            response = bstack1l1111l1l_opy_(bstack11l1ll1_opy_ (u"ࠧࡑࡑࡖࡘࠬᱍ"), cls.request_url(bstack11l1ll1_opy_ (u"ࠨࡣࡳ࡭࠴ࡼ࠲࠰ࡤࡸ࡭ࡱࡪࡳࠨᱎ")), data, config)
            if response.status_code != 200:
                bstack1lll1ll1l11_opy_ = response.json()
                if bstack1lll1ll1l11_opy_[bstack11l1ll1_opy_ (u"ࠩࡶࡹࡨࡩࡥࡴࡵࠪᱏ")] == False:
                    cls.bstack11l111l111l_opy_(bstack1lll1ll1l11_opy_)
                    return
                cls.bstack11l111ll1l1_opy_(bstack1lll1ll1l11_opy_[bstack11l1ll1_opy_ (u"ࠪࡳࡧࡹࡥࡳࡸࡤࡦ࡮ࡲࡩࡵࡻࠪ᱐")])
                cls.bstack11l1111l11l_opy_(bstack1lll1ll1l11_opy_[bstack11l1ll1_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠫ᱑")])
                return None
            bstack11l1111ll11_opy_ = cls.bstack11l11111lll_opy_(response)
            return bstack11l1111ll11_opy_
        except Exception as error:
            logger.error(bstack11l1ll1_opy_ (u"ࠧࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡࡹ࡫࡭ࡱ࡫ࠠࡤࡴࡨࡥࡹ࡯࡮ࡨࠢࡥࡹ࡮ࡲࡤࠡࡨࡲࡶ࡚ࠥࡥࡴࡶࡋࡹࡧࡀࠠࡼࡿࠥ᱒").format(str(error)))
            return None
    @classmethod
    @bstack111llll1ll_opy_(class_method=True)
    def stop(cls, bstack11l1111lll1_opy_=None):
        if not bstack11ll1ll1_opy_.on() and not bstack11lll11ll1_opy_.on():
            return
        if os.environ.get(bstack11l1ll1_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡚ࡅࡔࡖࡋ࡙ࡇࡥࡊࡘࡖࠪ᱓")) == bstack11l1ll1_opy_ (u"ࠢ࡯ࡷ࡯ࡰࠧ᱔") or os.environ.get(bstack11l1ll1_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡕࡇࡖࡘࡍ࡛ࡂࡠࡗࡘࡍࡉ࠭᱕")) == bstack11l1ll1_opy_ (u"ࠤࡱࡹࡱࡲࠢ᱖"):
            logger.error(bstack11l1ll1_opy_ (u"ࠪࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡩ࡯ࠢࡶࡸࡴࡶࠠࡣࡷ࡬ࡰࡩࠦࡲࡦࡳࡸࡩࡸࡺࠠࡵࡱࠣࡘࡪࡹࡴࡉࡷࡥ࠾ࠥࡓࡩࡴࡵ࡬ࡲ࡬ࠦࡡࡶࡶ࡫ࡩࡳࡺࡩࡤࡣࡷ࡭ࡴࡴࠠࡵࡱ࡮ࡩࡳ࠭᱗"))
            return {
                bstack11l1ll1_opy_ (u"ࠫࡸࡺࡡࡵࡷࡶࠫ᱘"): bstack11l1ll1_opy_ (u"ࠬ࡫ࡲࡳࡱࡵࠫ᱙"),
                bstack11l1ll1_opy_ (u"࠭࡭ࡦࡵࡶࡥ࡬࡫ࠧᱚ"): bstack11l1ll1_opy_ (u"ࠧࡕࡱ࡮ࡩࡳ࠵ࡢࡶ࡫࡯ࡨࡎࡊࠠࡪࡵࠣࡹࡳࡪࡥࡧ࡫ࡱࡩࡩ࠲ࠠࡣࡷ࡬ࡰࡩࠦࡣࡳࡧࡤࡸ࡮ࡵ࡮ࠡ࡯࡬࡫࡭ࡺࠠࡩࡣࡹࡩࠥ࡬ࡡࡪ࡮ࡨࡨࠬᱛ")
            }
        try:
            cls.bstack11l11lll111_opy_.shutdown()
            data = {
                bstack11l1ll1_opy_ (u"ࠨࡨ࡬ࡲ࡮ࡹࡨࡦࡦࡢࡥࡹ࠭ᱜ"): bstack1ll1l1ll_opy_()
            }
            if not bstack11l1111lll1_opy_ is None:
                data[bstack11l1ll1_opy_ (u"ࠩࡩ࡭ࡳ࡯ࡳࡩࡧࡧࡣࡲ࡫ࡴࡢࡦࡤࡸࡦ࠭ᱝ")] = [{
                    bstack11l1ll1_opy_ (u"ࠪࡶࡪࡧࡳࡰࡰࠪᱞ"): bstack11l1ll1_opy_ (u"ࠫࡺࡹࡥࡳࡡ࡮࡭ࡱࡲࡥࡥࠩᱟ"),
                    bstack11l1ll1_opy_ (u"ࠬࡹࡩࡨࡰࡤࡰࠬᱠ"): bstack11l1111lll1_opy_
                }]
            config = {
                bstack11l1ll1_opy_ (u"࠭ࡨࡦࡣࡧࡩࡷࡹࠧᱡ"): cls.default_headers()
            }
            bstack11lllll1l1l_opy_ = bstack11l1ll1_opy_ (u"ࠧࡢࡲ࡬࠳ࡻ࠷࠯ࡣࡷ࡬ࡰࡩࡹ࠯ࡼࡿ࠲ࡷࡹࡵࡰࠨᱢ").format(os.environ[bstack11l1ll1_opy_ (u"ࠣࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡕࡇࡖࡘࡍ࡛ࡂࡠࡗࡘࡍࡉࠨᱣ")])
            bstack11l111l1l11_opy_ = cls.request_url(bstack11lllll1l1l_opy_)
            response = bstack1l1111l1l_opy_(bstack11l1ll1_opy_ (u"ࠩࡓ࡙࡙࠭ᱤ"), bstack11l111l1l11_opy_, data, config)
            if not response.ok:
                raise Exception(bstack11l1ll1_opy_ (u"ࠥࡗࡹࡵࡰࠡࡴࡨࡵࡺ࡫ࡳࡵࠢࡱࡳࡹࠦ࡯࡬ࠤᱥ"))
        except Exception as error:
            logger.error(bstack11l1ll1_opy_ (u"ࠦࡊࡾࡣࡦࡲࡷ࡭ࡴࡴࠠࡪࡰࠣࡷࡹࡵࡰࠡࡤࡸ࡭ࡱࡪࠠࡳࡧࡴࡹࡪࡹࡴࠡࡶࡲࠤ࡙࡫ࡳࡵࡊࡸࡦ࠿ࡀࠠࠣᱦ") + str(error))
            return {
                bstack11l1ll1_opy_ (u"ࠬࡹࡴࡢࡶࡸࡷࠬᱧ"): bstack11l1ll1_opy_ (u"࠭ࡥࡳࡴࡲࡶࠬᱨ"),
                bstack11l1ll1_opy_ (u"ࠧ࡮ࡧࡶࡷࡦ࡭ࡥࠨᱩ"): str(error)
            }
    @classmethod
    @bstack111llll1ll_opy_(class_method=True)
    def bstack11l11111lll_opy_(cls, response):
        bstack1lll1ll1l11_opy_ = response.json() if not isinstance(response, dict) else response
        bstack11l1111ll11_opy_ = {}
        if bstack1lll1ll1l11_opy_.get(bstack11l1ll1_opy_ (u"ࠨ࡬ࡺࡸࠬᱪ")) is None:
            os.environ[bstack11l1ll1_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡖࡈࡗ࡙ࡎࡕࡃࡡࡍ࡛࡙࠭ᱫ")] = bstack11l1ll1_opy_ (u"ࠪࡲࡺࡲ࡬ࠨᱬ")
        else:
            os.environ[bstack11l1ll1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡘࡊ࡙ࡔࡉࡗࡅࡣࡏ࡝ࡔࠨᱭ")] = bstack1lll1ll1l11_opy_.get(bstack11l1ll1_opy_ (u"ࠬࡰࡷࡵࠩᱮ"), bstack11l1ll1_opy_ (u"࠭࡮ࡶ࡮࡯ࠫᱯ"))
        os.environ[bstack11l1ll1_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡔࡆࡕࡗࡌ࡚ࡈ࡟ࡖࡗࡌࡈࠬᱰ")] = bstack1lll1ll1l11_opy_.get(bstack11l1ll1_opy_ (u"ࠨࡤࡸ࡭ࡱࡪ࡟ࡩࡣࡶ࡬ࡪࡪ࡟ࡪࡦࠪᱱ"), bstack11l1ll1_opy_ (u"ࠩࡱࡹࡱࡲࠧᱲ"))
        logger.info(bstack11l1ll1_opy_ (u"ࠪࡘࡪࡹࡴࡩࡷࡥࠤࡸࡺࡡࡳࡶࡨࡨࠥࡽࡩࡵࡪࠣ࡭ࡩࡀࠠࠨᱳ") + os.getenv(bstack11l1ll1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡘࡊ࡙ࡔࡉࡗࡅࡣ࡚࡛ࡉࡅࠩᱴ")));
        if bstack11ll1ll1_opy_.bstack11l1111l111_opy_(cls.bs_config, cls.bstack1lll11ll1_opy_.get(bstack11l1ll1_opy_ (u"ࠬ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࡠࡷࡶࡩࡩ࠭ᱵ"), bstack11l1ll1_opy_ (u"࠭ࠧᱶ"))) is True:
            bstack11l111l11ll_opy_, build_hashed_id, bstack11l111l1111_opy_ = cls.bstack11l111l11l1_opy_(bstack1lll1ll1l11_opy_)
            if bstack11l111l11ll_opy_ != None and build_hashed_id != None:
                bstack11l1111ll11_opy_[bstack11l1ll1_opy_ (u"ࠧࡰࡤࡶࡩࡷࡼࡡࡣ࡫࡯࡭ࡹࡿࠧᱷ")] = {
                    bstack11l1ll1_opy_ (u"ࠨ࡬ࡺࡸࡤࡺ࡯࡬ࡧࡱࠫᱸ"): bstack11l111l11ll_opy_,
                    bstack11l1ll1_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡠࡪࡤࡷ࡭࡫ࡤࡠ࡫ࡧࠫᱹ"): build_hashed_id,
                    bstack11l1ll1_opy_ (u"ࠪࡥࡱࡲ࡯ࡸࡡࡶࡧࡷ࡫ࡥ࡯ࡵ࡫ࡳࡹࡹࠧᱺ"): bstack11l111l1111_opy_
                }
            else:
                bstack11l1111ll11_opy_[bstack11l1ll1_opy_ (u"ࠫࡴࡨࡳࡦࡴࡹࡥࡧ࡯࡬ࡪࡶࡼࠫᱻ")] = {}
        else:
            bstack11l1111ll11_opy_[bstack11l1ll1_opy_ (u"ࠬࡵࡢࡴࡧࡵࡺࡦࡨࡩ࡭࡫ࡷࡽࠬᱼ")] = {}
        if bstack11lll11ll1_opy_.bstack1l11lllllll_opy_(cls.bs_config) is True:
            bstack11l1111ll1l_opy_, build_hashed_id = cls.bstack11l11111l1l_opy_(bstack1lll1ll1l11_opy_)
            if bstack11l1111ll1l_opy_ != None and build_hashed_id != None:
                bstack11l1111ll11_opy_[bstack11l1ll1_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾ࠭ᱽ")] = {
                    bstack11l1ll1_opy_ (u"ࠧࡢࡷࡷ࡬ࡤࡺ࡯࡬ࡧࡱࠫ᱾"): bstack11l1111ll1l_opy_,
                    bstack11l1ll1_opy_ (u"ࠨࡤࡸ࡭ࡱࡪ࡟ࡩࡣࡶ࡬ࡪࡪ࡟ࡪࡦࠪ᱿"): build_hashed_id,
                }
            else:
                bstack11l1111ll11_opy_[bstack11l1ll1_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠩᲀ")] = {}
        else:
            bstack11l1111ll11_opy_[bstack11l1ll1_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠪᲁ")] = {}
        if bstack11l1111ll11_opy_[bstack11l1ll1_opy_ (u"ࠫࡴࡨࡳࡦࡴࡹࡥࡧ࡯࡬ࡪࡶࡼࠫᲂ")].get(bstack11l1ll1_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡣ࡭ࡧࡳࡩࡧࡧࡣ࡮ࡪࠧᲃ")) != None or bstack11l1111ll11_opy_[bstack11l1ll1_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾ࠭ᲄ")].get(bstack11l1ll1_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡥࡨࡢࡵ࡫ࡩࡩࡥࡩࡥࠩᲅ")) != None:
            cls.bstack11l111l1lll_opy_(bstack1lll1ll1l11_opy_.get(bstack11l1ll1_opy_ (u"ࠨ࡬ࡺࡸࠬᲆ")), bstack1lll1ll1l11_opy_.get(bstack11l1ll1_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡠࡪࡤࡷ࡭࡫ࡤࡠ࡫ࡧࠫᲇ")))
        return bstack11l1111ll11_opy_
    @classmethod
    def bstack11l111l11l1_opy_(cls, bstack1lll1ll1l11_opy_):
        if bstack1lll1ll1l11_opy_.get(bstack11l1ll1_opy_ (u"ࠪࡳࡧࡹࡥࡳࡸࡤࡦ࡮ࡲࡩࡵࡻࠪᲈ")) == None:
            cls.bstack11l111ll1l1_opy_()
            return [None, None, None]
        if bstack1lll1ll1l11_opy_[bstack11l1ll1_opy_ (u"ࠫࡴࡨࡳࡦࡴࡹࡥࡧ࡯࡬ࡪࡶࡼࠫᲉ")][bstack11l1ll1_opy_ (u"ࠬࡹࡵࡤࡥࡨࡷࡸ࠭ᲊ")] != True:
            cls.bstack11l111ll1l1_opy_(bstack1lll1ll1l11_opy_[bstack11l1ll1_opy_ (u"࠭࡯ࡣࡵࡨࡶࡻࡧࡢࡪ࡮࡬ࡸࡾ࠭᲋")])
            return [None, None, None]
        logger.debug(bstack11l1ll1_opy_ (u"ࠧࡕࡧࡶࡸࠥࡕࡢࡴࡧࡵࡺࡦࡨࡩ࡭࡫ࡷࡽࠥࡈࡵࡪ࡮ࡧࠤࡨࡸࡥࡢࡶ࡬ࡳࡳࠦࡓࡶࡥࡦࡩࡸࡹࡦࡶ࡮ࠤࠫ᲌"))
        os.environ[bstack11l1ll1_opy_ (u"ࠨࡄࡖࡣ࡙ࡋࡓࡕࡑࡓࡗࡤࡈࡕࡊࡎࡇࡣࡈࡕࡍࡑࡎࡈࡘࡊࡊࠧ᲍")] = bstack11l1ll1_opy_ (u"ࠩࡷࡶࡺ࡫ࠧ᲎")
        if bstack1lll1ll1l11_opy_.get(bstack11l1ll1_opy_ (u"ࠪ࡮ࡼࡺࠧ᲏")):
            os.environ[bstack11l1ll1_opy_ (u"ࠫࡈࡘࡅࡅࡇࡑࡘࡎࡇࡌࡔࡡࡉࡓࡗࡥࡃࡓࡃࡖࡌࡤࡘࡅࡑࡑࡕࡘࡎࡔࡇࠨᲐ")] = json.dumps({
                bstack11l1ll1_opy_ (u"ࠬࡻࡳࡦࡴࡱࡥࡲ࡫ࠧᲑ"): bstack1l11ll11l1l_opy_(cls.bs_config),
                bstack11l1ll1_opy_ (u"࠭ࡰࡢࡵࡶࡻࡴࡸࡤࠨᲒ"): bstack1l11llll111_opy_(cls.bs_config)
            })
        if bstack1lll1ll1l11_opy_.get(bstack11l1ll1_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡥࡨࡢࡵ࡫ࡩࡩࡥࡩࡥࠩᲓ")):
            os.environ[bstack11l1ll1_opy_ (u"ࠨࡄࡖࡣ࡙ࡋࡓࡕࡑࡓࡗࡤࡈࡕࡊࡎࡇࡣࡍࡇࡓࡉࡇࡇࡣࡎࡊࠧᲔ")] = bstack1lll1ll1l11_opy_[bstack11l1ll1_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡠࡪࡤࡷ࡭࡫ࡤࡠ࡫ࡧࠫᲕ")]
        if bstack1lll1ll1l11_opy_[bstack11l1ll1_opy_ (u"ࠪࡳࡧࡹࡥࡳࡸࡤࡦ࡮ࡲࡩࡵࡻࠪᲖ")].get(bstack11l1ll1_opy_ (u"ࠫࡴࡶࡴࡪࡱࡱࡷࠬᲗ"), {}).get(bstack11l1ll1_opy_ (u"ࠬࡧ࡬࡭ࡱࡺࡣࡸࡩࡲࡦࡧࡱࡷ࡭ࡵࡴࡴࠩᲘ")):
            os.environ[bstack11l1ll1_opy_ (u"࠭ࡂࡔࡡࡗࡉࡘ࡚ࡏࡑࡕࡢࡅࡑࡒࡏࡘࡡࡖࡇࡗࡋࡅࡏࡕࡋࡓ࡙࡙ࠧᲙ")] = str(bstack1lll1ll1l11_opy_[bstack11l1ll1_opy_ (u"ࠧࡰࡤࡶࡩࡷࡼࡡࡣ࡫࡯࡭ࡹࡿࠧᲚ")][bstack11l1ll1_opy_ (u"ࠨࡱࡳࡸ࡮ࡵ࡮ࡴࠩᲛ")][bstack11l1ll1_opy_ (u"ࠩࡤࡰࡱࡵࡷࡠࡵࡦࡶࡪ࡫࡮ࡴࡪࡲࡸࡸ࠭Ნ")])
        else:
            os.environ[bstack11l1ll1_opy_ (u"ࠪࡆࡘࡥࡔࡆࡕࡗࡓࡕ࡙࡟ࡂࡎࡏࡓ࡜ࡥࡓࡄࡔࡈࡉࡓ࡙ࡈࡐࡖࡖࠫᲝ")] = bstack11l1ll1_opy_ (u"ࠦࡳࡻ࡬࡭ࠤᲞ")
        return [bstack1lll1ll1l11_opy_[bstack11l1ll1_opy_ (u"ࠬࡰࡷࡵࠩᲟ")], bstack1lll1ll1l11_opy_[bstack11l1ll1_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡤ࡮ࡡࡴࡪࡨࡨࡤ࡯ࡤࠨᲠ")], os.environ[bstack11l1ll1_opy_ (u"ࠧࡃࡕࡢࡘࡊ࡙ࡔࡐࡒࡖࡣࡆࡒࡌࡐ࡙ࡢࡗࡈࡘࡅࡆࡐࡖࡌࡔ࡚ࡓࠨᲡ")]]
    @classmethod
    def bstack11l11111l1l_opy_(cls, bstack1lll1ll1l11_opy_):
        if bstack1lll1ll1l11_opy_.get(bstack11l1ll1_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠨᲢ")) == None:
            cls.bstack11l1111l11l_opy_()
            return [None, None]
        if bstack1lll1ll1l11_opy_[bstack11l1ll1_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠩᲣ")][bstack11l1ll1_opy_ (u"ࠪࡷࡺࡩࡣࡦࡵࡶࠫᲤ")] != True:
            cls.bstack11l1111l11l_opy_(bstack1lll1ll1l11_opy_[bstack11l1ll1_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠫᲥ")])
            return [None, None]
        if bstack1lll1ll1l11_opy_[bstack11l1ll1_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠬᲦ")].get(bstack11l1ll1_opy_ (u"࠭࡯ࡱࡶ࡬ࡳࡳࡹࠧᲧ")):
            logger.debug(bstack11l1ll1_opy_ (u"ࠧࡕࡧࡶࡸࠥࡇࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠥࡈࡵࡪ࡮ࡧࠤࡨࡸࡥࡢࡶ࡬ࡳࡳࠦࡓࡶࡥࡦࡩࡸࡹࡦࡶ࡮ࠤࠫᲨ"))
            parsed = json.loads(os.getenv(bstack11l1ll1_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡕࡇࡖࡘࡤࡇࡃࡄࡇࡖࡗࡎࡈࡉࡍࡋࡗ࡝ࡤࡉࡏࡏࡈࡌࡋ࡚ࡘࡁࡕࡋࡒࡒࡤ࡟ࡍࡍࠩᲩ"), bstack11l1ll1_opy_ (u"ࠩࡾࢁࠬᲪ")))
            capabilities = bstack1l1l1lll11_opy_.bstack1l1l111111l_opy_(bstack1lll1ll1l11_opy_[bstack11l1ll1_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠪᲫ")][bstack11l1ll1_opy_ (u"ࠫࡴࡶࡴࡪࡱࡱࡷࠬᲬ")][bstack11l1ll1_opy_ (u"ࠬࡩࡡࡱࡣࡥ࡭ࡱ࡯ࡴࡪࡧࡶࠫᲭ")], bstack11l1ll1_opy_ (u"࠭࡮ࡢ࡯ࡨࠫᲮ"), bstack11l1ll1_opy_ (u"ࠧࡷࡣ࡯ࡹࡪ࠭Ჯ"))
            bstack11l1111ll1l_opy_ = capabilities[bstack11l1ll1_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࡕࡱ࡮ࡩࡳ࠭Ჰ")]
            os.environ[bstack11l1ll1_opy_ (u"ࠩࡅࡗࡤࡇ࠱࠲࡛ࡢࡎ࡜࡚ࠧᲱ")] = bstack11l1111ll1l_opy_
            parsed[bstack11l1ll1_opy_ (u"ࠪࡷࡨࡧ࡮࡯ࡧࡵ࡚ࡪࡸࡳࡪࡱࡱࠫᲲ")] = capabilities[bstack11l1ll1_opy_ (u"ࠫࡸࡩࡡ࡯ࡰࡨࡶ࡛࡫ࡲࡴ࡫ࡲࡲࠬᲳ")]
            os.environ[bstack11l1ll1_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣ࡙ࡋࡓࡕࡡࡄࡇࡈࡋࡓࡔࡋࡅࡍࡑࡏࡔ࡚ࡡࡆࡓࡓࡌࡉࡈࡗࡕࡅ࡙ࡏࡏࡏࡡ࡜ࡑࡑ࠭Ჴ")] = json.dumps(parsed)
            scripts = bstack1l1l1lll11_opy_.bstack1l1l111111l_opy_(bstack1lll1ll1l11_opy_[bstack11l1ll1_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾ࠭Ჵ")][bstack11l1ll1_opy_ (u"ࠧࡰࡲࡷ࡭ࡴࡴࡳࠨᲶ")][bstack11l1ll1_opy_ (u"ࠨࡵࡦࡶ࡮ࡶࡴࡴࠩᲷ")], bstack11l1ll1_opy_ (u"ࠩࡱࡥࡲ࡫ࠧᲸ"), bstack11l1ll1_opy_ (u"ࠪࡧࡴࡳ࡭ࡢࡰࡧࠫᲹ"))
            bstack1l1ll1111l_opy_.bstack1l11ll111ll_opy_(scripts)
            commands = bstack1lll1ll1l11_opy_[bstack11l1ll1_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠫᲺ")][bstack11l1ll1_opy_ (u"ࠬࡵࡰࡵ࡫ࡲࡲࡸ࠭᲻")][bstack11l1ll1_opy_ (u"࠭ࡣࡰ࡯ࡰࡥࡳࡪࡳࡕࡱ࡚ࡶࡦࡶࠧ᲼")].get(bstack11l1ll1_opy_ (u"ࠧࡤࡱࡰࡱࡦࡴࡤࡴࠩᲽ"))
            bstack1l1ll1111l_opy_.bstack1l11lll1111_opy_(commands)
            bstack1l1ll1111l_opy_.store()
        return [bstack11l1111ll1l_opy_, bstack1lll1ll1l11_opy_[bstack11l1ll1_opy_ (u"ࠨࡤࡸ࡭ࡱࡪ࡟ࡩࡣࡶ࡬ࡪࡪ࡟ࡪࡦࠪᲾ")]]
    @classmethod
    def bstack11l111ll1l1_opy_(cls, response=None):
        os.environ[bstack11l1ll1_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡖࡈࡗ࡙ࡎࡕࡃࡡࡘ࡙ࡎࡊࠧᲿ")] = bstack11l1ll1_opy_ (u"ࠪࡲࡺࡲ࡬ࠨ᳀")
        os.environ[bstack11l1ll1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡘࡊ࡙ࡔࡉࡗࡅࡣࡏ࡝ࡔࠨ᳁")] = bstack11l1ll1_opy_ (u"ࠬࡴࡵ࡭࡮ࠪ᳂")
        os.environ[bstack11l1ll1_opy_ (u"࠭ࡂࡔࡡࡗࡉࡘ࡚ࡏࡑࡕࡢࡆ࡚ࡏࡌࡅࡡࡆࡓࡒࡖࡌࡆࡖࡈࡈࠬ᳃")] = bstack11l1ll1_opy_ (u"ࠧࡧࡣ࡯ࡷࡪ࠭᳄")
        os.environ[bstack11l1ll1_opy_ (u"ࠨࡄࡖࡣ࡙ࡋࡓࡕࡑࡓࡗࡤࡈࡕࡊࡎࡇࡣࡍࡇࡓࡉࡇࡇࡣࡎࡊࠧ᳅")] = bstack11l1ll1_opy_ (u"ࠤࡱࡹࡱࡲࠢ᳆")
        os.environ[bstack11l1ll1_opy_ (u"ࠪࡆࡘࡥࡔࡆࡕࡗࡓࡕ࡙࡟ࡂࡎࡏࡓ࡜ࡥࡓࡄࡔࡈࡉࡓ࡙ࡈࡐࡖࡖࠫ᳇")] = bstack11l1ll1_opy_ (u"ࠦࡳࡻ࡬࡭ࠤ᳈")
        cls.bstack11l111l111l_opy_(response, bstack11l1ll1_opy_ (u"ࠧࡵࡢࡴࡧࡵࡺࡦࡨࡩ࡭࡫ࡷࡽࠧ᳉"))
        return [None, None, None]
    @classmethod
    def bstack11l1111l11l_opy_(cls, response=None):
        os.environ[bstack11l1ll1_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡚ࡅࡔࡖࡋ࡙ࡇࡥࡕࡖࡋࡇࠫ᳊")] = bstack11l1ll1_opy_ (u"ࠧ࡯ࡷ࡯ࡰࠬ᳋")
        os.environ[bstack11l1ll1_opy_ (u"ࠨࡄࡖࡣࡆ࠷࠱࡚ࡡࡍ࡛࡙࠭᳌")] = bstack11l1ll1_opy_ (u"ࠩࡱࡹࡱࡲࠧ᳍")
        os.environ[bstack11l1ll1_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡗࡉࡘ࡚ࡈࡖࡄࡢࡎ࡜࡚ࠧ᳎")] = bstack11l1ll1_opy_ (u"ࠫࡳࡻ࡬࡭ࠩ᳏")
        cls.bstack11l111l111l_opy_(response, bstack11l1ll1_opy_ (u"ࠧࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠧ᳐"))
        return [None, None, None]
    @classmethod
    def bstack11l111l1lll_opy_(cls, jwt, build_hashed_id):
        os.environ[bstack11l1ll1_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡚ࡅࡔࡖࡋ࡙ࡇࡥࡊࡘࡖࠪ᳑")] = jwt
        os.environ[bstack11l1ll1_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡔࡆࡕࡗࡌ࡚ࡈ࡟ࡖࡗࡌࡈࠬ᳒")] = build_hashed_id
    @classmethod
    def bstack11l111l111l_opy_(cls, response=None, product=bstack11l1ll1_opy_ (u"ࠣࠤ᳓")):
        if response == None:
            logger.error(product + bstack11l1ll1_opy_ (u"ࠤࠣࡆࡺ࡯࡬ࡥࠢࡦࡶࡪࡧࡴࡪࡱࡱࠤ࡫ࡧࡩ࡭ࡧࡧ᳔ࠦ"))
        for error in response[bstack11l1ll1_opy_ (u"ࠪࡩࡷࡸ࡯ࡳࡵ᳕ࠪ")]:
            bstack1l11111l1ll_opy_ = error[bstack11l1ll1_opy_ (u"ࠫࡰ࡫ࡹࠨ᳖")]
            error_message = error[bstack11l1ll1_opy_ (u"ࠬࡳࡥࡴࡵࡤ࡫ࡪ᳗࠭")]
            if error_message:
                if bstack1l11111l1ll_opy_ == bstack11l1ll1_opy_ (u"ࠨࡅࡓࡔࡒࡖࡤࡇࡃࡄࡇࡖࡗࡤࡊࡅࡏࡋࡈࡈ᳘ࠧ"):
                    logger.info(error_message)
                else:
                    logger.error(error_message)
            else:
                logger.error(bstack11l1ll1_opy_ (u"ࠢࡅࡣࡷࡥࠥࡻࡰ࡭ࡱࡤࡨࠥࡺ࡯ࠡࡄࡵࡳࡼࡹࡥࡳࡕࡷࡥࡨࡱ᳙ࠠࠣ") + product + bstack11l1ll1_opy_ (u"ࠣࠢࡩࡥ࡮ࡲࡥࡥࠢࡧࡹࡪࠦࡴࡰࠢࡶࡳࡲ࡫ࠠࡦࡴࡵࡳࡷࠨ᳚"))
    @classmethod
    def bstack11l111111ll_opy_(cls):
        if cls.bstack11l11lll111_opy_ is not None:
            return
        cls.bstack11l11lll111_opy_ = bstack11l11lll1l1_opy_(cls.bstack11l1111l1ll_opy_)
        cls.bstack11l11lll111_opy_.start()
    @classmethod
    def bstack11l1111111_opy_(cls):
        if cls.bstack11l11lll111_opy_ is None:
            return
        cls.bstack11l11lll111_opy_.shutdown()
    @classmethod
    @bstack111llll1ll_opy_(class_method=True)
    def bstack11l1111l1ll_opy_(cls, bstack11l1111lll_opy_, event_url=bstack11l1ll1_opy_ (u"ࠩࡤࡴ࡮࠵ࡶ࠲࠱ࡥࡥࡹࡩࡨࠨ᳛")):
        config = {
            bstack11l1ll1_opy_ (u"ࠪ࡬ࡪࡧࡤࡦࡴࡶ᳜ࠫ"): cls.default_headers()
        }
        logger.debug(bstack11l1ll1_opy_ (u"ࠦࡵࡵࡳࡵࡡࡧࡥࡹࡧ࠺ࠡࡕࡨࡲࡩ࡯࡮ࡨࠢࡧࡥࡹࡧࠠࡵࡱࠣࡸࡪࡹࡴࡩࡷࡥࠤ࡫ࡵࡲࠡࡧࡹࡩࡳࡺࡳࠡࡽࢀ᳝ࠦ").format(bstack11l1ll1_opy_ (u"ࠬ࠲ࠠࠨ᳞").join([event[bstack11l1ll1_opy_ (u"࠭ࡥࡷࡧࡱࡸࡤࡺࡹࡱࡧ᳟ࠪ")] for event in bstack11l1111lll_opy_])))
        response = bstack1l1111l1l_opy_(bstack11l1ll1_opy_ (u"ࠧࡑࡑࡖࡘࠬ᳠"), cls.request_url(event_url), bstack11l1111lll_opy_, config)
        bstack1l11lll11ll_opy_ = response.json()
    @classmethod
    def bstack11111ll1_opy_(cls, bstack11l1111lll_opy_, event_url=bstack11l1ll1_opy_ (u"ࠨࡣࡳ࡭࠴ࡼ࠱࠰ࡤࡤࡸࡨ࡮ࠧ᳡")):
        logger.debug(bstack11l1ll1_opy_ (u"ࠤࡶࡩࡳࡪ࡟ࡥࡣࡷࡥ࠿ࠦࡁࡵࡶࡨࡱࡵࡺࡩ࡯ࡩࠣࡸࡴࠦࡡࡥࡦࠣࡨࡦࡺࡡࠡࡶࡲࠤࡧࡧࡴࡤࡪࠣࡻ࡮ࡺࡨࠡࡧࡹࡩࡳࡺ࡟ࡵࡻࡳࡩ࠿ࠦࡻࡾࠤ᳢").format(bstack11l1111lll_opy_[bstack11l1ll1_opy_ (u"ࠪࡩࡻ࡫࡮ࡵࡡࡷࡽࡵ࡫᳣ࠧ")]))
        if not bstack1l1l1lll11_opy_.bstack1l1l11111l1_opy_(bstack11l1111lll_opy_[bstack11l1ll1_opy_ (u"ࠫࡪࡼࡥ࡯ࡶࡢࡸࡾࡶࡥࠨ᳤")]):
            logger.debug(bstack11l1ll1_opy_ (u"ࠧࡹࡥ࡯ࡦࡢࡨࡦࡺࡡ࠻ࠢࡑࡳࡹࠦࡡࡥࡦ࡬ࡲ࡬ࠦࡤࡢࡶࡤࠤࡼ࡯ࡴࡩࠢࡨࡺࡪࡴࡴࡠࡶࡼࡴࡪࡀࠠࡼࡿ᳥ࠥ").format(bstack11l1111lll_opy_[bstack11l1ll1_opy_ (u"࠭ࡥࡷࡧࡱࡸࡤࡺࡹࡱࡧ᳦ࠪ")]))
            return
        bstack1l11l1ll1_opy_ = bstack1l1l1lll11_opy_.bstack1l11llll1l1_opy_(bstack11l1111lll_opy_[bstack11l1ll1_opy_ (u"ࠧࡦࡸࡨࡲࡹࡥࡴࡺࡲࡨ᳧ࠫ")], bstack11l1111lll_opy_.get(bstack11l1ll1_opy_ (u"ࠨࡶࡨࡷࡹࡥࡲࡶࡰ᳨ࠪ")))
        if bstack1l11l1ll1_opy_ != None:
            if bstack11l1111lll_opy_.get(bstack11l1ll1_opy_ (u"ࠩࡷࡩࡸࡺ࡟ࡳࡷࡱࠫᳩ")) != None:
                bstack11l1111lll_opy_[bstack11l1ll1_opy_ (u"ࠪࡸࡪࡹࡴࡠࡴࡸࡲࠬᳪ")][bstack11l1ll1_opy_ (u"ࠫࡵࡸ࡯ࡥࡷࡦࡸࡤࡳࡡࡱࠩᳫ")] = bstack1l11l1ll1_opy_
            else:
                bstack11l1111lll_opy_[bstack11l1ll1_opy_ (u"ࠬࡶࡲࡰࡦࡸࡧࡹࡥ࡭ࡢࡲࠪᳬ")] = bstack1l11l1ll1_opy_
        if event_url == bstack11l1ll1_opy_ (u"࠭ࡡࡱ࡫࠲ࡺ࠶࠵ࡢࡢࡶࡦ࡬᳭ࠬ"):
            cls.bstack11l111111ll_opy_()
            logger.debug(bstack11l1ll1_opy_ (u"ࠢࡴࡧࡱࡨࡤࡪࡡࡵࡣ࠽ࠤࡆࡪࡤࡪࡰࡪࠤࡩࡧࡴࡢࠢࡷࡳࠥࡨࡡࡵࡥ࡫ࠤࡼ࡯ࡴࡩࠢࡨࡺࡪࡴࡴࡠࡶࡼࡴࡪࡀࠠࡼࡿࠥᳮ").format(bstack11l1111lll_opy_[bstack11l1ll1_opy_ (u"ࠨࡧࡹࡩࡳࡺ࡟ࡵࡻࡳࡩࠬᳯ")]))
            cls.bstack11l11lll111_opy_.add(bstack11l1111lll_opy_)
        elif event_url == bstack11l1ll1_opy_ (u"ࠩࡤࡴ࡮࠵ࡶ࠲࠱ࡶࡧࡷ࡫ࡥ࡯ࡵ࡫ࡳࡹࡹࠧᳰ"):
            cls.bstack11l1111l1ll_opy_([bstack11l1111lll_opy_], event_url)
    @classmethod
    @bstack111llll1ll_opy_(class_method=True)
    def bstack1l1l1lll1l_opy_(cls, logs):
        bstack11l111l1ll1_opy_ = []
        for log in logs:
            bstack11l111ll111_opy_ = {
                bstack11l1ll1_opy_ (u"ࠪ࡯࡮ࡴࡤࠨᳱ"): bstack11l1ll1_opy_ (u"࡙ࠫࡋࡓࡕࡡࡏࡓࡌ࠭ᳲ"),
                bstack11l1ll1_opy_ (u"ࠬࡲࡥࡷࡧ࡯ࠫᳳ"): log[bstack11l1ll1_opy_ (u"࠭࡬ࡦࡸࡨࡰࠬ᳴")],
                bstack11l1ll1_opy_ (u"ࠧࡵ࡫ࡰࡩࡸࡺࡡ࡮ࡲࠪᳵ"): log[bstack11l1ll1_opy_ (u"ࠨࡶ࡬ࡱࡪࡹࡴࡢ࡯ࡳࠫᳶ")],
                bstack11l1ll1_opy_ (u"ࠩ࡫ࡸࡹࡶ࡟ࡳࡧࡶࡴࡴࡴࡳࡦࠩ᳷"): {},
                bstack11l1ll1_opy_ (u"ࠪࡱࡪࡹࡳࡢࡩࡨࠫ᳸"): log[bstack11l1ll1_opy_ (u"ࠫࡲ࡫ࡳࡴࡣࡪࡩࠬ᳹")],
            }
            if bstack11l1ll1_opy_ (u"ࠬࡺࡥࡴࡶࡢࡶࡺࡴ࡟ࡶࡷ࡬ࡨࠬᳺ") in log:
                bstack11l111ll111_opy_[bstack11l1ll1_opy_ (u"࠭ࡴࡦࡵࡷࡣࡷࡻ࡮ࡠࡷࡸ࡭ࡩ࠭᳻")] = log[bstack11l1ll1_opy_ (u"ࠧࡵࡧࡶࡸࡤࡸࡵ࡯ࡡࡸࡹ࡮ࡪࠧ᳼")]
            elif bstack11l1ll1_opy_ (u"ࠨࡪࡲࡳࡰࡥࡲࡶࡰࡢࡹࡺ࡯ࡤࠨ᳽") in log:
                bstack11l111ll111_opy_[bstack11l1ll1_opy_ (u"ࠩ࡫ࡳࡴࡱ࡟ࡳࡷࡱࡣࡺࡻࡩࡥࠩ᳾")] = log[bstack11l1ll1_opy_ (u"ࠪ࡬ࡴࡵ࡫ࡠࡴࡸࡲࡤࡻࡵࡪࡦࠪ᳿")]
            bstack11l111l1ll1_opy_.append(bstack11l111ll111_opy_)
        cls.bstack11111ll1_opy_({
            bstack11l1ll1_opy_ (u"ࠫࡪࡼࡥ࡯ࡶࡢࡸࡾࡶࡥࠨᴀ"): bstack11l1ll1_opy_ (u"ࠬࡒ࡯ࡨࡅࡵࡩࡦࡺࡥࡥࠩᴁ"),
            bstack11l1ll1_opy_ (u"࠭࡬ࡰࡩࡶࠫᴂ"): bstack11l111l1ll1_opy_
        })
    @classmethod
    @bstack111llll1ll_opy_(class_method=True)
    def bstack11l11111l11_opy_(cls, steps):
        bstack11l111l1l1l_opy_ = []
        for step in steps:
            bstack11l111ll11l_opy_ = {
                bstack11l1ll1_opy_ (u"ࠧ࡬࡫ࡱࡨࠬᴃ"): bstack11l1ll1_opy_ (u"ࠨࡖࡈࡗ࡙ࡥࡓࡕࡇࡓࠫᴄ"),
                bstack11l1ll1_opy_ (u"ࠩ࡯ࡩࡻ࡫࡬ࠨᴅ"): step[bstack11l1ll1_opy_ (u"ࠪࡰࡪࡼࡥ࡭ࠩᴆ")],
                bstack11l1ll1_opy_ (u"ࠫࡹ࡯࡭ࡦࡵࡷࡥࡲࡶࠧᴇ"): step[bstack11l1ll1_opy_ (u"ࠬࡺࡩ࡮ࡧࡶࡸࡦࡳࡰࠨᴈ")],
                bstack11l1ll1_opy_ (u"࠭࡭ࡦࡵࡶࡥ࡬࡫ࠧᴉ"): step[bstack11l1ll1_opy_ (u"ࠧ࡮ࡧࡶࡷࡦ࡭ࡥࠨᴊ")],
                bstack11l1ll1_opy_ (u"ࠨࡦࡸࡶࡦࡺࡩࡰࡰࠪᴋ"): step[bstack11l1ll1_opy_ (u"ࠩࡧࡹࡷࡧࡴࡪࡱࡱࠫᴌ")]
            }
            if bstack11l1ll1_opy_ (u"ࠪࡸࡪࡹࡴࡠࡴࡸࡲࡤࡻࡵࡪࡦࠪᴍ") in step:
                bstack11l111ll11l_opy_[bstack11l1ll1_opy_ (u"ࠫࡹ࡫ࡳࡵࡡࡵࡹࡳࡥࡵࡶ࡫ࡧࠫᴎ")] = step[bstack11l1ll1_opy_ (u"ࠬࡺࡥࡴࡶࡢࡶࡺࡴ࡟ࡶࡷ࡬ࡨࠬᴏ")]
            elif bstack11l1ll1_opy_ (u"࠭ࡨࡰࡱ࡮ࡣࡷࡻ࡮ࡠࡷࡸ࡭ࡩ࠭ᴐ") in step:
                bstack11l111ll11l_opy_[bstack11l1ll1_opy_ (u"ࠧࡩࡱࡲ࡯ࡤࡸࡵ࡯ࡡࡸࡹ࡮ࡪࠧᴑ")] = step[bstack11l1ll1_opy_ (u"ࠨࡪࡲࡳࡰࡥࡲࡶࡰࡢࡹࡺ࡯ࡤࠨᴒ")]
            bstack11l111l1l1l_opy_.append(bstack11l111ll11l_opy_)
        cls.bstack11111ll1_opy_({
            bstack11l1ll1_opy_ (u"ࠩࡨࡺࡪࡴࡴࡠࡶࡼࡴࡪ࠭ᴓ"): bstack11l1ll1_opy_ (u"ࠪࡐࡴ࡭ࡃࡳࡧࡤࡸࡪࡪࠧᴔ"),
            bstack11l1ll1_opy_ (u"ࠫࡱࡵࡧࡴࠩᴕ"): bstack11l111l1l1l_opy_
        })
    @classmethod
    @bstack111llll1ll_opy_(class_method=True)
    @measure(event_name=EVENTS.bstack1ll111llll_opy_, stage=STAGE.bstack1l1ll1llll_opy_)
    def bstack1lllll1l1l_opy_(cls, screenshot):
        cls.bstack11111ll1_opy_({
            bstack11l1ll1_opy_ (u"ࠬ࡫ࡶࡦࡰࡷࡣࡹࡿࡰࡦࠩᴖ"): bstack11l1ll1_opy_ (u"࠭ࡌࡰࡩࡆࡶࡪࡧࡴࡦࡦࠪᴗ"),
            bstack11l1ll1_opy_ (u"ࠧ࡭ࡱࡪࡷࠬᴘ"): [{
                bstack11l1ll1_opy_ (u"ࠨ࡭࡬ࡲࡩ࠭ᴙ"): bstack11l1ll1_opy_ (u"ࠩࡗࡉࡘ࡚࡟ࡔࡅࡕࡉࡊࡔࡓࡉࡑࡗࠫᴚ"),
                bstack11l1ll1_opy_ (u"ࠪࡸ࡮ࡳࡥࡴࡶࡤࡱࡵ࠭ᴛ"): datetime.datetime.utcnow().isoformat() + bstack11l1ll1_opy_ (u"ࠫ࡟࠭ᴜ"),
                bstack11l1ll1_opy_ (u"ࠬࡳࡥࡴࡵࡤ࡫ࡪ࠭ᴝ"): screenshot[bstack11l1ll1_opy_ (u"࠭ࡩ࡮ࡣࡪࡩࠬᴞ")],
                bstack11l1ll1_opy_ (u"ࠧࡵࡧࡶࡸࡤࡸࡵ࡯ࡡࡸࡹ࡮ࡪࠧᴟ"): screenshot[bstack11l1ll1_opy_ (u"ࠨࡶࡨࡷࡹࡥࡲࡶࡰࡢࡹࡺ࡯ࡤࠨᴠ")]
            }]
        }, event_url=bstack11l1ll1_opy_ (u"ࠩࡤࡴ࡮࠵ࡶ࠲࠱ࡶࡧࡷ࡫ࡥ࡯ࡵ࡫ࡳࡹࡹࠧᴡ"))
    @classmethod
    @bstack111llll1ll_opy_(class_method=True)
    def bstack1111l11l1_opy_(cls, driver):
        current_test_uuid = cls.current_test_uuid()
        if not current_test_uuid:
            return
        cls.bstack11111ll1_opy_({
            bstack11l1ll1_opy_ (u"ࠪࡩࡻ࡫࡮ࡵࡡࡷࡽࡵ࡫ࠧᴢ"): bstack11l1ll1_opy_ (u"ࠫࡈࡈࡔࡔࡧࡶࡷ࡮ࡵ࡮ࡄࡴࡨࡥࡹ࡫ࡤࠨᴣ"),
            bstack11l1ll1_opy_ (u"ࠬࡺࡥࡴࡶࡢࡶࡺࡴࠧᴤ"): {
                bstack11l1ll1_opy_ (u"ࠨࡵࡶ࡫ࡧࠦᴥ"): cls.current_test_uuid(),
                bstack11l1ll1_opy_ (u"ࠢࡪࡰࡷࡩ࡬ࡸࡡࡵ࡫ࡲࡲࡸࠨᴦ"): cls.bstack11l11lll1l_opy_(driver)
            }
        })
    @classmethod
    def bstack11l11ll1l1_opy_(cls, event: str, bstack11l1111lll_opy_: bstack111ll1l1l1_opy_):
        bstack111ll1lll1_opy_ = {
            bstack11l1ll1_opy_ (u"ࠨࡧࡹࡩࡳࡺ࡟ࡵࡻࡳࡩࠬᴧ"): event,
            bstack11l1111lll_opy_.bstack111llll111_opy_(): bstack11l1111lll_opy_.bstack11l111lll1_opy_(event)
        }
        cls.bstack11111ll1_opy_(bstack111ll1lll1_opy_)
        result = getattr(bstack11l1111lll_opy_, bstack11l1ll1_opy_ (u"ࠩࡵࡩࡸࡻ࡬ࡵࠩᴨ"), None)
        if event == bstack11l1ll1_opy_ (u"ࠪࡘࡪࡹࡴࡓࡷࡱࡗࡹࡧࡲࡵࡧࡧࠫᴩ"):
            threading.current_thread().bstackTestMeta = {bstack11l1ll1_opy_ (u"ࠫࡸࡺࡡࡵࡷࡶࠫᴪ"): bstack11l1ll1_opy_ (u"ࠬࡶࡥ࡯ࡦ࡬ࡲ࡬࠭ᴫ")}
        elif event == bstack11l1ll1_opy_ (u"࠭ࡔࡦࡵࡷࡖࡺࡴࡆࡪࡰ࡬ࡷ࡭࡫ࡤࠨᴬ"):
            threading.current_thread().bstackTestMeta = {bstack11l1ll1_opy_ (u"ࠧࡴࡶࡤࡸࡺࡹࠧᴭ"): getattr(result, bstack11l1ll1_opy_ (u"ࠨࡴࡨࡷࡺࡲࡴࠨᴮ"), bstack11l1ll1_opy_ (u"ࠩࠪᴯ"))}
    @classmethod
    def on(cls):
        if (os.environ.get(bstack11l1ll1_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡗࡉࡘ࡚ࡈࡖࡄࡢࡎ࡜࡚ࠧᴰ"), None) is None or os.environ[bstack11l1ll1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡘࡊ࡙ࡔࡉࡗࡅࡣࡏ࡝ࡔࠨᴱ")] == bstack11l1ll1_opy_ (u"ࠧࡴࡵ࡭࡮ࠥᴲ")) and (os.environ.get(bstack11l1ll1_opy_ (u"࠭ࡂࡔࡡࡄ࠵࠶࡟࡟ࡋ࡙ࡗࠫᴳ"), None) is None or os.environ[bstack11l1ll1_opy_ (u"ࠧࡃࡕࡢࡅ࠶࠷࡙ࡠࡌ࡚ࡘࠬᴴ")] == bstack11l1ll1_opy_ (u"ࠣࡰࡸࡰࡱࠨᴵ")):
            return False
        return True
    @staticmethod
    def bstack11l1111l1l1_opy_(func):
        def wrap(*args, **kwargs):
            if bstack11111l1l1_opy_.on():
                return func(*args, **kwargs)
            return
        return wrap
    @staticmethod
    def default_headers():
        headers = {
            bstack11l1ll1_opy_ (u"ࠩࡆࡳࡳࡺࡥ࡯ࡶ࠰ࡘࡾࡶࡥࠨᴶ"): bstack11l1ll1_opy_ (u"ࠪࡥࡵࡶ࡬ࡪࡥࡤࡸ࡮ࡵ࡮࠰࡬ࡶࡳࡳ࠭ᴷ"),
            bstack11l1ll1_opy_ (u"ࠫ࡝࠳ࡂࡔࡖࡄࡇࡐ࠳ࡔࡆࡕࡗࡓࡕ࡙ࠧᴸ"): bstack11l1ll1_opy_ (u"ࠬࡺࡲࡶࡧࠪᴹ")
        }
        if os.environ.get(bstack11l1ll1_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡚ࡅࡔࡖࡋ࡙ࡇࡥࡊࡘࡖࠪᴺ"), None):
            headers[bstack11l1ll1_opy_ (u"ࠧࡂࡷࡷ࡬ࡴࡸࡩࡻࡣࡷ࡭ࡴࡴࠧᴻ")] = bstack11l1ll1_opy_ (u"ࠨࡄࡨࡥࡷ࡫ࡲࠡࡽࢀࠫᴼ").format(os.environ[bstack11l1ll1_opy_ (u"ࠤࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡖࡈࡗ࡙ࡎࡕࡃࡡࡍ࡛࡙ࠨᴽ")])
        return headers
    @staticmethod
    def request_url(url):
        return bstack11l1ll1_opy_ (u"ࠪࡿࢂ࠵ࡻࡾࠩᴾ").format(bstack11l1111llll_opy_, url)
    @staticmethod
    def current_test_uuid():
        return getattr(threading.current_thread(), bstack11l1ll1_opy_ (u"ࠫࡨࡻࡲࡳࡧࡱࡸࡤࡺࡥࡴࡶࡢࡹࡺ࡯ࡤࠨᴿ"), None)
    @staticmethod
    def bstack11l11lll1l_opy_(driver):
        return {
            bstack11lll1l1l1l_opy_(): bstack11lll11ll1l_opy_(driver)
        }
    @staticmethod
    def bstack11l11111ll1_opy_(exception_info, report):
        return [{bstack11l1ll1_opy_ (u"ࠬࡨࡡࡤ࡭ࡷࡶࡦࡩࡥࠨᵀ"): [exception_info.exconly(), report.longreprtext]}]
    @staticmethod
    def bstack111l1l1111_opy_(typename):
        if bstack11l1ll1_opy_ (u"ࠨࡁࡴࡵࡨࡶࡹ࡯࡯࡯ࠤᵁ") in typename:
            return bstack11l1ll1_opy_ (u"ࠢࡂࡵࡶࡩࡷࡺࡩࡰࡰࡈࡶࡷࡵࡲࠣᵂ")
        return bstack11l1ll1_opy_ (u"ࠣࡗࡱ࡬ࡦࡴࡤ࡭ࡧࡧࡉࡷࡸ࡯ࡳࠤᵃ")