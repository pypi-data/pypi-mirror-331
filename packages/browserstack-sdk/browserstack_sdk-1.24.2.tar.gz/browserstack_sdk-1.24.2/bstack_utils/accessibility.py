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
import requests
import logging
import threading
from urllib.parse import urlparse
from bstack_utils.constants import bstack1l11ll1l1l1_opy_ as bstack1l11ll1l11l_opy_, EVENTS
from bstack_utils.bstack1l1ll1111l_opy_ import bstack1l1ll1111l_opy_
from bstack_utils.helper import bstack1ll1l1ll_opy_, bstack111ll1l111_opy_, bstack1ll111111_opy_, bstack1l11ll11l1l_opy_, \
  bstack1l11llll111_opy_, bstack11l1ll1lll_opy_, get_host_info, bstack1l1l111l1ll_opy_, bstack1l1111l1l_opy_, bstack111llll1ll_opy_
from browserstack_sdk._version import __version__
from bstack_utils.bstack1ll1ll111_opy_ import get_logger
from bstack_utils.bstack1ll111ll1l_opy_ import bstack1llll111lll_opy_
logger = get_logger(__name__)
bstack1ll111ll1l_opy_ = bstack1llll111lll_opy_()
@bstack111llll1ll_opy_(class_method=False)
def _1l11ll11ll1_opy_(driver, bstack111l1l1l1l_opy_):
  response = {}
  try:
    caps = driver.capabilities
    response = {
        bstack11l1ll1_opy_ (u"ࠨࡱࡶࡣࡳࡧ࡭ࡦࠩᐓ"): caps.get(bstack11l1ll1_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡒࡦࡳࡥࠨᐔ"), None),
        bstack11l1ll1_opy_ (u"ࠪࡳࡸࡥࡶࡦࡴࡶ࡭ࡴࡴࠧᐕ"): bstack111l1l1l1l_opy_.get(bstack11l1ll1_opy_ (u"ࠫࡴࡹࡖࡦࡴࡶ࡭ࡴࡴࠧᐖ"), None),
        bstack11l1ll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡥ࡮ࡢ࡯ࡨࠫᐗ"): caps.get(bstack11l1ll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡎࡢ࡯ࡨࠫᐘ"), None),
        bstack11l1ll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡠࡸࡨࡶࡸ࡯࡯࡯ࠩᐙ"): caps.get(bstack11l1ll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡘࡨࡶࡸ࡯࡯࡯ࠩᐚ"), None)
    }
  except Exception as error:
    logger.debug(bstack11l1ll1_opy_ (u"ࠩࡈࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥ࡯࡮ࠡࡨࡨࡸࡨ࡮ࡩ࡯ࡩࠣࡴࡱࡧࡴࡧࡱࡵࡱࠥࡪࡥࡵࡣ࡬ࡰࡸࠦࡷࡪࡶ࡫ࠤࡪࡸࡲࡰࡴࠣ࠾ࠥ࠭ᐛ") + str(error))
  return response
def on():
    if os.environ.get(bstack11l1ll1_opy_ (u"ࠪࡆࡘࡥࡁ࠲࠳࡜ࡣࡏ࡝ࡔࠨᐜ"), None) is None or os.environ[bstack11l1ll1_opy_ (u"ࠫࡇ࡙࡟ࡂ࠳࠴࡝ࡤࡐࡗࡕࠩᐝ")] == bstack11l1ll1_opy_ (u"ࠧࡴࡵ࡭࡮ࠥᐞ"):
        return False
    return True
def bstack1l11lllllll_opy_(config):
  return config.get(bstack11l1ll1_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾ࠭ᐟ"), False) or any([p.get(bstack11l1ll1_opy_ (u"ࠧࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠧᐠ"), False) == True for p in config.get(bstack11l1ll1_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫᐡ"), [])])
def bstack111l1l1l_opy_(config, bstack1ll1lll1l_opy_):
  try:
    if not bstack1ll111111_opy_(config):
      return False
    bstack1l11ll111l1_opy_ = config.get(bstack11l1ll1_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠩᐢ"), False)
    if int(bstack1ll1lll1l_opy_) < len(config.get(bstack11l1ll1_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭ᐣ"), [])) and config[bstack11l1ll1_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧᐤ")][bstack1ll1lll1l_opy_]:
      bstack1l11ll1llll_opy_ = config[bstack11l1ll1_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡳࠨᐥ")][bstack1ll1lll1l_opy_].get(bstack11l1ll1_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾ࠭ᐦ"), None)
    else:
      bstack1l11ll1llll_opy_ = config.get(bstack11l1ll1_opy_ (u"ࠧࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠧᐧ"), None)
    if bstack1l11ll1llll_opy_ != None:
      bstack1l11ll111l1_opy_ = bstack1l11ll1llll_opy_
    bstack1l11lll1ll1_opy_ = os.getenv(bstack11l1ll1_opy_ (u"ࠨࡄࡖࡣࡆ࠷࠱࡚ࡡࡍ࡛࡙࠭ᐨ")) is not None and len(os.getenv(bstack11l1ll1_opy_ (u"ࠩࡅࡗࡤࡇ࠱࠲࡛ࡢࡎ࡜࡚ࠧᐩ"))) > 0 and os.getenv(bstack11l1ll1_opy_ (u"ࠪࡆࡘࡥࡁ࠲࠳࡜ࡣࡏ࡝ࡔࠨᐪ")) != bstack11l1ll1_opy_ (u"ࠫࡳࡻ࡬࡭ࠩᐫ")
    return bstack1l11ll111l1_opy_ and bstack1l11lll1ll1_opy_
  except Exception as error:
    logger.debug(bstack11l1ll1_opy_ (u"ࠬࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡ࡫ࡱࠤࡻ࡫ࡲࡪࡨࡼ࡭ࡳ࡭ࠠࡵࡪࡨࠤࡆࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠤࡸ࡫ࡳࡴ࡫ࡲࡲࠥࡽࡩࡵࡪࠣࡩࡷࡸ࡯ࡳࠢ࠽ࠤࠬᐬ") + str(error))
  return False
