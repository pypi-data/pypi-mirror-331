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
import json
import logging
import datetime
import threading
from bstack_utils.helper import bstack1l1l111l1ll_opy_, bstack11l1ll1lll_opy_, get_host_info, bstack1l11lllll1l_opy_, \
 bstack1ll111111_opy_, bstack1ll1l1lll_opy_, bstack111llll1ll_opy_, bstack1l1l1111111_opy_, bstack1ll1l1ll_opy_
import bstack_utils.accessibility as bstack11lll11ll1_opy_
from bstack_utils.bstack11l11l1lll_opy_ import bstack11ll1ll1_opy_
from bstack_utils.percy import bstack111l1l11l_opy_
from bstack_utils.config import Config
bstack1ll1l11l1_opy_ = Config.bstack1l111l1ll1_opy_()
logger = logging.getLogger(__name__)
percy = bstack111l1l11l_opy_()
@bstack111llll1ll_opy_(class_method=False)
def bstack1l11llll11l_opy_(bs_config, bstack1lll11ll1_opy_):
  try:
    data = {
        bstack11l1ll1_opy_ (u"ࠩࡩࡳࡷࡳࡡࡵࠩᏕ"): bstack11l1ll1_opy_ (u"ࠪ࡮ࡸࡵ࡮ࠨᏖ"),
        bstack11l1ll1_opy_ (u"ࠫࡵࡸ࡯࡫ࡧࡦࡸࡤࡴࡡ࡮ࡧࠪᏗ"): bs_config.get(bstack11l1ll1_opy_ (u"ࠬࡶࡲࡰ࡬ࡨࡧࡹࡔࡡ࡮ࡧࠪᏘ"), bstack11l1ll1_opy_ (u"࠭ࠧᏙ")),
        bstack11l1ll1_opy_ (u"ࠧ࡯ࡣࡰࡩࠬᏚ"): bs_config.get(bstack11l1ll1_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡎࡢ࡯ࡨࠫᏛ"), os.path.basename(os.path.abspath(os.getcwd()))),
        bstack11l1ll1_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡠ࡫ࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬᏜ"): bs_config.get(bstack11l1ll1_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬᏝ")),
        bstack11l1ll1_opy_ (u"ࠫࡩ࡫ࡳࡤࡴ࡬ࡴࡹ࡯࡯࡯ࠩᏞ"): bs_config.get(bstack11l1ll1_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡈࡪࡹࡣࡳ࡫ࡳࡸ࡮ࡵ࡮ࠨᏟ"), bstack11l1ll1_opy_ (u"࠭ࠧᏠ")),
        bstack11l1ll1_opy_ (u"ࠧࡴࡶࡤࡶࡹ࡫ࡤࡠࡣࡷࠫᏡ"): bstack1ll1l1ll_opy_(),
        bstack11l1ll1_opy_ (u"ࠨࡶࡤ࡫ࡸ࠭Ꮲ"): bstack1l11lllll1l_opy_(bs_config),
        bstack11l1ll1_opy_ (u"ࠩ࡫ࡳࡸࡺ࡟ࡪࡰࡩࡳࠬᏣ"): get_host_info(),
        bstack11l1ll1_opy_ (u"ࠪࡧ࡮ࡥࡩ࡯ࡨࡲࠫᏤ"): bstack11l1ll1lll_opy_(),
        bstack11l1ll1_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡢࡶࡺࡴ࡟ࡪࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫᏥ"): os.environ.get(bstack11l1ll1_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡇ࡛ࡉࡍࡆࡢࡖ࡚ࡔ࡟ࡊࡆࡈࡒ࡙ࡏࡆࡊࡇࡕࠫᏦ")),
        bstack11l1ll1_opy_ (u"࠭ࡦࡢ࡫࡯ࡩࡩࡥࡴࡦࡵࡷࡷࡤࡸࡥࡳࡷࡱࠫᏧ"): os.environ.get(bstack11l1ll1_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡒࡆࡔࡘࡒࠬᏨ"), False),
        bstack11l1ll1_opy_ (u"ࠨࡸࡨࡶࡸ࡯࡯࡯ࡡࡦࡳࡳࡺࡲࡰ࡮ࠪᏩ"): bstack1l1l111l1ll_opy_(),
        bstack11l1ll1_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠩᏪ"): bstack1l1l1111ll1_opy_(),
        bstack11l1ll1_opy_ (u"ࠪࡪࡷࡧ࡭ࡦࡹࡲࡶࡰࡥࡤࡦࡶࡤ࡭ࡱࡹࠧᏫ"): bstack1l1l1111l1l_opy_(bstack1lll11ll1_opy_),
        bstack11l1ll1_opy_ (u"ࠫࡵࡸ࡯ࡥࡷࡦࡸࡤࡳࡡࡱࠩᏬ"): bstack1ll11ll1ll_opy_(bs_config, bstack1lll11ll1_opy_.get(bstack11l1ll1_opy_ (u"ࠬ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࡠࡷࡶࡩࡩ࠭Ꮽ"), bstack11l1ll1_opy_ (u"࠭ࠧᏮ"))),
        bstack11l1ll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡇࡵࡵࡱࡰࡥࡹ࡯࡯࡯ࠩᏯ"): bstack1ll111111_opy_(bs_config),
    }
    return data
  except Exception as error:
    logger.error(bstack11l1ll1_opy_ (u"ࠣࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤࡼ࡮ࡩ࡭ࡧࠣࡧࡷ࡫ࡡࡵ࡫ࡱ࡫ࠥࡶࡡࡺ࡮ࡲࡥࡩࠦࡦࡰࡴࠣࡘࡪࡹࡴࡉࡷࡥ࠾ࠥࠦࡻࡾࠤᏰ").format(str(error)))
    return None
