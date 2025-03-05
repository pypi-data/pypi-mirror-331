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
import requests
import logging
import threading
from urllib.parse import urlparse
from bstack_utils.constants import bstack111l11llll_opy_ as bstack1111lllll1_opy_, EVENTS
from bstack_utils.bstack1l11l1l111_opy_ import bstack1l11l1l111_opy_
from bstack_utils.helper import bstack1lll111ll_opy_, bstack11l11l1l11_opy_, bstack1l111lll11_opy_, bstack111l1l1ll1_opy_, \
  bstack111l111lll_opy_, bstack11ll1l111_opy_, get_host_info, bstack1111ll1lll_opy_, bstack11llllll_opy_, bstack111lll1lll_opy_
from browserstack_sdk._version import __version__
from bstack_utils.bstack1lll1ll1ll_opy_ import get_logger
from bstack_utils.bstack1lll1llll1_opy_ import bstack111l1l11l1_opy_
logger = get_logger(__name__)
bstack1lll1llll1_opy_ = bstack111l1l11l1_opy_()
@bstack111lll1lll_opy_(class_method=False)
def _111l1l1111_opy_(driver, bstack111ll1l111_opy_):
  response = {}
  try:
    caps = driver.capabilities
    response = {
        bstack111l11_opy_ (u"ࠧࡰࡵࡢࡲࡦࡳࡥࠨྲ"): caps.get(bstack111l11_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡑࡥࡲ࡫ࠧླ"), None),
        bstack111l11_opy_ (u"ࠩࡲࡷࡤࡼࡥࡳࡵ࡬ࡳࡳ࠭ྴ"): bstack111ll1l111_opy_.get(bstack111l11_opy_ (u"ࠪࡳࡸ࡜ࡥࡳࡵ࡬ࡳࡳ࠭ྵ"), None),
        bstack111l11_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡤࡴࡡ࡮ࡧࠪྶ"): caps.get(bstack111l11_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡔࡡ࡮ࡧࠪྷ"), None),
        bstack111l11_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸ࡟ࡷࡧࡵࡷ࡮ࡵ࡮ࠨྸ"): caps.get(bstack111l11_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡗࡧࡵࡷ࡮ࡵ࡮ࠨྐྵ"), None)
    }
  except Exception as error:
    logger.debug(bstack111l11_opy_ (u"ࠨࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤ࡮ࡴࠠࡧࡧࡷࡧ࡭࡯࡮ࡨࠢࡳࡰࡦࡺࡦࡰࡴࡰࠤࡩ࡫ࡴࡢ࡫࡯ࡷࠥࡽࡩࡵࡪࠣࡩࡷࡸ࡯ࡳࠢ࠽ࠤࠬྺ") + str(error))
  return response
def on():
    if os.environ.get(bstack111l11_opy_ (u"ࠩࡅࡗࡤࡇ࠱࠲࡛ࡢࡎ࡜࡚ࠧྻ"), None) is None or os.environ[bstack111l11_opy_ (u"ࠪࡆࡘࡥࡁ࠲࠳࡜ࡣࡏ࡝ࡔࠨྼ")] == bstack111l11_opy_ (u"ࠦࡳࡻ࡬࡭ࠤ྽"):
        return False
    return True