def bstack1lllll11l_opy_(test_tags):
  bstack1lll11l11l1_opy_ = os.getenv(bstack11l1ll1_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡚ࡅࡔࡖࡢࡅࡈࡉࡅࡔࡕࡌࡆࡎࡒࡉࡕ࡛ࡢࡇࡔࡔࡆࡊࡉࡘࡖࡆ࡚ࡉࡐࡐࡢ࡝ࡒࡒࠧᐭ"))
  if bstack1lll11l11l1_opy_ is None:
    return True
  bstack1lll11l11l1_opy_ = json.loads(bstack1lll11l11l1_opy_)
  try:
    include_tags = bstack1lll11l11l1_opy_[bstack11l1ll1_opy_ (u"ࠧࡪࡰࡦࡰࡺࡪࡥࡕࡣࡪࡷࡎࡴࡔࡦࡵࡷ࡭ࡳ࡭ࡓࡤࡱࡳࡩࠬᐮ")] if bstack11l1ll1_opy_ (u"ࠨ࡫ࡱࡧࡱࡻࡤࡦࡖࡤ࡫ࡸࡏ࡮ࡕࡧࡶࡸ࡮ࡴࡧࡔࡥࡲࡴࡪ࠭ᐯ") in bstack1lll11l11l1_opy_ and isinstance(bstack1lll11l11l1_opy_[bstack11l1ll1_opy_ (u"ࠩ࡬ࡲࡨࡲࡵࡥࡧࡗࡥ࡬ࡹࡉ࡯ࡖࡨࡷࡹ࡯࡮ࡨࡕࡦࡳࡵ࡫ࠧᐰ")], list) else []
    exclude_tags = bstack1lll11l11l1_opy_[bstack11l1ll1_opy_ (u"ࠪࡩࡽࡩ࡬ࡶࡦࡨࡘࡦ࡭ࡳࡊࡰࡗࡩࡸࡺࡩ࡯ࡩࡖࡧࡴࡶࡥࠨᐱ")] if bstack11l1ll1_opy_ (u"ࠫࡪࡾࡣ࡭ࡷࡧࡩ࡙ࡧࡧࡴࡋࡱࡘࡪࡹࡴࡪࡰࡪࡗࡨࡵࡰࡦࠩᐲ") in bstack1lll11l11l1_opy_ and isinstance(bstack1lll11l11l1_opy_[bstack11l1ll1_opy_ (u"ࠬ࡫ࡸࡤ࡮ࡸࡨࡪ࡚ࡡࡨࡵࡌࡲ࡙࡫ࡳࡵ࡫ࡱ࡫ࡘࡩ࡯ࡱࡧࠪᐳ")], list) else []
    excluded = any(tag in exclude_tags for tag in test_tags)
    included = len(include_tags) == 0 or any(tag in include_tags for tag in test_tags)
    return not excluded and included
  except Exception as error:
    logger.debug(bstack11l1ll1_opy_ (u"ࠨࡅࡳࡴࡲࡶࠥࡽࡨࡪ࡮ࡨࠤࡻࡧ࡬ࡪࡦࡤࡸ࡮ࡴࡧࠡࡶࡨࡷࡹࠦࡣࡢࡵࡨࠤ࡫ࡵࡲࠡࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠡࡤࡨࡪࡴࡸࡥࠡࡵࡦࡥࡳࡴࡩ࡯ࡩ࠱ࠤࡊࡸࡲࡰࡴࠣ࠾ࠥࠨᐴ") + str(error))
  return False
def bstack1l11ll1ll1l_opy_(config, bstack1l11ll1ll11_opy_, bstack1l11ll11lll_opy_, bstack1l11lll111l_opy_):
  bstack1l11ll11111_opy_ = bstack1l11ll11l1l_opy_(config)
  bstack1l11lll1l1l_opy_ = bstack1l11llll111_opy_(config)
  if bstack1l11ll11111_opy_ is None or bstack1l11lll1l1l_opy_ is None:
    logger.error(bstack11l1ll1_opy_ (u"ࠧࡆࡺࡦࡩࡵࡺࡩࡰࡰࠣࡻ࡭࡯࡬ࡦࠢࡦࡶࡪࡧࡴࡪࡰࡪࠤࡹ࡫ࡳࡵࠢࡵࡹࡳࠦࡦࡰࡴࠣࡆࡷࡵࡷࡴࡧࡵࡗࡹࡧࡣ࡬ࠢࡄࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠢࡄࡹࡹࡵ࡭ࡢࡶ࡬ࡳࡳࡀࠠࡎ࡫ࡶࡷ࡮ࡴࡧࠡࡣࡸࡸ࡭࡫࡮ࡵ࡫ࡦࡥࡹ࡯࡯࡯ࠢࡷࡳࡰ࡫࡮ࠨᐵ"))
    return [None, None]
  try:
    settings = json.loads(os.getenv(bstack11l1ll1_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡕࡇࡖࡘࡤࡇࡃࡄࡇࡖࡗࡎࡈࡉࡍࡋࡗ࡝ࡤࡉࡏࡏࡈࡌࡋ࡚ࡘࡁࡕࡋࡒࡒࡤ࡟ࡍࡍࠩᐶ"), bstack11l1ll1_opy_ (u"ࠩࡾࢁࠬᐷ")))
    data = {
        bstack11l1ll1_opy_ (u"ࠪࡴࡷࡵࡪࡦࡥࡷࡒࡦࡳࡥࠨᐸ"): config[bstack11l1ll1_opy_ (u"ࠫࡵࡸ࡯࡫ࡧࡦࡸࡓࡧ࡭ࡦࠩᐹ")],
        bstack11l1ll1_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡒࡦࡳࡥࠨᐺ"): config.get(bstack11l1ll1_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡓࡧ࡭ࡦࠩᐻ"), os.path.basename(os.getcwd())),
        bstack11l1ll1_opy_ (u"ࠧࡴࡶࡤࡶࡹ࡚ࡩ࡮ࡧࠪᐼ"): bstack1ll1l1ll_opy_(),
        bstack11l1ll1_opy_ (u"ࠨࡦࡨࡷࡨࡸࡩࡱࡶ࡬ࡳࡳ࠭ᐽ"): config.get(bstack11l1ll1_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡅࡧࡶࡧࡷ࡯ࡰࡵ࡫ࡲࡲࠬᐾ"), bstack11l1ll1_opy_ (u"ࠪࠫᐿ")),
        bstack11l1ll1_opy_ (u"ࠫࡸࡵࡵࡳࡥࡨࠫᑀ"): {
            bstack11l1ll1_opy_ (u"ࠬ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࡏࡣࡰࡩࠬᑁ"): bstack1l11ll1ll11_opy_,
            bstack11l1ll1_opy_ (u"࠭ࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡘࡨࡶࡸ࡯࡯࡯ࠩᑂ"): bstack1l11ll11lll_opy_,
            bstack11l1ll1_opy_ (u"ࠧࡴࡦ࡮࡚ࡪࡸࡳࡪࡱࡱࠫᑃ"): __version__,
            bstack11l1ll1_opy_ (u"ࠨ࡮ࡤࡲ࡬ࡻࡡࡨࡧࠪᑄ"): bstack11l1ll1_opy_ (u"ࠩࡳࡽࡹ࡮࡯࡯ࠩᑅ"),
            bstack11l1ll1_opy_ (u"ࠪࡸࡪࡹࡴࡇࡴࡤࡱࡪࡽ࡯ࡳ࡭ࠪᑆ"): bstack11l1ll1_opy_ (u"ࠫࡸ࡫࡬ࡦࡰ࡬ࡹࡲ࠭ᑇ"),
            bstack11l1ll1_opy_ (u"ࠬࡺࡥࡴࡶࡉࡶࡦࡳࡥࡸࡱࡵ࡯࡛࡫ࡲࡴ࡫ࡲࡲࠬᑈ"): bstack1l11lll111l_opy_
        },
        bstack11l1ll1_opy_ (u"࠭ࡳࡦࡶࡷ࡭ࡳ࡭ࡳࠨᑉ"): settings,
        bstack11l1ll1_opy_ (u"ࠧࡷࡧࡵࡷ࡮ࡵ࡮ࡄࡱࡱࡸࡷࡵ࡬ࠨᑊ"): bstack1l1l111l1ll_opy_(),
        bstack11l1ll1_opy_ (u"ࠨࡥ࡬ࡍࡳ࡬࡯ࠨᑋ"): bstack11l1ll1lll_opy_(),
        bstack11l1ll1_opy_ (u"ࠩ࡫ࡳࡸࡺࡉ࡯ࡨࡲࠫᑌ"): get_host_info(),
        bstack11l1ll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡃࡸࡸࡴࡳࡡࡵ࡫ࡲࡲࠬᑍ"): bstack1ll111111_opy_(config)
    }
    headers = {
        bstack11l1ll1_opy_ (u"ࠫࡈࡵ࡮ࡵࡧࡱࡸ࠲࡚ࡹࡱࡧࠪᑎ"): bstack11l1ll1_opy_ (u"ࠬࡧࡰࡱ࡮࡬ࡧࡦࡺࡩࡰࡰ࠲࡮ࡸࡵ࡮ࠨᑏ"),
    }
    config = {
        bstack11l1ll1_opy_ (u"࠭ࡡࡶࡶ࡫ࠫᑐ"): (bstack1l11ll11111_opy_, bstack1l11lll1l1l_opy_),
        bstack11l1ll1_opy_ (u"ࠧࡩࡧࡤࡨࡪࡸࡳࠨᑑ"): headers
    }
    response = bstack1l1111l1l_opy_(bstack11l1ll1_opy_ (u"ࠨࡒࡒࡗ࡙࠭ᑒ"), bstack1l11ll1l11l_opy_ + bstack11l1ll1_opy_ (u"ࠩ࠲ࡺ࠷࠵ࡴࡦࡵࡷࡣࡷࡻ࡮ࡴࠩᑓ"), data, config)
    bstack1l11lll11ll_opy_ = response.json()
    if bstack1l11lll11ll_opy_[bstack11l1ll1_opy_ (u"ࠪࡷࡺࡩࡣࡦࡵࡶࠫᑔ")]:
      parsed = json.loads(os.getenv(bstack11l1ll1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡘࡊ࡙ࡔࡠࡃࡆࡇࡊ࡙ࡓࡊࡄࡌࡐࡎ࡚࡙ࡠࡅࡒࡒࡋࡏࡇࡖࡔࡄࡘࡎࡕࡎࡠ࡛ࡐࡐࠬᑕ"), bstack11l1ll1_opy_ (u"ࠬࢁࡽࠨᑖ")))
      parsed[bstack11l1ll1_opy_ (u"࠭ࡳࡤࡣࡱࡲࡪࡸࡖࡦࡴࡶ࡭ࡴࡴࠧᑗ")] = bstack1l11lll11ll_opy_[bstack11l1ll1_opy_ (u"ࠧࡥࡣࡷࡥࠬᑘ")][bstack11l1ll1_opy_ (u"ࠨࡵࡦࡥࡳࡴࡥࡳࡘࡨࡶࡸ࡯࡯࡯ࠩᑙ")]
      os.environ[bstack11l1ll1_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡖࡈࡗ࡙ࡥࡁࡄࡅࡈࡗࡘࡏࡂࡊࡎࡌࡘ࡞ࡥࡃࡐࡐࡉࡍࡌ࡛ࡒࡂࡖࡌࡓࡓࡥ࡙ࡎࡎࠪᑚ")] = json.dumps(parsed)
      bstack1l1ll1111l_opy_.bstack1l11ll111ll_opy_(bstack1l11lll11ll_opy_[bstack11l1ll1_opy_ (u"ࠪࡨࡦࡺࡡࠨᑛ")][bstack11l1ll1_opy_ (u"ࠫࡸࡩࡲࡪࡲࡷࡷࠬᑜ")])
      bstack1l1ll1111l_opy_.bstack1l11lll1111_opy_(bstack1l11lll11ll_opy_[bstack11l1ll1_opy_ (u"ࠬࡪࡡࡵࡣࠪᑝ")][bstack11l1ll1_opy_ (u"࠭ࡣࡰ࡯ࡰࡥࡳࡪࡳࠨᑞ")])
      bstack1l1ll1111l_opy_.store()
      return bstack1l11lll11ll_opy_[bstack11l1ll1_opy_ (u"ࠧࡥࡣࡷࡥࠬᑟ")][bstack11l1ll1_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࡕࡱ࡮ࡩࡳ࠭ᑠ")], bstack1l11lll11ll_opy_[bstack11l1ll1_opy_ (u"ࠩࡧࡥࡹࡧࠧᑡ")][bstack11l1ll1_opy_ (u"ࠪ࡭ࡩ࠭ᑢ")]
    else:
      logger.error(bstack11l1ll1_opy_ (u"ࠫࡊࡾࡣࡦࡲࡷ࡭ࡴࡴࠠࡸࡪ࡬ࡰࡪࠦࡲࡶࡰࡱ࡭ࡳ࡭ࠠࡃࡴࡲࡻࡸ࡫ࡲࡔࡶࡤࡧࡰࠦࡁࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࠦࡁࡶࡶࡲࡱࡦࡺࡩࡰࡰ࠽ࠤࠬᑣ") + bstack1l11lll11ll_opy_[bstack11l1ll1_opy_ (u"ࠬࡳࡥࡴࡵࡤ࡫ࡪ࠭ᑤ")])
      if bstack1l11lll11ll_opy_[bstack11l1ll1_opy_ (u"࠭࡭ࡦࡵࡶࡥ࡬࡫ࠧᑥ")] == bstack11l1ll1_opy_ (u"ࠧࡊࡰࡹࡥࡱ࡯ࡤࠡࡥࡲࡲ࡫࡯ࡧࡶࡴࡤࡸ࡮ࡵ࡮ࠡࡲࡤࡷࡸ࡫ࡤ࠯ࠩᑦ"):
        for bstack1l11ll1111l_opy_ in bstack1l11lll11ll_opy_[bstack11l1ll1_opy_ (u"ࠨࡧࡵࡶࡴࡸࡳࠨᑧ")]:
          logger.error(bstack1l11ll1111l_opy_[bstack11l1ll1_opy_ (u"ࠩࡰࡩࡸࡹࡡࡨࡧࠪᑨ")])
      return None, None
  except Exception as error:
    logger.error(bstack11l1ll1_opy_ (u"ࠥࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡷࡩ࡫࡯ࡩࠥࡩࡲࡦࡣࡷ࡭ࡳ࡭ࠠࡵࡧࡶࡸࠥࡸࡵ࡯ࠢࡩࡳࡷࠦࡂࡳࡱࡺࡷࡪࡸࡓࡵࡣࡦ࡯ࠥࡇࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠥࡇࡵࡵࡱࡰࡥࡹ࡯࡯࡯࠼ࠣࠦᑩ") +  str(error))
    return None, None
def bstack1l11ll1lll1_opy_():
  if os.getenv(bstack11l1ll1_opy_ (u"ࠫࡇ࡙࡟ࡂ࠳࠴࡝ࡤࡐࡗࡕࠩᑪ")) is None:
    return {
        bstack11l1ll1_opy_ (u"ࠬࡹࡴࡢࡶࡸࡷࠬᑫ"): bstack11l1ll1_opy_ (u"࠭ࡥࡳࡴࡲࡶࠬᑬ"),
        bstack11l1ll1_opy_ (u"ࠧ࡮ࡧࡶࡷࡦ࡭ࡥࠨᑭ"): bstack11l1ll1_opy_ (u"ࠨࡄࡸ࡭ࡱࡪࠠࡤࡴࡨࡥࡹ࡯࡯࡯ࠢ࡫ࡥࡩࠦࡦࡢ࡫࡯ࡩࡩ࠴ࠧᑮ")
    }
  data = {bstack11l1ll1_opy_ (u"ࠩࡨࡲࡩ࡚ࡩ࡮ࡧࠪᑯ"): bstack1ll1l1ll_opy_()}
  headers = {
      bstack11l1ll1_opy_ (u"ࠪࡅࡺࡺࡨࡰࡴ࡬ࡾࡦࡺࡩࡰࡰࠪᑰ"): bstack11l1ll1_opy_ (u"ࠫࡇ࡫ࡡࡳࡧࡵࠤࠬᑱ") + os.getenv(bstack11l1ll1_opy_ (u"ࠧࡈࡓࡠࡃ࠴࠵࡞ࡥࡊࡘࡖࠥᑲ")),
      bstack11l1ll1_opy_ (u"࠭ࡃࡰࡰࡷࡩࡳࡺ࠭ࡕࡻࡳࡩࠬᑳ"): bstack11l1ll1_opy_ (u"ࠧࡢࡲࡳࡰ࡮ࡩࡡࡵ࡫ࡲࡲ࠴ࡰࡳࡰࡰࠪᑴ")
  }
  response = bstack1l1111l1l_opy_(bstack11l1ll1_opy_ (u"ࠨࡒࡘࡘࠬᑵ"), bstack1l11ll1l11l_opy_ + bstack11l1ll1_opy_ (u"ࠩ࠲ࡸࡪࡹࡴࡠࡴࡸࡲࡸ࠵ࡳࡵࡱࡳࠫᑶ"), data, { bstack11l1ll1_opy_ (u"ࠪ࡬ࡪࡧࡤࡦࡴࡶࠫᑷ"): headers })
  try:
    if response.status_code == 200:
      logger.info(bstack11l1ll1_opy_ (u"ࠦࡇࡸ࡯ࡸࡵࡨࡶࡘࡺࡡࡤ࡭ࠣࡅࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠣࡅࡺࡺ࡯࡮ࡣࡷ࡭ࡴࡴࠠࡕࡧࡶࡸࠥࡘࡵ࡯ࠢࡰࡥࡷࡱࡥࡥࠢࡤࡷࠥࡩ࡯࡮ࡲ࡯ࡩࡹ࡫ࡤࠡࡣࡷࠤࠧᑸ") + bstack111ll1l111_opy_().isoformat() + bstack11l1ll1_opy_ (u"ࠬࡠࠧᑹ"))
      return {bstack11l1ll1_opy_ (u"࠭ࡳࡵࡣࡷࡹࡸ࠭ᑺ"): bstack11l1ll1_opy_ (u"ࠧࡴࡷࡦࡧࡪࡹࡳࠨᑻ"), bstack11l1ll1_opy_ (u"ࠨ࡯ࡨࡷࡸࡧࡧࡦࠩᑼ"): bstack11l1ll1_opy_ (u"ࠩࠪᑽ")}
    else:
      response.raise_for_status()
  except requests.RequestException as error:
    logger.error(bstack11l1ll1_opy_ (u"ࠥࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡷࡩ࡫࡯ࡩࠥࡳࡡࡳ࡭࡬ࡲ࡬ࠦࡣࡰ࡯ࡳࡰࡪࡺࡩࡰࡰࠣࡳ࡫ࠦࡂࡳࡱࡺࡷࡪࡸࡓࡵࡣࡦ࡯ࠥࡇࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠥࡇࡵࡵࡱࡰࡥࡹ࡯࡯࡯ࠢࡗࡩࡸࡺࠠࡓࡷࡱ࠾ࠥࠨᑾ") + str(error))
    return {
        bstack11l1ll1_opy_ (u"ࠫࡸࡺࡡࡵࡷࡶࠫᑿ"): bstack11l1ll1_opy_ (u"ࠬ࡫ࡲࡳࡱࡵࠫᒀ"),
        bstack11l1ll1_opy_ (u"࠭࡭ࡦࡵࡶࡥ࡬࡫ࠧᒁ"): str(error)
    }
def bstack11llllll_opy_(caps, options, desired_capabilities={}):
  try:
    bstack1ll1llllll1_opy_ = caps.get(bstack11l1ll1_opy_ (u"ࠧࡣࡵࡷࡥࡨࡱ࠺ࡰࡲࡷ࡭ࡴࡴࡳࠨᒂ"), {}).get(bstack11l1ll1_opy_ (u"ࠨࡦࡨࡺ࡮ࡩࡥࡏࡣࡰࡩࠬᒃ"), caps.get(bstack11l1ll1_opy_ (u"ࠩࡧࡩࡻ࡯ࡣࡦࠩᒄ"), bstack11l1ll1_opy_ (u"ࠪࠫᒅ")))
    if bstack1ll1llllll1_opy_:
      logger.warn(bstack11l1ll1_opy_ (u"ࠦࡆࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠤࡆࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࠡࡹ࡬ࡰࡱࠦࡲࡶࡰࠣࡳࡳࡲࡹࠡࡱࡱࠤࡉ࡫ࡳ࡬ࡶࡲࡴࠥࡨࡲࡰࡹࡶࡩࡷࡹ࠮ࠣᒆ"))
      return False
    if options:
      bstack1l11ll1l111_opy_ = options.to_capabilities()
    elif desired_capabilities:
      bstack1l11ll1l111_opy_ = desired_capabilities
    else:
      bstack1l11ll1l111_opy_ = {}
    browser = caps.get(bstack11l1ll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡔࡡ࡮ࡧࠪᒇ"), bstack11l1ll1_opy_ (u"࠭ࠧᒈ")).lower() or bstack1l11ll1l111_opy_.get(bstack11l1ll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡏࡣࡰࡩࠬᒉ"), bstack11l1ll1_opy_ (u"ࠨࠩᒊ")).lower()
    if browser != bstack11l1ll1_opy_ (u"ࠩࡦ࡬ࡷࡵ࡭ࡦࠩᒋ"):
      logger.warning(bstack11l1ll1_opy_ (u"ࠥࡅࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠣࡅࡺࡺ࡯࡮ࡣࡷ࡭ࡴࡴࠠࡸ࡫࡯ࡰࠥࡸࡵ࡯ࠢࡲࡲࡱࡿࠠࡰࡰࠣࡇ࡭ࡸ࡯࡮ࡧࠣࡦࡷࡵࡷࡴࡧࡵࡷ࠳ࠨᒌ"))
      return False
    browser_version = caps.get(bstack11l1ll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶ࡛࡫ࡲࡴ࡫ࡲࡲࠬᒍ")) or caps.get(bstack11l1ll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡥࡶࡦࡴࡶ࡭ࡴࡴࠧᒎ")) or bstack1l11ll1l111_opy_.get(bstack11l1ll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡖࡦࡴࡶ࡭ࡴࡴࠧᒏ")) or bstack1l11ll1l111_opy_.get(bstack11l1ll1_opy_ (u"ࠧࡣࡵࡷࡥࡨࡱ࠺ࡰࡲࡷ࡭ࡴࡴࡳࠨᒐ"), {}).get(bstack11l1ll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡘࡨࡶࡸ࡯࡯࡯ࠩᒑ")) or bstack1l11ll1l111_opy_.get(bstack11l1ll1_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬࠼ࡲࡴࡹ࡯࡯࡯ࡵࠪᒒ"), {}).get(bstack11l1ll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡣࡻ࡫ࡲࡴ࡫ࡲࡲࠬᒓ"))
    if browser_version and browser_version != bstack11l1ll1_opy_ (u"ࠫࡱࡧࡴࡦࡵࡷࠫᒔ") and int(browser_version.split(bstack11l1ll1_opy_ (u"ࠬ࠴ࠧᒕ"))[0]) <= 98:
      logger.warning(bstack11l1ll1_opy_ (u"ࠨࡁࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࠦࡁࡶࡶࡲࡱࡦࡺࡩࡰࡰࠣࡻ࡮ࡲ࡬ࠡࡴࡸࡲࠥࡵ࡮࡭ࡻࠣࡳࡳࠦࡃࡩࡴࡲࡱࡪࠦࡢࡳࡱࡺࡷࡪࡸࠠࡷࡧࡵࡷ࡮ࡵ࡮ࠡࡩࡵࡩࡦࡺࡥࡳࠢࡷ࡬ࡦࡴࠠ࠺࠺࠱ࠦᒖ"))
      return False
    if not options:
      bstack1lll1l11l1l_opy_ = caps.get(bstack11l1ll1_opy_ (u"ࠧࡨࡱࡲ࡫࠿ࡩࡨࡳࡱࡰࡩࡔࡶࡴࡪࡱࡱࡷࠬᒗ")) or bstack1l11ll1l111_opy_.get(bstack11l1ll1_opy_ (u"ࠨࡩࡲࡳ࡬ࡀࡣࡩࡴࡲࡱࡪࡕࡰࡵ࡫ࡲࡲࡸ࠭ᒘ"), {})
      if bstack11l1ll1_opy_ (u"ࠩ࠰࠱࡭࡫ࡡࡥ࡮ࡨࡷࡸ࠭ᒙ") in bstack1lll1l11l1l_opy_.get(bstack11l1ll1_opy_ (u"ࠪࡥࡷ࡭ࡳࠨᒚ"), []):
        logger.warn(bstack11l1ll1_opy_ (u"ࠦࡆࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠤࡆࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࠡࡹ࡬ࡰࡱࠦ࡮ࡰࡶࠣࡶࡺࡴࠠࡰࡰࠣࡰࡪ࡭ࡡࡤࡻࠣ࡬ࡪࡧࡤ࡭ࡧࡶࡷࠥࡳ࡯ࡥࡧ࠱ࠤࡘࡽࡩࡵࡥ࡫ࠤࡹࡵࠠ࡯ࡧࡺࠤ࡭࡫ࡡࡥ࡮ࡨࡷࡸࠦ࡭ࡰࡦࡨࠤࡴࡸࠠࡢࡸࡲ࡭ࡩࠦࡵࡴ࡫ࡱ࡫ࠥ࡮ࡥࡢࡦ࡯ࡩࡸࡹࠠ࡮ࡱࡧࡩ࠳ࠨᒛ"))
        return False
    return True
  except Exception as error:
    logger.debug(bstack11l1ll1_opy_ (u"ࠧࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡ࡫ࡱࠤࡻࡧ࡬ࡪࡦࡤࡸࡪࠦࡡ࠲࠳ࡼࠤࡸࡻࡰࡱࡱࡵࡸࠥࡀࠢᒜ") + str(error))
    return False
def set_capabilities(caps, config):
  try:
    bstack1llll11l1l1_opy_ = config.get(bstack11l1ll1_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࡕࡰࡵ࡫ࡲࡲࡸ࠭ᒝ"), {})
    bstack1llll11l1l1_opy_[bstack11l1ll1_opy_ (u"ࠧࡢࡷࡷ࡬࡙ࡵ࡫ࡦࡰࠪᒞ")] = os.getenv(bstack11l1ll1_opy_ (u"ࠨࡄࡖࡣࡆ࠷࠱࡚ࡡࡍ࡛࡙࠭ᒟ"))
    bstack1l11lll1l11_opy_ = json.loads(os.getenv(bstack11l1ll1_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡖࡈࡗ࡙ࡥࡁࡄࡅࡈࡗࡘࡏࡂࡊࡎࡌࡘ࡞ࡥࡃࡐࡐࡉࡍࡌ࡛ࡒࡂࡖࡌࡓࡓࡥ࡙ࡎࡎࠪᒠ"), bstack11l1ll1_opy_ (u"ࠪࡿࢂ࠭ᒡ"))).get(bstack11l1ll1_opy_ (u"ࠫࡸࡩࡡ࡯ࡰࡨࡶ࡛࡫ࡲࡴ࡫ࡲࡲࠬᒢ"))
    caps[bstack11l1ll1_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠬᒣ")] = True
    if bstack11l1ll1_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰࡀ࡯ࡱࡶ࡬ࡳࡳࡹࠧᒤ") in caps:
      caps[bstack11l1ll1_opy_ (u"ࠧࡣࡵࡷࡥࡨࡱ࠺ࡰࡲࡷ࡭ࡴࡴࡳࠨᒥ")][bstack11l1ll1_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࡐࡲࡷ࡭ࡴࡴࡳࠨᒦ")] = bstack1llll11l1l1_opy_
      caps[bstack11l1ll1_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬࠼ࡲࡴࡹ࡯࡯࡯ࡵࠪᒧ")][bstack11l1ll1_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࡒࡴࡹ࡯࡯࡯ࡵࠪᒨ")][bstack11l1ll1_opy_ (u"ࠫࡸࡩࡡ࡯ࡰࡨࡶ࡛࡫ࡲࡴ࡫ࡲࡲࠬᒩ")] = bstack1l11lll1l11_opy_
    else:
      caps[bstack11l1ll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࡓࡵࡺࡩࡰࡰࡶࠫᒪ")] = bstack1llll11l1l1_opy_
      caps[bstack11l1ll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࡔࡶࡴࡪࡱࡱࡷࠬᒫ")][bstack11l1ll1_opy_ (u"ࠧࡴࡥࡤࡲࡳ࡫ࡲࡗࡧࡵࡷ࡮ࡵ࡮ࠨᒬ")] = bstack1l11lll1l11_opy_
  except Exception as error:
    logger.debug(bstack11l1ll1_opy_ (u"ࠣࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤࡼ࡮ࡩ࡭ࡧࠣࡷࡪࡺࡴࡪࡰࡪࠤࡆࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠤࡆࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࠡࡥࡤࡴࡦࡨࡩ࡭࡫ࡷ࡭ࡪࡹ࠮ࠡࡇࡵࡶࡴࡸ࠺ࠡࠤᒭ") +  str(error))
def bstack1l1ll1l111_opy_(driver, bstack1l11lll1lll_opy_):
  try:
    setattr(driver, bstack11l1ll1_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬ࡃ࠴࠵ࡾ࡙ࡨࡰࡷ࡯ࡨࡘࡩࡡ࡯ࠩᒮ"), True)
    session = driver.session_id
    if session:
      bstack1l11lll11l1_opy_ = True
      current_url = driver.current_url
      try:
        url = urlparse(current_url)
      except Exception as e:
        bstack1l11lll11l1_opy_ = False
      bstack1l11lll11l1_opy_ = url.scheme in [bstack11l1ll1_opy_ (u"ࠥ࡬ࡹࡺࡰࠣᒯ"), bstack11l1ll1_opy_ (u"ࠦ࡭ࡺࡴࡱࡵࠥᒰ")]
      if bstack1l11lll11l1_opy_:
        if bstack1l11lll1lll_opy_:
          logger.info(bstack11l1ll1_opy_ (u"࡙ࠧࡥࡵࡷࡳࠤ࡫ࡵࡲࠡࡃࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠡࡶࡨࡷࡹ࡯࡮ࡨࠢ࡫ࡥࡸࠦࡳࡵࡣࡵࡸࡪࡪ࠮ࠡࡃࡸࡸࡴࡳࡡࡵࡧࠣࡸࡪࡹࡴࠡࡥࡤࡷࡪࠦࡥࡹࡧࡦࡹࡹ࡯࡯࡯ࠢࡺ࡭ࡱࡲࠠࡣࡧࡪ࡭ࡳࠦ࡭ࡰ࡯ࡨࡲࡹࡧࡲࡪ࡮ࡼ࠲ࠧᒱ"))
      return bstack1l11lll1lll_opy_
  except Exception as e:
    logger.error(bstack11l1ll1_opy_ (u"ࠨࡅࡹࡥࡨࡴࡹ࡯࡯࡯ࠢ࡬ࡲࠥࡹࡴࡢࡴࡷ࡭ࡳ࡭ࠠࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠠࡢࡷࡷࡳࡲࡧࡴࡪࡱࡱࠤࡸࡩࡡ࡯ࠢࡩࡳࡷࠦࡴࡩ࡫ࡶࠤࡹ࡫ࡳࡵࠢࡦࡥࡸ࡫࠺ࠡࠤᒲ") + str(e))
    return False
def bstack11111111l_opy_(driver, name, path):
  try:
    bstack1lll11l1ll1_opy_ = {
        bstack11l1ll1_opy_ (u"ࠧࡵࡪࡗࡩࡸࡺࡒࡶࡰࡘࡹ࡮ࡪࠧᒳ"): threading.current_thread().current_test_uuid,
        bstack11l1ll1_opy_ (u"ࠨࡶ࡫ࡆࡺ࡯࡬ࡥࡗࡸ࡭ࡩ࠭ᒴ"): os.environ.get(bstack11l1ll1_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡖࡈࡗ࡙ࡎࡕࡃࡡࡘ࡙ࡎࡊࠧᒵ"), bstack11l1ll1_opy_ (u"ࠪࠫᒶ")),
        bstack11l1ll1_opy_ (u"ࠫࡹ࡮ࡊࡸࡶࡗࡳࡰ࡫࡮ࠨᒷ"): os.environ.get(bstack11l1ll1_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣ࡙ࡋࡓࡕࡊࡘࡆࡤࡐࡗࡕࠩᒸ"), bstack11l1ll1_opy_ (u"࠭ࠧᒹ"))
    }
    bstack1lll11l1l1l_opy_ = bstack1ll111ll1l_opy_.bstack1lll11l1111_opy_(EVENTS.bstack11l1ll1111_opy_.value)
    logger.debug(bstack11l1ll1_opy_ (u"ࠧࡑࡧࡵࡪࡴࡸ࡭ࡪࡰࡪࠤࡸࡩࡡ࡯ࠢࡥࡩ࡫ࡵࡲࡦࠢࡶࡥࡻ࡯࡮ࡨࠢࡵࡩࡸࡻ࡬ࡵࡵࠪᒺ"))
    try:
      logger.debug(driver.execute_async_script(bstack1l1ll1111l_opy_.perform_scan, {bstack11l1ll1_opy_ (u"ࠣ࡯ࡨࡸ࡭ࡵࡤࠣᒻ"): name}))
      bstack1ll111ll1l_opy_.end(EVENTS.bstack11l1ll1111_opy_.value, bstack1lll11l1l1l_opy_ + bstack11l1ll1_opy_ (u"ࠤ࠽ࡷࡹࡧࡲࡵࠤᒼ"), bstack1lll11l1l1l_opy_ + bstack11l1ll1_opy_ (u"ࠥ࠾ࡪࡴࡤࠣᒽ"), True, None)
    except Exception as error:
      bstack1ll111ll1l_opy_.end(EVENTS.bstack11l1ll1111_opy_.value, bstack1lll11l1l1l_opy_ + bstack11l1ll1_opy_ (u"ࠦ࠿ࡹࡴࡢࡴࡷࠦᒾ"), bstack1lll11l1l1l_opy_ + bstack11l1ll1_opy_ (u"ࠧࡀࡥ࡯ࡦࠥᒿ"), False, str(error))
    bstack1lll11l1l1l_opy_ = bstack1ll111ll1l_opy_.bstack1l11ll1l1ll_opy_(EVENTS.bstack1lll1111lll_opy_.value)
    bstack1ll111ll1l_opy_.mark(bstack1lll11l1l1l_opy_ + bstack11l1ll1_opy_ (u"ࠨ࠺ࡴࡶࡤࡶࡹࠨᓀ"))
    try:
      logger.debug(driver.execute_async_script(bstack1l1ll1111l_opy_.bstack1l11ll11l11_opy_, bstack1lll11l1ll1_opy_))
      bstack1ll111ll1l_opy_.end(bstack1lll11l1l1l_opy_, bstack1lll11l1l1l_opy_ + bstack11l1ll1_opy_ (u"ࠢ࠻ࡵࡷࡥࡷࡺࠢᓁ"), bstack1lll11l1l1l_opy_ + bstack11l1ll1_opy_ (u"ࠣ࠼ࡨࡲࡩࠨᓂ"),True, None)
    except Exception as error:
      bstack1ll111ll1l_opy_.end(bstack1lll11l1l1l_opy_, bstack1lll11l1l1l_opy_ + bstack11l1ll1_opy_ (u"ࠤ࠽ࡷࡹࡧࡲࡵࠤᓃ"), bstack1lll11l1l1l_opy_ + bstack11l1ll1_opy_ (u"ࠥ࠾ࡪࡴࡤࠣᓄ"),False, str(error))
    logger.info(bstack11l1ll1_opy_ (u"ࠦࡆࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠤࡹ࡫ࡳࡵ࡫ࡱ࡫ࠥ࡬࡯ࡳࠢࡷ࡬࡮ࡹࠠࡵࡧࡶࡸࠥࡩࡡࡴࡧࠣ࡬ࡦࡹࠠࡦࡰࡧࡩࡩ࠴ࠢᓅ"))
  except Exception as bstack1lll11111ll_opy_:
    logger.error(bstack11l1ll1_opy_ (u"ࠧࡇࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠥࡸࡥࡴࡷ࡯ࡸࡸࠦࡣࡰࡷ࡯ࡨࠥࡴ࡯ࡵࠢࡥࡩࠥࡶࡲࡰࡥࡨࡷࡸ࡫ࡤࠡࡨࡲࡶࠥࡺࡨࡦࠢࡷࡩࡸࡺࠠࡤࡣࡶࡩ࠿ࠦࠢᓆ") + str(path) + bstack11l1ll1_opy_ (u"ࠨࠠࡆࡴࡵࡳࡷࠦ࠺ࠣᓇ") + str(bstack1lll11111ll_opy_))