def bstack1l1l1111l1l_opy_(framework):
  return {
    bstack11l1ll1_opy_ (u"ࠩࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࡓࡧ࡭ࡦࠩᏱ"): framework.get(bstack11l1ll1_opy_ (u"ࠪࡪࡷࡧ࡭ࡦࡹࡲࡶࡰࡥ࡮ࡢ࡯ࡨࠫᏲ"), bstack11l1ll1_opy_ (u"ࠫࡕࡿࡴࡦࡵࡷࠫᏳ")),
    bstack11l1ll1_opy_ (u"ࠬ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࡗࡧࡵࡷ࡮ࡵ࡮ࠨᏴ"): framework.get(bstack11l1ll1_opy_ (u"࠭ࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡡࡹࡩࡷࡹࡩࡰࡰࠪᏵ")),
    bstack11l1ll1_opy_ (u"ࠧࡴࡦ࡮࡚ࡪࡸࡳࡪࡱࡱࠫ᏶"): framework.get(bstack11l1ll1_opy_ (u"ࠨࡵࡧ࡯ࡤࡼࡥࡳࡵ࡬ࡳࡳ࠭᏷")),
    bstack11l1ll1_opy_ (u"ࠩ࡯ࡥࡳ࡭ࡵࡢࡩࡨࠫᏸ"): bstack11l1ll1_opy_ (u"ࠪࡴࡾࡺࡨࡰࡰࠪᏹ"),
    bstack11l1ll1_opy_ (u"ࠫࡹ࡫ࡳࡵࡈࡵࡥࡲ࡫ࡷࡰࡴ࡮ࠫᏺ"): framework.get(bstack11l1ll1_opy_ (u"ࠬࡺࡥࡴࡶࡉࡶࡦࡳࡥࡸࡱࡵ࡯ࠬᏻ"))
  }
def bstack1ll11ll1ll_opy_(bs_config, framework):
  bstack11llll1l_opy_ = False
  bstack1ll111l11_opy_ = False
  bstack1l11llll1ll_opy_ = False
  if bstack11l1ll1_opy_ (u"࠭ࡴࡶࡴࡥࡳࡘࡩࡡ࡭ࡧࠪᏼ") in bs_config:
    bstack1l11llll1ll_opy_ = True
  elif bstack11l1ll1_opy_ (u"ࠧࡢࡲࡳࠫᏽ") in bs_config:
    bstack11llll1l_opy_ = True
  else:
    bstack1ll111l11_opy_ = True
  bstack1l11l1ll1_opy_ = {
    bstack11l1ll1_opy_ (u"ࠨࡱࡥࡷࡪࡸࡶࡢࡤ࡬ࡰ࡮ࡺࡹࠨ᏾"): bstack11ll1ll1_opy_.bstack1l1l11111ll_opy_(bs_config, framework),
    bstack11l1ll1_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠩ᏿"): bstack11lll11ll1_opy_.bstack1l11lllllll_opy_(bs_config),
    bstack11l1ll1_opy_ (u"ࠪࡴࡪࡸࡣࡺࠩ᐀"): bs_config.get(bstack11l1ll1_opy_ (u"ࠫࡵ࡫ࡲࡤࡻࠪᐁ"), False),
    bstack11l1ll1_opy_ (u"ࠬࡧࡵࡵࡱࡰࡥࡹ࡫ࠧᐂ"): bstack1ll111l11_opy_,
    bstack11l1ll1_opy_ (u"࠭ࡡࡱࡲࡢࡥࡺࡺ࡯࡮ࡣࡷࡩࠬᐃ"): bstack11llll1l_opy_,
    bstack11l1ll1_opy_ (u"ࠧࡵࡷࡵࡦࡴࡹࡣࡢ࡮ࡨࠫᐄ"): bstack1l11llll1ll_opy_
  }
  return bstack1l11l1ll1_opy_