def bstack111l1l111l_opy_(config):
  return config.get(bstack111l11_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠬ྾"), False) or any([p.get(bstack111l11_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾ࠭྿"), False) == True for p in config.get(bstack111l11_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵࠪ࿀"), [])])
def bstack1ll1l1ll11_opy_(config, bstack111ll111_opy_):
  try:
    if not bstack1l111lll11_opy_(config):
      return False
    bstack111l11ll11_opy_ = config.get(bstack111l11_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠨ࿁"), False)
    if int(bstack111ll111_opy_) < len(config.get(bstack111l11_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬ࿂"), [])) and config[bstack111l11_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭࿃")][bstack111ll111_opy_]:
      bstack111l111l1l_opy_ = config[bstack111l11_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧ࿄")][bstack111ll111_opy_].get(bstack111l11_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠬ࿅"), None)
    else:
      bstack111l111l1l_opy_ = config.get(bstack111l11_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾ࿆࠭"), None)
    if bstack111l111l1l_opy_ != None:
      bstack111l11ll11_opy_ = bstack111l111l1l_opy_
    bstack1111lll1l1_opy_ = os.getenv(bstack111l11_opy_ (u"ࠧࡃࡕࡢࡅ࠶࠷࡙ࡠࡌ࡚ࡘࠬ࿇")) is not None and len(os.getenv(bstack111l11_opy_ (u"ࠨࡄࡖࡣࡆ࠷࠱࡚ࡡࡍ࡛࡙࠭࿈"))) > 0 and os.getenv(bstack111l11_opy_ (u"ࠩࡅࡗࡤࡇ࠱࠲࡛ࡢࡎ࡜࡚ࠧ࿉")) != bstack111l11_opy_ (u"ࠪࡲࡺࡲ࡬ࠨ࿊")
    return bstack111l11ll11_opy_ and bstack1111lll1l1_opy_
  except Exception as error:
    logger.debug(bstack111l11_opy_ (u"ࠫࡊࡾࡣࡦࡲࡷ࡭ࡴࡴࠠࡪࡰࠣࡺࡪࡸࡩࡧࡻ࡬ࡲ࡬ࠦࡴࡩࡧࠣࡅࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠣࡷࡪࡹࡳࡪࡱࡱࠤࡼ࡯ࡴࡩࠢࡨࡶࡷࡵࡲࠡ࠼ࠣࠫ࿋") + str(error))
  return False
def bstack1ll1lllll1_opy_(test_tags):
  bstack111l1l11ll_opy_ = os.getenv(bstack111l11_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣ࡙ࡋࡓࡕࡡࡄࡇࡈࡋࡓࡔࡋࡅࡍࡑࡏࡔ࡚ࡡࡆࡓࡓࡌࡉࡈࡗࡕࡅ࡙ࡏࡏࡏࡡ࡜ࡑࡑ࠭࿌"))
  if bstack111l1l11ll_opy_ is None:
    return True
  bstack111l1l11ll_opy_ = json.loads(bstack111l1l11ll_opy_)
  try:
    include_tags = bstack111l1l11ll_opy_[bstack111l11_opy_ (u"࠭ࡩ࡯ࡥ࡯ࡹࡩ࡫ࡔࡢࡩࡶࡍࡳ࡚ࡥࡴࡶ࡬ࡲ࡬࡙ࡣࡰࡲࡨࠫ࿍")] if bstack111l11_opy_ (u"ࠧࡪࡰࡦࡰࡺࡪࡥࡕࡣࡪࡷࡎࡴࡔࡦࡵࡷ࡭ࡳ࡭ࡓࡤࡱࡳࡩࠬ࿎") in bstack111l1l11ll_opy_ and isinstance(bstack111l1l11ll_opy_[bstack111l11_opy_ (u"ࠨ࡫ࡱࡧࡱࡻࡤࡦࡖࡤ࡫ࡸࡏ࡮ࡕࡧࡶࡸ࡮ࡴࡧࡔࡥࡲࡴࡪ࠭࿏")], list) else []
    exclude_tags = bstack111l1l11ll_opy_[bstack111l11_opy_ (u"ࠩࡨࡼࡨࡲࡵࡥࡧࡗࡥ࡬ࡹࡉ࡯ࡖࡨࡷࡹ࡯࡮ࡨࡕࡦࡳࡵ࡫ࠧ࿐")] if bstack111l11_opy_ (u"ࠪࡩࡽࡩ࡬ࡶࡦࡨࡘࡦ࡭ࡳࡊࡰࡗࡩࡸࡺࡩ࡯ࡩࡖࡧࡴࡶࡥࠨ࿑") in bstack111l1l11ll_opy_ and isinstance(bstack111l1l11ll_opy_[bstack111l11_opy_ (u"ࠫࡪࡾࡣ࡭ࡷࡧࡩ࡙ࡧࡧࡴࡋࡱࡘࡪࡹࡴࡪࡰࡪࡗࡨࡵࡰࡦࠩ࿒")], list) else []
    excluded = any(tag in exclude_tags for tag in test_tags)
    included = len(include_tags) == 0 or any(tag in include_tags for tag in test_tags)
    return not excluded and included
  except Exception as error:
    logger.debug(bstack111l11_opy_ (u"ࠧࡋࡲࡳࡱࡵࠤࡼ࡮ࡩ࡭ࡧࠣࡺࡦࡲࡩࡥࡣࡷ࡭ࡳ࡭ࠠࡵࡧࡶࡸࠥࡩࡡࡴࡧࠣࡪࡴࡸࠠࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠠࡣࡧࡩࡳࡷ࡫ࠠࡴࡥࡤࡲࡳ࡯࡮ࡨ࠰ࠣࡉࡷࡸ࡯ࡳࠢ࠽ࠤࠧ࿓") + str(error))
  return False
def bstack1111ll1l1l_opy_(config, bstack1111llll1l_opy_, bstack111l1111l1_opy_, bstack111l11111l_opy_):
  bstack111l11l11l_opy_ = bstack111l1l1ll1_opy_(config)
  bstack1111llll11_opy_ = bstack111l111lll_opy_(config)
  if bstack111l11l11l_opy_ is None or bstack1111llll11_opy_ is None:
    logger.error(bstack111l11_opy_ (u"࠭ࡅࡹࡥࡨࡴࡹ࡯࡯࡯ࠢࡺ࡬࡮ࡲࡥࠡࡥࡵࡩࡦࡺࡩ࡯ࡩࠣࡸࡪࡹࡴࠡࡴࡸࡲࠥ࡬࡯ࡳࠢࡅࡶࡴࡽࡳࡦࡴࡖࡸࡦࡩ࡫ࠡࡃࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠡࡃࡸࡸࡴࡳࡡࡵ࡫ࡲࡲ࠿ࠦࡍࡪࡵࡶ࡭ࡳ࡭ࠠࡢࡷࡷ࡬ࡪࡴࡴࡪࡥࡤࡸ࡮ࡵ࡮ࠡࡶࡲ࡯ࡪࡴࠧ࿔"))
    return [None, None]
  try:
    settings = json.loads(os.getenv(bstack111l11_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡔࡆࡕࡗࡣࡆࡉࡃࡆࡕࡖࡍࡇࡏࡌࡊࡖ࡜ࡣࡈࡕࡎࡇࡋࡊ࡙ࡗࡇࡔࡊࡑࡑࡣ࡞ࡓࡌࠨ࿕"), bstack111l11_opy_ (u"ࠨࡽࢀࠫ࿖")))
    data = {
        bstack111l11_opy_ (u"ࠩࡳࡶࡴࡰࡥࡤࡶࡑࡥࡲ࡫ࠧ࿗"): config[bstack111l11_opy_ (u"ࠪࡴࡷࡵࡪࡦࡥࡷࡒࡦࡳࡥࠨ࿘")],
        bstack111l11_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡑࡥࡲ࡫ࠧ࿙"): config.get(bstack111l11_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡒࡦࡳࡥࠨ࿚"), os.path.basename(os.getcwd())),
        bstack111l11_opy_ (u"࠭ࡳࡵࡣࡵࡸ࡙࡯࡭ࡦࠩ࿛"): bstack1lll111ll_opy_(),
        bstack111l11_opy_ (u"ࠧࡥࡧࡶࡧࡷ࡯ࡰࡵ࡫ࡲࡲࠬ࿜"): config.get(bstack111l11_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡄࡦࡵࡦࡶ࡮ࡶࡴࡪࡱࡱࠫ࿝"), bstack111l11_opy_ (u"ࠩࠪ࿞")),
        bstack111l11_opy_ (u"ࠪࡷࡴࡻࡲࡤࡧࠪ࿟"): {
            bstack111l11_opy_ (u"ࠫ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱࡎࡢ࡯ࡨࠫ࿠"): bstack1111llll1l_opy_,
            bstack111l11_opy_ (u"ࠬ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࡗࡧࡵࡷ࡮ࡵ࡮ࠨ࿡"): bstack111l1111l1_opy_,
            bstack111l11_opy_ (u"࠭ࡳࡥ࡭࡙ࡩࡷࡹࡩࡰࡰࠪ࿢"): __version__,
            bstack111l11_opy_ (u"ࠧ࡭ࡣࡱ࡫ࡺࡧࡧࡦࠩ࿣"): bstack111l11_opy_ (u"ࠨࡲࡼࡸ࡭ࡵ࡮ࠨ࿤"),
            bstack111l11_opy_ (u"ࠩࡷࡩࡸࡺࡆࡳࡣࡰࡩࡼࡵࡲ࡬ࠩ࿥"): bstack111l11_opy_ (u"ࠪࡷࡪࡲࡥ࡯࡫ࡸࡱࠬ࿦"),
            bstack111l11_opy_ (u"ࠫࡹ࡫ࡳࡵࡈࡵࡥࡲ࡫ࡷࡰࡴ࡮࡚ࡪࡸࡳࡪࡱࡱࠫ࿧"): bstack111l11111l_opy_
        },
        bstack111l11_opy_ (u"ࠬࡹࡥࡵࡶ࡬ࡲ࡬ࡹࠧ࿨"): settings,
        bstack111l11_opy_ (u"࠭ࡶࡦࡴࡶ࡭ࡴࡴࡃࡰࡰࡷࡶࡴࡲࠧ࿩"): bstack1111ll1lll_opy_(),
        bstack111l11_opy_ (u"ࠧࡤ࡫ࡌࡲ࡫ࡵࠧ࿪"): bstack11ll1l111_opy_(),
        bstack111l11_opy_ (u"ࠨࡪࡲࡷࡹࡏ࡮ࡧࡱࠪ࿫"): get_host_info(),
        bstack111l11_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡂࡷࡷࡳࡲࡧࡴࡪࡱࡱࠫ࿬"): bstack1l111lll11_opy_(config)
    }
    headers = {
        bstack111l11_opy_ (u"ࠪࡇࡴࡴࡴࡦࡰࡷ࠱࡙ࡿࡰࡦࠩ࿭"): bstack111l11_opy_ (u"ࠫࡦࡶࡰ࡭࡫ࡦࡥࡹ࡯࡯࡯࠱࡭ࡷࡴࡴࠧ࿮"),
    }
    config = {
        bstack111l11_opy_ (u"ࠬࡧࡵࡵࡪࠪ࿯"): (bstack111l11l11l_opy_, bstack1111llll11_opy_),
        bstack111l11_opy_ (u"࠭ࡨࡦࡣࡧࡩࡷࡹࠧ࿰"): headers
    }
    response = bstack11llllll_opy_(bstack111l11_opy_ (u"ࠧࡑࡑࡖࡘࠬ࿱"), bstack1111lllll1_opy_ + bstack111l11_opy_ (u"ࠨ࠱ࡹ࠶࠴ࡺࡥࡴࡶࡢࡶࡺࡴࡳࠨ࿲"), data, config)
    bstack1111llllll_opy_ = response.json()
    if bstack1111llllll_opy_[bstack111l11_opy_ (u"ࠩࡶࡹࡨࡩࡥࡴࡵࠪ࿳")]:
      parsed = json.loads(os.getenv(bstack111l11_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡗࡉࡘ࡚࡟ࡂࡅࡆࡉࡘ࡙ࡉࡃࡋࡏࡍ࡙࡟࡟ࡄࡑࡑࡊࡎࡍࡕࡓࡃࡗࡍࡔࡔ࡟࡚ࡏࡏࠫ࿴"), bstack111l11_opy_ (u"ࠫࢀࢃࠧ࿵")))
      parsed[bstack111l11_opy_ (u"ࠬࡹࡣࡢࡰࡱࡩࡷ࡜ࡥࡳࡵ࡬ࡳࡳ࠭࿶")] = bstack1111llllll_opy_[bstack111l11_opy_ (u"࠭ࡤࡢࡶࡤࠫ࿷")][bstack111l11_opy_ (u"ࠧࡴࡥࡤࡲࡳ࡫ࡲࡗࡧࡵࡷ࡮ࡵ࡮ࠨ࿸")]
      os.environ[bstack111l11_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡕࡇࡖࡘࡤࡇࡃࡄࡇࡖࡗࡎࡈࡉࡍࡋࡗ࡝ࡤࡉࡏࡏࡈࡌࡋ࡚ࡘࡁࡕࡋࡒࡒࡤ࡟ࡍࡍࠩ࿹")] = json.dumps(parsed)
      bstack1l11l1l111_opy_.bstack111l1l1lll_opy_(bstack1111llllll_opy_[bstack111l11_opy_ (u"ࠩࡧࡥࡹࡧࠧ࿺")][bstack111l11_opy_ (u"ࠪࡷࡨࡸࡩࡱࡶࡶࠫ࿻")])
      bstack1l11l1l111_opy_.bstack111l11l1ll_opy_(bstack1111llllll_opy_[bstack111l11_opy_ (u"ࠫࡩࡧࡴࡢࠩ࿼")][bstack111l11_opy_ (u"ࠬࡩ࡯࡮࡯ࡤࡲࡩࡹࠧ࿽")])
      bstack1l11l1l111_opy_.store()
      return bstack1111llllll_opy_[bstack111l11_opy_ (u"࠭ࡤࡢࡶࡤࠫ࿾")][bstack111l11_opy_ (u"ࠧࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࡔࡰ࡭ࡨࡲࠬ࿿")], bstack1111llllll_opy_[bstack111l11_opy_ (u"ࠨࡦࡤࡸࡦ࠭က")][bstack111l11_opy_ (u"ࠩ࡬ࡨࠬခ")]
    else:
      logger.error(bstack111l11_opy_ (u"ࠪࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡷࡩ࡫࡯ࡩࠥࡸࡵ࡯ࡰ࡬ࡲ࡬ࠦࡂࡳࡱࡺࡷࡪࡸࡓࡵࡣࡦ࡯ࠥࡇࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠥࡇࡵࡵࡱࡰࡥࡹ࡯࡯࡯࠼ࠣࠫဂ") + bstack1111llllll_opy_[bstack111l11_opy_ (u"ࠫࡲ࡫ࡳࡴࡣࡪࡩࠬဃ")])
      if bstack1111llllll_opy_[bstack111l11_opy_ (u"ࠬࡳࡥࡴࡵࡤ࡫ࡪ࠭င")] == bstack111l11_opy_ (u"࠭ࡉ࡯ࡸࡤࡰ࡮ࡪࠠࡤࡱࡱࡪ࡮࡭ࡵࡳࡣࡷ࡭ࡴࡴࠠࡱࡣࡶࡷࡪࡪ࠮ࠨစ"):
        for bstack111l11lll1_opy_ in bstack1111llllll_opy_[bstack111l11_opy_ (u"ࠧࡦࡴࡵࡳࡷࡹࠧဆ")]:
          logger.error(bstack111l11lll1_opy_[bstack111l11_opy_ (u"ࠨ࡯ࡨࡷࡸࡧࡧࡦࠩဇ")])
      return None, None
  except Exception as error:
    logger.error(bstack111l11_opy_ (u"ࠤࡈࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥࡽࡨࡪ࡮ࡨࠤࡨࡸࡥࡢࡶ࡬ࡲ࡬ࠦࡴࡦࡵࡷࠤࡷࡻ࡮ࠡࡨࡲࡶࠥࡈࡲࡰࡹࡶࡩࡷ࡙ࡴࡢࡥ࡮ࠤࡆࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠤࡆࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮࠻ࠢࠥဈ") +  str(error))
    return None, None
def bstack111l1l1l1l_opy_():
  if os.getenv(bstack111l11_opy_ (u"ࠪࡆࡘࡥࡁ࠲࠳࡜ࡣࡏ࡝ࡔࠨဉ")) is None:
    return {
        bstack111l11_opy_ (u"ࠫࡸࡺࡡࡵࡷࡶࠫည"): bstack111l11_opy_ (u"ࠬ࡫ࡲࡳࡱࡵࠫဋ"),
        bstack111l11_opy_ (u"࠭࡭ࡦࡵࡶࡥ࡬࡫ࠧဌ"): bstack111l11_opy_ (u"ࠧࡃࡷ࡬ࡰࡩࠦࡣࡳࡧࡤࡸ࡮ࡵ࡮ࠡࡪࡤࡨࠥ࡬ࡡࡪ࡮ࡨࡨ࠳࠭ဍ")
    }
  data = {bstack111l11_opy_ (u"ࠨࡧࡱࡨ࡙࡯࡭ࡦࠩဎ"): bstack1lll111ll_opy_()}
  headers = {
      bstack111l11_opy_ (u"ࠩࡄࡹࡹ࡮࡯ࡳ࡫ࡽࡥࡹ࡯࡯࡯ࠩဏ"): bstack111l11_opy_ (u"ࠪࡆࡪࡧࡲࡦࡴࠣࠫတ") + os.getenv(bstack111l11_opy_ (u"ࠦࡇ࡙࡟ࡂ࠳࠴࡝ࡤࡐࡗࡕࠤထ")),
      bstack111l11_opy_ (u"ࠬࡉ࡯࡯ࡶࡨࡲࡹ࠳ࡔࡺࡲࡨࠫဒ"): bstack111l11_opy_ (u"࠭ࡡࡱࡲ࡯࡭ࡨࡧࡴࡪࡱࡱ࠳࡯ࡹ࡯࡯ࠩဓ")
  }
  response = bstack11llllll_opy_(bstack111l11_opy_ (u"ࠧࡑࡗࡗࠫန"), bstack1111lllll1_opy_ + bstack111l11_opy_ (u"ࠨ࠱ࡷࡩࡸࡺ࡟ࡳࡷࡱࡷ࠴ࡹࡴࡰࡲࠪပ"), data, { bstack111l11_opy_ (u"ࠩ࡫ࡩࡦࡪࡥࡳࡵࠪဖ"): headers })
  try:
    if response.status_code == 200:
      logger.info(bstack111l11_opy_ (u"ࠥࡆࡷࡵࡷࡴࡧࡵࡗࡹࡧࡣ࡬ࠢࡄࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠢࡄࡹࡹࡵ࡭ࡢࡶ࡬ࡳࡳࠦࡔࡦࡵࡷࠤࡗࡻ࡮ࠡ࡯ࡤࡶࡰ࡫ࡤࠡࡣࡶࠤࡨࡵ࡭ࡱ࡮ࡨࡸࡪࡪࠠࡢࡶࠣࠦဗ") + bstack11l11l1l11_opy_().isoformat() + bstack111l11_opy_ (u"ࠫ࡟࠭ဘ"))
      return {bstack111l11_opy_ (u"ࠬࡹࡴࡢࡶࡸࡷࠬမ"): bstack111l11_opy_ (u"࠭ࡳࡶࡥࡦࡩࡸࡹࠧယ"), bstack111l11_opy_ (u"ࠧ࡮ࡧࡶࡷࡦ࡭ࡥࠨရ"): bstack111l11_opy_ (u"ࠨࠩလ")}
    else:
      response.raise_for_status()
  except requests.RequestException as error:
    logger.error(bstack111l11_opy_ (u"ࠤࡈࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥࡽࡨࡪ࡮ࡨࠤࡲࡧࡲ࡬࡫ࡱ࡫ࠥࡩ࡯࡮ࡲ࡯ࡩࡹ࡯࡯࡯ࠢࡲࡪࠥࡈࡲࡰࡹࡶࡩࡷ࡙ࡴࡢࡥ࡮ࠤࡆࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠤࡆࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࠡࡖࡨࡷࡹࠦࡒࡶࡰ࠽ࠤࠧဝ") + str(error))
    return {
        bstack111l11_opy_ (u"ࠪࡷࡹࡧࡴࡶࡵࠪသ"): bstack111l11_opy_ (u"ࠫࡪࡸࡲࡰࡴࠪဟ"),
        bstack111l11_opy_ (u"ࠬࡳࡥࡴࡵࡤ࡫ࡪ࠭ဠ"): str(error)
    }
def bstack1l1111ll_opy_(caps, options, desired_capabilities={}):
  try:
    bstack1111lll11l_opy_ = caps.get(bstack111l11_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰࡀ࡯ࡱࡶ࡬ࡳࡳࡹࠧအ"), {}).get(bstack111l11_opy_ (u"ࠧࡥࡧࡹ࡭ࡨ࡫ࡎࡢ࡯ࡨࠫဢ"), caps.get(bstack111l11_opy_ (u"ࠨࡦࡨࡺ࡮ࡩࡥࠨဣ"), bstack111l11_opy_ (u"ࠩࠪဤ")))
    if bstack1111lll11l_opy_:
      logger.warn(bstack111l11_opy_ (u"ࠥࡅࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠣࡅࡺࡺ࡯࡮ࡣࡷ࡭ࡴࡴࠠࡸ࡫࡯ࡰࠥࡸࡵ࡯ࠢࡲࡲࡱࡿࠠࡰࡰࠣࡈࡪࡹ࡫ࡵࡱࡳࠤࡧࡸ࡯ࡸࡵࡨࡶࡸ࠴ࠢဥ"))
      return False
    if options:
      bstack111l1l1l11_opy_ = options.to_capabilities()
    elif desired_capabilities:
      bstack111l1l1l11_opy_ = desired_capabilities
    else:
      bstack111l1l1l11_opy_ = {}
    browser = caps.get(bstack111l11_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡓࡧ࡭ࡦࠩဦ"), bstack111l11_opy_ (u"ࠬ࠭ဧ")).lower() or bstack111l1l1l11_opy_.get(bstack111l11_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡎࡢ࡯ࡨࠫဨ"), bstack111l11_opy_ (u"ࠧࠨဩ")).lower()
    if browser != bstack111l11_opy_ (u"ࠨࡥ࡫ࡶࡴࡳࡥࠨဪ"):
      logger.warn(bstack111l11_opy_ (u"ࠤࡄࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠢࡄࡹࡹࡵ࡭ࡢࡶ࡬ࡳࡳࠦࡷࡪ࡮࡯ࠤࡷࡻ࡮ࠡࡱࡱࡰࡾࠦ࡯࡯ࠢࡆ࡬ࡷࡵ࡭ࡦࠢࡥࡶࡴࡽࡳࡦࡴࡶ࠲ࠧါ"))
      return False
    browser_version = caps.get(bstack111l11_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵ࡚ࡪࡸࡳࡪࡱࡱࠫာ")) or caps.get(bstack111l11_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡤࡼࡥࡳࡵ࡬ࡳࡳ࠭ိ")) or bstack111l1l1l11_opy_.get(bstack111l11_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷ࡜ࡥࡳࡵ࡬ࡳࡳ࠭ီ")) or bstack111l1l1l11_opy_.get(bstack111l11_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰࡀ࡯ࡱࡶ࡬ࡳࡳࡹࠧု"), {}).get(bstack111l11_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡗࡧࡵࡷ࡮ࡵ࡮ࠨူ")) or bstack111l1l1l11_opy_.get(bstack111l11_opy_ (u"ࠨࡤࡶࡸࡦࡩ࡫࠻ࡱࡳࡸ࡮ࡵ࡮ࡴࠩေ"), {}).get(bstack111l11_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡢࡺࡪࡸࡳࡪࡱࡱࠫဲ"))
    if browser_version and browser_version != bstack111l11_opy_ (u"ࠪࡰࡦࡺࡥࡴࡶࠪဳ") and int(browser_version.split(bstack111l11_opy_ (u"ࠫ࠳࠭ဴ"))[0]) <= 98:
      logger.warn(bstack111l11_opy_ (u"ࠧࡇࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠥࡇࡵࡵࡱࡰࡥࡹ࡯࡯࡯ࠢࡺ࡭ࡱࡲࠠࡳࡷࡱࠤࡴࡴ࡬ࡺࠢࡲࡲࠥࡉࡨࡳࡱࡰࡩࠥࡨࡲࡰࡹࡶࡩࡷࠦࡶࡦࡴࡶ࡭ࡴࡴࠠࡨࡴࡨࡥࡹ࡫ࡲࠡࡶ࡫ࡥࡳࠦ࠹࠹࠰ࠥဵ"))
      return False
    if not options:
      bstack1111ll1ll1_opy_ = caps.get(bstack111l11_opy_ (u"࠭ࡧࡰࡱࡪ࠾ࡨ࡮ࡲࡰ࡯ࡨࡓࡵࡺࡩࡰࡰࡶࠫံ")) or bstack111l1l1l11_opy_.get(bstack111l11_opy_ (u"ࠧࡨࡱࡲ࡫࠿ࡩࡨࡳࡱࡰࡩࡔࡶࡴࡪࡱࡱࡷ့ࠬ"), {})
      if bstack111l11_opy_ (u"ࠨ࠯࠰࡬ࡪࡧࡤ࡭ࡧࡶࡷࠬး") in bstack1111ll1ll1_opy_.get(bstack111l11_opy_ (u"ࠩࡤࡶ࡬ࡹ္ࠧ"), []):
        logger.warn(bstack111l11_opy_ (u"ࠥࡅࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠣࡅࡺࡺ࡯࡮ࡣࡷ࡭ࡴࡴࠠࡸ࡫࡯ࡰࠥࡴ࡯ࡵࠢࡵࡹࡳࠦ࡯࡯ࠢ࡯ࡩ࡬ࡧࡣࡺࠢ࡫ࡩࡦࡪ࡬ࡦࡵࡶࠤࡲࡵࡤࡦ࠰ࠣࡗࡼ࡯ࡴࡤࡪࠣࡸࡴࠦ࡮ࡦࡹࠣ࡬ࡪࡧࡤ࡭ࡧࡶࡷࠥࡳ࡯ࡥࡧࠣࡳࡷࠦࡡࡷࡱ࡬ࡨࠥࡻࡳࡪࡰࡪࠤ࡭࡫ࡡࡥ࡮ࡨࡷࡸࠦ࡭ࡰࡦࡨ࠲်ࠧ"))
        return False
    return True
  except Exception as error:
    logger.debug(bstack111l11_opy_ (u"ࠦࡊࡾࡣࡦࡲࡷ࡭ࡴࡴࠠࡪࡰࠣࡺࡦࡲࡩࡥࡣࡷࡩࠥࡧ࠱࠲ࡻࠣࡷࡺࡶࡰࡰࡴࡷࠤ࠿ࠨျ") + str(error))
    return False
def set_capabilities(caps, config):
  try:
    bstack111l111l11_opy_ = config.get(bstack111l11_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࡔࡶࡴࡪࡱࡱࡷࠬြ"), {})
    bstack111l111l11_opy_[bstack111l11_opy_ (u"࠭ࡡࡶࡶ࡫ࡘࡴࡱࡥ࡯ࠩွ")] = os.getenv(bstack111l11_opy_ (u"ࠧࡃࡕࡢࡅ࠶࠷࡙ࡠࡌ࡚ࡘࠬှ"))
    bstack111l11ll1l_opy_ = json.loads(os.getenv(bstack111l11_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡕࡇࡖࡘࡤࡇࡃࡄࡇࡖࡗࡎࡈࡉࡍࡋࡗ࡝ࡤࡉࡏࡏࡈࡌࡋ࡚ࡘࡁࡕࡋࡒࡒࡤ࡟ࡍࡍࠩဿ"), bstack111l11_opy_ (u"ࠩࡾࢁࠬ၀"))).get(bstack111l11_opy_ (u"ࠪࡷࡨࡧ࡮࡯ࡧࡵ࡚ࡪࡸࡳࡪࡱࡱࠫ၁"))
    caps[bstack111l11_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠫ၂")] = True
    if bstack111l11_opy_ (u"ࠬࡨࡳࡵࡣࡦ࡯࠿ࡵࡰࡵ࡫ࡲࡲࡸ࠭၃") in caps:
      caps[bstack111l11_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰࡀ࡯ࡱࡶ࡬ࡳࡳࡹࠧ၄")][bstack111l11_opy_ (u"ࠧࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࡏࡱࡶ࡬ࡳࡳࡹࠧ၅")] = bstack111l111l11_opy_
      caps[bstack111l11_opy_ (u"ࠨࡤࡶࡸࡦࡩ࡫࠻ࡱࡳࡸ࡮ࡵ࡮ࡴࠩ၆")][bstack111l11_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࡑࡳࡸ࡮ࡵ࡮ࡴࠩ၇")][bstack111l11_opy_ (u"ࠪࡷࡨࡧ࡮࡯ࡧࡵ࡚ࡪࡸࡳࡪࡱࡱࠫ၈")] = bstack111l11ll1l_opy_
    else:
      caps[bstack111l11_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࡒࡴࡹ࡯࡯࡯ࡵࠪ၉")] = bstack111l111l11_opy_
      caps[bstack111l11_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࡓࡵࡺࡩࡰࡰࡶࠫ၊")][bstack111l11_opy_ (u"࠭ࡳࡤࡣࡱࡲࡪࡸࡖࡦࡴࡶ࡭ࡴࡴࠧ။")] = bstack111l11ll1l_opy_
  except Exception as error:
    logger.debug(bstack111l11_opy_ (u"ࠢࡆࡺࡦࡩࡵࡺࡩࡰࡰࠣࡻ࡭࡯࡬ࡦࠢࡶࡩࡹࡺࡩ࡯ࡩࠣࡅࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠣࡅࡺࡺ࡯࡮ࡣࡷ࡭ࡴࡴࠠࡤࡣࡳࡥࡧ࡯࡬ࡪࡶ࡬ࡩࡸ࠴ࠠࡆࡴࡵࡳࡷࡀࠠࠣ၌") +  str(error))
def bstack111llllll_opy_(driver, bstack111l111ll1_opy_):
  try:
    setattr(driver, bstack111l11_opy_ (u"ࠨࡤࡶࡸࡦࡩ࡫ࡂ࠳࠴ࡽࡘ࡮࡯ࡶ࡮ࡧࡗࡨࡧ࡮ࠨ၍"), True)
    session = driver.session_id
    if session:
      bstack111l111111_opy_ = True
      current_url = driver.current_url
      try:
        url = urlparse(current_url)
      except Exception as e:
        bstack111l111111_opy_ = False
      bstack111l111111_opy_ = url.scheme in [bstack111l11_opy_ (u"ࠤ࡫ࡸࡹࡶࠢ၎"), bstack111l11_opy_ (u"ࠥ࡬ࡹࡺࡰࡴࠤ၏")]
      if bstack111l111111_opy_:
        if bstack111l111ll1_opy_:
          logger.info(bstack111l11_opy_ (u"ࠦࡘ࡫ࡴࡶࡲࠣࡪࡴࡸࠠࡂࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠠࡵࡧࡶࡸ࡮ࡴࡧࠡࡪࡤࡷࠥࡹࡴࡢࡴࡷࡩࡩ࠴ࠠࡂࡷࡷࡳࡲࡧࡴࡦࠢࡷࡩࡸࡺࠠࡤࡣࡶࡩࠥ࡫ࡸࡦࡥࡸࡸ࡮ࡵ࡮ࠡࡹ࡬ࡰࡱࠦࡢࡦࡩ࡬ࡲࠥࡳ࡯࡮ࡧࡱࡸࡦࡸࡩ࡭ࡻ࠱ࠦၐ"))
      return bstack111l111ll1_opy_
  except Exception as e:
    logger.error(bstack111l11_opy_ (u"ࠧࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡ࡫ࡱࠤࡸࡺࡡࡳࡶ࡬ࡲ࡬ࠦࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࠦࡡࡶࡶࡲࡱࡦࡺࡩࡰࡰࠣࡷࡨࡧ࡮ࠡࡨࡲࡶࠥࡺࡨࡪࡵࠣࡸࡪࡹࡴࠡࡥࡤࡷࡪࡀࠠࠣၑ") + str(e))
    return False
def bstack11lll1l11_opy_(driver, name, path):
  try:
    bstack1111lll111_opy_ = {
        bstack111l11_opy_ (u"࠭ࡴࡩࡖࡨࡷࡹࡘࡵ࡯ࡗࡸ࡭ࡩ࠭ၒ"): threading.current_thread().current_test_uuid,
        bstack111l11_opy_ (u"ࠧࡵࡪࡅࡹ࡮ࡲࡤࡖࡷ࡬ࡨࠬၓ"): os.environ.get(bstack111l11_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡕࡇࡖࡘࡍ࡛ࡂࡠࡗࡘࡍࡉ࠭ၔ"), bstack111l11_opy_ (u"ࠩࠪၕ")),
        bstack111l11_opy_ (u"ࠪࡸ࡭ࡐࡷࡵࡖࡲ࡯ࡪࡴࠧၖ"): os.environ.get(bstack111l11_opy_ (u"ࠫࡇ࡙࡟ࡕࡇࡖࡘࡍ࡛ࡂࡠࡌ࡚ࡘࠬၗ"), bstack111l11_opy_ (u"ࠬ࠭ၘ"))
    }
    bstack1111lll1ll_opy_ = bstack1lll1llll1_opy_.bstack111l1ll111_opy_(EVENTS.bstack1ll1llll11_opy_.value)
    bstack1lll1llll1_opy_.mark(bstack1111lll1ll_opy_ + bstack111l11_opy_ (u"ࠨ࠺ࡴࡶࡤࡶࡹࠨၙ"))
    logger.debug(bstack111l11_opy_ (u"ࠧࡑࡧࡵࡪࡴࡸ࡭ࡪࡰࡪࠤࡸࡩࡡ࡯ࠢࡥࡩ࡫ࡵࡲࡦࠢࡶࡥࡻ࡯࡮ࡨࠢࡵࡩࡸࡻ࡬ࡵࡵࠪၚ"))
    try:
      logger.debug(driver.execute_async_script(bstack1l11l1l111_opy_.perform_scan, {bstack111l11_opy_ (u"ࠣ࡯ࡨࡸ࡭ࡵࡤࠣၛ"): name}))
      bstack1lll1llll1_opy_.end(bstack1111lll1ll_opy_, bstack1111lll1ll_opy_ + bstack111l11_opy_ (u"ࠤ࠽ࡷࡹࡧࡲࡵࠤၜ"), bstack1111lll1ll_opy_ + bstack111l11_opy_ (u"ࠥ࠾ࡪࡴࡤࠣၝ"), True, None)
    except Exception as error:
      bstack1lll1llll1_opy_.end(bstack1111lll1ll_opy_, bstack1111lll1ll_opy_ + bstack111l11_opy_ (u"ࠦ࠿ࡹࡴࡢࡴࡷࠦၞ"), bstack1111lll1ll_opy_ + bstack111l11_opy_ (u"ࠧࡀࡥ࡯ࡦࠥၟ"), False, str(error))
    bstack1111lll1ll_opy_ = bstack1lll1llll1_opy_.bstack111l1ll111_opy_(EVENTS.bstack111l11l111_opy_.value)
    bstack1lll1llll1_opy_.mark(bstack1111lll1ll_opy_ + bstack111l11_opy_ (u"ࠨ࠺ࡴࡶࡤࡶࡹࠨၠ"))
    try:
      logger.debug(driver.execute_async_script(bstack1l11l1l111_opy_.bstack111l1111ll_opy_, bstack1111lll111_opy_))
      bstack1lll1llll1_opy_.end(bstack1111lll1ll_opy_, bstack1111lll1ll_opy_ + bstack111l11_opy_ (u"ࠢ࠻ࡵࡷࡥࡷࡺࠢၡ"), bstack1111lll1ll_opy_ + bstack111l11_opy_ (u"ࠣ࠼ࡨࡲࡩࠨၢ"),True, None)
    except Exception as error:
      bstack1lll1llll1_opy_.end(bstack1111lll1ll_opy_, bstack1111lll1ll_opy_ + bstack111l11_opy_ (u"ࠤ࠽ࡷࡹࡧࡲࡵࠤၣ"), bstack1111lll1ll_opy_ + bstack111l11_opy_ (u"ࠥ࠾ࡪࡴࡤࠣၤ"),False, str(error))
    logger.info(bstack111l11_opy_ (u"ࠦࡆࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠤࡹ࡫ࡳࡵ࡫ࡱ࡫ࠥ࡬࡯ࡳࠢࡷ࡬࡮ࡹࠠࡵࡧࡶࡸࠥࡩࡡࡴࡧࠣ࡬ࡦࡹࠠࡦࡰࡧࡩࡩ࠴ࠢၥ"))
  except Exception as bstack111l11l1l1_opy_:
    logger.error(bstack111l11_opy_ (u"ࠧࡇࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠥࡸࡥࡴࡷ࡯ࡸࡸࠦࡣࡰࡷ࡯ࡨࠥࡴ࡯ࡵࠢࡥࡩࠥࡶࡲࡰࡥࡨࡷࡸ࡫ࡤࠡࡨࡲࡶࠥࡺࡨࡦࠢࡷࡩࡸࡺࠠࡤࡣࡶࡩ࠿ࠦࠢၦ") + str(path) + bstack111l11_opy_ (u"ࠨࠠࡆࡴࡵࡳࡷࠦ࠺ࠣၧ") + str(bstack111l11l1l1_opy_))