@bstack111llll1ll_opy_(class_method=False)
def bstack1l1l1111ll1_opy_():
  try:
    bstack1l1l111l1l1_opy_ = json.loads(os.getenv(bstack11l1ll1_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡕࡇࡖࡘࡤࡇࡃࡄࡇࡖࡗࡎࡈࡉࡍࡋࡗ࡝ࡤࡉࡏࡏࡈࡌࡋ࡚ࡘࡁࡕࡋࡒࡒࡤ࡟ࡍࡍࠩᐅ"), bstack11l1ll1_opy_ (u"ࠩࡾࢁࠬᐆ")))
    return {
        bstack11l1ll1_opy_ (u"ࠪࡷࡪࡺࡴࡪࡰࡪࡷࠬᐇ"): bstack1l1l111l1l1_opy_
    }
  except Exception as error:
    logger.error(bstack11l1ll1_opy_ (u"ࠦࡊࡾࡣࡦࡲࡷ࡭ࡴࡴࠠࡸࡪ࡬ࡰࡪࠦࡣࡳࡧࡤࡸ࡮ࡴࡧࠡࡩࡨࡸࡤࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࡤࡹࡥࡵࡶ࡬ࡲ࡬ࡹࠠࡧࡱࡵࠤ࡙࡫ࡳࡵࡊࡸࡦ࠿ࠦࠠࡼࡿࠥᐈ").format(str(error)))
    return {}
def bstack1l1l111111l_opy_(array, bstack1l1l1111lll_opy_, bstack1l1l1111l11_opy_):
  result = {}
  for o in array:
    key = o[bstack1l1l1111lll_opy_]
    result[key] = o[bstack1l1l1111l11_opy_]
  return result
def bstack1l1l11111l1_opy_(bstack1l11l11l1_opy_=bstack11l1ll1_opy_ (u"ࠬ࠭ᐉ")):
  bstack1l11llllll1_opy_ = bstack11lll11ll1_opy_.on()
  bstack1l1l111l111_opy_ = bstack11ll1ll1_opy_.on()
  bstack1l1l111l11l_opy_ = percy.bstack1l1111111_opy_()
  if bstack1l1l111l11l_opy_ and not bstack1l1l111l111_opy_ and not bstack1l11llllll1_opy_:
    return bstack1l11l11l1_opy_ not in [bstack11l1ll1_opy_ (u"࠭ࡃࡃࡖࡖࡩࡸࡹࡩࡰࡰࡆࡶࡪࡧࡴࡦࡦࠪᐊ"), bstack11l1ll1_opy_ (u"ࠧࡍࡱࡪࡇࡷ࡫ࡡࡵࡧࡧࠫᐋ")]
  elif bstack1l11llllll1_opy_ and not bstack1l1l111l111_opy_:
    return bstack1l11l11l1_opy_ not in [bstack11l1ll1_opy_ (u"ࠨࡊࡲࡳࡰࡘࡵ࡯ࡕࡷࡥࡷࡺࡥࡥࠩᐌ"), bstack11l1ll1_opy_ (u"ࠩࡋࡳࡴࡱࡒࡶࡰࡉ࡭ࡳ࡯ࡳࡩࡧࡧࠫᐍ"), bstack11l1ll1_opy_ (u"ࠪࡐࡴ࡭ࡃࡳࡧࡤࡸࡪࡪࠧᐎ")]
  return bstack1l11llllll1_opy_ or bstack1l1l111l111_opy_ or bstack1l1l111l11l_opy_
@bstack111llll1ll_opy_(class_method=False)
def bstack1l11llll1l1_opy_(bstack1l11l11l1_opy_, test=None):
  bstack1l11lllll11_opy_ = bstack11lll11ll1_opy_.on()
  if not bstack1l11lllll11_opy_ or bstack1l11l11l1_opy_ not in [bstack11l1ll1_opy_ (u"࡙ࠫ࡫ࡳࡵࡔࡸࡲࡋ࡯࡮ࡪࡵ࡫ࡩࡩ࠭ᐏ")] or test == None:
    return None
  return {
    bstack11l1ll1_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠬᐐ"): bstack1l11lllll11_opy_ and bstack1ll1l1lll_opy_(threading.current_thread(), bstack11l1ll1_opy_ (u"࠭ࡡ࠲࠳ࡼࡔࡱࡧࡴࡧࡱࡵࡱࠬᐑ"), None) == True and bstack11lll11ll1_opy_.bstack1lllll11l_opy_(test[bstack11l1ll1_opy_ (u"ࠧࡵࡣࡪࡷࠬᐒ")])
  }