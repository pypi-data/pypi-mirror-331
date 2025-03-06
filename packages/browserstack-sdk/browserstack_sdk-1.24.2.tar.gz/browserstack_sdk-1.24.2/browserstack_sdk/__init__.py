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
import atexit
import signal
import yaml
import socket
import datetime
import string
import random
import collections.abc
import traceback
import copy
from packaging import version
from browserstack.local import Local
from urllib.parse import urlparse
from dotenv import load_dotenv
from bstack_utils.measure import bstack1ll111ll1l_opy_
from bstack_utils.measure import measure
from bstack_utils.percy import *
from browserstack_sdk.bstack1l1l1lllll_opy_ import *
from bstack_utils.percy_sdk import PercySDK
from bstack_utils.bstack111l1ll1_opy_ import bstack1ll1l1ll11_opy_
import time
import requests
from bstack_utils.constants import EVENTS, STAGE
from bstack_utils.measure import measure
def bstack11111lll1_opy_():
  global CONFIG
  headers = {
        bstack11l1ll1_opy_ (u"ࠪࡇࡴࡴࡴࡦࡰࡷ࠱ࡹࡿࡰࡦࠩࡶ"): bstack11l1ll1_opy_ (u"ࠫࡦࡶࡰ࡭࡫ࡦࡥࡹ࡯࡯࡯࠱࡭ࡷࡴࡴࠧࡷ"),
      }
  proxies = bstack1l11l1l1_opy_(CONFIG, bstack11lll1111l_opy_)
  try:
    response = requests.get(bstack11lll1111l_opy_, headers=headers, proxies=proxies, timeout=5)
    if response.json():
      bstack11ll1111l1_opy_ = response.json()[bstack11l1ll1_opy_ (u"ࠬ࡮ࡵࡣࡵࠪࡸ")]
      logger.debug(bstack1111l1lll_opy_.format(response.json()))
      return bstack11ll1111l1_opy_
    else:
      logger.debug(bstack11ll1ll1ll_opy_.format(bstack11l1ll1_opy_ (u"ࠨࡒࡦࡵࡳࡳࡳࡹࡥࠡࡌࡖࡓࡓࠦࡰࡢࡴࡶࡩࠥ࡫ࡲࡳࡱࡵࠤࠧࡹ")))
  except Exception as e:
    logger.debug(bstack11ll1ll1ll_opy_.format(e))
def bstack1ll11l11_opy_(hub_url):
  global CONFIG
  url = bstack11l1ll1_opy_ (u"ࠢࡩࡶࡷࡴࡸࡀ࠯࠰ࠤࡺ")+  hub_url + bstack11l1ll1_opy_ (u"ࠣ࠱ࡦ࡬ࡪࡩ࡫ࠣࡻ")
  headers = {
        bstack11l1ll1_opy_ (u"ࠩࡆࡳࡳࡺࡥ࡯ࡶ࠰ࡸࡾࡶࡥࠨࡼ"): bstack11l1ll1_opy_ (u"ࠪࡥࡵࡶ࡬ࡪࡥࡤࡸ࡮ࡵ࡮࠰࡬ࡶࡳࡳ࠭ࡽ"),
      }
  proxies = bstack1l11l1l1_opy_(CONFIG, url)
  try:
    start_time = time.perf_counter()
    requests.get(url, headers=headers, proxies=proxies, timeout=5)
    latency = time.perf_counter() - start_time
    logger.debug(bstack1111ll11_opy_.format(hub_url, latency))
    return dict(hub_url=hub_url, latency=latency)
  except Exception as e:
    logger.debug(bstack1lllllll1l_opy_.format(hub_url, e))
@measure(event_name=EVENTS.bstack1l1l11l1l_opy_, stage=STAGE.bstack1l1ll1llll_opy_)
def bstack111l1l1ll_opy_():
  try:
    global bstack1l1ll11ll1_opy_
    bstack11ll1111l1_opy_ = bstack11111lll1_opy_()
    bstack1ll11l1ll1_opy_ = []
    results = []
    for bstack11lll1l11l_opy_ in bstack11ll1111l1_opy_:
      bstack1ll11l1ll1_opy_.append(bstack1l11ll1l11_opy_(target=bstack1ll11l11_opy_,args=(bstack11lll1l11l_opy_,)))
    for t in bstack1ll11l1ll1_opy_:
      t.start()
    for t in bstack1ll11l1ll1_opy_:
      results.append(t.join())
    bstack1llll1l1_opy_ = {}
    for item in results:
      hub_url = item[bstack11l1ll1_opy_ (u"ࠫ࡭ࡻࡢࡠࡷࡵࡰࠬࡾ")]
      latency = item[bstack11l1ll1_opy_ (u"ࠬࡲࡡࡵࡧࡱࡧࡾ࠭ࡿ")]
      bstack1llll1l1_opy_[hub_url] = latency
    bstack1l1l1l11l1_opy_ = min(bstack1llll1l1_opy_, key= lambda x: bstack1llll1l1_opy_[x])
    bstack1l1ll11ll1_opy_ = bstack1l1l1l11l1_opy_
    logger.debug(bstack111l1lll1_opy_.format(bstack1l1l1l11l1_opy_))
  except Exception as e:
    logger.debug(bstack1l1ll1l1ll_opy_.format(e))
from bstack_utils.messages import *
from bstack_utils import bstack1ll1ll111_opy_
from bstack_utils.constants import *
from bstack_utils.helper import bstack11ll11l1_opy_, bstack1l1111l1l_opy_, bstack1llll1ll11_opy_, bstack1ll1l1lll_opy_, \
  bstack1ll111111_opy_, \
  Notset, bstack1l1lll1l1l_opy_, \
  bstack1l11l11l1l_opy_, bstack11lllll11l_opy_, bstack11l111ll_opy_, bstack11l1ll1lll_opy_, bstack1l11ll1l1_opy_, bstack11l11lll_opy_, \
  bstack11llll111_opy_, \
  bstack11lllll1l_opy_, bstack11111ll1l_opy_, bstack1l1111l11_opy_, bstack1l1111l1_opy_, \
  bstack1l1ll11lll_opy_, bstack1ll1l11l1l_opy_, bstack111l1l111_opy_, bstack11l1ll11l_opy_
from bstack_utils.bstack11l111l1l_opy_ import bstack1ll1ll1lll_opy_, bstack111l1ll1l_opy_
from bstack_utils.bstack11ll1l11ll_opy_ import bstack1l111111ll_opy_
from bstack_utils.bstack1l111l1l_opy_ import bstack1ll1llllll_opy_, bstack11l1111l1_opy_
from bstack_utils.bstack1l1ll1111l_opy_ import bstack1l1ll1111l_opy_
from bstack_utils.proxy import bstack111l111ll_opy_, bstack1l11l1l1_opy_, bstack1l1ll1lll1_opy_, bstack1lll11lll1_opy_
from browserstack_sdk.bstack11lll111l_opy_ import *
from browserstack_sdk.bstack11l1llllll_opy_ import *
from bstack_utils.bstack1lll11ll11_opy_ import bstack11l1ll1l_opy_
from browserstack_sdk.sdk_cli.bstack1l1l11lll1_opy_ import bstack1l1l11lll1_opy_, bstack1ll1ll1l11_opy_, bstack1111l1ll1_opy_, bstack1llll11111_opy_
from browserstack_sdk.bstack1l1ll1l11_opy_ import *
import logging
import requests
from bstack_utils.constants import *
from bstack_utils.bstack1ll1ll111_opy_ import get_logger
from bstack_utils.measure import measure
logger = get_logger(__name__)
@measure(event_name=EVENTS.bstack1ll1ll1l_opy_, stage=STAGE.bstack1l1ll1llll_opy_)
def bstack1lll1111l_opy_():
    global bstack1l1ll11ll1_opy_
    try:
        bstack1ll1l111l1_opy_ = bstack1111ll1l_opy_()
        bstack1l1ll111ll_opy_(bstack1ll1l111l1_opy_)
        hub_url = bstack1ll1l111l1_opy_.get(bstack11l1ll1_opy_ (u"ࠨࡵࡳ࡮ࠥࢀ"), bstack11l1ll1_opy_ (u"ࠢࠣࢁ"))
        if hub_url.endswith(bstack11l1ll1_opy_ (u"ࠨ࠱ࡺࡨ࠴࡮ࡵࡣࠩࢂ")):
            hub_url = hub_url.rsplit(bstack11l1ll1_opy_ (u"ࠩ࠲ࡻࡩ࠵ࡨࡶࡤࠪࢃ"), 1)[0]
        if hub_url.startswith(bstack11l1ll1_opy_ (u"ࠪ࡬ࡹࡺࡰ࠻࠱࠲ࠫࢄ")):
            hub_url = hub_url[7:]
        elif hub_url.startswith(bstack11l1ll1_opy_ (u"ࠫ࡭ࡺࡴࡱࡵ࠽࠳࠴࠭ࢅ")):
            hub_url = hub_url[8:]
        bstack1l1ll11ll1_opy_ = hub_url
    except Exception as e:
        raise RuntimeError(e)
def bstack1111ll1l_opy_():
    global CONFIG
    bstack111ll1ll1_opy_ = CONFIG.get(bstack11l1ll1_opy_ (u"ࠬࡺࡵࡳࡤࡲࡗࡨࡧ࡬ࡦࡑࡳࡸ࡮ࡵ࡮ࡴࠩࢆ"), {}).get(bstack11l1ll1_opy_ (u"࠭ࡧࡳ࡫ࡧࡒࡦࡳࡥࠨࢇ"), bstack11l1ll1_opy_ (u"ࠧࡏࡑࡢࡋࡗࡏࡄࡠࡐࡄࡑࡊࡥࡐࡂࡕࡖࡉࡉ࠭࢈"))
    if not isinstance(bstack111ll1ll1_opy_, str):
        raise ValueError(bstack11l1ll1_opy_ (u"ࠣࡃࡗࡗࠥࡀࠠࡈࡴ࡬ࡨࠥࡴࡡ࡮ࡧࠣࡱࡺࡹࡴࠡࡤࡨࠤࡦࠦࡶࡢ࡮࡬ࡨࠥࡹࡴࡳ࡫ࡱ࡫ࠧࢉ"))
    try:
        bstack1ll1l111l1_opy_ = bstack1l111l1111_opy_(bstack111ll1ll1_opy_)
        return bstack1ll1l111l1_opy_
    except Exception as e:
        logger.error(bstack11l1ll1_opy_ (u"ࠤࡄࡘࡘࠦ࠺ࠡࡇࡵࡶࡴࡸࠠࡪࡰࠣ࡫ࡪࡺࡴࡪࡰࡪࠤ࡬ࡸࡩࡥࠢࡧࡩࡹࡧࡩ࡭ࡵࠣ࠾ࠥࢁࡽࠣࢊ").format(str(e)))
        return {}
def bstack1l111l1111_opy_(bstack111ll1ll1_opy_):
    global CONFIG
    try:
        if not CONFIG[bstack11l1ll1_opy_ (u"ࠪࡹࡸ࡫ࡲࡏࡣࡰࡩࠬࢋ")] or not CONFIG[bstack11l1ll1_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶࡏࡪࡿࠧࢌ")]:
            raise ValueError(bstack11l1ll1_opy_ (u"ࠧࡓࡩࡴࡵ࡬ࡲ࡬ࠦࡂࡳࡱࡺࡷࡪࡸࡓࡵࡣࡦ࡯ࠥࡻࡳࡦࡴࡱࡥࡲ࡫ࠠࡰࡴࠣࡥࡨࡩࡥࡴࡵࠣ࡯ࡪࡿࠢࢍ"))
        url = bstack11l1lllll_opy_ + bstack111ll1ll1_opy_
        auth = (CONFIG[bstack11l1ll1_opy_ (u"࠭ࡵࡴࡧࡵࡒࡦࡳࡥࠨࢎ")], CONFIG[bstack11l1ll1_opy_ (u"ࠧࡢࡥࡦࡩࡸࡹࡋࡦࡻࠪ࢏")])
        response = requests.get(url, auth=auth)
        if response.status_code == 200 and response.text:
            bstack1lll1ll11_opy_ = json.loads(response.text)
            return bstack1lll1ll11_opy_
    except ValueError as ve:
        logger.error(bstack11l1ll1_opy_ (u"ࠣࡃࡗࡗࠥࡀࠠࡆࡴࡵࡳࡷࠦࡩ࡯ࠢࡩࡩࡹࡩࡨࡪࡰࡪࠤ࡬ࡸࡩࡥࠢࡧࡩࡹࡧࡩ࡭ࡵࠣ࠾ࠥࢁࡽࠣ࢐").format(str(ve)))
        raise ValueError(ve)
    except Exception as e:
        logger.error(bstack11l1ll1_opy_ (u"ࠤࡄࡘࡘࠦ࠺ࠡࡇࡵࡶࡴࡸࠠࡪࡰࠣࡪࡪࡺࡣࡩ࡫ࡱ࡫ࠥ࡭ࡲࡪࡦࠣࡨࡪࡺࡡࡪ࡮ࡶࠤ࠿ࠦࡻࡾࠤ࢑").format(str(e)))
        raise RuntimeError(e)
    return {}
def bstack1l1ll111ll_opy_(bstack1111ll1l1_opy_):
    global CONFIG
    if bstack11l1ll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡎࡲࡧࡦࡲࠧ࢒") not in CONFIG or str(CONFIG[bstack11l1ll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡏࡳࡨࡧ࡬ࠨ࢓")]).lower() == bstack11l1ll1_opy_ (u"ࠬ࡬ࡡ࡭ࡵࡨࠫ࢔"):
        CONFIG[bstack11l1ll1_opy_ (u"࠭࡬ࡰࡥࡤࡰࠬ࢕")] = False
    elif bstack11l1ll1_opy_ (u"ࠧࡪࡵࡗࡶ࡮ࡧ࡬ࡈࡴ࡬ࡨࠬ࢖") in bstack1111ll1l1_opy_:
        bstack111l1l11_opy_ = CONFIG.get(bstack11l1ll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡕࡷࡥࡨࡱࡌࡰࡥࡤࡰࡔࡶࡴࡪࡱࡱࡷࠬࢗ"), {})
        logger.debug(bstack11l1ll1_opy_ (u"ࠤࡄࡘࡘࠦ࠺ࠡࡇࡻ࡭ࡸࡺࡩ࡯ࡩࠣࡰࡴࡩࡡ࡭ࠢࡲࡴࡹ࡯࡯࡯ࡵ࠽ࠤࠪࡹࠢ࢘"), bstack111l1l11_opy_)
        bstack11111lll_opy_ = bstack1111ll1l1_opy_.get(bstack11l1ll1_opy_ (u"ࠥࡧࡺࡹࡴࡰ࡯ࡕࡩࡵ࡫ࡡࡵࡧࡵࡷ࢙ࠧ"), [])
        bstack1l1ll1l11l_opy_ = bstack11l1ll1_opy_ (u"ࠦ࠱ࠨ࢚").join(bstack11111lll_opy_)
        logger.debug(bstack11l1ll1_opy_ (u"ࠧࡇࡔࡔࠢ࠽ࠤࡈࡻࡳࡵࡱࡰࠤࡷ࡫ࡰࡦࡣࡷࡩࡷࠦࡳࡵࡴ࡬ࡲ࡬ࡀࠠࠦࡵ࢛ࠥ"), bstack1l1ll1l11l_opy_)
        bstack1lll1llll1_opy_ = {
            bstack11l1ll1_opy_ (u"ࠨ࡬ࡰࡥࡤࡰࡎࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠣ࢜"): bstack11l1ll1_opy_ (u"ࠢࡢࡶࡶ࠱ࡷ࡫ࡰࡦࡣࡷࡩࡷࠨ࢝"),
            bstack11l1ll1_opy_ (u"ࠣࡨࡲࡶࡨ࡫ࡌࡰࡥࡤࡰࠧ࢞"): bstack11l1ll1_opy_ (u"ࠤࡷࡶࡺ࡫ࠢ࢟"),
            bstack11l1ll1_opy_ (u"ࠥࡧࡺࡹࡴࡰ࡯࠰ࡶࡪࡶࡥࡢࡶࡨࡶࠧࢠ"): bstack1l1ll1l11l_opy_
        }
        bstack111l1l11_opy_.update(bstack1lll1llll1_opy_)
        logger.debug(bstack11l1ll1_opy_ (u"ࠦࡆ࡚ࡓࠡ࠼࡙ࠣࡵࡪࡡࡵࡧࡧࠤࡱࡵࡣࡢ࡮ࠣࡳࡵࡺࡩࡰࡰࡶ࠾ࠥࠫࡳࠣࢡ"), bstack111l1l11_opy_)
        CONFIG[bstack11l1ll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷ࡙ࡴࡢࡥ࡮ࡐࡴࡩࡡ࡭ࡑࡳࡸ࡮ࡵ࡮ࡴࠩࢢ")] = bstack111l1l11_opy_
        logger.debug(bstack11l1ll1_opy_ (u"ࠨࡁࡕࡕࠣ࠾ࠥࡌࡩ࡯ࡣ࡯ࠤࡈࡕࡎࡇࡋࡊ࠾ࠥࠫࡳࠣࢣ"), CONFIG)
def bstack11l11l11_opy_():
    bstack1ll1l111l1_opy_ = bstack1111ll1l_opy_()
    if not bstack1ll1l111l1_opy_[bstack11l1ll1_opy_ (u"ࠧࡱ࡮ࡤࡽࡼࡸࡩࡨࡪࡷ࡙ࡷࡲࠧࢤ")]:
      raise ValueError(bstack11l1ll1_opy_ (u"ࠣࡲ࡯ࡥࡾࡽࡲࡪࡩ࡫ࡸ࡚ࡸ࡬ࠡ࡫ࡶࠤࡲ࡯ࡳࡴ࡫ࡱ࡫ࠥ࡬ࡲࡰ࡯ࠣ࡫ࡷ࡯ࡤࠡࡦࡨࡸࡦ࡯࡬ࡴ࠰ࠥࢥ"))
    return bstack1ll1l111l1_opy_[bstack11l1ll1_opy_ (u"ࠩࡳࡰࡦࡿࡷࡳ࡫ࡪ࡬ࡹ࡛ࡲ࡭ࠩࢦ")] + bstack11l1ll1_opy_ (u"ࠪࡃࡨࡧࡰࡴ࠿ࠪࢧ")
@measure(event_name=EVENTS.bstack1ll1lll11l_opy_, stage=STAGE.bstack1l1ll1llll_opy_)
def bstack1l1lll11ll_opy_() -> list:
    global CONFIG
    result = []
    if CONFIG:
        auth = (CONFIG[bstack11l1ll1_opy_ (u"ࠫࡺࡹࡥࡳࡐࡤࡱࡪ࠭ࢨ")], CONFIG[bstack11l1ll1_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷࡐ࡫ࡹࠨࢩ")])
        url = bstack11ll1ll11_opy_
        logger.debug(bstack11l1ll1_opy_ (u"ࠨࡁࡵࡶࡨࡱࡵࡺࡩ࡯ࡩࠣࡸࡴࠦࡦࡦࡶࡦ࡬ࠥࡨࡵࡪ࡮ࡧࡷࠥ࡬ࡲࡰ࡯ࠣࡆࡷࡵࡷࡴࡧࡵࡗࡹࡧࡣ࡬ࠢࡗࡹࡷࡨ࡯ࡔࡥࡤࡰࡪࠦࡁࡑࡋࠥࢪ"))
        try:
            response = requests.get(url, auth=auth, headers={bstack11l1ll1_opy_ (u"ࠢࡄࡱࡱࡸࡪࡴࡴ࠮ࡖࡼࡴࡪࠨࢫ"): bstack11l1ll1_opy_ (u"ࠣࡣࡳࡴࡱ࡯ࡣࡢࡶ࡬ࡳࡳ࠵ࡪࡴࡱࡱࠦࢬ")})
            if response.status_code == 200:
                bstack1l1l1llll_opy_ = json.loads(response.text)
                bstack111l11ll1_opy_ = bstack1l1l1llll_opy_.get(bstack11l1ll1_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡴࠩࢭ"), [])
                if bstack111l11ll1_opy_:
                    bstack1ll1l1lll1_opy_ = bstack111l11ll1_opy_[0]
                    build_hashed_id = bstack1ll1l1lll1_opy_.get(bstack11l1ll1_opy_ (u"ࠪ࡬ࡦࡹࡨࡦࡦࡢ࡭ࡩ࠭ࢮ"))
                    bstack1l1ll111l1_opy_ = bstack1ll1l11l11_opy_ + build_hashed_id
                    result.extend([build_hashed_id, bstack1l1ll111l1_opy_])
                    logger.info(bstack11llll1lll_opy_.format(bstack1l1ll111l1_opy_))
                    bstack11l1lll11l_opy_ = CONFIG[bstack11l1ll1_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡑࡥࡲ࡫ࠧࢯ")]
                    if bstack11l1ll1_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠧࢰ") in CONFIG:
                      bstack11l1lll11l_opy_ += bstack11l1ll1_opy_ (u"࠭ࠠࠨࢱ") + CONFIG[bstack11l1ll1_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡏࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࠩࢲ")]
                    if bstack11l1lll11l_opy_ != bstack1ll1l1lll1_opy_.get(bstack11l1ll1_opy_ (u"ࠨࡰࡤࡱࡪ࠭ࢳ")):
                      logger.debug(bstack11ll1ll111_opy_.format(bstack1ll1l1lll1_opy_.get(bstack11l1ll1_opy_ (u"ࠩࡱࡥࡲ࡫ࠧࢴ")), bstack11l1lll11l_opy_))
                    return result
                else:
                    logger.debug(bstack11l1ll1_opy_ (u"ࠥࡅ࡙࡙ࠠ࠻ࠢࡑࡳࠥࡨࡵࡪ࡮ࡧࡷࠥ࡬࡯ࡶࡰࡧࠤ࡮ࡴࠠࡵࡪࡨࠤࡷ࡫ࡳࡱࡱࡱࡷࡪ࠴ࠢࢵ"))
            else:
                logger.debug(bstack11l1ll1_opy_ (u"ࠦࡆ࡚ࡓࠡ࠼ࠣࡊࡦ࡯࡬ࡦࡦࠣࡸࡴࠦࡦࡦࡶࡦ࡬ࠥࡨࡵࡪ࡮ࡧࡷ࠳ࠨࢶ"))
        except Exception as e:
            logger.error(bstack11l1ll1_opy_ (u"ࠧࡇࡔࡔࠢ࠽ࠤࡊࡸࡲࡰࡴࠣ࡭ࡳࠦࡧࡦࡶࡷ࡭ࡳ࡭ࠠࡣࡷ࡬ࡰࡩࡹࠠ࠻ࠢࡾࢁࠧࢷ").format(str(e)))
    else:
        logger.debug(bstack11l1ll1_opy_ (u"ࠨࡁࡕࡕࠣ࠾ࠥࡉࡏࡏࡈࡌࡋࠥ࡯ࡳࠡࡰࡲࡸࠥࡹࡥࡵ࠰࡙ࠣࡳࡧࡢ࡭ࡧࠣࡸࡴࠦࡦࡦࡶࡦ࡬ࠥࡨࡵࡪ࡮ࡧࡷ࠳ࠨࢸ"))
    return [None, None]
import bstack_utils.bstack1lll1lll1_opy_ as bstack1l1l1lll11_opy_
import bstack_utils.bstack1l1l11ll1l_opy_ as bstack111l1111l_opy_
from browserstack_sdk.sdk_cli.cli import cli
if os.getenv(bstack11l1ll1_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡃࡍࡋࡢࡌࡔࡕࡋࡔࠩࢹ")):
  cli.bstack1l111111l_opy_()
else:
  os.environ[bstack11l1ll1_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡄࡎࡌࡣࡍࡕࡏࡌࡕࠪࢺ")] = bstack11l1ll1_opy_ (u"ࠩࡷࡶࡺ࡫ࠧࢻ")
bstack111111ll_opy_ = bstack11l1ll1_opy_ (u"ࠪࠤࠥ࠵ࠪࠡ࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࠥ࠰࠯࡝ࡰࠣࠤ࡮࡬ࠨࡱࡣࡪࡩࠥࡃ࠽࠾ࠢࡹࡳ࡮ࡪࠠ࠱ࠫࠣࡿࡡࡴࠠࠡࠢࡷࡶࡾࢁ࡜࡯ࠢࡦࡳࡳࡹࡴࠡࡨࡶࠤࡂࠦࡲࡦࡳࡸ࡭ࡷ࡫ࠨ࡝ࠩࡩࡷࡡ࠭ࠩ࠼࡞ࡱࠤࠥࠦࠠࠡࡨࡶ࠲ࡦࡶࡰࡦࡰࡧࡊ࡮ࡲࡥࡔࡻࡱࡧ࠭ࡨࡳࡵࡣࡦ࡯ࡤࡶࡡࡵࡪ࠯ࠤࡏ࡙ࡏࡏ࠰ࡶࡸࡷ࡯࡮ࡨ࡫ࡩࡽ࠭ࡶ࡟ࡪࡰࡧࡩࡽ࠯ࠠࠬࠢࠥ࠾ࠧࠦࠫࠡࡌࡖࡓࡓ࠴ࡳࡵࡴ࡬ࡲ࡬࡯ࡦࡺࠪࡍࡗࡔࡔ࠮ࡱࡣࡵࡷࡪ࠮ࠨࡢࡹࡤ࡭ࡹࠦ࡮ࡦࡹࡓࡥ࡬࡫࠲࠯ࡧࡹࡥࡱࡻࡡࡵࡧࠫࠦ࠭࠯ࠠ࠾ࡀࠣࡿࢂࠨࠬࠡ࡞ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡡࡨࡼࡪࡩࡵࡵࡱࡵ࠾ࠥࢁࠢࡢࡥࡷ࡭ࡴࡴࠢ࠻ࠢࠥ࡫ࡪࡺࡓࡦࡵࡶ࡭ࡴࡴࡄࡦࡶࡤ࡭ࡱࡹࠢࡾ࡞ࠪ࠭࠮࠯࡛ࠣࡪࡤࡷ࡭࡫ࡤࡠ࡫ࡧࠦࡢ࠯ࠠࠬࠢࠥ࠰ࡡࡢ࡮ࠣࠫ࡟ࡲࠥࠦࠠࠡࡿࡦࡥࡹࡩࡨࠩࡧࡻ࠭ࢀࡢ࡮ࠡࠢࠣࠤࢂࡢ࡮ࠡࠢࢀࡠࡳࠦࠠ࠰ࠬࠣࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃࠠࠫ࠱ࠪࢼ")
bstack1lllllll11_opy_ = bstack11l1ll1_opy_ (u"ࠫࡡࡴ࠯ࠫࠢࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࠦࠪ࠰࡞ࡱࡧࡴࡴࡳࡵࠢࡥࡷࡹࡧࡣ࡬ࡡࡳࡥࡹ࡮ࠠ࠾ࠢࡳࡶࡴࡩࡥࡴࡵ࠱ࡥࡷ࡭ࡶ࡜ࡲࡵࡳࡨ࡫ࡳࡴ࠰ࡤࡶ࡬ࡼ࠮࡭ࡧࡱ࡫ࡹ࡮ࠠ࠮ࠢ࠶ࡡࡡࡴࡣࡰࡰࡶࡸࠥࡨࡳࡵࡣࡦ࡯ࡤࡩࡡࡱࡵࠣࡁࠥࡶࡲࡰࡥࡨࡷࡸ࠴ࡡࡳࡩࡹ࡟ࡵࡸ࡯ࡤࡧࡶࡷ࠳ࡧࡲࡨࡸ࠱ࡰࡪࡴࡧࡵࡪࠣ࠱ࠥ࠷࡝࡝ࡰࡦࡳࡳࡹࡴࠡࡲࡢ࡭ࡳࡪࡥࡹࠢࡀࠤࡵࡸ࡯ࡤࡧࡶࡷ࠳ࡧࡲࡨࡸ࡞ࡴࡷࡵࡣࡦࡵࡶ࠲ࡦࡸࡧࡷ࠰࡯ࡩࡳ࡭ࡴࡩࠢ࠰ࠤ࠷ࡣ࡜࡯ࡲࡵࡳࡨ࡫ࡳࡴ࠰ࡤࡶ࡬ࡼࠠ࠾ࠢࡳࡶࡴࡩࡥࡴࡵ࠱ࡥࡷ࡭ࡶ࠯ࡵ࡯࡭ࡨ࡫ࠨ࠱࠮ࠣࡴࡷࡵࡣࡦࡵࡶ࠲ࡦࡸࡧࡷ࠰࡯ࡩࡳ࡭ࡴࡩࠢ࠰ࠤ࠸࠯࡜࡯ࡥࡲࡲࡸࡺࠠࡪ࡯ࡳࡳࡷࡺ࡟ࡱ࡮ࡤࡽࡼࡸࡩࡨࡪࡷ࠸ࡤࡨࡳࡵࡣࡦ࡯ࠥࡃࠠࡳࡧࡴࡹ࡮ࡸࡥࠩࠤࡳࡰࡦࡿࡷࡳ࡫ࡪ࡬ࡹࠨࠩ࠼࡞ࡱ࡭ࡲࡶ࡯ࡳࡶࡢࡴࡱࡧࡹࡸࡴ࡬࡫࡭ࡺ࠴ࡠࡤࡶࡸࡦࡩ࡫࠯ࡥ࡫ࡶࡴࡳࡩࡶ࡯࠱ࡰࡦࡻ࡮ࡤࡪࠣࡁࠥࡧࡳࡺࡰࡦࠤ࠭ࡲࡡࡶࡰࡦ࡬ࡔࡶࡴࡪࡱࡱࡷ࠮ࠦ࠽࠿ࠢࡾࡠࡳࡲࡥࡵࠢࡦࡥࡵࡹ࠻࡝ࡰࡷࡶࡾࠦࡻ࡝ࡰࡦࡥࡵࡹࠠ࠾ࠢࡍࡗࡔࡔ࠮ࡱࡣࡵࡷࡪ࠮ࡢࡴࡶࡤࡧࡰࡥࡣࡢࡲࡶ࠭ࡡࡴࠠࠡࡿࠣࡧࡦࡺࡣࡩࠪࡨࡼ࠮ࠦࡻ࡝ࡰࠣࠤࠥࠦࡽ࡝ࡰࠣࠤࡷ࡫ࡴࡶࡴࡱࠤࡦࡽࡡࡪࡶࠣ࡭ࡲࡶ࡯ࡳࡶࡢࡴࡱࡧࡹࡸࡴ࡬࡫࡭ࡺ࠴ࡠࡤࡶࡸࡦࡩ࡫࠯ࡥ࡫ࡶࡴࡳࡩࡶ࡯࠱ࡧࡴࡴ࡮ࡦࡥࡷࠬࢀࡢ࡮ࠡࠢࠣࠤࡼࡹࡅ࡯ࡦࡳࡳ࡮ࡴࡴ࠻ࠢࡣࡻࡸࡹ࠺࠰࠱ࡦࡨࡵ࠴ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡩ࡯࡮࠱ࡳࡰࡦࡿࡷࡳ࡫ࡪ࡬ࡹࡅࡣࡢࡲࡶࡁࠩࢁࡥ࡯ࡥࡲࡨࡪ࡛ࡒࡊࡅࡲࡱࡵࡵ࡮ࡦࡰࡷࠬࡏ࡙ࡏࡏ࠰ࡶࡸࡷ࡯࡮ࡨ࡫ࡩࡽ࠭ࡩࡡࡱࡵࠬ࠭ࢂࡦࠬ࡝ࡰࠣࠤࠥࠦ࠮࠯࠰࡯ࡥࡺࡴࡣࡩࡑࡳࡸ࡮ࡵ࡮ࡴ࡞ࡱࠤࠥࢃࠩ࡝ࡰࢀࡠࡳ࠵ࠪࠡ࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࠥ࠰࠯࡝ࡰࠪࢽ")
from ._version import __version__
bstack1l1l1111_opy_ = None
CONFIG = {}
bstack1llll1ll1_opy_ = {}
bstack1ll11l11ll_opy_ = {}
bstack1l1l1ll1_opy_ = None
bstack1l111111_opy_ = None
bstack1lll1l11l_opy_ = None
bstack1ll1ll1ll_opy_ = -1
bstack1lll1l1ll_opy_ = 0
bstack1111llll_opy_ = bstack11l1l1lll_opy_
bstack111lll1l1_opy_ = 1
bstack11ll1ll1l1_opy_ = False
bstack1lll1l111_opy_ = False
bstack111111ll1_opy_ = bstack11l1ll1_opy_ (u"ࠬ࠭ࢾ")
bstack1ll1lll1ll_opy_ = bstack11l1ll1_opy_ (u"࠭ࠧࢿ")
bstack11ll11ll1_opy_ = False
bstack1111l1111_opy_ = True
bstack11ll11ll_opy_ = bstack11l1ll1_opy_ (u"ࠧࠨࣀ")
bstack1l1ll1l1l1_opy_ = []
bstack1l1ll11ll1_opy_ = bstack11l1ll1_opy_ (u"ࠨࠩࣁ")
bstack1111111ll_opy_ = False
bstack11ll111l1_opy_ = None
bstack1l1llll11l_opy_ = None
bstack1l111lllll_opy_ = None
bstack1l11lll1l1_opy_ = -1
bstack1lll11l1ll_opy_ = os.path.join(os.path.expanduser(bstack11l1ll1_opy_ (u"ࠩࢁࠫࣂ")), bstack11l1ll1_opy_ (u"ࠪ࠲ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࠪࣃ"), bstack11l1ll1_opy_ (u"ࠫ࠳ࡸ࡯ࡣࡱࡷ࠱ࡷ࡫ࡰࡰࡴࡷ࠱࡭࡫࡬ࡱࡧࡵ࠲࡯ࡹ࡯࡯ࠩࣄ"))
bstack1ll111l1ll_opy_ = 0
bstack11llllll1_opy_ = 0
bstack11l11111_opy_ = []
bstack1l11ll111l_opy_ = []
bstack1111lll1l_opy_ = []
bstack111lll11_opy_ = []
bstack1l111l1l11_opy_ = bstack11l1ll1_opy_ (u"ࠬ࠭ࣅ")
bstack1lll1ll1l1_opy_ = bstack11l1ll1_opy_ (u"࠭ࠧࣆ")
bstack1lll11lll_opy_ = False
bstack1111l1l1l_opy_ = False
bstack1llll111l1_opy_ = {}
bstack11lll111ll_opy_ = None
bstack1llll11l_opy_ = None
bstack1l11ll11_opy_ = None
bstack11l11l1l1_opy_ = None
bstack11ll11lll_opy_ = None
bstack1ll11ll1l_opy_ = None
bstack1lllll1l11_opy_ = None
bstack11ll111l1l_opy_ = None
bstack1l1l1l1111_opy_ = None
bstack111lllll_opy_ = None
bstack111ll1lll_opy_ = None
bstack1llll111ll_opy_ = None
bstack1l1llll1ll_opy_ = None
bstack1lllll11ll_opy_ = None
bstack1lllll1ll1_opy_ = None
bstack11l1lllll1_opy_ = None
bstack1l1l111l1_opy_ = None
bstack111111l11_opy_ = None
bstack1lll1lll11_opy_ = None
bstack11l111l1_opy_ = None
bstack1llllllll_opy_ = None
bstack1l1ll1l1_opy_ = None
bstack11ll1l1lll_opy_ = False
bstack11ll11ll1l_opy_ = bstack11l1ll1_opy_ (u"ࠢࠣࣇ")
logger = bstack1ll1ll111_opy_.get_logger(__name__, bstack1111llll_opy_)
bstack1ll1l11l1_opy_ = Config.bstack1l111l1ll1_opy_()
percy = bstack111l1l11l_opy_()
bstack111ll11ll_opy_ = bstack1ll1l1ll11_opy_()
bstack1l11111lll_opy_ = bstack1l1ll1l11_opy_()
def bstack1l11ll11l_opy_():
  global CONFIG
  global bstack1lll11lll_opy_
  global bstack1ll1l11l1_opy_
  bstack11ll11111_opy_ = bstack1111llll1_opy_(CONFIG)
  if bstack1ll111111_opy_(CONFIG):
    if (bstack11l1ll1_opy_ (u"ࠨࡵ࡮࡭ࡵ࡙ࡥࡴࡵ࡬ࡳࡳࡔࡡ࡮ࡧࠪࣈ") in bstack11ll11111_opy_ and str(bstack11ll11111_opy_[bstack11l1ll1_opy_ (u"ࠩࡶ࡯࡮ࡶࡓࡦࡵࡶ࡭ࡴࡴࡎࡢ࡯ࡨࠫࣉ")]).lower() == bstack11l1ll1_opy_ (u"ࠪࡸࡷࡻࡥࠨ࣊")):
      bstack1lll11lll_opy_ = True
    bstack1ll1l11l1_opy_.bstack1l1l11l111_opy_(bstack11ll11111_opy_.get(bstack11l1ll1_opy_ (u"ࠫࡸࡱࡩࡱࡕࡨࡷࡸ࡯࡯࡯ࡕࡷࡥࡹࡻࡳࠨ࣋"), False))
  else:
    bstack1lll11lll_opy_ = True
    bstack1ll1l11l1_opy_.bstack1l1l11l111_opy_(True)
def bstack1l1ll1ll1l_opy_():
  from appium.version import version as appium_version
  return version.parse(appium_version)
def bstack1ll111111l_opy_():
  from selenium import webdriver
  return version.parse(webdriver.__version__)
def bstack11l1ll1l11_opy_():
  args = sys.argv
  for i in range(len(args)):
    if bstack11l1ll1_opy_ (u"ࠧ࠳࠭ࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡩ࡯࡯ࡨ࡬࡫࡫࡯࡬ࡦࠤ࣌") == args[i].lower() or bstack11l1ll1_opy_ (u"ࠨ࠭࠮ࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡤࡱࡱࡪ࡮࡭ࠢ࣍") == args[i].lower():
      path = args[i + 1]
      sys.argv.remove(args[i])
      sys.argv.remove(path)
      global bstack11ll11ll_opy_
      bstack11ll11ll_opy_ += bstack11l1ll1_opy_ (u"ࠧ࠮࠯ࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡄࡱࡱࡪ࡮࡭ࡆࡪ࡮ࡨࠤࠬ࣎") + path
      return path
  return None
bstack1l11ll1lll_opy_ = re.compile(bstack11l1ll1_opy_ (u"ࡳࠤ࠱࠮ࡄࡢࠤࡼࠪ࠱࠮ࡄ࠯ࡽ࠯ࠬࡂ࣏ࠦ"))
def bstack11llll11l1_opy_(loader, node):
  value = loader.construct_scalar(node)
  for group in bstack1l11ll1lll_opy_.findall(value):
    if group is not None and os.environ.get(group) is not None:
      value = value.replace(bstack11l1ll1_opy_ (u"ࠤࠧࡿ࣐ࠧ") + group + bstack11l1ll1_opy_ (u"ࠥࢁ࣑ࠧ"), os.environ.get(group))
  return value
def bstack1l11ll11ll_opy_():
  bstack11l1ll1ll_opy_ = bstack11l1ll1l11_opy_()
  if bstack11l1ll1ll_opy_ and os.path.exists(os.path.abspath(bstack11l1ll1ll_opy_)):
    fileName = bstack11l1ll1ll_opy_
  if bstack11l1ll1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡇࡔࡔࡆࡊࡉࡢࡊࡎࡒࡅࠨ࣒") in os.environ and os.path.exists(
          os.path.abspath(os.environ[bstack11l1ll1_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡈࡕࡎࡇࡋࡊࡣࡋࡏࡌࡆ࣓ࠩ")])) and not bstack11l1ll1_opy_ (u"࠭ࡦࡪ࡮ࡨࡒࡦࡳࡥࠨࣔ") in locals():
    fileName = os.environ[bstack11l1ll1_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡃࡐࡐࡉࡍࡌࡥࡆࡊࡎࡈࠫࣕ")]
  if bstack11l1ll1_opy_ (u"ࠨࡨ࡬ࡰࡪࡔࡡ࡮ࡧࠪࣖ") in locals():
    bstack11l1l11_opy_ = os.path.abspath(fileName)
  else:
    bstack11l1l11_opy_ = bstack11l1ll1_opy_ (u"ࠩࠪࣗ")
  bstack11llll11l_opy_ = os.getcwd()
  bstack1lll111l1_opy_ = bstack11l1ll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡼࡱࡱ࠭ࣘ")
  bstack11l1l11ll_opy_ = bstack11l1ll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡽࡦࡳ࡬ࠨࣙ")
  while (not os.path.exists(bstack11l1l11_opy_)) and bstack11llll11l_opy_ != bstack11l1ll1_opy_ (u"ࠧࠨࣚ"):
    bstack11l1l11_opy_ = os.path.join(bstack11llll11l_opy_, bstack1lll111l1_opy_)
    if not os.path.exists(bstack11l1l11_opy_):
      bstack11l1l11_opy_ = os.path.join(bstack11llll11l_opy_, bstack11l1l11ll_opy_)
    if bstack11llll11l_opy_ != os.path.dirname(bstack11llll11l_opy_):
      bstack11llll11l_opy_ = os.path.dirname(bstack11llll11l_opy_)
    else:
      bstack11llll11l_opy_ = bstack11l1ll1_opy_ (u"ࠨࠢࣛ")
  return bstack11l1l11_opy_ if os.path.exists(bstack11l1l11_opy_) else None
def bstack1ll1l1l1l1_opy_():
  bstack11l1l11_opy_ = bstack1l11ll11ll_opy_()
  if not os.path.exists(bstack11l1l11_opy_):
    bstack1l11l1lll_opy_(
      bstack1l1l111l1l_opy_.format(os.getcwd()))
  try:
    with open(bstack11l1l11_opy_, bstack11l1ll1_opy_ (u"ࠧࡳࠩࣜ")) as stream:
      yaml.add_implicit_resolver(bstack11l1ll1_opy_ (u"ࠣࠣࡳࡥࡹ࡮ࡥࡹࠤࣝ"), bstack1l11ll1lll_opy_)
      yaml.add_constructor(bstack11l1ll1_opy_ (u"ࠤࠤࡴࡦࡺࡨࡦࡺࠥࣞ"), bstack11llll11l1_opy_)
      config = yaml.load(stream, yaml.FullLoader)
      return config
  except:
    with open(bstack11l1l11_opy_, bstack11l1ll1_opy_ (u"ࠪࡶࠬࣟ")) as stream:
      try:
        config = yaml.safe_load(stream)
        return config
      except yaml.YAMLError as exc:
        bstack1l11l1lll_opy_(bstack1ll1111l11_opy_.format(str(exc)))
def bstack1ll11l1l1_opy_(config):
  bstack1ll1111ll1_opy_ = bstack1lll11l11l_opy_(config)
  for option in list(bstack1ll1111ll1_opy_):
    if option.lower() in bstack1ll1l111ll_opy_ and option != bstack1ll1l111ll_opy_[option.lower()]:
      bstack1ll1111ll1_opy_[bstack1ll1l111ll_opy_[option.lower()]] = bstack1ll1111ll1_opy_[option]
      del bstack1ll1111ll1_opy_[option]
  return config
def bstack1l11lll11l_opy_():
  global bstack1ll11l11ll_opy_
  for key, bstack11lll11lll_opy_ in bstack111ll1l1l_opy_.items():
    if isinstance(bstack11lll11lll_opy_, list):
      for var in bstack11lll11lll_opy_:
        if var in os.environ and os.environ[var] and str(os.environ[var]).strip():
          bstack1ll11l11ll_opy_[key] = os.environ[var]
          break
    elif bstack11lll11lll_opy_ in os.environ and os.environ[bstack11lll11lll_opy_] and str(os.environ[bstack11lll11lll_opy_]).strip():
      bstack1ll11l11ll_opy_[key] = os.environ[bstack11lll11lll_opy_]
  if bstack11l1ll1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡐࡔࡉࡁࡍࡡࡌࡈࡊࡔࡔࡊࡈࡌࡉࡗ࠭࣠") in os.environ:
    bstack1ll11l11ll_opy_[bstack11l1ll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷ࡙ࡴࡢࡥ࡮ࡐࡴࡩࡡ࡭ࡑࡳࡸ࡮ࡵ࡮ࡴࠩ࣡")] = {}
    bstack1ll11l11ll_opy_[bstack11l1ll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡓࡵࡣࡦ࡯ࡑࡵࡣࡢ࡮ࡒࡴࡹ࡯࡯࡯ࡵࠪ࣢")][bstack11l1ll1_opy_ (u"ࠧ࡭ࡱࡦࡥࡱࡏࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࣣࠩ")] = os.environ[bstack11l1ll1_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡍࡑࡆࡅࡑࡥࡉࡅࡇࡑࡘࡎࡌࡉࡆࡔࠪࣤ")]
def bstack11ll11l11_opy_():
  global bstack1llll1ll1_opy_
  global bstack11ll11ll_opy_
  for idx, val in enumerate(sys.argv):
    if idx < len(sys.argv) and bstack11l1ll1_opy_ (u"ࠩ࠰࠱ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡰࡴࡩࡡ࡭ࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬࣥ").lower() == val.lower():
      bstack1llll1ll1_opy_[bstack11l1ll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡗࡹࡧࡣ࡬ࡎࡲࡧࡦࡲࡏࡱࡶ࡬ࡳࡳࡹࣦࠧ")] = {}
      bstack1llll1ll1_opy_[bstack11l1ll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡘࡺࡡࡤ࡭ࡏࡳࡨࡧ࡬ࡐࡲࡷ࡭ࡴࡴࡳࠨࣧ")][bstack11l1ll1_opy_ (u"ࠬࡲ࡯ࡤࡣ࡯ࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠧࣨ")] = sys.argv[idx + 1]
      del sys.argv[idx:idx + 2]
      break
  for key, bstack1lllll1l1_opy_ in bstack1l1l1l1ll1_opy_.items():
    if isinstance(bstack1lllll1l1_opy_, list):
      for idx, val in enumerate(sys.argv):
        for var in bstack1lllll1l1_opy_:
          if idx < len(sys.argv) and bstack11l1ll1_opy_ (u"࠭࠭࠮ࣩࠩ") + var.lower() == val.lower() and not key in bstack1llll1ll1_opy_:
            bstack1llll1ll1_opy_[key] = sys.argv[idx + 1]
            bstack11ll11ll_opy_ += bstack11l1ll1_opy_ (u"ࠧࠡ࠯࠰ࠫ࣪") + var + bstack11l1ll1_opy_ (u"ࠨࠢࠪ࣫") + sys.argv[idx + 1]
            del sys.argv[idx:idx + 2]
            break
    else:
      for idx, val in enumerate(sys.argv):
        if idx < len(sys.argv) and bstack11l1ll1_opy_ (u"ࠩ࠰࠱ࠬ࣬") + bstack1lllll1l1_opy_.lower() == val.lower() and not key in bstack1llll1ll1_opy_:
          bstack1llll1ll1_opy_[key] = sys.argv[idx + 1]
          bstack11ll11ll_opy_ += bstack11l1ll1_opy_ (u"ࠪࠤ࠲࠳࣭ࠧ") + bstack1lllll1l1_opy_ + bstack11l1ll1_opy_ (u"࣮ࠫࠥ࠭") + sys.argv[idx + 1]
          del sys.argv[idx:idx + 2]
def bstack1l11l11ll_opy_(config):
  bstack1llll111_opy_ = config.keys()
  for bstack1l111111l1_opy_, bstack11ll1111ll_opy_ in bstack1111lll11_opy_.items():
    if bstack11ll1111ll_opy_ in bstack1llll111_opy_:
      config[bstack1l111111l1_opy_] = config[bstack11ll1111ll_opy_]
      del config[bstack11ll1111ll_opy_]
  for bstack1l111111l1_opy_, bstack11ll1111ll_opy_ in bstack1ll111ll1_opy_.items():
    if isinstance(bstack11ll1111ll_opy_, list):
      for bstack1lllll11l1_opy_ in bstack11ll1111ll_opy_:
        if bstack1lllll11l1_opy_ in bstack1llll111_opy_:
          config[bstack1l111111l1_opy_] = config[bstack1lllll11l1_opy_]
          del config[bstack1lllll11l1_opy_]
          break
    elif bstack11ll1111ll_opy_ in bstack1llll111_opy_:
      config[bstack1l111111l1_opy_] = config[bstack11ll1111ll_opy_]
      del config[bstack11ll1111ll_opy_]
  for bstack1lllll11l1_opy_ in list(config):
    for bstack1l1l1ll1l_opy_ in bstack1ll11ll1_opy_:
      if bstack1lllll11l1_opy_.lower() == bstack1l1l1ll1l_opy_.lower() and bstack1lllll11l1_opy_ != bstack1l1l1ll1l_opy_:
        config[bstack1l1l1ll1l_opy_] = config[bstack1lllll11l1_opy_]
        del config[bstack1lllll11l1_opy_]
  bstack1l11111ll_opy_ = [{}]
  if not config.get(bstack11l1ll1_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡳࠨ࣯")):
    config[bstack11l1ll1_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࣰࠩ")] = [{}]
  bstack1l11111ll_opy_ = config[bstack11l1ll1_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵࣱࠪ")]
  for platform in bstack1l11111ll_opy_:
    for bstack1lllll11l1_opy_ in list(platform):
      for bstack1l1l1ll1l_opy_ in bstack1ll11ll1_opy_:
        if bstack1lllll11l1_opy_.lower() == bstack1l1l1ll1l_opy_.lower() and bstack1lllll11l1_opy_ != bstack1l1l1ll1l_opy_:
          platform[bstack1l1l1ll1l_opy_] = platform[bstack1lllll11l1_opy_]
          del platform[bstack1lllll11l1_opy_]
  for bstack1l111111l1_opy_, bstack11ll1111ll_opy_ in bstack1ll111ll1_opy_.items():
    for platform in bstack1l11111ll_opy_:
      if isinstance(bstack11ll1111ll_opy_, list):
        for bstack1lllll11l1_opy_ in bstack11ll1111ll_opy_:
          if bstack1lllll11l1_opy_ in platform:
            platform[bstack1l111111l1_opy_] = platform[bstack1lllll11l1_opy_]
            del platform[bstack1lllll11l1_opy_]
            break
      elif bstack11ll1111ll_opy_ in platform:
        platform[bstack1l111111l1_opy_] = platform[bstack11ll1111ll_opy_]
        del platform[bstack11ll1111ll_opy_]
  for bstack11ll111ll1_opy_ in bstack1lll1l1l1_opy_:
    if bstack11ll111ll1_opy_ in config:
      if not bstack1lll1l1l1_opy_[bstack11ll111ll1_opy_] in config:
        config[bstack1lll1l1l1_opy_[bstack11ll111ll1_opy_]] = {}
      config[bstack1lll1l1l1_opy_[bstack11ll111ll1_opy_]].update(config[bstack11ll111ll1_opy_])
      del config[bstack11ll111ll1_opy_]
  for platform in bstack1l11111ll_opy_:
    for bstack11ll111ll1_opy_ in bstack1lll1l1l1_opy_:
      if bstack11ll111ll1_opy_ in list(platform):
        if not bstack1lll1l1l1_opy_[bstack11ll111ll1_opy_] in platform:
          platform[bstack1lll1l1l1_opy_[bstack11ll111ll1_opy_]] = {}
        platform[bstack1lll1l1l1_opy_[bstack11ll111ll1_opy_]].update(platform[bstack11ll111ll1_opy_])
        del platform[bstack11ll111ll1_opy_]
  config = bstack1ll11l1l1_opy_(config)
  return config
def bstack1l1ll11l1l_opy_(config):
  global bstack1ll1lll1ll_opy_
  bstack11lllll1ll_opy_ = False
  if bstack11l1ll1_opy_ (u"ࠨࡶࡸࡶࡧࡵࡓࡤࡣ࡯ࡩࣲࠬ") in config and str(config[bstack11l1ll1_opy_ (u"ࠩࡷࡹࡷࡨ࡯ࡔࡥࡤࡰࡪ࠭ࣳ")]).lower() != bstack11l1ll1_opy_ (u"ࠪࡪࡦࡲࡳࡦࠩࣴ"):
    if bstack11l1ll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡏࡳࡨࡧ࡬ࠨࣵ") not in config or str(config[bstack11l1ll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡐࡴࡩࡡ࡭ࣶࠩ")]).lower() == bstack11l1ll1_opy_ (u"࠭ࡦࡢ࡮ࡶࡩࠬࣷ"):
      config[bstack11l1ll1_opy_ (u"ࠧ࡭ࡱࡦࡥࡱ࠭ࣸ")] = False
    else:
      bstack1ll1l111l1_opy_ = bstack1111ll1l_opy_()
      if bstack11l1ll1_opy_ (u"ࠨ࡫ࡶࡘࡷ࡯ࡡ࡭ࡉࡵ࡭ࡩࣹ࠭") in bstack1ll1l111l1_opy_:
        if not bstack11l1ll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡖࡸࡦࡩ࡫ࡍࡱࡦࡥࡱࡕࡰࡵ࡫ࡲࡲࡸࣺ࠭") in config:
          config[bstack11l1ll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡗࡹࡧࡣ࡬ࡎࡲࡧࡦࡲࡏࡱࡶ࡬ࡳࡳࡹࠧࣻ")] = {}
        config[bstack11l1ll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡘࡺࡡࡤ࡭ࡏࡳࡨࡧ࡬ࡐࡲࡷ࡭ࡴࡴࡳࠨࣼ")][bstack11l1ll1_opy_ (u"ࠬࡲ࡯ࡤࡣ࡯ࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠧࣽ")] = bstack11l1ll1_opy_ (u"࠭ࡡࡵࡵ࠰ࡶࡪࡶࡥࡢࡶࡨࡶࠬࣾ")
        bstack11lllll1ll_opy_ = True
        bstack1ll1lll1ll_opy_ = config[bstack11l1ll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡔࡶࡤࡧࡰࡒ࡯ࡤࡣ࡯ࡓࡵࡺࡩࡰࡰࡶࠫࣿ")].get(bstack11l1ll1_opy_ (u"ࠨ࡮ࡲࡧࡦࡲࡉࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࠪऀ"))
  if bstack1ll111111_opy_(config) and bstack11l1ll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡍࡱࡦࡥࡱ࠭ँ") in config and str(config[bstack11l1ll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡎࡲࡧࡦࡲࠧं")]).lower() != bstack11l1ll1_opy_ (u"ࠫ࡫ࡧ࡬ࡴࡧࠪः") and not bstack11lllll1ll_opy_:
    if not bstack11l1ll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷ࡙ࡴࡢࡥ࡮ࡐࡴࡩࡡ࡭ࡑࡳࡸ࡮ࡵ࡮ࡴࠩऄ") in config:
      config[bstack11l1ll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡓࡵࡣࡦ࡯ࡑࡵࡣࡢ࡮ࡒࡴࡹ࡯࡯࡯ࡵࠪअ")] = {}
    if not config[bstack11l1ll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡔࡶࡤࡧࡰࡒ࡯ࡤࡣ࡯ࡓࡵࡺࡩࡰࡰࡶࠫआ")].get(bstack11l1ll1_opy_ (u"ࠨࡵ࡮࡭ࡵࡈࡩ࡯ࡣࡵࡽࡎࡴࡩࡵ࡫ࡤࡰ࡮ࡹࡡࡵ࡫ࡲࡲࠬइ")) and not bstack11l1ll1_opy_ (u"ࠩ࡯ࡳࡨࡧ࡬ࡊࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫई") in config[bstack11l1ll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡗࡹࡧࡣ࡬ࡎࡲࡧࡦࡲࡏࡱࡶ࡬ࡳࡳࡹࠧउ")]:
      bstack1ll1l1ll_opy_ = datetime.datetime.now()
      bstack11l11ll11_opy_ = bstack1ll1l1ll_opy_.strftime(bstack11l1ll1_opy_ (u"ࠫࠪࡪ࡟ࠦࡤࡢࠩࡍࠫࡍࠨऊ"))
      hostname = socket.gethostname()
      bstack1l1lll1l_opy_ = bstack11l1ll1_opy_ (u"ࠬ࠭ऋ").join(random.choices(string.ascii_lowercase + string.digits, k=4))
      identifier = bstack11l1ll1_opy_ (u"࠭ࡻࡾࡡࡾࢁࡤࢁࡽࠨऌ").format(bstack11l11ll11_opy_, hostname, bstack1l1lll1l_opy_)
      config[bstack11l1ll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡔࡶࡤࡧࡰࡒ࡯ࡤࡣ࡯ࡓࡵࡺࡩࡰࡰࡶࠫऍ")][bstack11l1ll1_opy_ (u"ࠨ࡮ࡲࡧࡦࡲࡉࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࠪऎ")] = identifier
    bstack1ll1lll1ll_opy_ = config[bstack11l1ll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡖࡸࡦࡩ࡫ࡍࡱࡦࡥࡱࡕࡰࡵ࡫ࡲࡲࡸ࠭ए")].get(bstack11l1ll1_opy_ (u"ࠪࡰࡴࡩࡡ࡭ࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬऐ"))
  return config
def bstack1lll11111l_opy_():
  bstack1l111lll1l_opy_ =  bstack11l1ll1lll_opy_()[bstack11l1ll1_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡢࡲࡺࡳࡢࡦࡴࠪऑ")]
  return bstack1l111lll1l_opy_ if bstack1l111lll1l_opy_ else -1
def bstack111111111_opy_(bstack1l111lll1l_opy_):
  global CONFIG
  if not bstack11l1ll1_opy_ (u"ࠬࠪࡻࡃࡗࡌࡐࡉࡥࡎࡖࡏࡅࡉࡗࢃࠧऒ") in CONFIG[bstack11l1ll1_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡎࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠨओ")]:
    return
  CONFIG[bstack11l1ll1_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡏࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࠩऔ")] = CONFIG[bstack11l1ll1_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡉࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࠪक")].replace(
    bstack11l1ll1_opy_ (u"ࠩࠧࡿࡇ࡛ࡉࡍࡆࡢࡒ࡚ࡓࡂࡆࡔࢀࠫख"),
    str(bstack1l111lll1l_opy_)
  )
def bstack1l111l1ll_opy_():
  global CONFIG
  if not bstack11l1ll1_opy_ (u"ࠪࠨࢀࡊࡁࡕࡇࡢࡘࡎࡓࡅࡾࠩग") in CONFIG[bstack11l1ll1_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭घ")]:
    return
  bstack1ll1l1ll_opy_ = datetime.datetime.now()
  bstack11l11ll11_opy_ = bstack1ll1l1ll_opy_.strftime(bstack11l1ll1_opy_ (u"ࠬࠫࡤ࠮ࠧࡥ࠱ࠪࡎ࠺ࠦࡏࠪङ"))
  CONFIG[bstack11l1ll1_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡎࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠨच")] = CONFIG[bstack11l1ll1_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡏࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࠩछ")].replace(
    bstack11l1ll1_opy_ (u"ࠨࠦࡾࡈࡆ࡚ࡅࡠࡖࡌࡑࡊࢃࠧज"),
    bstack11l11ll11_opy_
  )
def bstack1l11ll11l1_opy_():
  global CONFIG
  if bstack11l1ll1_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡊࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫझ") in CONFIG and not bool(CONFIG[bstack11l1ll1_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬञ")]):
    del CONFIG[bstack11l1ll1_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭ट")]
    return
  if not bstack11l1ll1_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠧठ") in CONFIG:
    CONFIG[bstack11l1ll1_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡎࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠨड")] = bstack11l1ll1_opy_ (u"ࠧࠤࠦࡾࡆ࡚ࡏࡌࡅࡡࡑ࡙ࡒࡈࡅࡓࡿࠪढ")
  if bstack11l1ll1_opy_ (u"ࠨࠦࡾࡈࡆ࡚ࡅࡠࡖࡌࡑࡊࢃࠧण") in CONFIG[bstack11l1ll1_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡊࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫत")]:
    bstack1l111l1ll_opy_()
    os.environ[bstack11l1ll1_opy_ (u"ࠪࡆࡘ࡚ࡁࡄࡍࡢࡇࡔࡓࡂࡊࡐࡈࡈࡤࡈࡕࡊࡎࡇࡣࡎࡊࠧथ")] = CONFIG[bstack11l1ll1_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭द")]
  if not bstack11l1ll1_opy_ (u"ࠬࠪࡻࡃࡗࡌࡐࡉࡥࡎࡖࡏࡅࡉࡗࢃࠧध") in CONFIG[bstack11l1ll1_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡎࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠨन")]:
    return
  bstack1l111lll1l_opy_ = bstack11l1ll1_opy_ (u"ࠧࠨऩ")
  bstack11lllllll1_opy_ = bstack1lll11111l_opy_()
  if bstack11lllllll1_opy_ != -1:
    bstack1l111lll1l_opy_ = bstack11l1ll1_opy_ (u"ࠨࡅࡌࠤࠬप") + str(bstack11lllllll1_opy_)
  if bstack1l111lll1l_opy_ == bstack11l1ll1_opy_ (u"ࠩࠪफ"):
    bstack1ll1llll11_opy_ = bstack1l1l1l111l_opy_(CONFIG[bstack11l1ll1_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡐࡤࡱࡪ࠭ब")])
    if bstack1ll1llll11_opy_ != -1:
      bstack1l111lll1l_opy_ = str(bstack1ll1llll11_opy_)
  if bstack1l111lll1l_opy_:
    bstack111111111_opy_(bstack1l111lll1l_opy_)
    os.environ[bstack11l1ll1_opy_ (u"ࠫࡇ࡙ࡔࡂࡅࡎࡣࡈࡕࡍࡃࡋࡑࡉࡉࡥࡂࡖࡋࡏࡈࡤࡏࡄࠨभ")] = CONFIG[bstack11l1ll1_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠧम")]
def bstack11lll11l1_opy_(bstack1l11111l11_opy_, bstack1llll1l111_opy_, path):
  bstack1l1111ll_opy_ = {
    bstack11l1ll1_opy_ (u"࠭ࡩࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࠪय"): bstack1llll1l111_opy_
  }
  if os.path.exists(path):
    bstack11lll11l_opy_ = json.load(open(path, bstack11l1ll1_opy_ (u"ࠧࡳࡤࠪर")))
  else:
    bstack11lll11l_opy_ = {}
  bstack11lll11l_opy_[bstack1l11111l11_opy_] = bstack1l1111ll_opy_
  with open(path, bstack11l1ll1_opy_ (u"ࠣࡹ࠮ࠦऱ")) as outfile:
    json.dump(bstack11lll11l_opy_, outfile)
def bstack1l1l1l111l_opy_(bstack1l11111l11_opy_):
  bstack1l11111l11_opy_ = str(bstack1l11111l11_opy_)
  bstack1l11l1llll_opy_ = os.path.join(os.path.expanduser(bstack11l1ll1_opy_ (u"ࠩࢁࠫल")), bstack11l1ll1_opy_ (u"ࠪ࠲ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࠪळ"))
  try:
    if not os.path.exists(bstack1l11l1llll_opy_):
      os.makedirs(bstack1l11l1llll_opy_)
    file_path = os.path.join(os.path.expanduser(bstack11l1ll1_opy_ (u"ࠫࢃ࠭ऴ")), bstack11l1ll1_opy_ (u"ࠬ࠴ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࠬव"), bstack11l1ll1_opy_ (u"࠭࠮ࡣࡷ࡬ࡰࡩ࠳࡮ࡢ࡯ࡨ࠱ࡨࡧࡣࡩࡧ࠱࡮ࡸࡵ࡮ࠨश"))
    if not os.path.isfile(file_path):
      with open(file_path, bstack11l1ll1_opy_ (u"ࠧࡸࠩष")):
        pass
      with open(file_path, bstack11l1ll1_opy_ (u"ࠣࡹ࠮ࠦस")) as outfile:
        json.dump({}, outfile)
    with open(file_path, bstack11l1ll1_opy_ (u"ࠩࡵࠫह")) as bstack1ll1llll_opy_:
      bstack11lll1l1l1_opy_ = json.load(bstack1ll1llll_opy_)
    if bstack1l11111l11_opy_ in bstack11lll1l1l1_opy_:
      bstack11ll1l1l11_opy_ = bstack11lll1l1l1_opy_[bstack1l11111l11_opy_][bstack11l1ll1_opy_ (u"ࠪ࡭ࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠧऺ")]
      bstack11ll11l1l1_opy_ = int(bstack11ll1l1l11_opy_) + 1
      bstack11lll11l1_opy_(bstack1l11111l11_opy_, bstack11ll11l1l1_opy_, file_path)
      return bstack11ll11l1l1_opy_
    else:
      bstack11lll11l1_opy_(bstack1l11111l11_opy_, 1, file_path)
      return 1
  except Exception as e:
    logger.warn(bstack1l1l11ll_opy_.format(str(e)))
    return -1
def bstack11ll11111l_opy_(config):
  if not config[bstack11l1ll1_opy_ (u"ࠫࡺࡹࡥࡳࡐࡤࡱࡪ࠭ऻ")] or not config[bstack11l1ll1_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷࡐ࡫ࡹࠨ़")]:
    return True
  else:
    return False
def bstack111llllll_opy_(config, index=0):
  global bstack11ll11ll1_opy_
  bstack1lll111111_opy_ = {}
  caps = bstack1ll1lll11_opy_ + bstack1l11ll1ll1_opy_
  if config.get(bstack11l1ll1_opy_ (u"࠭ࡴࡶࡴࡥࡳࡘࡩࡡ࡭ࡧࠪऽ"), False):
    bstack1lll111111_opy_[bstack11l1ll1_opy_ (u"ࠧࡵࡷࡵࡦࡴࡹࡣࡢ࡮ࡨࠫा")] = True
    bstack1lll111111_opy_[bstack11l1ll1_opy_ (u"ࠨࡶࡸࡶࡧࡵࡓࡤࡣ࡯ࡩࡔࡶࡴࡪࡱࡱࡷࠬि")] = config.get(bstack11l1ll1_opy_ (u"ࠩࡷࡹࡷࡨ࡯ࡔࡥࡤࡰࡪࡕࡰࡵ࡫ࡲࡲࡸ࠭ी"), {})
  if bstack11ll11ll1_opy_:
    caps += bstack1ll1ll1ll1_opy_
  for key in config:
    if key in caps + [bstack11l1ll1_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭ु")]:
      continue
    bstack1lll111111_opy_[key] = config[key]
  if bstack11l1ll1_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧू") in config:
    for bstack1ll11l11l1_opy_ in config[bstack11l1ll1_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡳࠨृ")][index]:
      if bstack1ll11l11l1_opy_ in caps:
        continue
      bstack1lll111111_opy_[bstack1ll11l11l1_opy_] = config[bstack11l1ll1_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠩॄ")][index][bstack1ll11l11l1_opy_]
  bstack1lll111111_opy_[bstack11l1ll1_opy_ (u"ࠧࡩࡱࡶࡸࡓࡧ࡭ࡦࠩॅ")] = socket.gethostname()
  if bstack11l1ll1_opy_ (u"ࠨࡸࡨࡶࡸ࡯࡯࡯ࠩॆ") in bstack1lll111111_opy_:
    del (bstack1lll111111_opy_[bstack11l1ll1_opy_ (u"ࠩࡹࡩࡷࡹࡩࡰࡰࠪे")])
  return bstack1lll111111_opy_
def bstack111lll111_opy_(config):
  global bstack11ll11ll1_opy_
  bstack1ll1l11l_opy_ = {}
  caps = bstack1l11ll1ll1_opy_
  if bstack11ll11ll1_opy_:
    caps += bstack1ll1ll1ll1_opy_
  for key in caps:
    if key in config:
      bstack1ll1l11l_opy_[key] = config[key]
  return bstack1ll1l11l_opy_
def bstack11llll1l1l_opy_(bstack1lll111111_opy_, bstack1ll1l11l_opy_):
  bstack1llll1l1l1_opy_ = {}
  for key in bstack1lll111111_opy_.keys():
    if key in bstack1111lll11_opy_:
      bstack1llll1l1l1_opy_[bstack1111lll11_opy_[key]] = bstack1lll111111_opy_[key]
    else:
      bstack1llll1l1l1_opy_[key] = bstack1lll111111_opy_[key]
  for key in bstack1ll1l11l_opy_:
    if key in bstack1111lll11_opy_:
      bstack1llll1l1l1_opy_[bstack1111lll11_opy_[key]] = bstack1ll1l11l_opy_[key]
    else:
      bstack1llll1l1l1_opy_[key] = bstack1ll1l11l_opy_[key]
  return bstack1llll1l1l1_opy_
def bstack1l11llll1l_opy_(config, index=0):
  global bstack11ll11ll1_opy_
  caps = {}
  config = copy.deepcopy(config)
  bstack11l1l1llll_opy_ = bstack11ll11l1_opy_(bstack1l111lll11_opy_, config, logger)
  bstack1ll1l11l_opy_ = bstack111lll111_opy_(config)
  bstack1111ll111_opy_ = bstack1l11ll1ll1_opy_
  bstack1111ll111_opy_ += bstack1l11111ll1_opy_
  bstack1ll1l11l_opy_ = update(bstack1ll1l11l_opy_, bstack11l1l1llll_opy_)
  if bstack11ll11ll1_opy_:
    bstack1111ll111_opy_ += bstack1ll1ll1ll1_opy_
  if bstack11l1ll1_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭ै") in config:
    if bstack11l1ll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡓࡧ࡭ࡦࠩॉ") in config[bstack11l1ll1_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡳࠨॊ")][index]:
      caps[bstack11l1ll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡎࡢ࡯ࡨࠫो")] = config[bstack11l1ll1_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵࠪौ")][index][bstack11l1ll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡐࡤࡱࡪ्࠭")]
    if bstack11l1ll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴ࡙ࡩࡷࡹࡩࡰࡰࠪॎ") in config[bstack11l1ll1_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭ॏ")][index]:
      caps[bstack11l1ll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶ࡛࡫ࡲࡴ࡫ࡲࡲࠬॐ")] = str(config[bstack11l1ll1_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡳࠨ॑")][index][bstack11l1ll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡖࡦࡴࡶ࡭ࡴࡴ॒ࠧ")])
    bstack1lll1ll1_opy_ = bstack11ll11l1_opy_(bstack1l111lll11_opy_, config[bstack11l1ll1_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵࠪ॓")][index], logger)
    bstack1111ll111_opy_ += list(bstack1lll1ll1_opy_.keys())
    for bstack1111l11l_opy_ in bstack1111ll111_opy_:
      if bstack1111l11l_opy_ in config[bstack11l1ll1_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫ॔")][index]:
        if bstack1111l11l_opy_ == bstack11l1ll1_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰ࡚ࡪࡸࡳࡪࡱࡱࠫॕ"):
          try:
            bstack1lll1ll1_opy_[bstack1111l11l_opy_] = str(config[bstack11l1ll1_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭ॖ")][index][bstack1111l11l_opy_] * 1.0)
          except:
            bstack1lll1ll1_opy_[bstack1111l11l_opy_] = str(config[bstack11l1ll1_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧॗ")][index][bstack1111l11l_opy_])
        else:
          bstack1lll1ll1_opy_[bstack1111l11l_opy_] = config[bstack11l1ll1_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡳࠨक़")][index][bstack1111l11l_opy_]
        del (config[bstack11l1ll1_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠩख़")][index][bstack1111l11l_opy_])
    bstack1ll1l11l_opy_ = update(bstack1ll1l11l_opy_, bstack1lll1ll1_opy_)
  bstack1lll111111_opy_ = bstack111llllll_opy_(config, index)
  for bstack1lllll11l1_opy_ in bstack1l11ll1ll1_opy_ + list(bstack11l1l1llll_opy_.keys()):
    if bstack1lllll11l1_opy_ in bstack1lll111111_opy_:
      bstack1ll1l11l_opy_[bstack1lllll11l1_opy_] = bstack1lll111111_opy_[bstack1lllll11l1_opy_]
      del (bstack1lll111111_opy_[bstack1lllll11l1_opy_])
  if bstack1l1lll1l1l_opy_(config):
    bstack1lll111111_opy_[bstack11l1ll1_opy_ (u"ࠧࡶࡵࡨ࡛࠸ࡉࠧग़")] = True
    caps.update(bstack1ll1l11l_opy_)
    caps[bstack11l1ll1_opy_ (u"ࠨࡤࡶࡸࡦࡩ࡫࠻ࡱࡳࡸ࡮ࡵ࡮ࡴࠩज़")] = bstack1lll111111_opy_
  else:
    bstack1lll111111_opy_[bstack11l1ll1_opy_ (u"ࠩࡸࡷࡪ࡝࠳ࡄࠩड़")] = False
    caps.update(bstack11llll1l1l_opy_(bstack1lll111111_opy_, bstack1ll1l11l_opy_))
    if bstack11l1ll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡒࡦࡳࡥࠨढ़") in caps:
      caps[bstack11l1ll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࠬफ़")] = caps[bstack11l1ll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡔࡡ࡮ࡧࠪय़")]
      del (caps[bstack11l1ll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡎࡢ࡯ࡨࠫॠ")])
    if bstack11l1ll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡗࡧࡵࡷ࡮ࡵ࡮ࠨॡ") in caps:
      caps[bstack11l1ll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡡࡹࡩࡷࡹࡩࡰࡰࠪॢ")] = caps[bstack11l1ll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴ࡙ࡩࡷࡹࡩࡰࡰࠪॣ")]
      del (caps[bstack11l1ll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵ࡚ࡪࡸࡳࡪࡱࡱࠫ।")])
  return caps
def bstack1l11111l1_opy_():
  global bstack1l1ll11ll1_opy_
  global CONFIG
  if bstack1ll111111l_opy_() <= version.parse(bstack11l1ll1_opy_ (u"ࠫ࠸࠴࠱࠴࠰࠳ࠫ॥")):
    if bstack1l1ll11ll1_opy_ != bstack11l1ll1_opy_ (u"ࠬ࠭०"):
      return bstack11l1ll1_opy_ (u"ࠨࡨࡵࡶࡳ࠾࠴࠵ࠢ१") + bstack1l1ll11ll1_opy_ + bstack11l1ll1_opy_ (u"ࠢ࠻࠺࠳࠳ࡼࡪ࠯ࡩࡷࡥࠦ२")
    return bstack1ll11l1l1l_opy_
  if bstack1l1ll11ll1_opy_ != bstack11l1ll1_opy_ (u"ࠨࠩ३"):
    return bstack11l1ll1_opy_ (u"ࠤ࡫ࡸࡹࡶࡳ࠻࠱࠲ࠦ४") + bstack1l1ll11ll1_opy_ + bstack11l1ll1_opy_ (u"ࠥ࠳ࡼࡪ࠯ࡩࡷࡥࠦ५")
  return bstack11l1l1l1_opy_
def bstack111l111l1_opy_(options):
  return hasattr(options, bstack11l1ll1_opy_ (u"ࠫࡸ࡫ࡴࡠࡥࡤࡴࡦࡨࡩ࡭࡫ࡷࡽࠬ६"))
def update(d, u):
  for k, v in u.items():
    if isinstance(v, collections.abc.Mapping):
      d[k] = update(d.get(k, {}), v)
    else:
      if isinstance(v, list):
        d[k] = d.get(k, []) + v
      else:
        d[k] = v
  return d
def bstack111lllll1_opy_(options, bstack1111111l_opy_):
  for bstack1llllll1ll_opy_ in bstack1111111l_opy_:
    if bstack1llllll1ll_opy_ in [bstack11l1ll1_opy_ (u"ࠬࡧࡲࡨࡵࠪ७"), bstack11l1ll1_opy_ (u"࠭ࡥࡹࡶࡨࡲࡸ࡯࡯࡯ࡵࠪ८")]:
      continue
    if bstack1llllll1ll_opy_ in options._experimental_options:
      options._experimental_options[bstack1llllll1ll_opy_] = update(options._experimental_options[bstack1llllll1ll_opy_],
                                                         bstack1111111l_opy_[bstack1llllll1ll_opy_])
    else:
      options.add_experimental_option(bstack1llllll1ll_opy_, bstack1111111l_opy_[bstack1llllll1ll_opy_])
  if bstack11l1ll1_opy_ (u"ࠧࡢࡴࡪࡷࠬ९") in bstack1111111l_opy_:
    for arg in bstack1111111l_opy_[bstack11l1ll1_opy_ (u"ࠨࡣࡵ࡫ࡸ࠭॰")]:
      options.add_argument(arg)
    del (bstack1111111l_opy_[bstack11l1ll1_opy_ (u"ࠩࡤࡶ࡬ࡹࠧॱ")])
  if bstack11l1ll1_opy_ (u"ࠪࡩࡽࡺࡥ࡯ࡵ࡬ࡳࡳࡹࠧॲ") in bstack1111111l_opy_:
    for ext in bstack1111111l_opy_[bstack11l1ll1_opy_ (u"ࠫࡪࡾࡴࡦࡰࡶ࡭ࡴࡴࡳࠨॳ")]:
      try:
        options.add_extension(ext)
      except OSError:
        options.add_encoded_extension(ext)
    del (bstack1111111l_opy_[bstack11l1ll1_opy_ (u"ࠬ࡫ࡸࡵࡧࡱࡷ࡮ࡵ࡮ࡴࠩॴ")])
def bstack11ll11l11l_opy_(options, bstack1ll11l1l11_opy_):
  if bstack11l1ll1_opy_ (u"࠭ࡰࡳࡧࡩࡷࠬॵ") in bstack1ll11l1l11_opy_:
    for bstack11l1lll1l1_opy_ in bstack1ll11l1l11_opy_[bstack11l1ll1_opy_ (u"ࠧࡱࡴࡨࡪࡸ࠭ॶ")]:
      if bstack11l1lll1l1_opy_ in options._preferences:
        options._preferences[bstack11l1lll1l1_opy_] = update(options._preferences[bstack11l1lll1l1_opy_], bstack1ll11l1l11_opy_[bstack11l1ll1_opy_ (u"ࠨࡲࡵࡩ࡫ࡹࠧॷ")][bstack11l1lll1l1_opy_])
      else:
        options.set_preference(bstack11l1lll1l1_opy_, bstack1ll11l1l11_opy_[bstack11l1ll1_opy_ (u"ࠩࡳࡶࡪ࡬ࡳࠨॸ")][bstack11l1lll1l1_opy_])
  if bstack11l1ll1_opy_ (u"ࠪࡥࡷ࡭ࡳࠨॹ") in bstack1ll11l1l11_opy_:
    for arg in bstack1ll11l1l11_opy_[bstack11l1ll1_opy_ (u"ࠫࡦࡸࡧࡴࠩॺ")]:
      options.add_argument(arg)
def bstack1l1lllll_opy_(options, bstack11ll1l1l1l_opy_):
  if bstack11l1ll1_opy_ (u"ࠬࡽࡥࡣࡸ࡬ࡩࡼ࠭ॻ") in bstack11ll1l1l1l_opy_:
    options.use_webview(bool(bstack11ll1l1l1l_opy_[bstack11l1ll1_opy_ (u"࠭ࡷࡦࡤࡹ࡭ࡪࡽࠧॼ")]))
  bstack111lllll1_opy_(options, bstack11ll1l1l1l_opy_)
def bstack111lll11l_opy_(options, bstack1l1ll11111_opy_):
  for bstack111ll1ll_opy_ in bstack1l1ll11111_opy_:
    if bstack111ll1ll_opy_ in [bstack11l1ll1_opy_ (u"ࠧࡵࡧࡦ࡬ࡳࡵ࡬ࡰࡩࡼࡔࡷ࡫ࡶࡪࡧࡺࠫॽ"), bstack11l1ll1_opy_ (u"ࠨࡣࡵ࡫ࡸ࠭ॾ")]:
      continue
    options.set_capability(bstack111ll1ll_opy_, bstack1l1ll11111_opy_[bstack111ll1ll_opy_])
  if bstack11l1ll1_opy_ (u"ࠩࡤࡶ࡬ࡹࠧॿ") in bstack1l1ll11111_opy_:
    for arg in bstack1l1ll11111_opy_[bstack11l1ll1_opy_ (u"ࠪࡥࡷ࡭ࡳࠨঀ")]:
      options.add_argument(arg)
  if bstack11l1ll1_opy_ (u"ࠫࡹ࡫ࡣࡩࡰࡲࡰࡴ࡭ࡹࡑࡴࡨࡺ࡮࡫ࡷࠨঁ") in bstack1l1ll11111_opy_:
    options.bstack1lll11l111_opy_(bool(bstack1l1ll11111_opy_[bstack11l1ll1_opy_ (u"ࠬࡺࡥࡤࡪࡱࡳࡱࡵࡧࡺࡒࡵࡩࡻ࡯ࡥࡸࠩং")]))
def bstack1lll11111_opy_(options, bstack11l1llll1_opy_):
  for bstack1lllll1ll_opy_ in bstack11l1llll1_opy_:
    if bstack1lllll1ll_opy_ in [bstack11l1ll1_opy_ (u"࠭ࡡࡥࡦ࡬ࡸ࡮ࡵ࡮ࡢ࡮ࡒࡴࡹ࡯࡯࡯ࡵࠪঃ"), bstack11l1ll1_opy_ (u"ࠧࡢࡴࡪࡷࠬ঄")]:
      continue
    options._options[bstack1lllll1ll_opy_] = bstack11l1llll1_opy_[bstack1lllll1ll_opy_]
  if bstack11l1ll1_opy_ (u"ࠨࡣࡧࡨ࡮ࡺࡩࡰࡰࡤࡰࡔࡶࡴࡪࡱࡱࡷࠬঅ") in bstack11l1llll1_opy_:
    for bstack1111l111l_opy_ in bstack11l1llll1_opy_[bstack11l1ll1_opy_ (u"ࠩࡤࡨࡩ࡯ࡴࡪࡱࡱࡥࡱࡕࡰࡵ࡫ࡲࡲࡸ࠭আ")]:
      options.bstack111l11ll_opy_(
        bstack1111l111l_opy_, bstack11l1llll1_opy_[bstack11l1ll1_opy_ (u"ࠪࡥࡩࡪࡩࡵ࡫ࡲࡲࡦࡲࡏࡱࡶ࡬ࡳࡳࡹࠧই")][bstack1111l111l_opy_])
  if bstack11l1ll1_opy_ (u"ࠫࡦࡸࡧࡴࠩঈ") in bstack11l1llll1_opy_:
    for arg in bstack11l1llll1_opy_[bstack11l1ll1_opy_ (u"ࠬࡧࡲࡨࡵࠪউ")]:
      options.add_argument(arg)
def bstack1l11llllll_opy_(options, caps):
  if not hasattr(options, bstack11l1ll1_opy_ (u"࠭ࡋࡆ࡛ࠪঊ")):
    return
  if options.KEY == bstack11l1ll1_opy_ (u"ࠧࡨࡱࡲ࡫࠿ࡩࡨࡳࡱࡰࡩࡔࡶࡴࡪࡱࡱࡷࠬঋ") and options.KEY in caps:
    bstack111lllll1_opy_(options, caps[bstack11l1ll1_opy_ (u"ࠨࡩࡲࡳ࡬ࡀࡣࡩࡴࡲࡱࡪࡕࡰࡵ࡫ࡲࡲࡸ࠭ঌ")])
  elif options.KEY == bstack11l1ll1_opy_ (u"ࠩࡰࡳࡿࡀࡦࡪࡴࡨࡪࡴࡾࡏࡱࡶ࡬ࡳࡳࡹࠧ঍") and options.KEY in caps:
    bstack11ll11l11l_opy_(options, caps[bstack11l1ll1_opy_ (u"ࠪࡱࡴࢀ࠺ࡧ࡫ࡵࡩ࡫ࡵࡸࡐࡲࡷ࡭ࡴࡴࡳࠨ঎")])
  elif options.KEY == bstack11l1ll1_opy_ (u"ࠫࡸࡧࡦࡢࡴ࡬࠲ࡴࡶࡴࡪࡱࡱࡷࠬএ") and options.KEY in caps:
    bstack111lll11l_opy_(options, caps[bstack11l1ll1_opy_ (u"ࠬࡹࡡࡧࡣࡵ࡭࠳ࡵࡰࡵ࡫ࡲࡲࡸ࠭ঐ")])
  elif options.KEY == bstack11l1ll1_opy_ (u"࠭࡭ࡴ࠼ࡨࡨ࡬࡫ࡏࡱࡶ࡬ࡳࡳࡹࠧ঑") and options.KEY in caps:
    bstack1l1lllll_opy_(options, caps[bstack11l1ll1_opy_ (u"ࠧ࡮ࡵ࠽ࡩࡩ࡭ࡥࡐࡲࡷ࡭ࡴࡴࡳࠨ঒")])
  elif options.KEY == bstack11l1ll1_opy_ (u"ࠨࡵࡨ࠾࡮࡫ࡏࡱࡶ࡬ࡳࡳࡹࠧও") and options.KEY in caps:
    bstack1lll11111_opy_(options, caps[bstack11l1ll1_opy_ (u"ࠩࡶࡩ࠿࡯ࡥࡐࡲࡷ࡭ࡴࡴࡳࠨঔ")])
def bstack11l1ll1l1_opy_(caps):
  global bstack11ll11ll1_opy_
  if isinstance(os.environ.get(bstack11l1ll1_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡌࡗࡤࡇࡐࡑࡡࡄ࡙࡙ࡕࡍࡂࡖࡈࠫক")), str):
    bstack11ll11ll1_opy_ = eval(os.getenv(bstack11l1ll1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡍࡘࡥࡁࡑࡒࡢࡅ࡚࡚ࡏࡎࡃࡗࡉࠬখ")))
  if bstack11ll11ll1_opy_:
    if bstack1l1ll1ll1l_opy_() < version.parse(bstack11l1ll1_opy_ (u"ࠬ࠸࠮࠴࠰࠳ࠫগ")):
      return None
    else:
      from appium.options.common.base import AppiumOptions
      options = AppiumOptions().load_capabilities(caps)
      return options
  else:
    browser = bstack11l1ll1_opy_ (u"࠭ࡣࡩࡴࡲࡱࡪ࠭ঘ")
    if bstack11l1ll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡏࡣࡰࡩࠬঙ") in caps:
      browser = caps[bstack11l1ll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡐࡤࡱࡪ࠭চ")]
    elif bstack11l1ll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࠪছ") in caps:
      browser = caps[bstack11l1ll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࠫজ")]
    browser = str(browser).lower()
    if browser == bstack11l1ll1_opy_ (u"ࠫ࡮ࡶࡨࡰࡰࡨࠫঝ") or browser == bstack11l1ll1_opy_ (u"ࠬ࡯ࡰࡢࡦࠪঞ"):
      browser = bstack11l1ll1_opy_ (u"࠭ࡳࡢࡨࡤࡶ࡮࠭ট")
    if browser == bstack11l1ll1_opy_ (u"ࠧࡴࡣࡰࡷࡺࡴࡧࠨঠ"):
      browser = bstack11l1ll1_opy_ (u"ࠨࡥ࡫ࡶࡴࡳࡥࠨড")
    if browser not in [bstack11l1ll1_opy_ (u"ࠩࡦ࡬ࡷࡵ࡭ࡦࠩঢ"), bstack11l1ll1_opy_ (u"ࠪࡩࡩ࡭ࡥࠨণ"), bstack11l1ll1_opy_ (u"ࠫ࡮࡫ࠧত"), bstack11l1ll1_opy_ (u"ࠬࡹࡡࡧࡣࡵ࡭ࠬথ"), bstack11l1ll1_opy_ (u"࠭ࡦࡪࡴࡨࡪࡴࡾࠧদ")]:
      return None
    try:
      package = bstack11l1ll1_opy_ (u"ࠧࡴࡧ࡯ࡩࡳ࡯ࡵ࡮࠰ࡺࡩࡧࡪࡲࡪࡸࡨࡶ࠳ࢁࡽ࠯ࡱࡳࡸ࡮ࡵ࡮ࡴࠩধ").format(browser)
      name = bstack11l1ll1_opy_ (u"ࠨࡑࡳࡸ࡮ࡵ࡮ࡴࠩন")
      browser_options = getattr(__import__(package, fromlist=[name]), name)
      options = browser_options()
      if not bstack111l111l1_opy_(options):
        return None
      for bstack1lllll11l1_opy_ in caps.keys():
        options.set_capability(bstack1lllll11l1_opy_, caps[bstack1lllll11l1_opy_])
      bstack1l11llllll_opy_(options, caps)
      return options
    except Exception as e:
      logger.debug(str(e))
      return None
def bstack11lll1l11_opy_(options, bstack11l11ll1_opy_):
  if not bstack111l111l1_opy_(options):
    return
  for bstack1lllll11l1_opy_ in bstack11l11ll1_opy_.keys():
    if bstack1lllll11l1_opy_ in bstack1l11111ll1_opy_:
      continue
    if bstack1lllll11l1_opy_ in options._caps and type(options._caps[bstack1lllll11l1_opy_]) in [dict, list]:
      options._caps[bstack1lllll11l1_opy_] = update(options._caps[bstack1lllll11l1_opy_], bstack11l11ll1_opy_[bstack1lllll11l1_opy_])
    else:
      options.set_capability(bstack1lllll11l1_opy_, bstack11l11ll1_opy_[bstack1lllll11l1_opy_])
  bstack1l11llllll_opy_(options, bstack11l11ll1_opy_)
  if bstack11l1ll1_opy_ (u"ࠩࡰࡳࡿࡀࡤࡦࡤࡸ࡫࡬࡫ࡲࡂࡦࡧࡶࡪࡹࡳࠨ঩") in options._caps:
    if options._caps[bstack11l1ll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡒࡦࡳࡥࠨপ")] and options._caps[bstack11l1ll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡓࡧ࡭ࡦࠩফ")].lower() != bstack11l1ll1_opy_ (u"ࠬ࡬ࡩࡳࡧࡩࡳࡽ࠭ব"):
      del options._caps[bstack11l1ll1_opy_ (u"࠭࡭ࡰࡼ࠽ࡨࡪࡨࡵࡨࡩࡨࡶࡆࡪࡤࡳࡧࡶࡷࠬভ")]
def bstack1lllll11_opy_(proxy_config):
  if bstack11l1ll1_opy_ (u"ࠧࡩࡶࡷࡴࡸࡖࡲࡰࡺࡼࠫম") in proxy_config:
    proxy_config[bstack11l1ll1_opy_ (u"ࠨࡵࡶࡰࡕࡸ࡯ࡹࡻࠪয")] = proxy_config[bstack11l1ll1_opy_ (u"ࠩ࡫ࡸࡹࡶࡳࡑࡴࡲࡼࡾ࠭র")]
    del (proxy_config[bstack11l1ll1_opy_ (u"ࠪ࡬ࡹࡺࡰࡴࡒࡵࡳࡽࡿࠧ঱")])
  if bstack11l1ll1_opy_ (u"ࠫࡵࡸ࡯ࡹࡻࡗࡽࡵ࡫ࠧল") in proxy_config and proxy_config[bstack11l1ll1_opy_ (u"ࠬࡶࡲࡰࡺࡼࡘࡾࡶࡥࠨ঳")].lower() != bstack11l1ll1_opy_ (u"࠭ࡤࡪࡴࡨࡧࡹ࠭঴"):
    proxy_config[bstack11l1ll1_opy_ (u"ࠧࡱࡴࡲࡼࡾ࡚ࡹࡱࡧࠪ঵")] = bstack11l1ll1_opy_ (u"ࠨ࡯ࡤࡲࡺࡧ࡬ࠨশ")
  if bstack11l1ll1_opy_ (u"ࠩࡳࡶࡴࡾࡹࡂࡷࡷࡳࡨࡵ࡮ࡧ࡫ࡪ࡙ࡷࡲࠧষ") in proxy_config:
    proxy_config[bstack11l1ll1_opy_ (u"ࠪࡴࡷࡵࡸࡺࡖࡼࡴࡪ࠭স")] = bstack11l1ll1_opy_ (u"ࠫࡵࡧࡣࠨহ")
  return proxy_config
def bstack1l11l1l111_opy_(config, proxy):
  from selenium.webdriver.common.proxy import Proxy
  if not bstack11l1ll1_opy_ (u"ࠬࡶࡲࡰࡺࡼࠫ঺") in config:
    return proxy
  config[bstack11l1ll1_opy_ (u"࠭ࡰࡳࡱࡻࡽࠬ঻")] = bstack1lllll11_opy_(config[bstack11l1ll1_opy_ (u"ࠧࡱࡴࡲࡼࡾ়࠭")])
  if proxy == None:
    proxy = Proxy(config[bstack11l1ll1_opy_ (u"ࠨࡲࡵࡳࡽࡿࠧঽ")])
  return proxy
def bstack11lll1ll1l_opy_(self):
  global CONFIG
  global bstack1llll111ll_opy_
  try:
    proxy = bstack1l1ll1lll1_opy_(CONFIG)
    if proxy:
      if proxy.endswith(bstack11l1ll1_opy_ (u"ࠩ࠱ࡴࡦࡩࠧা")):
        proxies = bstack111l111ll_opy_(proxy, bstack1l11111l1_opy_())
        if len(proxies) > 0:
          protocol, bstack1lll1l1l1l_opy_ = proxies.popitem()
          if bstack11l1ll1_opy_ (u"ࠥ࠾࠴࠵ࠢি") in bstack1lll1l1l1l_opy_:
            return bstack1lll1l1l1l_opy_
          else:
            return bstack11l1ll1_opy_ (u"ࠦ࡭ࡺࡴࡱ࠼࠲࠳ࠧী") + bstack1lll1l1l1l_opy_
      else:
        return proxy
  except Exception as e:
    logger.error(bstack11l1ll1_opy_ (u"ࠧࡋࡲࡳࡱࡵࠤ࡮ࡴࠠࡴࡧࡷࡸ࡮ࡴࡧࠡࡲࡵࡳࡽࡿࠠࡶࡴ࡯ࠤ࠿ࠦࡻࡾࠤু").format(str(e)))
  return bstack1llll111ll_opy_(self)
def bstack1l1ll1lll_opy_():
  global CONFIG
  return bstack1lll11lll1_opy_(CONFIG) and bstack11l11lll_opy_() and bstack1ll111111l_opy_() >= version.parse(bstack11llll11_opy_)
def bstack11l1l1l1l_opy_():
  global CONFIG
  return (bstack11l1ll1_opy_ (u"࠭ࡨࡵࡶࡳࡔࡷࡵࡸࡺࠩূ") in CONFIG or bstack11l1ll1_opy_ (u"ࠧࡩࡶࡷࡴࡸࡖࡲࡰࡺࡼࠫৃ") in CONFIG) and bstack11llll111_opy_()
def bstack1lll11l11l_opy_(config):
  bstack1ll1111ll1_opy_ = {}
  if bstack11l1ll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡕࡷࡥࡨࡱࡌࡰࡥࡤࡰࡔࡶࡴࡪࡱࡱࡷࠬৄ") in config:
    bstack1ll1111ll1_opy_ = config[bstack11l1ll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡖࡸࡦࡩ࡫ࡍࡱࡦࡥࡱࡕࡰࡵ࡫ࡲࡲࡸ࠭৅")]
  if bstack11l1ll1_opy_ (u"ࠪࡰࡴࡩࡡ࡭ࡑࡳࡸ࡮ࡵ࡮ࡴࠩ৆") in config:
    bstack1ll1111ll1_opy_ = config[bstack11l1ll1_opy_ (u"ࠫࡱࡵࡣࡢ࡮ࡒࡴࡹ࡯࡯࡯ࡵࠪে")]
  proxy = bstack1l1ll1lll1_opy_(config)
  if proxy:
    if proxy.endswith(bstack11l1ll1_opy_ (u"ࠬ࠴ࡰࡢࡥࠪৈ")) and os.path.isfile(proxy):
      bstack1ll1111ll1_opy_[bstack11l1ll1_opy_ (u"࠭࠭ࡱࡣࡦ࠱࡫࡯࡬ࡦࠩ৉")] = proxy
    else:
      parsed_url = None
      if proxy.endswith(bstack11l1ll1_opy_ (u"ࠧ࠯ࡲࡤࡧࠬ৊")):
        proxies = bstack1l11l1l1_opy_(config, bstack1l11111l1_opy_())
        if len(proxies) > 0:
          protocol, bstack1lll1l1l1l_opy_ = proxies.popitem()
          if bstack11l1ll1_opy_ (u"ࠣ࠼࠲࠳ࠧো") in bstack1lll1l1l1l_opy_:
            parsed_url = urlparse(bstack1lll1l1l1l_opy_)
          else:
            parsed_url = urlparse(protocol + bstack11l1ll1_opy_ (u"ࠤ࠽࠳࠴ࠨৌ") + bstack1lll1l1l1l_opy_)
      else:
        parsed_url = urlparse(proxy)
      if parsed_url and parsed_url.hostname: bstack1ll1111ll1_opy_[bstack11l1ll1_opy_ (u"ࠪࡴࡷࡵࡸࡺࡊࡲࡷࡹ্࠭")] = str(parsed_url.hostname)
      if parsed_url and parsed_url.port: bstack1ll1111ll1_opy_[bstack11l1ll1_opy_ (u"ࠫࡵࡸ࡯ࡹࡻࡓࡳࡷࡺࠧৎ")] = str(parsed_url.port)
      if parsed_url and parsed_url.username: bstack1ll1111ll1_opy_[bstack11l1ll1_opy_ (u"ࠬࡶࡲࡰࡺࡼ࡙ࡸ࡫ࡲࠨ৏")] = str(parsed_url.username)
      if parsed_url and parsed_url.password: bstack1ll1111ll1_opy_[bstack11l1ll1_opy_ (u"࠭ࡰࡳࡱࡻࡽࡕࡧࡳࡴࠩ৐")] = str(parsed_url.password)
  return bstack1ll1111ll1_opy_
def bstack1111llll1_opy_(config):
  if bstack11l1ll1_opy_ (u"ࠧࡵࡧࡶࡸࡈࡵ࡮ࡵࡧࡻࡸࡔࡶࡴࡪࡱࡱࡷࠬ৑") in config:
    return config[bstack11l1ll1_opy_ (u"ࠨࡶࡨࡷࡹࡉ࡯࡯ࡶࡨࡼࡹࡕࡰࡵ࡫ࡲࡲࡸ࠭৒")]
  return {}
def bstack11ll1lllll_opy_(caps):
  global bstack1ll1lll1ll_opy_
  if bstack11l1ll1_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬࠼ࡲࡴࡹ࡯࡯࡯ࡵࠪ৓") in caps:
    caps[bstack11l1ll1_opy_ (u"ࠪࡦࡸࡺࡡࡤ࡭࠽ࡳࡵࡺࡩࡰࡰࡶࠫ৔")][bstack11l1ll1_opy_ (u"ࠫࡱࡵࡣࡢ࡮ࠪ৕")] = True
    if bstack1ll1lll1ll_opy_:
      caps[bstack11l1ll1_opy_ (u"ࠬࡨࡳࡵࡣࡦ࡯࠿ࡵࡰࡵ࡫ࡲࡲࡸ࠭৖")][bstack11l1ll1_opy_ (u"࠭࡬ࡰࡥࡤࡰࡎࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠨৗ")] = bstack1ll1lll1ll_opy_
  else:
    caps[bstack11l1ll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴࡬ࡰࡥࡤࡰࠬ৘")] = True
    if bstack1ll1lll1ll_opy_:
      caps[bstack11l1ll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮࡭ࡱࡦࡥࡱࡏࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࠩ৙")] = bstack1ll1lll1ll_opy_
@measure(event_name=EVENTS.bstack11ll1l1l1_opy_, stage=STAGE.bstack1l1ll1llll_opy_, bstack1l11l1ll_opy_=bstack1lll1l11l_opy_)
def bstack1ll1l1ll1_opy_():
  global CONFIG
  if not bstack1ll111111_opy_(CONFIG) or cli.is_enabled(CONFIG):
    return
  if bstack11l1ll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡍࡱࡦࡥࡱ࠭৚") in CONFIG and bstack111l1l111_opy_(CONFIG[bstack11l1ll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡎࡲࡧࡦࡲࠧ৛")]):
    if (
      bstack11l1ll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡘࡺࡡࡤ࡭ࡏࡳࡨࡧ࡬ࡐࡲࡷ࡭ࡴࡴࡳࠨড়") in CONFIG
      and bstack111l1l111_opy_(CONFIG[bstack11l1ll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷ࡙ࡴࡢࡥ࡮ࡐࡴࡩࡡ࡭ࡑࡳࡸ࡮ࡵ࡮ࡴࠩঢ়")].get(bstack11l1ll1_opy_ (u"࠭ࡳ࡬࡫ࡳࡆ࡮ࡴࡡࡳࡻࡌࡲ࡮ࡺࡩࡢ࡮࡬ࡷࡦࡺࡩࡰࡰࠪ৞")))
    ):
      logger.debug(bstack11l1ll1_opy_ (u"ࠢࡍࡱࡦࡥࡱࠦࡢࡪࡰࡤࡶࡾࠦ࡮ࡰࡶࠣࡷࡹࡧࡲࡵࡧࡧࠤࡦࡹࠠࡴ࡭࡬ࡴࡇ࡯࡮ࡢࡴࡼࡍࡳ࡯ࡴࡪࡣ࡯࡭ࡸࡧࡴࡪࡱࡱࠤ࡮ࡹࠠࡦࡰࡤࡦࡱ࡫ࡤࠣয়"))
      return
    bstack1ll1111ll1_opy_ = bstack1lll11l11l_opy_(CONFIG)
    bstack11l1ll11ll_opy_(CONFIG[bstack11l1ll1_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡌࡧࡼࠫৠ")], bstack1ll1111ll1_opy_)
def bstack11l1ll11ll_opy_(key, bstack1ll1111ll1_opy_):
  global bstack1l1l1111_opy_
  logger.info(bstack1llllll11_opy_)
  try:
    bstack1l1l1111_opy_ = Local()
    bstack1l1lll111_opy_ = {bstack11l1ll1_opy_ (u"ࠩ࡮ࡩࡾ࠭ৡ"): key}
    bstack1l1lll111_opy_.update(bstack1ll1111ll1_opy_)
    logger.debug(bstack1l111l1l1l_opy_.format(str(bstack1l1lll111_opy_)))
    bstack1l1l1111_opy_.start(**bstack1l1lll111_opy_)
    if bstack1l1l1111_opy_.isRunning():
      logger.info(bstack11l11l1ll_opy_)
  except Exception as e:
    bstack1l11l1lll_opy_(bstack1lll1l11ll_opy_.format(str(e)))
def bstack1l1111ll11_opy_():
  global bstack1l1l1111_opy_
  if bstack1l1l1111_opy_.isRunning():
    logger.info(bstack1l1lll1l11_opy_)
    bstack1l1l1111_opy_.stop()
  bstack1l1l1111_opy_ = None
def bstack1l11l1lll1_opy_(bstack1llllll111_opy_=[]):
  global CONFIG
  bstack11lll1lll_opy_ = []
  bstack1ll111l1_opy_ = [bstack11l1ll1_opy_ (u"ࠪࡳࡸ࠭ৢ"), bstack11l1ll1_opy_ (u"ࠫࡴࡹࡖࡦࡴࡶ࡭ࡴࡴࠧৣ"), bstack11l1ll1_opy_ (u"ࠬࡪࡥࡷ࡫ࡦࡩࡓࡧ࡭ࡦࠩ৤"), bstack11l1ll1_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡗࡧࡵࡷ࡮ࡵ࡮ࠨ৥"), bstack11l1ll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡏࡣࡰࡩࠬ০"), bstack11l1ll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡘࡨࡶࡸ࡯࡯࡯ࠩ১")]
  try:
    for err in bstack1llllll111_opy_:
      bstack1ll1ll11l1_opy_ = {}
      for k in bstack1ll111l1_opy_:
        val = CONFIG[bstack11l1ll1_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬ২")][int(err[bstack11l1ll1_opy_ (u"ࠪ࡭ࡳࡪࡥࡹࠩ৩")])].get(k)
        if val:
          bstack1ll1ll11l1_opy_[k] = val
      if(err[bstack11l1ll1_opy_ (u"ࠫࡪࡸࡲࡰࡴࠪ৪")] != bstack11l1ll1_opy_ (u"ࠬ࠭৫")):
        bstack1ll1ll11l1_opy_[bstack11l1ll1_opy_ (u"࠭ࡴࡦࡵࡷࡷࠬ৬")] = {
          err[bstack11l1ll1_opy_ (u"ࠧ࡯ࡣࡰࡩࠬ৭")]: err[bstack11l1ll1_opy_ (u"ࠨࡧࡵࡶࡴࡸࠧ৮")]
        }
        bstack11lll1lll_opy_.append(bstack1ll1ll11l1_opy_)
  except Exception as e:
    logger.debug(bstack11l1ll1_opy_ (u"ࠩࡈࡶࡷࡵࡲࠡ࡫ࡱࠤ࡫ࡵࡲ࡮ࡣࡷࡸ࡮ࡴࡧࠡࡦࡤࡸࡦࠦࡦࡰࡴࠣࡩࡻ࡫࡮ࡵ࠼ࠣࠫ৯") + str(e))
  finally:
    return bstack11lll1lll_opy_
def bstack1l1l1l111_opy_(file_name):
  bstack1llll11ll1_opy_ = []
  try:
    bstack1l11111l1l_opy_ = os.path.join(tempfile.gettempdir(), file_name)
    if os.path.exists(bstack1l11111l1l_opy_):
      with open(bstack1l11111l1l_opy_) as f:
        bstack111l1l1l1_opy_ = json.load(f)
        bstack1llll11ll1_opy_ = bstack111l1l1l1_opy_
      os.remove(bstack1l11111l1l_opy_)
    return bstack1llll11ll1_opy_
  except Exception as e:
    logger.debug(bstack11l1ll1_opy_ (u"ࠪࡉࡷࡸ࡯ࡳࠢ࡬ࡲࠥ࡬ࡩ࡯ࡦ࡬ࡲ࡬ࠦࡥࡳࡴࡲࡶࠥࡲࡩࡴࡶ࠽ࠤࠬৰ") + str(e))
    return bstack1llll11ll1_opy_
def bstack1llll11l1_opy_():
  try:
      from bstack_utils.constants import bstack1l1lllllll_opy_, EVENTS
      from bstack_utils.helper import bstack1l1111l1l_opy_, get_host_info, bstack1ll1l11l1_opy_
      from datetime import datetime
      from filelock import FileLock
      bstack1l111l11_opy_ = os.path.join(os.getcwd(), bstack11l1ll1_opy_ (u"ࠫࡱࡵࡧࠨৱ"), bstack11l1ll1_opy_ (u"ࠬࡱࡥࡺ࠯ࡰࡩࡹࡸࡩࡤࡵ࠱࡮ࡸࡵ࡮ࠨ৲"))
      lock = FileLock(bstack1l111l11_opy_+bstack11l1ll1_opy_ (u"ࠨ࠮࡭ࡱࡦ࡯ࠧ৳"))
      def bstack11111ll1_opy_():
          try:
              with lock:
                  with open(bstack1l111l11_opy_, bstack11l1ll1_opy_ (u"ࠢࡳࠤ৴"), encoding=bstack11l1ll1_opy_ (u"ࠣࡷࡷࡪ࠲࠾ࠢ৵")) as file:
                      data = json.load(file)
                      config = {
                          bstack11l1ll1_opy_ (u"ࠤ࡫ࡩࡦࡪࡥࡳࡵࠥ৶"): {
                              bstack11l1ll1_opy_ (u"ࠥࡇࡴࡴࡴࡦࡰࡷ࠱࡙ࡿࡰࡦࠤ৷"): bstack11l1ll1_opy_ (u"ࠦࡦࡶࡰ࡭࡫ࡦࡥࡹ࡯࡯࡯࠱࡭ࡷࡴࡴࠢ৸"),
                          }
                      }
                      bstack1l1l11l1_opy_ = datetime.utcnow()
                      bstack1ll1l1ll_opy_ = bstack1l1l11l1_opy_.strftime(bstack11l1ll1_opy_ (u"࡙ࠧࠫ࠮ࠧࡰ࠱ࠪࡪࡔࠦࡊ࠽ࠩࡒࡀࠥࡔ࠰ࠨࡪ࡛ࠥࡔࡄࠤ৹"))
                      bstack1ll1lllll_opy_ = os.environ.get(bstack11l1ll1_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡚ࡅࡔࡖࡋ࡙ࡇࡥࡕࡖࡋࡇࠫ৺")) if os.environ.get(bstack11l1ll1_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡔࡆࡕࡗࡌ࡚ࡈ࡟ࡖࡗࡌࡈࠬ৻")) else bstack1ll1l11l1_opy_.get_property(bstack11l1ll1_opy_ (u"ࠣࡵࡧ࡯ࡗࡻ࡮ࡊࡦࠥৼ"))
                      payload = {
                          bstack11l1ll1_opy_ (u"ࠤࡨࡺࡪࡴࡴࡠࡶࡼࡴࡪࠨ৽"): bstack11l1ll1_opy_ (u"ࠥࡷࡩࡱ࡟ࡦࡸࡨࡲࡹࡹࠢ৾"),
                          bstack11l1ll1_opy_ (u"ࠦࡩࡧࡴࡢࠤ৿"): {
                              bstack11l1ll1_opy_ (u"ࠧࡺࡥࡴࡶ࡫ࡹࡧࡥࡵࡶ࡫ࡧࠦ਀"): bstack1ll1lllll_opy_,
                              bstack11l1ll1_opy_ (u"ࠨࡣࡳࡧࡤࡸࡪࡪ࡟ࡥࡣࡼࠦਁ"): bstack1ll1l1ll_opy_,
                              bstack11l1ll1_opy_ (u"ࠢࡦࡸࡨࡲࡹࡥ࡮ࡢ࡯ࡨࠦਂ"): bstack11l1ll1_opy_ (u"ࠣࡕࡇࡏࡋ࡫ࡡࡵࡷࡵࡩࡕ࡫ࡲࡧࡱࡵࡱࡦࡴࡣࡦࠤਃ"),
                              bstack11l1ll1_opy_ (u"ࠤࡨࡺࡪࡴࡴࡠ࡬ࡶࡳࡳࠨ਄"): {
                                  bstack11l1ll1_opy_ (u"ࠥࡱࡪࡧࡳࡶࡴࡨࡷࠧਅ"): data,
                                  bstack11l1ll1_opy_ (u"ࠦࡸࡪ࡫ࡓࡷࡱࡍࡩࠨਆ"): bstack1ll1l11l1_opy_.get_property(bstack11l1ll1_opy_ (u"ࠧࡹࡤ࡬ࡔࡸࡲࡎࡪࠢਇ"))
                              },
                              bstack11l1ll1_opy_ (u"ࠨࡵࡴࡧࡵࡣࡩࡧࡴࡢࠤਈ"): bstack1ll1l11l1_opy_.get_property(bstack11l1ll1_opy_ (u"ࠢࡶࡵࡨࡶࡓࡧ࡭ࡦࠤਉ")),
                              bstack11l1ll1_opy_ (u"ࠣࡪࡲࡷࡹࡥࡩ࡯ࡨࡲࠦਊ"): get_host_info()
                          }
                      }
                      response = bstack1l1111l1l_opy_(bstack11l1ll1_opy_ (u"ࠤࡓࡓࡘ࡚ࠢ਋"), bstack1l1lllllll_opy_, payload, config)
                      if(response.status_code >= 200 and response.status_code < 300):
                          logger.debug(bstack11l1ll1_opy_ (u"ࠥࡈࡦࡺࡡࠡࡵࡨࡲࡹࠦࡳࡶࡥࡦࡩࡸࡹࡦࡶ࡮࡯ࡽࠥࡺ࡯ࠡࡽࢀࠤࡼ࡯ࡴࡩࠢࡧࡥࡹࡧࠠࡼࡿࠥ਌").format(bstack1l1lllllll_opy_, payload))
                      else:
                          logger.debug(bstack11l1ll1_opy_ (u"ࠦࡗ࡫ࡱࡶࡧࡶࡸࠥ࡬ࡡࡪ࡮ࡨࡨࠥ࡬࡯ࡳࠢࡾࢁࠥࡽࡩࡵࡪࠣࡨࡦࡺࡡࠡࡽࢀࠦ਍").format(bstack1l1lllllll_opy_, payload))
          except Exception as e:
              logger.debug(bstack11l1ll1_opy_ (u"ࠧࡌࡡࡪ࡮ࡨࡨࠥࡺ࡯ࠡࡵࡨࡲࡩࠦ࡫ࡦࡻࠣࡱࡪࡺࡲࡪࡥࡶࠤࡩࡧࡴࡢࠢࡺ࡭ࡹ࡮ࠠࡦࡴࡵࡳࡷࠦࡻࡾࠤ਎").format(e))
      bstack11111ll1_opy_()
      bstack11lllll11l_opy_(bstack1l111l11_opy_, logger)
  except:
    pass
def bstack1ll111ll11_opy_():
  global bstack11ll11ll1l_opy_
  global bstack1l1ll1l1l1_opy_
  global bstack11l11111_opy_
  global bstack1l11ll111l_opy_
  global bstack1111lll1l_opy_
  global bstack1lll1ll1l1_opy_
  global CONFIG
  bstack111ll1l1_opy_ = os.environ.get(bstack11l1ll1_opy_ (u"࠭ࡆࡓࡃࡐࡉ࡜ࡕࡒࡌࡡࡘࡗࡊࡊࠧਏ"))
  if bstack111ll1l1_opy_ in [bstack11l1ll1_opy_ (u"ࠧࡳࡱࡥࡳࡹ࠭ਐ"), bstack11l1ll1_opy_ (u"ࠨࡲࡤࡦࡴࡺࠧ਑")]:
    bstack1l1llll1l1_opy_()
  percy.shutdown()
  if bstack11ll11ll1l_opy_:
    logger.warning(bstack1l111ll11_opy_.format(str(bstack11ll11ll1l_opy_)))
  else:
    try:
      bstack11lll11l_opy_ = bstack1l11l11l1l_opy_(bstack11l1ll1_opy_ (u"ࠩ࠱ࡦࡸࡺࡡࡤ࡭࠰ࡧࡴࡴࡦࡪࡩ࠱࡮ࡸࡵ࡮ࠨ਒"), logger)
      if bstack11lll11l_opy_.get(bstack11l1ll1_opy_ (u"ࠪࡲࡺࡪࡧࡦࡡ࡯ࡳࡨࡧ࡬ࠨਓ")) and bstack11lll11l_opy_.get(bstack11l1ll1_opy_ (u"ࠫࡳࡻࡤࡨࡧࡢࡰࡴࡩࡡ࡭ࠩਔ")).get(bstack11l1ll1_opy_ (u"ࠬ࡮࡯ࡴࡶࡱࡥࡲ࡫ࠧਕ")):
        logger.warning(bstack1l111ll11_opy_.format(str(bstack11lll11l_opy_[bstack11l1ll1_opy_ (u"࠭࡮ࡶࡦࡪࡩࡤࡲ࡯ࡤࡣ࡯ࠫਖ")][bstack11l1ll1_opy_ (u"ࠧࡩࡱࡶࡸࡳࡧ࡭ࡦࠩਗ")])))
    except Exception as e:
      logger.error(e)
  if cli.is_running():
    bstack1l1l11lll1_opy_.invoke(bstack1ll1ll1l11_opy_.bstack11lll1l111_opy_)
  logger.info(bstack11ll1l1ll_opy_)
  global bstack1l1l1111_opy_
  if bstack1l1l1111_opy_:
    bstack1l1111ll11_opy_()
  try:
    for driver in bstack1l1ll1l1l1_opy_:
      driver.quit()
  except Exception as e:
    pass
  logger.info(bstack11llllll11_opy_)
  if bstack1lll1ll1l1_opy_ == bstack11l1ll1_opy_ (u"ࠨࡴࡲࡦࡴࡺࠧਘ"):
    bstack1111lll1l_opy_ = bstack1l1l1l111_opy_(bstack11l1ll1_opy_ (u"ࠩࡵࡳࡧࡵࡴࡠࡧࡵࡶࡴࡸ࡟࡭࡫ࡶࡸ࠳ࡰࡳࡰࡰࠪਙ"))
  if bstack1lll1ll1l1_opy_ == bstack11l1ll1_opy_ (u"ࠪࡴࡾࡺࡥࡴࡶࠪਚ") and len(bstack1l11ll111l_opy_) == 0:
    bstack1l11ll111l_opy_ = bstack1l1l1l111_opy_(bstack11l1ll1_opy_ (u"ࠫࡵࡽ࡟ࡱࡻࡷࡩࡸࡺ࡟ࡦࡴࡵࡳࡷࡥ࡬ࡪࡵࡷ࠲࡯ࡹ࡯࡯ࠩਛ"))
    if len(bstack1l11ll111l_opy_) == 0:
      bstack1l11ll111l_opy_ = bstack1l1l1l111_opy_(bstack11l1ll1_opy_ (u"ࠬࡶࡹࡵࡧࡶࡸࡤࡶࡰࡱࡡࡨࡶࡷࡵࡲࡠ࡮࡬ࡷࡹ࠴ࡪࡴࡱࡱࠫਜ"))
  bstack1llll1l1l_opy_ = bstack11l1ll1_opy_ (u"࠭ࠧਝ")
  if len(bstack11l11111_opy_) > 0:
    bstack1llll1l1l_opy_ = bstack1l11l1lll1_opy_(bstack11l11111_opy_)
  elif len(bstack1l11ll111l_opy_) > 0:
    bstack1llll1l1l_opy_ = bstack1l11l1lll1_opy_(bstack1l11ll111l_opy_)
  elif len(bstack1111lll1l_opy_) > 0:
    bstack1llll1l1l_opy_ = bstack1l11l1lll1_opy_(bstack1111lll1l_opy_)
  elif len(bstack111lll11_opy_) > 0:
    bstack1llll1l1l_opy_ = bstack1l11l1lll1_opy_(bstack111lll11_opy_)
  if bool(bstack1llll1l1l_opy_):
    bstack1lll1llll_opy_(bstack1llll1l1l_opy_)
  else:
    bstack1lll1llll_opy_()
  bstack11lllll11l_opy_(bstack1llll1ll1l_opy_, logger)
  if bstack111ll1l1_opy_ not in [bstack11l1ll1_opy_ (u"ࠧࡳࡱࡥࡳࡹ࠳ࡩ࡯ࡶࡨࡶࡳࡧ࡬ࠨਞ")]:
    bstack1llll11l1_opy_()
  bstack1ll1ll111_opy_.bstack1l1l1lll1l_opy_(CONFIG)
  if len(bstack1111lll1l_opy_) > 0:
    sys.exit(len(bstack1111lll1l_opy_))
def bstack1ll1l1ll1l_opy_(bstack11l1llll_opy_, frame):
  global bstack1ll1l11l1_opy_
  logger.error(bstack1lll1l11l1_opy_)
  bstack1ll1l11l1_opy_.bstack1l111llll1_opy_(bstack11l1ll1_opy_ (u"ࠨࡵࡧ࡯ࡐ࡯࡬࡭ࡐࡲࠫਟ"), bstack11l1llll_opy_)
  if hasattr(signal, bstack11l1ll1_opy_ (u"ࠩࡖ࡭࡬ࡴࡡ࡭ࡵࠪਠ")):
    bstack1ll1l11l1_opy_.bstack1l111llll1_opy_(bstack11l1ll1_opy_ (u"ࠪࡷࡩࡱࡋࡪ࡮࡯ࡗ࡮࡭࡮ࡢ࡮ࠪਡ"), signal.Signals(bstack11l1llll_opy_).name)
  else:
    bstack1ll1l11l1_opy_.bstack1l111llll1_opy_(bstack11l1ll1_opy_ (u"ࠫࡸࡪ࡫ࡌ࡫࡯ࡰࡘ࡯ࡧ࡯ࡣ࡯ࠫਢ"), bstack11l1ll1_opy_ (u"࡙ࠬࡉࡈࡗࡑࡏࡓࡕࡗࡏࠩਣ"))
  if cli.is_running():
    bstack1l1l11lll1_opy_.invoke(bstack1ll1ll1l11_opy_.bstack11lll1l111_opy_)
  bstack111ll1l1_opy_ = os.environ.get(bstack11l1ll1_opy_ (u"࠭ࡆࡓࡃࡐࡉ࡜ࡕࡒࡌࡡࡘࡗࡊࡊࠧਤ"))
  if bstack111ll1l1_opy_ == bstack11l1ll1_opy_ (u"ࠧࡱࡻࡷࡩࡸࡺࠧਥ") and not cli.is_enabled(CONFIG):
    bstack11111l1l1_opy_.stop(bstack1ll1l11l1_opy_.get_property(bstack11l1ll1_opy_ (u"ࠨࡵࡧ࡯ࡐ࡯࡬࡭ࡕ࡬࡫ࡳࡧ࡬ࠨਦ")))
  bstack1ll111ll11_opy_()
  sys.exit(1)
def bstack1l11l1lll_opy_(err):
  logger.critical(bstack1l1l1111ll_opy_.format(str(err)))
  bstack1lll1llll_opy_(bstack1l1l1111ll_opy_.format(str(err)), True)
  atexit.unregister(bstack1ll111ll11_opy_)
  bstack1l1llll1l1_opy_()
  sys.exit(1)
def bstack1ll11lll1_opy_(error, message):
  logger.critical(str(error))
  logger.critical(message)
  bstack1lll1llll_opy_(message, True)
  atexit.unregister(bstack1ll111ll11_opy_)
  bstack1l1llll1l1_opy_()
  sys.exit(1)
def bstack1l11ll1l1l_opy_():
  global CONFIG
  global bstack1llll1ll1_opy_
  global bstack1ll11l11ll_opy_
  global bstack1111l1111_opy_
  CONFIG = bstack1ll1l1l1l1_opy_()
  load_dotenv(CONFIG.get(bstack11l1ll1_opy_ (u"ࠩࡨࡲࡻࡌࡩ࡭ࡧࠪਧ")))
  bstack1l11lll11l_opy_()
  bstack11ll11l11_opy_()
  CONFIG = bstack1l11l11ll_opy_(CONFIG)
  update(CONFIG, bstack1ll11l11ll_opy_)
  update(CONFIG, bstack1llll1ll1_opy_)
  if not cli.is_enabled(CONFIG):
    CONFIG = bstack1l1ll11l1l_opy_(CONFIG)
  bstack1111l1111_opy_ = bstack1ll111111_opy_(CONFIG)
  os.environ[bstack11l1ll1_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡄ࡙࡙ࡕࡍࡂࡖࡌࡓࡓ࠭ਨ")] = bstack1111l1111_opy_.__str__()
  bstack1ll1l11l1_opy_.bstack1l111llll1_opy_(bstack11l1ll1_opy_ (u"ࠫࡧࡹࡴࡢࡥ࡮ࡣࡸ࡫ࡳࡴ࡫ࡲࡲࠬ਩"), bstack1111l1111_opy_)
  if (bstack11l1ll1_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡒࡦࡳࡥࠨਪ") in CONFIG and bstack11l1ll1_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡓࡧ࡭ࡦࠩਫ") in bstack1llll1ll1_opy_) or (
          bstack11l1ll1_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡔࡡ࡮ࡧࠪਬ") in CONFIG and bstack11l1ll1_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡎࡢ࡯ࡨࠫਭ") not in bstack1ll11l11ll_opy_):
    if os.getenv(bstack11l1ll1_opy_ (u"ࠩࡅࡗ࡙ࡇࡃࡌࡡࡆࡓࡒࡈࡉࡏࡇࡇࡣࡇ࡛ࡉࡍࡆࡢࡍࡉ࠭ਮ")):
      CONFIG[bstack11l1ll1_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬਯ")] = os.getenv(bstack11l1ll1_opy_ (u"ࠫࡇ࡙ࡔࡂࡅࡎࡣࡈࡕࡍࡃࡋࡑࡉࡉࡥࡂࡖࡋࡏࡈࡤࡏࡄࠨਰ"))
    else:
      if not CONFIG.get(bstack11l1ll1_opy_ (u"ࠧ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࠣ਱"), bstack11l1ll1_opy_ (u"ࠨࠢਲ")) in bstack1ll11ll11l_opy_:
        bstack1l11ll11l1_opy_()
  elif (bstack11l1ll1_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡔࡡ࡮ࡧࠪਲ਼") not in CONFIG and bstack11l1ll1_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡉࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࠪ਴") in CONFIG) or (
          bstack11l1ll1_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡏࡣࡰࡩࠬਵ") in bstack1ll11l11ll_opy_ and bstack11l1ll1_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡐࡤࡱࡪ࠭ਸ਼") not in bstack1llll1ll1_opy_):
    del (CONFIG[bstack11l1ll1_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭਷")])
  if bstack11ll11111l_opy_(CONFIG):
    bstack1l11l1lll_opy_(bstack1l111ll1_opy_)
  Config.bstack1l111l1ll1_opy_().bstack1l111llll1_opy_(bstack11l1ll1_opy_ (u"ࠧࡻࡳࡦࡴࡑࡥࡲ࡫ࠢਸ"), CONFIG[bstack11l1ll1_opy_ (u"࠭ࡵࡴࡧࡵࡒࡦࡳࡥࠨਹ")])
  bstack11ll1ll1l_opy_()
  bstack1ll111ll_opy_()
  if bstack11ll11ll1_opy_ and not CONFIG.get(bstack11l1ll1_opy_ (u"ࠢࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࠥ਺"), bstack11l1ll1_opy_ (u"ࠣࠤ਻")) in bstack1ll11ll11l_opy_:
    CONFIG[bstack11l1ll1_opy_ (u"ࠩࡤࡴࡵ਼࠭")] = bstack1l1lll1l1_opy_(CONFIG)
    logger.info(bstack11l1l1lll1_opy_.format(CONFIG[bstack11l1ll1_opy_ (u"ࠪࡥࡵࡶࠧ਽")]))
  if not bstack1111l1111_opy_:
    CONFIG[bstack11l1ll1_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧਾ")] = [{}]
def bstack1ll11111ll_opy_(config, bstack1lll111l1l_opy_):
  global CONFIG
  global bstack11ll11ll1_opy_
  CONFIG = config
  bstack11ll11ll1_opy_ = bstack1lll111l1l_opy_
def bstack1ll111ll_opy_():
  global CONFIG
  global bstack11ll11ll1_opy_
  if bstack11l1ll1_opy_ (u"ࠬࡧࡰࡱࠩਿ") in CONFIG:
    try:
      from appium import version
    except Exception as e:
      bstack1ll11lll1_opy_(e, bstack11lll1ll_opy_)
    bstack11ll11ll1_opy_ = True
    bstack1ll1l11l1_opy_.bstack1l111llll1_opy_(bstack11l1ll1_opy_ (u"࠭ࡡࡱࡲࡢࡥࡺࡺ࡯࡮ࡣࡷࡩࠬੀ"), True)
def bstack1l1lll1l1_opy_(config):
  bstack1ll1lll1_opy_ = bstack11l1ll1_opy_ (u"ࠧࠨੁ")
  app = config[bstack11l1ll1_opy_ (u"ࠨࡣࡳࡴࠬੂ")]
  if isinstance(app, str):
    if os.path.splitext(app)[1] in bstack11l1llll11_opy_:
      if os.path.exists(app):
        bstack1ll1lll1_opy_ = bstack1l1l1l1lll_opy_(config, app)
      elif bstack11llll1l11_opy_(app):
        bstack1ll1lll1_opy_ = app
      else:
        bstack1l11l1lll_opy_(bstack11l11l1l_opy_.format(app))
    else:
      if bstack11llll1l11_opy_(app):
        bstack1ll1lll1_opy_ = app
      elif os.path.exists(app):
        bstack1ll1lll1_opy_ = bstack1l1l1l1lll_opy_(app)
      else:
        bstack1l11l1lll_opy_(bstack1ll11l111_opy_)
  else:
    if len(app) > 2:
      bstack1l11l1lll_opy_(bstack11llll1ll1_opy_)
    elif len(app) == 2:
      if bstack11l1ll1_opy_ (u"ࠩࡳࡥࡹ࡮ࠧ੃") in app and bstack11l1ll1_opy_ (u"ࠪࡧࡺࡹࡴࡰ࡯ࡢ࡭ࡩ࠭੄") in app:
        if os.path.exists(app[bstack11l1ll1_opy_ (u"ࠫࡵࡧࡴࡩࠩ੅")]):
          bstack1ll1lll1_opy_ = bstack1l1l1l1lll_opy_(config, app[bstack11l1ll1_opy_ (u"ࠬࡶࡡࡵࡪࠪ੆")], app[bstack11l1ll1_opy_ (u"࠭ࡣࡶࡵࡷࡳࡲࡥࡩࡥࠩੇ")])
        else:
          bstack1l11l1lll_opy_(bstack11l11l1l_opy_.format(app))
      else:
        bstack1l11l1lll_opy_(bstack11llll1ll1_opy_)
    else:
      for key in app:
        if key in bstack1l1l11ll1_opy_:
          if key == bstack11l1ll1_opy_ (u"ࠧࡱࡣࡷ࡬ࠬੈ"):
            if os.path.exists(app[key]):
              bstack1ll1lll1_opy_ = bstack1l1l1l1lll_opy_(config, app[key])
            else:
              bstack1l11l1lll_opy_(bstack11l11l1l_opy_.format(app))
          else:
            bstack1ll1lll1_opy_ = app[key]
        else:
          bstack1l11l1lll_opy_(bstack1l111l111_opy_)
  return bstack1ll1lll1_opy_
def bstack11llll1l11_opy_(bstack1ll1lll1_opy_):
  import re
  bstack1l11l11l_opy_ = re.compile(bstack11l1ll1_opy_ (u"ࡳࠤࡡ࡟ࡦ࠳ࡺࡂ࠯࡝࠴࠲࠿࡜ࡠ࠰࡟࠱ࡢ࠰ࠤࠣ੉"))
  bstack11ll1lll11_opy_ = re.compile(bstack11l1ll1_opy_ (u"ࡴࠥࡢࡠࡧ࠭ࡻࡃ࠰࡞࠵࠳࠹࡝ࡡ࠱ࡠ࠲ࡣࠪ࠰࡝ࡤ࠱ࡿࡇ࡛࠭࠲࠰࠽ࡡࡥ࠮࡝࠯ࡠ࠮ࠩࠨ੊"))
  if bstack11l1ll1_opy_ (u"ࠪࡦࡸࡀ࠯࠰ࠩੋ") in bstack1ll1lll1_opy_ or re.fullmatch(bstack1l11l11l_opy_, bstack1ll1lll1_opy_) or re.fullmatch(bstack11ll1lll11_opy_, bstack1ll1lll1_opy_):
    return True
  else:
    return False
@measure(event_name=EVENTS.bstack1lll1l11_opy_, stage=STAGE.bstack1l1ll1llll_opy_, bstack1l11l1ll_opy_=bstack1lll1l11l_opy_)
def bstack1l1l1l1lll_opy_(config, path, bstack1l111ll1l_opy_=None):
  import requests
  from requests_toolbelt.multipart.encoder import MultipartEncoder
  import hashlib
  md5_hash = hashlib.md5(open(os.path.abspath(path), bstack11l1ll1_opy_ (u"ࠫࡷࡨࠧੌ")).read()).hexdigest()
  bstack11l11l111_opy_ = bstack11l1l1l11_opy_(md5_hash)
  bstack1ll1lll1_opy_ = None
  if bstack11l11l111_opy_:
    logger.info(bstack1ll11l1lll_opy_.format(bstack11l11l111_opy_, md5_hash))
    return bstack11l11l111_opy_
  bstack1l1l1ll111_opy_ = datetime.datetime.now()
  bstack111llll1_opy_ = MultipartEncoder(
    fields={
      bstack11l1ll1_opy_ (u"ࠬ࡬ࡩ࡭ࡧ੍ࠪ"): (os.path.basename(path), open(os.path.abspath(path), bstack11l1ll1_opy_ (u"࠭ࡲࡣࠩ੎")), bstack11l1ll1_opy_ (u"ࠧࡵࡧࡻࡸ࠴ࡶ࡬ࡢ࡫ࡱࠫ੏")),
      bstack11l1ll1_opy_ (u"ࠨࡥࡸࡷࡹࡵ࡭ࡠ࡫ࡧࠫ੐"): bstack1l111ll1l_opy_
    }
  )
  response = requests.post(bstack1l11ll1ll_opy_, data=bstack111llll1_opy_,
                           headers={bstack11l1ll1_opy_ (u"ࠩࡆࡳࡳࡺࡥ࡯ࡶ࠰ࡘࡾࡶࡥࠨੑ"): bstack111llll1_opy_.content_type},
                           auth=(config[bstack11l1ll1_opy_ (u"ࠪࡹࡸ࡫ࡲࡏࡣࡰࡩࠬ੒")], config[bstack11l1ll1_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶࡏࡪࡿࠧ੓")]))
  try:
    res = json.loads(response.text)
    bstack1ll1lll1_opy_ = res[bstack11l1ll1_opy_ (u"ࠬࡧࡰࡱࡡࡸࡶࡱ࠭੔")]
    logger.info(bstack1lll11l1l1_opy_.format(bstack1ll1lll1_opy_))
    bstack11ll1111l_opy_(md5_hash, bstack1ll1lll1_opy_)
    cli.bstack111l11l1_opy_(bstack11l1ll1_opy_ (u"ࠨࡨࡵࡶࡳ࠾ࡺࡶ࡬ࡰࡣࡧࡣࡦࡶࡰࠣ੕"), datetime.datetime.now() - bstack1l1l1ll111_opy_)
  except ValueError as err:
    bstack1l11l1lll_opy_(bstack11l1ll1l1l_opy_.format(str(err)))
  return bstack1ll1lll1_opy_
def bstack11ll1ll1l_opy_(framework_name=None, args=None):
  global CONFIG
  global bstack111lll1l1_opy_
  bstack1ll1l1l1_opy_ = 1
  bstack11ll1l11_opy_ = 1
  if bstack11l1ll1_opy_ (u"ࠧࡱࡣࡵࡥࡱࡲࡥ࡭ࡵࡓࡩࡷࡖ࡬ࡢࡶࡩࡳࡷࡳࠧ੖") in CONFIG:
    bstack11ll1l11_opy_ = CONFIG[bstack11l1ll1_opy_ (u"ࠨࡲࡤࡶࡦࡲ࡬ࡦ࡮ࡶࡔࡪࡸࡐ࡭ࡣࡷࡪࡴࡸ࡭ࠨ੗")]
  else:
    bstack11ll1l11_opy_ = bstack1lll1l1lll_opy_(framework_name, args) or 1
  if bstack11l1ll1_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬ੘") in CONFIG:
    bstack1ll1l1l1_opy_ = len(CONFIG[bstack11l1ll1_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭ਖ਼")])
  bstack111lll1l1_opy_ = int(bstack11ll1l11_opy_) * int(bstack1ll1l1l1_opy_)
def bstack1lll1l1lll_opy_(framework_name, args):
  if framework_name == bstack1l11l11ll1_opy_ and args and bstack11l1ll1_opy_ (u"ࠫ࠲࠳ࡰࡳࡱࡦࡩࡸࡹࡥࡴࠩਗ਼") in args:
      bstack1ll1l11ll_opy_ = args.index(bstack11l1ll1_opy_ (u"ࠬ࠳࠭ࡱࡴࡲࡧࡪࡹࡳࡦࡵࠪਜ਼"))
      return int(args[bstack1ll1l11ll_opy_ + 1]) or 1
  return 1
def bstack11l1l1l11_opy_(md5_hash):
  bstack1lll1l1l_opy_ = os.path.join(os.path.expanduser(bstack11l1ll1_opy_ (u"࠭ࡾࠨੜ")), bstack11l1ll1_opy_ (u"ࠧ࠯ࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࠧ੝"), bstack11l1ll1_opy_ (u"ࠨࡣࡳࡴ࡚ࡶ࡬ࡰࡣࡧࡑࡉ࠻ࡈࡢࡵ࡫࠲࡯ࡹ࡯࡯ࠩਫ਼"))
  if os.path.exists(bstack1lll1l1l_opy_):
    bstack1l1lll1lll_opy_ = json.load(open(bstack1lll1l1l_opy_, bstack11l1ll1_opy_ (u"ࠩࡵࡦࠬ੟")))
    if md5_hash in bstack1l1lll1lll_opy_:
      bstack111l11l11_opy_ = bstack1l1lll1lll_opy_[md5_hash]
      bstack1lllllllll_opy_ = datetime.datetime.now()
      bstack1l111l111l_opy_ = datetime.datetime.strptime(bstack111l11l11_opy_[bstack11l1ll1_opy_ (u"ࠪࡸ࡮ࡳࡥࡴࡶࡤࡱࡵ࠭੠")], bstack11l1ll1_opy_ (u"ࠫࠪࡪ࠯ࠦ࡯࠲ࠩ࡞ࠦࠥࡉ࠼ࠨࡑ࠿ࠫࡓࠨ੡"))
      if (bstack1lllllllll_opy_ - bstack1l111l111l_opy_).days > 30:
        return None
      elif version.parse(str(__version__)) > version.parse(bstack111l11l11_opy_[bstack11l1ll1_opy_ (u"ࠬࡹࡤ࡬ࡡࡹࡩࡷࡹࡩࡰࡰࠪ੢")]):
        return None
      return bstack111l11l11_opy_[bstack11l1ll1_opy_ (u"࠭ࡩࡥࠩ੣")]
  else:
    return None
def bstack11ll1111l_opy_(md5_hash, bstack1ll1lll1_opy_):
  bstack1l11l1llll_opy_ = os.path.join(os.path.expanduser(bstack11l1ll1_opy_ (u"ࠧࡿࠩ੤")), bstack11l1ll1_opy_ (u"ࠨ࠰ࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࠨ੥"))
  if not os.path.exists(bstack1l11l1llll_opy_):
    os.makedirs(bstack1l11l1llll_opy_)
  bstack1lll1l1l_opy_ = os.path.join(os.path.expanduser(bstack11l1ll1_opy_ (u"ࠩࢁࠫ੦")), bstack11l1ll1_opy_ (u"ࠪ࠲ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࠪ੧"), bstack11l1ll1_opy_ (u"ࠫࡦࡶࡰࡖࡲ࡯ࡳࡦࡪࡍࡅ࠷ࡋࡥࡸ࡮࠮࡫ࡵࡲࡲࠬ੨"))
  bstack1l1lll1111_opy_ = {
    bstack11l1ll1_opy_ (u"ࠬ࡯ࡤࠨ੩"): bstack1ll1lll1_opy_,
    bstack11l1ll1_opy_ (u"࠭ࡴࡪ࡯ࡨࡷࡹࡧ࡭ࡱࠩ੪"): datetime.datetime.strftime(datetime.datetime.now(), bstack11l1ll1_opy_ (u"ࠧࠦࡦ࠲ࠩࡲ࠵࡚ࠥࠢࠨࡌ࠿ࠫࡍ࠻ࠧࡖࠫ੫")),
    bstack11l1ll1_opy_ (u"ࠨࡵࡧ࡯ࡤࡼࡥࡳࡵ࡬ࡳࡳ࠭੬"): str(__version__)
  }
  if os.path.exists(bstack1lll1l1l_opy_):
    bstack1l1lll1lll_opy_ = json.load(open(bstack1lll1l1l_opy_, bstack11l1ll1_opy_ (u"ࠩࡵࡦࠬ੭")))
  else:
    bstack1l1lll1lll_opy_ = {}
  bstack1l1lll1lll_opy_[md5_hash] = bstack1l1lll1111_opy_
  with open(bstack1lll1l1l_opy_, bstack11l1ll1_opy_ (u"ࠥࡻ࠰ࠨ੮")) as outfile:
    json.dump(bstack1l1lll1lll_opy_, outfile)
def bstack1l1111111l_opy_(self):
  return
def bstack1ll111lll_opy_(self):
  return
def bstack11lll1llll_opy_(self):
  global bstack1l1llll1ll_opy_
  bstack1l1llll1ll_opy_(self)
def bstack1ll1ll1111_opy_():
  global bstack1l111lllll_opy_
  bstack1l111lllll_opy_ = True
@measure(event_name=EVENTS.bstack1ll1l1111l_opy_, stage=STAGE.bstack1l1ll1llll_opy_, bstack1l11l1ll_opy_=bstack1lll1l11l_opy_)
def bstack1l1l1l11_opy_(self):
  global bstack111111ll1_opy_
  global bstack1l1l1ll1_opy_
  global bstack1llll11l_opy_
  try:
    if bstack11l1ll1_opy_ (u"ࠫࡵࡿࡴࡦࡵࡷࠫ੯") in bstack111111ll1_opy_ and self.session_id != None and bstack1ll1l1lll_opy_(threading.current_thread(), bstack11l1ll1_opy_ (u"ࠬࡺࡥࡴࡶࡖࡸࡦࡺࡵࡴࠩੰ"), bstack11l1ll1_opy_ (u"࠭ࠧੱ")) != bstack11l1ll1_opy_ (u"ࠧࡴ࡭࡬ࡴࡵ࡫ࡤࠨੲ"):
      bstack1l111ll1l1_opy_ = bstack11l1ll1_opy_ (u"ࠨࡲࡤࡷࡸ࡫ࡤࠨੳ") if len(threading.current_thread().bstackTestErrorMessages) == 0 else bstack11l1ll1_opy_ (u"ࠩࡩࡥ࡮ࡲࡥࡥࠩੴ")
      if bstack1l111ll1l1_opy_ == bstack11l1ll1_opy_ (u"ࠪࡪࡦ࡯࡬ࡦࡦࠪੵ"):
        bstack1l1ll11lll_opy_(logger)
      if self != None:
        bstack1ll1llllll_opy_(self, bstack1l111ll1l1_opy_, bstack11l1ll1_opy_ (u"ࠫ࠱ࠦࠧ੶").join(threading.current_thread().bstackTestErrorMessages))
    threading.current_thread().testStatus = bstack11l1ll1_opy_ (u"ࠬ࠭੷")
    if bstack11l1ll1_opy_ (u"࠭ࡰࡺࡶࡨࡷࡹ࠭੸") in bstack111111ll1_opy_ and getattr(threading.current_thread(), bstack11l1ll1_opy_ (u"ࠧࡢ࠳࠴ࡽࡕࡲࡡࡵࡨࡲࡶࡲ࠭੹"), None):
      bstack11l111lll_opy_.bstack1l1l1l11ll_opy_(self, bstack1llll111l1_opy_, logger, wait=True)
    if bstack11l1ll1_opy_ (u"ࠨࡤࡨ࡬ࡦࡼࡥࠨ੺") in bstack111111ll1_opy_:
      if not threading.currentThread().behave_test_status:
        bstack1ll1llllll_opy_(self, bstack11l1ll1_opy_ (u"ࠤࡳࡥࡸࡹࡥࡥࠤ੻"))
      bstack111l1111l_opy_.bstack11111l111_opy_(self)
  except Exception as e:
    logger.debug(bstack11l1ll1_opy_ (u"ࠥࡉࡷࡸ࡯ࡳࠢࡺ࡬࡮ࡲࡥࠡ࡯ࡤࡶࡰ࡯࡮ࡨࠢࡶࡸࡦࡺࡵࡴ࠼ࠣࠦ੼") + str(e))
  bstack1llll11l_opy_(self)
  self.session_id = None
def bstack1l11ll111_opy_(self, *args, **kwargs):
  try:
    from selenium.webdriver.remote.remote_connection import RemoteConnection
    from bstack_utils.helper import bstack1l1ll11l_opy_
    global bstack111111ll1_opy_
    command_executor = kwargs.get(bstack11l1ll1_opy_ (u"ࠫࡨࡵ࡭࡮ࡣࡱࡨࡤ࡫ࡸࡦࡥࡸࡸࡴࡸࠧ੽"), bstack11l1ll1_opy_ (u"ࠬ࠭੾"))
    bstack1l1ll1ll11_opy_ = False
    if type(command_executor) == str and bstack11l1ll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡩ࡯࡮ࠩ੿") in command_executor:
      bstack1l1ll1ll11_opy_ = True
    elif isinstance(command_executor, RemoteConnection) and bstack11l1ll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡣࡰ࡯ࠪ઀") in str(getattr(command_executor, bstack11l1ll1_opy_ (u"ࠨࡡࡸࡶࡱ࠭ઁ"), bstack11l1ll1_opy_ (u"ࠩࠪં"))):
      bstack1l1ll1ll11_opy_ = True
    else:
      return bstack11lll111ll_opy_(self, *args, **kwargs)
    if bstack1l1ll1ll11_opy_:
      bstack1l11l1ll1_opy_ = bstack1l1l1lll11_opy_.bstack1ll11ll1ll_opy_(CONFIG, bstack111111ll1_opy_)
      if kwargs.get(bstack11l1ll1_opy_ (u"ࠪࡳࡵࡺࡩࡰࡰࡶࠫઃ")):
        kwargs[bstack11l1ll1_opy_ (u"ࠫࡴࡶࡴࡪࡱࡱࡷࠬ઄")] = bstack1l1ll11l_opy_(kwargs[bstack11l1ll1_opy_ (u"ࠬࡵࡰࡵ࡫ࡲࡲࡸ࠭અ")], bstack111111ll1_opy_, bstack1l11l1ll1_opy_)
      elif kwargs.get(bstack11l1ll1_opy_ (u"࠭ࡤࡦࡵ࡬ࡶࡪࡪ࡟ࡤࡣࡳࡥࡧ࡯࡬ࡪࡶ࡬ࡩࡸ࠭આ")):
        kwargs[bstack11l1ll1_opy_ (u"ࠧࡥࡧࡶ࡭ࡷ࡫ࡤࡠࡥࡤࡴࡦࡨࡩ࡭࡫ࡷ࡭ࡪࡹࠧઇ")] = bstack1l1ll11l_opy_(kwargs[bstack11l1ll1_opy_ (u"ࠨࡦࡨࡷ࡮ࡸࡥࡥࡡࡦࡥࡵࡧࡢࡪ࡮࡬ࡸ࡮࡫ࡳࠨઈ")], bstack111111ll1_opy_, bstack1l11l1ll1_opy_)
  except Exception as e:
    logger.error(bstack11l1ll1_opy_ (u"ࠤࡈࡶࡷࡵࡲࠡࡹ࡫ࡩࡳࠦࡰࡳࡱࡦࡩࡸࡹࡩ࡯ࡩࠣࡗࡉࡑࠠࡤࡣࡳࡷ࠿ࠦࡻࡾࠤઉ").format(str(e)))
  return bstack11lll111ll_opy_(self, *args, **kwargs)
@measure(event_name=EVENTS.bstack1l11ll1111_opy_, stage=STAGE.bstack1l1ll1llll_opy_, bstack1l11l1ll_opy_=bstack1lll1l11l_opy_)
def bstack11llll1111_opy_(self, command_executor=bstack11l1ll1_opy_ (u"ࠥ࡬ࡹࡺࡰ࠻࠱࠲࠵࠷࠽࠮࠱࠰࠳࠲࠶ࡀ࠴࠵࠶࠷ࠦઊ"), *args, **kwargs):
  bstack1llll1ll_opy_ = bstack1l11ll111_opy_(self, command_executor=command_executor, *args, **kwargs)
  if not bstack11ll1ll1_opy_.on():
    return bstack1llll1ll_opy_
  try:
    logger.debug(bstack11l1ll1_opy_ (u"ࠫࡈࡵ࡭࡮ࡣࡱࡨࠥࡋࡸࡦࡥࡸࡸࡴࡸࠠࡸࡪࡨࡲࠥࡈࡲࡰࡹࡶࡩࡷ࡙ࡴࡢࡥ࡮ࠤࡆࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࠡ࡫ࡶࠤ࡫ࡧ࡬ࡴࡧࠣ࠱ࠥࢁࡽࠨઋ").format(str(command_executor)))
    logger.debug(bstack11l1ll1_opy_ (u"ࠬࡎࡵࡣࠢࡘࡖࡑࠦࡩࡴࠢ࠰ࠤࢀࢃࠧઌ").format(str(command_executor._url)))
    from selenium.webdriver.remote.remote_connection import RemoteConnection
    if isinstance(command_executor, RemoteConnection) and bstack11l1ll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡩ࡯࡮ࠩઍ") in command_executor._url:
      bstack1ll1l11l1_opy_.bstack1l111llll1_opy_(bstack11l1ll1_opy_ (u"ࠧࡣࡵࡷࡥࡨࡱ࡟ࡴࡧࡶࡷ࡮ࡵ࡮ࠨ઎"), True)
  except:
    pass
  if (isinstance(command_executor, str) and bstack11l1ll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡤࡱࡰࠫએ") in command_executor):
    bstack1ll1l11l1_opy_.bstack1l111llll1_opy_(bstack11l1ll1_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬ࡡࡶࡩࡸࡹࡩࡰࡰࠪઐ"), True)
  threading.current_thread().bstackSessionDriver = self
  bstack1ll1l1l1l_opy_ = getattr(threading.current_thread(), bstack11l1ll1_opy_ (u"ࠪࡦࡸࡺࡡࡤ࡭ࡗࡩࡸࡺࡍࡦࡶࡤࠫઑ"), None)
  if bstack11l1ll1_opy_ (u"ࠫࡧ࡫ࡨࡢࡸࡨࠫ઒") in bstack111111ll1_opy_ or bstack11l1ll1_opy_ (u"ࠬࡸ࡯ࡣࡱࡷࠫઓ") in bstack111111ll1_opy_:
    bstack11111l1l1_opy_.bstack1111l11l1_opy_(self)
  if bstack11l1ll1_opy_ (u"࠭ࡰࡺࡶࡨࡷࡹ࠭ઔ") in bstack111111ll1_opy_ and bstack1ll1l1l1l_opy_ and bstack1ll1l1l1l_opy_.get(bstack11l1ll1_opy_ (u"ࠧࡴࡶࡤࡸࡺࡹࠧક"), bstack11l1ll1_opy_ (u"ࠨࠩખ")) == bstack11l1ll1_opy_ (u"ࠩࡳࡩࡳࡪࡩ࡯ࡩࠪગ"):
    bstack11111l1l1_opy_.bstack1111l11l1_opy_(self)
  return bstack1llll1ll_opy_
def bstack1llll1lll1_opy_(args):
  return bstack11l1ll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡡࡨࡼࡪࡩࡵࡵࡱࡵࠫઘ") in str(args)
def bstack1l111ll11l_opy_(self, driver_command, *args, **kwargs):
  global bstack11l111l1_opy_
  global bstack11ll1l1lll_opy_
  bstack1l1111ll1_opy_ = bstack1ll1l1lll_opy_(threading.current_thread(), bstack11l1ll1_opy_ (u"ࠫ࡮ࡹࡁ࠲࠳ࡼࡘࡪࡹࡴࠨઙ"), None) and bstack1ll1l1lll_opy_(
          threading.current_thread(), bstack11l1ll1_opy_ (u"ࠬࡧ࠱࠲ࡻࡓࡰࡦࡺࡦࡰࡴࡰࠫચ"), None)
  bstack11ll1l1l_opy_ = getattr(self, bstack11l1ll1_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰࡇ࠱࠲ࡻࡖ࡬ࡴࡻ࡬ࡥࡕࡦࡥࡳ࠭છ"), None) != None and getattr(self, bstack11l1ll1_opy_ (u"ࠧࡣࡵࡷࡥࡨࡱࡁ࠲࠳ࡼࡗ࡭ࡵࡵ࡭ࡦࡖࡧࡦࡴࠧજ"), None) == True
  if not bstack11ll1l1lll_opy_ and bstack1111l1111_opy_ and bstack11l1ll1_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠨઝ") in CONFIG and CONFIG[bstack11l1ll1_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠩઞ")] == True and bstack1l1ll1111l_opy_.bstack11l1l1111_opy_(driver_command) and (bstack11ll1l1l_opy_ or bstack1l1111ll1_opy_) and not bstack1llll1lll1_opy_(args):
    try:
      bstack11ll1l1lll_opy_ = True
      logger.debug(bstack11l1ll1_opy_ (u"ࠪࡔࡪࡸࡦࡰࡴࡰ࡭ࡳ࡭ࠠࡴࡥࡤࡲࠥ࡬࡯ࡳࠢࡾࢁࠬટ").format(driver_command))
      logger.debug(perform_scan(self, driver_command=driver_command))
    except Exception as err:
      logger.debug(bstack11l1ll1_opy_ (u"ࠫࡋࡧࡩ࡭ࡧࡧࠤࡹࡵࠠࡱࡧࡵࡪࡴࡸ࡭ࠡࡵࡦࡥࡳࠦࡻࡾࠩઠ").format(str(err)))
    bstack11ll1l1lll_opy_ = False
  response = bstack11l111l1_opy_(self, driver_command, *args, **kwargs)
  if (bstack11l1ll1_opy_ (u"ࠬࡸ࡯ࡣࡱࡷࠫડ") in str(bstack111111ll1_opy_).lower() or bstack11l1ll1_opy_ (u"࠭ࡢࡦࡪࡤࡺࡪ࠭ઢ") in str(bstack111111ll1_opy_).lower()) and bstack11ll1ll1_opy_.on():
    try:
      if driver_command == bstack11l1ll1_opy_ (u"ࠧࡴࡥࡵࡩࡪࡴࡳࡩࡱࡷࠫણ"):
        bstack11111l1l1_opy_.bstack1lllll1l1l_opy_({
            bstack11l1ll1_opy_ (u"ࠨ࡫ࡰࡥ࡬࡫ࠧત"): response[bstack11l1ll1_opy_ (u"ࠩࡹࡥࡱࡻࡥࠨથ")],
            bstack11l1ll1_opy_ (u"ࠪࡸࡪࡹࡴࡠࡴࡸࡲࡤࡻࡵࡪࡦࠪદ"): bstack11111l1l1_opy_.current_test_uuid() if bstack11111l1l1_opy_.current_test_uuid() else bstack11ll1ll1_opy_.current_hook_uuid()
        })
    except:
      pass
  return response
@measure(event_name=EVENTS.bstack1l1ll1ll1_opy_, stage=STAGE.bstack1l1ll1llll_opy_, bstack1l11l1ll_opy_=bstack1lll1l11l_opy_)
def bstack11l111111_opy_(self, command_executor,
             desired_capabilities=None, browser_profile=None, proxy=None,
             keep_alive=True, file_detector=None, options=None, *args, **kwargs):
  global CONFIG
  global bstack1l1l1ll1_opy_
  global bstack1ll1ll1ll_opy_
  global bstack1lll1l11l_opy_
  global bstack11ll1ll1l1_opy_
  global bstack1lll1l111_opy_
  global bstack111111ll1_opy_
  global bstack11lll111ll_opy_
  global bstack1l1ll1l1l1_opy_
  global bstack1l11lll1l1_opy_
  global bstack1llll111l1_opy_
  CONFIG[bstack11l1ll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡖࡈࡐ࠭ધ")] = str(bstack111111ll1_opy_) + str(__version__)
  bstack11ll1ll11l_opy_ = os.environ[bstack11l1ll1_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣ࡙ࡋࡓࡕࡊࡘࡆࡤ࡛ࡕࡊࡆࠪન")]
  bstack1l11l1ll1_opy_ = bstack1l1l1lll11_opy_.bstack1ll11ll1ll_opy_(CONFIG, bstack111111ll1_opy_)
  CONFIG[bstack11l1ll1_opy_ (u"࠭ࡴࡦࡵࡷ࡬ࡺࡨࡂࡶ࡫࡯ࡨ࡚ࡻࡩࡥࠩ઩")] = bstack11ll1ll11l_opy_
  CONFIG[bstack11l1ll1_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡖࡲࡰࡦࡸࡧࡹࡓࡡࡱࠩપ")] = bstack1l11l1ll1_opy_
  command_executor = bstack1l11111l1_opy_()
  logger.debug(bstack11ll111l11_opy_.format(command_executor))
  proxy = bstack1l11l1l111_opy_(CONFIG, proxy)
  bstack1ll1lll1l_opy_ = 0 if bstack1ll1ll1ll_opy_ < 0 else bstack1ll1ll1ll_opy_
  try:
    if bstack11ll1ll1l1_opy_ is True:
      bstack1ll1lll1l_opy_ = int(multiprocessing.current_process().name)
    elif bstack1lll1l111_opy_ is True:
      bstack1ll1lll1l_opy_ = int(threading.current_thread().name)
  except:
    bstack1ll1lll1l_opy_ = 0
  bstack11l11ll1_opy_ = bstack1l11llll1l_opy_(CONFIG, bstack1ll1lll1l_opy_)
  logger.debug(bstack1llll11l1l_opy_.format(str(bstack11l11ll1_opy_)))
  if bstack11l1ll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࡌࡰࡥࡤࡰࠬફ") in CONFIG and bstack111l1l111_opy_(CONFIG[bstack11l1ll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡍࡱࡦࡥࡱ࠭બ")]):
    bstack11ll1lllll_opy_(bstack11l11ll1_opy_)
  if bstack11lll11ll1_opy_.bstack111l1l1l_opy_(CONFIG, bstack1ll1lll1l_opy_) and bstack11lll11ll1_opy_.bstack11llllll_opy_(bstack11l11ll1_opy_, options, desired_capabilities):
    threading.current_thread().a11yPlatform = True
    if cli.accessibility is None or not cli.accessibility.is_enabled():
      bstack11lll11ll1_opy_.set_capabilities(bstack11l11ll1_opy_, CONFIG)
  if desired_capabilities:
    bstack1111l111_opy_ = bstack1l11l11ll_opy_(desired_capabilities)
    bstack1111l111_opy_[bstack11l1ll1_opy_ (u"ࠪࡹࡸ࡫ࡗ࠴ࡅࠪભ")] = bstack1l1lll1l1l_opy_(CONFIG)
    bstack1l11lllll1_opy_ = bstack1l11llll1l_opy_(bstack1111l111_opy_)
    if bstack1l11lllll1_opy_:
      bstack11l11ll1_opy_ = update(bstack1l11lllll1_opy_, bstack11l11ll1_opy_)
    desired_capabilities = None
  if options:
    bstack11lll1l11_opy_(options, bstack11l11ll1_opy_)
  if not options:
    options = bstack11l1ll1l1_opy_(bstack11l11ll1_opy_)
  bstack1llll111l1_opy_ = CONFIG.get(bstack11l1ll1_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧમ"))[bstack1ll1lll1l_opy_]
  if proxy and bstack1ll111111l_opy_() >= version.parse(bstack11l1ll1_opy_ (u"ࠬ࠺࠮࠲࠲࠱࠴ࠬય")):
    options.proxy(proxy)
  if options and bstack1ll111111l_opy_() >= version.parse(bstack11l1ll1_opy_ (u"࠭࠳࠯࠺࠱࠴ࠬર")):
    desired_capabilities = None
  if (
          not options and not desired_capabilities
  ) or (
          bstack1ll111111l_opy_() < version.parse(bstack11l1ll1_opy_ (u"ࠧ࠴࠰࠻࠲࠵࠭઱")) and not desired_capabilities
  ):
    desired_capabilities = {}
    desired_capabilities.update(bstack11l11ll1_opy_)
  logger.info(bstack1ll1ll11_opy_)
  bstack1ll111ll1l_opy_.end(EVENTS.bstack1l111l11l_opy_.value, EVENTS.bstack1l111l11l_opy_.value + bstack11l1ll1_opy_ (u"ࠣ࠼ࡶࡸࡦࡸࡴࠣલ"), EVENTS.bstack1l111l11l_opy_.value + bstack11l1ll1_opy_ (u"ࠤ࠽ࡩࡳࡪࠢળ"), status=True, failure=None, test_name=bstack1lll1l11l_opy_)
  if bstack1ll111111l_opy_() >= version.parse(bstack11l1ll1_opy_ (u"ࠪ࠸࠳࠷࠰࠯࠲ࠪ઴")):
    bstack11lll111ll_opy_(self, command_executor=command_executor,
              options=options, keep_alive=keep_alive, file_detector=file_detector, *args, **kwargs)
  elif bstack1ll111111l_opy_() >= version.parse(bstack11l1ll1_opy_ (u"ࠫ࠸࠴࠸࠯࠲ࠪવ")):
    bstack11lll111ll_opy_(self, command_executor=command_executor,
              desired_capabilities=desired_capabilities, options=options,
              browser_profile=browser_profile, proxy=proxy,
              keep_alive=keep_alive, file_detector=file_detector)
  elif bstack1ll111111l_opy_() >= version.parse(bstack11l1ll1_opy_ (u"ࠬ࠸࠮࠶࠵࠱࠴ࠬશ")):
    bstack11lll111ll_opy_(self, command_executor=command_executor,
              desired_capabilities=desired_capabilities,
              browser_profile=browser_profile, proxy=proxy,
              keep_alive=keep_alive, file_detector=file_detector)
  else:
    bstack11lll111ll_opy_(self, command_executor=command_executor,
              desired_capabilities=desired_capabilities,
              browser_profile=browser_profile, proxy=proxy,
              keep_alive=keep_alive)
  try:
    bstack1lll1lllll_opy_ = bstack11l1ll1_opy_ (u"࠭ࠧષ")
    if bstack1ll111111l_opy_() >= version.parse(bstack11l1ll1_opy_ (u"ࠧ࠵࠰࠳࠲࠵ࡨ࠱ࠨસ")):
      bstack1lll1lllll_opy_ = self.caps.get(bstack11l1ll1_opy_ (u"ࠣࡱࡳࡸ࡮ࡳࡡ࡭ࡊࡸࡦ࡚ࡸ࡬ࠣહ"))
    else:
      bstack1lll1lllll_opy_ = self.capabilities.get(bstack11l1ll1_opy_ (u"ࠤࡲࡴࡹ࡯࡭ࡢ࡮ࡋࡹࡧ࡛ࡲ࡭ࠤ઺"))
    if bstack1lll1lllll_opy_:
      bstack1l1111l11_opy_(bstack1lll1lllll_opy_)
      if bstack1ll111111l_opy_() <= version.parse(bstack11l1ll1_opy_ (u"ࠪ࠷࠳࠷࠳࠯࠲ࠪ઻")):
        self.command_executor._url = bstack11l1ll1_opy_ (u"ࠦ࡭ࡺࡴࡱ࠼࠲࠳઼ࠧ") + bstack1l1ll11ll1_opy_ + bstack11l1ll1_opy_ (u"ࠧࡀ࠸࠱࠱ࡺࡨ࠴࡮ࡵࡣࠤઽ")
      else:
        self.command_executor._url = bstack11l1ll1_opy_ (u"ࠨࡨࡵࡶࡳࡷ࠿࠵࠯ࠣા") + bstack1lll1lllll_opy_ + bstack11l1ll1_opy_ (u"ࠢ࠰ࡹࡧ࠳࡭ࡻࡢࠣિ")
      logger.debug(bstack1ll1111l1_opy_.format(bstack1lll1lllll_opy_))
    else:
      logger.debug(bstack11l11ll1l_opy_.format(bstack11l1ll1_opy_ (u"ࠣࡑࡳࡸ࡮ࡳࡡ࡭ࠢࡋࡹࡧࠦ࡮ࡰࡶࠣࡪࡴࡻ࡮ࡥࠤી")))
  except Exception as e:
    logger.debug(bstack11l11ll1l_opy_.format(e))
  if bstack11l1ll1_opy_ (u"ࠩࡵࡳࡧࡵࡴࠨુ") in bstack111111ll1_opy_:
    bstack1llllll11l_opy_(bstack1ll1ll1ll_opy_, bstack1l11lll1l1_opy_)
  bstack1l1l1ll1_opy_ = self.session_id
  if bstack11l1ll1_opy_ (u"ࠪࡴࡾࡺࡥࡴࡶࠪૂ") in bstack111111ll1_opy_ or bstack11l1ll1_opy_ (u"ࠫࡧ࡫ࡨࡢࡸࡨࠫૃ") in bstack111111ll1_opy_ or bstack11l1ll1_opy_ (u"ࠬࡸ࡯ࡣࡱࡷࠫૄ") in bstack111111ll1_opy_:
    threading.current_thread().bstackSessionId = self.session_id
    threading.current_thread().bstackSessionDriver = self
    threading.current_thread().bstackTestErrorMessages = []
  bstack1ll1l1l1l_opy_ = getattr(threading.current_thread(), bstack11l1ll1_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰ࡚ࡥࡴࡶࡐࡩࡹࡧࠧૅ"), None)
  if bstack11l1ll1_opy_ (u"ࠧࡣࡧ࡫ࡥࡻ࡫ࠧ૆") in bstack111111ll1_opy_ or bstack11l1ll1_opy_ (u"ࠨࡴࡲࡦࡴࡺࠧે") in bstack111111ll1_opy_:
    bstack11111l1l1_opy_.bstack1111l11l1_opy_(self)
  if bstack11l1ll1_opy_ (u"ࠩࡳࡽࡹ࡫ࡳࡵࠩૈ") in bstack111111ll1_opy_ and bstack1ll1l1l1l_opy_ and bstack1ll1l1l1l_opy_.get(bstack11l1ll1_opy_ (u"ࠪࡷࡹࡧࡴࡶࡵࠪૉ"), bstack11l1ll1_opy_ (u"ࠫࠬ૊")) == bstack11l1ll1_opy_ (u"ࠬࡶࡥ࡯ࡦ࡬ࡲ࡬࠭ો"):
    bstack11111l1l1_opy_.bstack1111l11l1_opy_(self)
  bstack1l1ll1l1l1_opy_.append(self)
  if bstack11l1ll1_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠩૌ") in CONFIG and bstack11l1ll1_opy_ (u"ࠧࡴࡧࡶࡷ࡮ࡵ࡮ࡏࡣࡰࡩ્ࠬ") in CONFIG[bstack11l1ll1_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫ૎")][bstack1ll1lll1l_opy_]:
    bstack1lll1l11l_opy_ = CONFIG[bstack11l1ll1_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬ૏")][bstack1ll1lll1l_opy_][bstack11l1ll1_opy_ (u"ࠪࡷࡪࡹࡳࡪࡱࡱࡒࡦࡳࡥࠨૐ")]
  logger.debug(bstack1l1ll111l_opy_.format(bstack1l1l1ll1_opy_))
try:
  try:
    import Browser
    from subprocess import Popen
    from browserstack_sdk.__init__ import bstack11l11l11_opy_
    def bstack1l1l1l1l1_opy_(self, args, bufsize=-1, executable=None,
              stdin=None, stdout=None, stderr=None,
              preexec_fn=None, close_fds=True,
              shell=False, cwd=None, env=None, universal_newlines=None,
              startupinfo=None, creationflags=0,
              restore_signals=True, start_new_session=False,
              pass_fds=(), *, user=None, group=None, extra_groups=None,
              encoding=None, errors=None, text=None, umask=-1, pipesize=-1):
      global CONFIG
      global bstack1111111ll_opy_
      if(bstack11l1ll1_opy_ (u"ࠦ࡮ࡴࡤࡦࡺ࠱࡮ࡸࠨ૑") in args[1]):
        with open(os.path.join(os.path.expanduser(bstack11l1ll1_opy_ (u"ࠬࢄࠧ૒")), bstack11l1ll1_opy_ (u"࠭࠮ࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠭૓"), bstack11l1ll1_opy_ (u"ࠧ࠯ࡵࡨࡷࡸ࡯࡯࡯࡫ࡧࡷ࠳ࡺࡸࡵࠩ૔")), bstack11l1ll1_opy_ (u"ࠨࡹࠪ૕")) as fp:
          fp.write(bstack11l1ll1_opy_ (u"ࠤࠥ૖"))
        if(not os.path.exists(os.path.join(os.path.dirname(args[1]), bstack11l1ll1_opy_ (u"ࠥ࡭ࡳࡪࡥࡹࡡࡥࡷࡹࡧࡣ࡬࠰࡭ࡷࠧ૗")))):
          with open(args[1], bstack11l1ll1_opy_ (u"ࠫࡷ࠭૘")) as f:
            lines = f.readlines()
            index = next((i for i, line in enumerate(lines) if bstack11l1ll1_opy_ (u"ࠬࡧࡳࡺࡰࡦࠤ࡫ࡻ࡮ࡤࡶ࡬ࡳࡳࠦ࡟࡯ࡧࡺࡔࡦ࡭ࡥࠩࡥࡲࡲࡹ࡫ࡸࡵ࠮ࠣࡴࡦ࡭ࡥࠡ࠿ࠣࡺࡴ࡯ࡤࠡ࠲ࠬࠫ૙") in line), None)
            if index is not None:
                lines.insert(index+2, bstack111111ll_opy_)
            if bstack11l1ll1_opy_ (u"࠭ࡴࡶࡴࡥࡳࡘࡩࡡ࡭ࡧࠪ૚") in CONFIG and str(CONFIG[bstack11l1ll1_opy_ (u"ࠧࡵࡷࡵࡦࡴ࡙ࡣࡢ࡮ࡨࠫ૛")]).lower() != bstack11l1ll1_opy_ (u"ࠨࡨࡤࡰࡸ࡫ࠧ૜"):
                bstack1l11111l_opy_ = bstack11l11l11_opy_()
                bstack1lllllll11_opy_ = bstack11l1ll1_opy_ (u"ࠩࠪࠫࠏ࠵ࠪࠡ࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࠥ࠰࠯ࠋࡥࡲࡲࡸࡺࠠࡣࡵࡷࡥࡨࡱ࡟ࡱࡣࡷ࡬ࠥࡃࠠࡱࡴࡲࡧࡪࡹࡳ࠯ࡣࡵ࡫ࡻࡡࡰࡳࡱࡦࡩࡸࡹ࠮ࡢࡴࡪࡺ࠳ࡲࡥ࡯ࡩࡷ࡬ࠥ࠳ࠠ࠴࡟࠾ࠎࡨࡵ࡮ࡴࡶࠣࡦࡸࡺࡡࡤ࡭ࡢࡧࡦࡶࡳࠡ࠿ࠣࡴࡷࡵࡣࡦࡵࡶ࠲ࡦࡸࡧࡷ࡝ࡳࡶࡴࡩࡥࡴࡵ࠱ࡥࡷ࡭ࡶ࠯࡮ࡨࡲ࡬ࡺࡨࠡ࠯ࠣ࠵ࡢࡁࠊࡤࡱࡱࡷࡹࠦࡰࡠ࡫ࡱࡨࡪࡾࠠ࠾ࠢࡳࡶࡴࡩࡥࡴࡵ࠱ࡥࡷ࡭ࡶ࡜ࡲࡵࡳࡨ࡫ࡳࡴ࠰ࡤࡶ࡬ࡼ࠮࡭ࡧࡱ࡫ࡹ࡮ࠠ࠮ࠢ࠵ࡡࡀࠐࡰࡳࡱࡦࡩࡸࡹ࠮ࡢࡴࡪࡺࠥࡃࠠࡱࡴࡲࡧࡪࡹࡳ࠯ࡣࡵ࡫ࡻ࠴ࡳ࡭࡫ࡦࡩ࠭࠶ࠬࠡࡲࡵࡳࡨ࡫ࡳࡴ࠰ࡤࡶ࡬ࡼ࠮࡭ࡧࡱ࡫ࡹ࡮ࠠ࠮ࠢ࠶࠭ࡀࠐࡣࡰࡰࡶࡸࠥ࡯࡭ࡱࡱࡵࡸࡤࡶ࡬ࡢࡻࡺࡶ࡮࡭ࡨࡵ࠶ࡢࡦࡸࡺࡡࡤ࡭ࠣࡁࠥࡸࡥࡲࡷ࡬ࡶࡪ࠮ࠢࡱ࡮ࡤࡽࡼࡸࡩࡨࡪࡷࠦ࠮ࡁࠊࡪ࡯ࡳࡳࡷࡺ࡟ࡱ࡮ࡤࡽࡼࡸࡩࡨࡪࡷ࠸ࡤࡨࡳࡵࡣࡦ࡯࠳ࡩࡨࡳࡱࡰ࡭ࡺࡳ࠮࡭ࡣࡸࡲࡨ࡮ࠠ࠾ࠢࡤࡷࡾࡴࡣࠡࠪ࡯ࡥࡺࡴࡣࡩࡑࡳࡸ࡮ࡵ࡮ࡴࠫࠣࡁࡃࠦࡻࡼࠌࠣࠤࡱ࡫ࡴࠡࡥࡤࡴࡸࡁࠊࠡࠢࡷࡶࡾࠦࡻࡼࠌࠣࠤࠥࠦࡣࡢࡲࡶࠤࡂࠦࡊࡔࡑࡑ࠲ࡵࡧࡲࡴࡧࠫࡦࡸࡺࡡࡤ࡭ࡢࡧࡦࡶࡳࠪ࠽ࠍࠤࠥࢃࡽࠡࡥࡤࡸࡨ࡮ࠠࠩࡧࡻ࠭ࠥࢁࡻࠋࠢࠣࠤࠥࡩ࡯࡯ࡵࡲࡰࡪ࠴ࡥࡳࡴࡲࡶ࠭ࠨࡆࡢ࡫࡯ࡩࡩࠦࡴࡰࠢࡳࡥࡷࡹࡥࠡࡥࡤࡴࡦࡨࡩ࡭࡫ࡷ࡭ࡪࡹ࠺ࠣ࠮ࠣࡩࡽ࠯࠻ࠋࠢࠣࢁࢂࠐࠠࠡࡴࡨࡸࡺࡸ࡮ࠡࡣࡺࡥ࡮ࡺࠠࡪ࡯ࡳࡳࡷࡺ࡟ࡱ࡮ࡤࡽࡼࡸࡩࡨࡪࡷ࠸ࡤࡨࡳࡵࡣࡦ࡯࠳ࡩࡨࡳࡱࡰ࡭ࡺࡳ࠮ࡤࡱࡱࡲࡪࡩࡴࠩࡽࡾࠎࠥࠦࠠࠡࡹࡶࡉࡳࡪࡰࡰ࡫ࡱࡸ࠿ࠦࠧࡼࡥࡧࡴ࡚ࡸ࡬ࡾࠩࠣ࠯ࠥ࡫࡮ࡤࡱࡧࡩ࡚ࡘࡉࡄࡱࡰࡴࡴࡴࡥ࡯ࡶࠫࡎࡘࡕࡎ࠯ࡵࡷࡶ࡮ࡴࡧࡪࡨࡼࠬࡨࡧࡰࡴࠫࠬ࠰ࠏࠦࠠࠡࠢ࠱࠲࠳ࡲࡡࡶࡰࡦ࡬ࡔࡶࡴࡪࡱࡱࡷࠏࠦࠠࡾࡿࠬ࠿ࠏࢃࡽ࠼ࠌ࠲࠮ࠥࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾ࠢ࠭࠳ࠏ࠭ࠧࠨ૝").format(bstack1l11111l_opy_=bstack1l11111l_opy_)
            lines.insert(1, bstack1lllllll11_opy_)
            f.seek(0)
            with open(os.path.join(os.path.dirname(args[1]), bstack11l1ll1_opy_ (u"ࠥ࡭ࡳࡪࡥࡹࡡࡥࡷࡹࡧࡣ࡬࠰࡭ࡷࠧ૞")), bstack11l1ll1_opy_ (u"ࠫࡼ࠭૟")) as bstack1ll11l1111_opy_:
              bstack1ll11l1111_opy_.writelines(lines)
        CONFIG[bstack11l1ll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡗࡉࡑࠧૠ")] = str(bstack111111ll1_opy_) + str(__version__)
        bstack11ll1ll11l_opy_ = os.environ[bstack11l1ll1_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡚ࡅࡔࡖࡋ࡙ࡇࡥࡕࡖࡋࡇࠫૡ")]
        bstack1l11l1ll1_opy_ = bstack1l1l1lll11_opy_.bstack1ll11ll1ll_opy_(CONFIG, bstack111111ll1_opy_)
        CONFIG[bstack11l1ll1_opy_ (u"ࠧࡵࡧࡶࡸ࡭ࡻࡢࡃࡷ࡬ࡰࡩ࡛ࡵࡪࡦࠪૢ")] = bstack11ll1ll11l_opy_
        CONFIG[bstack11l1ll1_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡐࡳࡱࡧࡹࡨࡺࡍࡢࡲࠪૣ")] = bstack1l11l1ll1_opy_
        bstack1ll1lll1l_opy_ = 0 if bstack1ll1ll1ll_opy_ < 0 else bstack1ll1ll1ll_opy_
        try:
          if bstack11ll1ll1l1_opy_ is True:
            bstack1ll1lll1l_opy_ = int(multiprocessing.current_process().name)
          elif bstack1lll1l111_opy_ is True:
            bstack1ll1lll1l_opy_ = int(threading.current_thread().name)
        except:
          bstack1ll1lll1l_opy_ = 0
        CONFIG[bstack11l1ll1_opy_ (u"ࠤࡸࡷࡪ࡝࠳ࡄࠤ૤")] = False
        CONFIG[bstack11l1ll1_opy_ (u"ࠥ࡭ࡸࡖ࡬ࡢࡻࡺࡶ࡮࡭ࡨࡵࠤ૥")] = True
        bstack11l11ll1_opy_ = bstack1l11llll1l_opy_(CONFIG, bstack1ll1lll1l_opy_)
        logger.debug(bstack1llll11l1l_opy_.format(str(bstack11l11ll1_opy_)))
        if CONFIG.get(bstack11l1ll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡏࡳࡨࡧ࡬ࠨ૦")):
          bstack11ll1lllll_opy_(bstack11l11ll1_opy_)
        if bstack11l1ll1_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡳࠨ૧") in CONFIG and bstack11l1ll1_opy_ (u"࠭ࡳࡦࡵࡶ࡭ࡴࡴࡎࡢ࡯ࡨࠫ૨") in CONFIG[bstack11l1ll1_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵࠪ૩")][bstack1ll1lll1l_opy_]:
          bstack1lll1l11l_opy_ = CONFIG[bstack11l1ll1_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫ૪")][bstack1ll1lll1l_opy_][bstack11l1ll1_opy_ (u"ࠩࡶࡩࡸࡹࡩࡰࡰࡑࡥࡲ࡫ࠧ૫")]
        args.append(os.path.join(os.path.expanduser(bstack11l1ll1_opy_ (u"ࠪࢂࠬ૬")), bstack11l1ll1_opy_ (u"ࠫ࠳ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࠫ૭"), bstack11l1ll1_opy_ (u"ࠬ࠴ࡳࡦࡵࡶ࡭ࡴࡴࡩࡥࡵ࠱ࡸࡽࡺࠧ૮")))
        args.append(str(threading.get_ident()))
        args.append(json.dumps(bstack11l11ll1_opy_))
        args[1] = os.path.join(os.path.dirname(args[1]), bstack11l1ll1_opy_ (u"ࠨࡩ࡯ࡦࡨࡼࡤࡨࡳࡵࡣࡦ࡯࠳ࡰࡳࠣ૯"))
      bstack1111111ll_opy_ = True
      return bstack1lllll1ll1_opy_(self, args, bufsize=bufsize, executable=executable,
                    stdin=stdin, stdout=stdout, stderr=stderr,
                    preexec_fn=preexec_fn, close_fds=close_fds,
                    shell=shell, cwd=cwd, env=env, universal_newlines=universal_newlines,
                    startupinfo=startupinfo, creationflags=creationflags,
                    restore_signals=restore_signals, start_new_session=start_new_session,
                    pass_fds=pass_fds, user=user, group=group, extra_groups=extra_groups,
                    encoding=encoding, errors=errors, text=text, umask=umask, pipesize=pipesize)
  except Exception as e:
    pass
  import playwright._impl._api_structures
  import playwright._impl._helper
  def bstack1ll1ll1l1l_opy_(self,
        executablePath = None,
        channel = None,
        args = None,
        ignoreDefaultArgs = None,
        handleSIGINT = None,
        handleSIGTERM = None,
        handleSIGHUP = None,
        timeout = None,
        env = None,
        headless = None,
        devtools = None,
        proxy = None,
        downloadsPath = None,
        slowMo = None,
        tracesDir = None,
        chromiumSandbox = None,
        firefoxUserPrefs = None
        ):
    global CONFIG
    global bstack1ll1ll1ll_opy_
    global bstack1lll1l11l_opy_
    global bstack11ll1ll1l1_opy_
    global bstack1lll1l111_opy_
    global bstack111111ll1_opy_
    CONFIG[bstack11l1ll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࡙ࡄࡌࠩ૰")] = str(bstack111111ll1_opy_) + str(__version__)
    bstack11ll1ll11l_opy_ = os.environ[bstack11l1ll1_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡕࡇࡖࡘࡍ࡛ࡂࡠࡗࡘࡍࡉ࠭૱")]
    bstack1l11l1ll1_opy_ = bstack1l1l1lll11_opy_.bstack1ll11ll1ll_opy_(CONFIG, bstack111111ll1_opy_)
    CONFIG[bstack11l1ll1_opy_ (u"ࠩࡷࡩࡸࡺࡨࡶࡤࡅࡹ࡮ࡲࡤࡖࡷ࡬ࡨࠬ૲")] = bstack11ll1ll11l_opy_
    CONFIG[bstack11l1ll1_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡒࡵࡳࡩࡻࡣࡵࡏࡤࡴࠬ૳")] = bstack1l11l1ll1_opy_
    bstack1ll1lll1l_opy_ = 0 if bstack1ll1ll1ll_opy_ < 0 else bstack1ll1ll1ll_opy_
    try:
      if bstack11ll1ll1l1_opy_ is True:
        bstack1ll1lll1l_opy_ = int(multiprocessing.current_process().name)
      elif bstack1lll1l111_opy_ is True:
        bstack1ll1lll1l_opy_ = int(threading.current_thread().name)
    except:
      bstack1ll1lll1l_opy_ = 0
    CONFIG[bstack11l1ll1_opy_ (u"ࠦ࡮ࡹࡐ࡭ࡣࡼࡻࡷ࡯ࡧࡩࡶࠥ૴")] = True
    bstack11l11ll1_opy_ = bstack1l11llll1l_opy_(CONFIG, bstack1ll1lll1l_opy_)
    logger.debug(bstack1llll11l1l_opy_.format(str(bstack11l11ll1_opy_)))
    if CONFIG.get(bstack11l1ll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡐࡴࡩࡡ࡭ࠩ૵")):
      bstack11ll1lllll_opy_(bstack11l11ll1_opy_)
    if bstack11l1ll1_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠩ૶") in CONFIG and bstack11l1ll1_opy_ (u"ࠧࡴࡧࡶࡷ࡮ࡵ࡮ࡏࡣࡰࡩࠬ૷") in CONFIG[bstack11l1ll1_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫ૸")][bstack1ll1lll1l_opy_]:
      bstack1lll1l11l_opy_ = CONFIG[bstack11l1ll1_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬૹ")][bstack1ll1lll1l_opy_][bstack11l1ll1_opy_ (u"ࠪࡷࡪࡹࡳࡪࡱࡱࡒࡦࡳࡥࠨૺ")]
    import urllib
    import json
    if bstack11l1ll1_opy_ (u"ࠫࡹࡻࡲࡣࡱࡖࡧࡦࡲࡥࠨૻ") in CONFIG and str(CONFIG[bstack11l1ll1_opy_ (u"ࠬࡺࡵࡳࡤࡲࡗࡨࡧ࡬ࡦࠩૼ")]).lower() != bstack11l1ll1_opy_ (u"࠭ࡦࡢ࡮ࡶࡩࠬ૽"):
        bstack1l111lll1_opy_ = bstack11l11l11_opy_()
        bstack1l11111l_opy_ = bstack1l111lll1_opy_ + urllib.parse.quote(json.dumps(bstack11l11ll1_opy_))
    else:
        bstack1l11111l_opy_ = bstack11l1ll1_opy_ (u"ࠧࡸࡵࡶ࠾࠴࠵ࡣࡥࡲ࠱ࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡦࡳࡲ࠵ࡰ࡭ࡣࡼࡻࡷ࡯ࡧࡩࡶࡂࡧࡦࡶࡳ࠾ࠩ૾") + urllib.parse.quote(json.dumps(bstack11l11ll1_opy_))
    browser = self.connect(bstack1l11111l_opy_)
    return browser
except Exception as e:
    pass
def bstack11lll1l1ll_opy_():
    global bstack1111111ll_opy_
    global bstack111111ll1_opy_
    global CONFIG
    try:
        from playwright._impl._browser_type import BrowserType
        from bstack_utils.helper import bstack11lll1ll1_opy_
        global bstack1ll1l11l1_opy_
        if not bstack1111l1111_opy_:
          global bstack1l1ll1l1_opy_
          if not bstack1l1ll1l1_opy_:
            from bstack_utils.helper import bstack1l1ll1l1l_opy_, bstack1l11lll111_opy_, bstack11ll1llll_opy_
            bstack1l1ll1l1_opy_ = bstack1l1ll1l1l_opy_()
            bstack1l11lll111_opy_(bstack111111ll1_opy_)
            bstack1l11l1ll1_opy_ = bstack1l1l1lll11_opy_.bstack1ll11ll1ll_opy_(CONFIG, bstack111111ll1_opy_)
            bstack1ll1l11l1_opy_.bstack1l111llll1_opy_(bstack11l1ll1_opy_ (u"ࠣࡒࡏࡅ࡞࡝ࡒࡊࡉࡋࡘࡤࡖࡒࡐࡆࡘࡇ࡙ࡥࡍࡂࡒࠥ૿"), bstack1l11l1ll1_opy_)
          BrowserType.connect = bstack11lll1ll1_opy_
          return
        BrowserType.launch = bstack1ll1ll1l1l_opy_
        bstack1111111ll_opy_ = True
    except Exception as e:
        pass
    try:
      import Browser
      from subprocess import Popen
      Popen.__init__ = bstack1l1l1l1l1_opy_
      bstack1111111ll_opy_ = True
    except Exception as e:
      pass
def bstack1ll1l111l_opy_(context, bstack1l1llllll_opy_):
  try:
    context.page.evaluate(bstack11l1ll1_opy_ (u"ࠤࡢࠤࡂࡄࠠࡼࡿࠥ଀"), bstack11l1ll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡡࡨࡼࡪࡩࡵࡵࡱࡵ࠾ࠥࢁࠢࡢࡥࡷ࡭ࡴࡴࠢ࠻ࠢࠥࡷࡪࡺࡓࡦࡵࡶ࡭ࡴࡴࡎࡢ࡯ࡨࠦ࠱ࠦࠢࡢࡴࡪࡹࡲ࡫࡮ࡵࡵࠥ࠾ࠥࢁࠢ࡯ࡣࡰࡩࠧࡀࠧଁ")+ json.dumps(bstack1l1llllll_opy_) + bstack11l1ll1_opy_ (u"ࠦࢂࢃࠢଂ"))
  except Exception as e:
    logger.debug(bstack11l1ll1_opy_ (u"ࠧ࡫ࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡ࡫ࡱࠤࡵࡲࡡࡺࡹࡵ࡭࡬࡮ࡴࠡࡵࡨࡷࡸ࡯࡯࡯ࠢࡱࡥࡲ࡫ࠠࡼࡿ࠽ࠤࢀࢃࠢଃ").format(str(e), traceback.format_exc()))
def bstack1ll1111l1l_opy_(context, message, level):
  try:
    context.page.evaluate(bstack11l1ll1_opy_ (u"ࠨ࡟ࠡ࠿ࡁࠤࢀࢃࠢ଄"), bstack11l1ll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡥࡥࡹࡧࡦࡹࡹࡵࡲ࠻ࠢࡾࠦࡦࡩࡴࡪࡱࡱࠦ࠿ࠦࠢࡢࡰࡱࡳࡹࡧࡴࡦࠤ࠯ࠤࠧࡧࡲࡨࡷࡰࡩࡳࡺࡳࠣ࠼ࠣࡿࠧࡪࡡࡵࡣࠥ࠾ࠬଅ") + json.dumps(message) + bstack11l1ll1_opy_ (u"ࠨ࠮ࠥࡰࡪࡼࡥ࡭ࠤ࠽ࠫଆ") + json.dumps(level) + bstack11l1ll1_opy_ (u"ࠩࢀࢁࠬଇ"))
  except Exception as e:
    logger.debug(bstack11l1ll1_opy_ (u"ࠥࡩࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡩ࡯ࠢࡳࡰࡦࡿࡷࡳ࡫ࡪ࡬ࡹࠦࡡ࡯ࡰࡲࡸࡦࡺࡩࡰࡰࠣࡿࢂࡀࠠࡼࡿࠥଈ").format(str(e), traceback.format_exc()))
@measure(event_name=EVENTS.bstack11111ll11_opy_, stage=STAGE.bstack1l1ll1llll_opy_, bstack1l11l1ll_opy_=bstack1lll1l11l_opy_)
def bstack1l11lllll_opy_(self, url):
  global bstack1lllll11ll_opy_
  try:
    bstack1l1l111lll_opy_(url)
  except Exception as err:
    logger.debug(bstack1111l1l1_opy_.format(str(err)))
  try:
    bstack1lllll11ll_opy_(self, url)
  except Exception as e:
    try:
      bstack1l111ll1ll_opy_ = str(e)
      if any(err_msg in bstack1l111ll1ll_opy_ for err_msg in bstack1llll111l_opy_):
        bstack1l1l111lll_opy_(url, True)
    except Exception as err:
      logger.debug(bstack1111l1l1_opy_.format(str(err)))
    raise e
def bstack1ll1l1llll_opy_(self):
  global bstack1l1llll11l_opy_
  bstack1l1llll11l_opy_ = self
  return
def bstack111ll1l11_opy_(self):
  global bstack11ll111l1_opy_
  bstack11ll111l1_opy_ = self
  return
def bstack1ll11ll1l1_opy_(test_name, bstack1111lllll_opy_):
  global CONFIG
  if percy.bstack1l1111111_opy_() == bstack11l1ll1_opy_ (u"ࠦࡹࡸࡵࡦࠤଉ"):
    bstack1l11ll1l_opy_ = os.path.relpath(bstack1111lllll_opy_, start=os.getcwd())
    suite_name, _ = os.path.splitext(bstack1l11ll1l_opy_)
    bstack1l11l1ll_opy_ = suite_name + bstack11l1ll1_opy_ (u"ࠧ࠳ࠢଊ") + test_name
    threading.current_thread().percySessionName = bstack1l11l1ll_opy_
def bstack1lll1111ll_opy_(self, test, *args, **kwargs):
  global bstack1l11ll11_opy_
  test_name = None
  bstack1111lllll_opy_ = None
  if test:
    test_name = str(test.name)
    bstack1111lllll_opy_ = str(test.source)
  bstack1ll11ll1l1_opy_(test_name, bstack1111lllll_opy_)
  bstack1l11ll11_opy_(self, test, *args, **kwargs)
@measure(event_name=EVENTS.bstack1llll1111_opy_, stage=STAGE.bstack1l1ll1llll_opy_, bstack1l11l1ll_opy_=bstack1lll1l11l_opy_)
def bstack1lll111ll1_opy_(driver, bstack1l11l1ll_opy_):
  if not bstack1lll11lll_opy_ and bstack1l11l1ll_opy_:
      bstack11l1lll1ll_opy_ = {
          bstack11l1ll1_opy_ (u"࠭ࡡࡤࡶ࡬ࡳࡳ࠭ଋ"): bstack11l1ll1_opy_ (u"ࠧࡴࡧࡷࡗࡪࡹࡳࡪࡱࡱࡒࡦࡳࡥࠨଌ"),
          bstack11l1ll1_opy_ (u"ࠨࡣࡵ࡫ࡺࡳࡥ࡯ࡶࡶࠫ଍"): {
              bstack11l1ll1_opy_ (u"ࠩࡱࡥࡲ࡫ࠧ଎"): bstack1l11l1ll_opy_
          }
      }
      bstack1lll1ll11l_opy_ = bstack11l1ll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡡࡨࡼࡪࡩࡵࡵࡱࡵ࠾ࠥࢁࡽࠨଏ").format(json.dumps(bstack11l1lll1ll_opy_))
      driver.execute_script(bstack1lll1ll11l_opy_)
  if bstack1l111111_opy_:
      bstack11l111l11_opy_ = {
          bstack11l1ll1_opy_ (u"ࠫࡦࡩࡴࡪࡱࡱࠫଐ"): bstack11l1ll1_opy_ (u"ࠬࡧ࡮࡯ࡱࡷࡥࡹ࡫ࠧ଑"),
          bstack11l1ll1_opy_ (u"࠭ࡡࡳࡩࡸࡱࡪࡴࡴࡴࠩ଒"): {
              bstack11l1ll1_opy_ (u"ࠧࡥࡣࡷࡥࠬଓ"): bstack1l11l1ll_opy_ + bstack11l1ll1_opy_ (u"ࠨࠢࡳࡥࡸࡹࡥࡥࠣࠪଔ"),
              bstack11l1ll1_opy_ (u"ࠩ࡯ࡩࡻ࡫࡬ࠨକ"): bstack11l1ll1_opy_ (u"ࠪ࡭ࡳ࡬࡯ࠨଖ")
          }
      }
      if bstack1l111111_opy_.status == bstack11l1ll1_opy_ (u"ࠫࡕࡇࡓࡔࠩଗ"):
          bstack1l1llll1l_opy_ = bstack11l1ll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡣࡪࡾࡥࡤࡷࡷࡳࡷࡀࠠࡼࡿࠪଘ").format(json.dumps(bstack11l111l11_opy_))
          driver.execute_script(bstack1l1llll1l_opy_)
          bstack1ll1llllll_opy_(driver, bstack11l1ll1_opy_ (u"࠭ࡰࡢࡵࡶࡩࡩ࠭ଙ"))
      elif bstack1l111111_opy_.status == bstack11l1ll1_opy_ (u"ࠧࡇࡃࡌࡐࠬଚ"):
          reason = bstack11l1ll1_opy_ (u"ࠣࠤଛ")
          bstack1l11l111l1_opy_ = bstack1l11l1ll_opy_ + bstack11l1ll1_opy_ (u"ࠩࠣࡪࡦ࡯࡬ࡦࡦࠪଜ")
          if bstack1l111111_opy_.message:
              reason = str(bstack1l111111_opy_.message)
              bstack1l11l111l1_opy_ = bstack1l11l111l1_opy_ + bstack11l1ll1_opy_ (u"ࠪࠤࡼ࡯ࡴࡩࠢࡨࡶࡷࡵࡲ࠻ࠢࠪଝ") + reason
          bstack11l111l11_opy_[bstack11l1ll1_opy_ (u"ࠫࡦࡸࡧࡶ࡯ࡨࡲࡹࡹࠧଞ")] = {
              bstack11l1ll1_opy_ (u"ࠬࡲࡥࡷࡧ࡯ࠫଟ"): bstack11l1ll1_opy_ (u"࠭ࡥࡳࡴࡲࡶࠬଠ"),
              bstack11l1ll1_opy_ (u"ࠧࡥࡣࡷࡥࠬଡ"): bstack1l11l111l1_opy_
          }
          bstack1l1llll1l_opy_ = bstack11l1ll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࡟ࡦࡺࡨࡧࡺࡺ࡯ࡳ࠼ࠣࡿࢂ࠭ଢ").format(json.dumps(bstack11l111l11_opy_))
          driver.execute_script(bstack1l1llll1l_opy_)
          bstack1ll1llllll_opy_(driver, bstack11l1ll1_opy_ (u"ࠩࡩࡥ࡮ࡲࡥࡥࠩଣ"), reason)
          bstack1ll1l11l1l_opy_(reason, str(bstack1l111111_opy_), str(bstack1ll1ll1ll_opy_), logger)
@measure(event_name=EVENTS.bstack1ll111llll_opy_, stage=STAGE.bstack1l1ll1llll_opy_, bstack1l11l1ll_opy_=bstack1lll1l11l_opy_)
def bstack111l1111_opy_(driver, test):
  if percy.bstack1l1111111_opy_() == bstack11l1ll1_opy_ (u"ࠥࡸࡷࡻࡥࠣତ") and percy.bstack111llll1l_opy_() == bstack11l1ll1_opy_ (u"ࠦࡹ࡫ࡳࡵࡥࡤࡷࡪࠨଥ"):
      bstack1llll1llll_opy_ = bstack1ll1l1lll_opy_(threading.current_thread(), bstack11l1ll1_opy_ (u"ࠬࡶࡥࡳࡥࡼࡗࡪࡹࡳࡪࡱࡱࡒࡦࡳࡥࠨଦ"), None)
      bstack1l111l1lll_opy_(driver, bstack1llll1llll_opy_, test)
  if bstack1ll1l1lll_opy_(threading.current_thread(), bstack11l1ll1_opy_ (u"࠭ࡩࡴࡃ࠴࠵ࡾ࡚ࡥࡴࡶࠪଧ"), None) and bstack1ll1l1lll_opy_(
          threading.current_thread(), bstack11l1ll1_opy_ (u"ࠧࡢ࠳࠴ࡽࡕࡲࡡࡵࡨࡲࡶࡲ࠭ନ"), None):
      logger.info(bstack11l1ll1_opy_ (u"ࠣࡃࡸࡸࡴࡳࡡࡵࡧࠣࡸࡪࡹࡴࠡࡥࡤࡷࡪࠦࡥࡹࡧࡦࡹࡹ࡯࡯࡯ࠢ࡫ࡥࡸࠦࡥ࡯ࡦࡨࡨ࠳ࠦࡐࡳࡱࡦࡩࡸࡹࡩ࡯ࡩࠣࡪࡴࡸࠠࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠠࡵࡧࡶࡸ࡮ࡴࡧࠡ࡫ࡶࠤࡺࡴࡤࡦࡴࡺࡥࡾ࠴ࠠࠣ଩"))
      bstack11lll11ll1_opy_.bstack11111111l_opy_(driver, name=test.name, path=test.source)
def bstack1lllll111_opy_(test, bstack1l11l1ll_opy_):
    try:
      bstack1l1l1ll111_opy_ = datetime.datetime.now()
      data = {}
      if test:
        data[bstack11l1ll1_opy_ (u"ࠩࡱࡥࡲ࡫ࠧପ")] = bstack1l11l1ll_opy_
      if bstack1l111111_opy_:
        if bstack1l111111_opy_.status == bstack11l1ll1_opy_ (u"ࠪࡔࡆ࡙ࡓࠨଫ"):
          data[bstack11l1ll1_opy_ (u"ࠫࡸࡺࡡࡵࡷࡶࠫବ")] = bstack11l1ll1_opy_ (u"ࠬࡶࡡࡴࡵࡨࡨࠬଭ")
        elif bstack1l111111_opy_.status == bstack11l1ll1_opy_ (u"࠭ࡆࡂࡋࡏࠫମ"):
          data[bstack11l1ll1_opy_ (u"ࠧࡴࡶࡤࡸࡺࡹࠧଯ")] = bstack11l1ll1_opy_ (u"ࠨࡨࡤ࡭ࡱ࡫ࡤࠨର")
          if bstack1l111111_opy_.message:
            data[bstack11l1ll1_opy_ (u"ࠩࡵࡩࡦࡹ࡯࡯ࠩ଱")] = str(bstack1l111111_opy_.message)
      user = CONFIG[bstack11l1ll1_opy_ (u"ࠪࡹࡸ࡫ࡲࡏࡣࡰࡩࠬଲ")]
      key = CONFIG[bstack11l1ll1_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶࡏࡪࡿࠧଳ")]
      url = bstack11l1ll1_opy_ (u"ࠬ࡮ࡴࡵࡲࡶ࠾࠴࠵ࡻࡾ࠼ࡾࢁࡅࡧࡰࡪ࠰ࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡥࡲࡱ࠴ࡧࡵࡵࡱࡰࡥࡹ࡫࠯ࡴࡧࡶࡷ࡮ࡵ࡮ࡴ࠱ࡾࢁ࠳ࡰࡳࡰࡰࠪ଴").format(user, key, bstack1l1l1ll1_opy_)
      headers = {
        bstack11l1ll1_opy_ (u"࠭ࡃࡰࡰࡷࡩࡳࡺ࠭ࡵࡻࡳࡩࠬଵ"): bstack11l1ll1_opy_ (u"ࠧࡢࡲࡳࡰ࡮ࡩࡡࡵ࡫ࡲࡲ࠴ࡰࡳࡰࡰࠪଶ"),
      }
      if bool(data):
        requests.put(url, json=data, headers=headers)
        cli.bstack111l11l1_opy_(bstack11l1ll1_opy_ (u"ࠣࡪࡷࡸࡵࡀࡵࡱࡦࡤࡸࡪࡥࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡤࡹࡴࡢࡶࡸࡷࠧଷ"), datetime.datetime.now() - bstack1l1l1ll111_opy_)
    except Exception as e:
      logger.error(bstack1l1l11l1ll_opy_.format(str(e)))
def bstack11111l11l_opy_(test, bstack1l11l1ll_opy_):
  global CONFIG
  global bstack11ll111l1_opy_
  global bstack1l1llll11l_opy_
  global bstack1l1l1ll1_opy_
  global bstack1l111111_opy_
  global bstack1lll1l11l_opy_
  global bstack11l11l1l1_opy_
  global bstack11ll11lll_opy_
  global bstack1ll11ll1l_opy_
  global bstack1llllllll_opy_
  global bstack1l1ll1l1l1_opy_
  global bstack1llll111l1_opy_
  try:
    if not bstack1l1l1ll1_opy_:
      with open(os.path.join(os.path.expanduser(bstack11l1ll1_opy_ (u"ࠩࢁࠫସ")), bstack11l1ll1_opy_ (u"ࠪ࠲ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࠪହ"), bstack11l1ll1_opy_ (u"ࠫ࠳ࡹࡥࡴࡵ࡬ࡳࡳ࡯ࡤࡴ࠰ࡷࡼࡹ࠭଺"))) as f:
        bstack111111l1l_opy_ = json.loads(bstack11l1ll1_opy_ (u"ࠧࢁࠢ଻") + f.read().strip() + bstack11l1ll1_opy_ (u"࠭ࠢࡹࠤ࠽ࠤࠧࡿࠢࠨ଼") + bstack11l1ll1_opy_ (u"ࠢࡾࠤଽ"))
        bstack1l1l1ll1_opy_ = bstack111111l1l_opy_[str(threading.get_ident())]
  except:
    pass
  if bstack1l1ll1l1l1_opy_:
    for driver in bstack1l1ll1l1l1_opy_:
      if bstack1l1l1ll1_opy_ == driver.session_id:
        if test:
          bstack111l1111_opy_(driver, test)
        bstack1lll111ll1_opy_(driver, bstack1l11l1ll_opy_)
  elif bstack1l1l1ll1_opy_:
    bstack1lllll111_opy_(test, bstack1l11l1ll_opy_)
  if bstack11ll111l1_opy_:
    bstack11ll11lll_opy_(bstack11ll111l1_opy_)
  if bstack1l1llll11l_opy_:
    bstack1ll11ll1l_opy_(bstack1l1llll11l_opy_)
  if bstack1l111lllll_opy_:
    bstack1llllllll_opy_()
def bstack1l1ll111_opy_(self, test, *args, **kwargs):
  bstack1l11l1ll_opy_ = None
  if test:
    bstack1l11l1ll_opy_ = str(test.name)
  bstack11111l11l_opy_(test, bstack1l11l1ll_opy_)
  bstack11l11l1l1_opy_(self, test, *args, **kwargs)
def bstack1ll1111111_opy_(self, parent, test, skip_on_failure=None, rpa=False):
  global bstack1lllll1l11_opy_
  global CONFIG
  global bstack1l1ll1l1l1_opy_
  global bstack1l1l1ll1_opy_
  bstack1lllll1111_opy_ = None
  try:
    if bstack1ll1l1lll_opy_(threading.current_thread(), bstack11l1ll1_opy_ (u"ࠨࡣ࠴࠵ࡾࡖ࡬ࡢࡶࡩࡳࡷࡳࠧା"), None):
      try:
        if not bstack1l1l1ll1_opy_:
          with open(os.path.join(os.path.expanduser(bstack11l1ll1_opy_ (u"ࠩࢁࠫି")), bstack11l1ll1_opy_ (u"ࠪ࠲ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࠪୀ"), bstack11l1ll1_opy_ (u"ࠫ࠳ࡹࡥࡴࡵ࡬ࡳࡳ࡯ࡤࡴ࠰ࡷࡼࡹ࠭ୁ"))) as f:
            bstack111111l1l_opy_ = json.loads(bstack11l1ll1_opy_ (u"ࠧࢁࠢୂ") + f.read().strip() + bstack11l1ll1_opy_ (u"࠭ࠢࡹࠤ࠽ࠤࠧࡿࠢࠨୃ") + bstack11l1ll1_opy_ (u"ࠢࡾࠤୄ"))
            bstack1l1l1ll1_opy_ = bstack111111l1l_opy_[str(threading.get_ident())]
      except:
        pass
      if bstack1l1ll1l1l1_opy_:
        for driver in bstack1l1ll1l1l1_opy_:
          if bstack1l1l1ll1_opy_ == driver.session_id:
            bstack1lllll1111_opy_ = driver
    bstack1l11l1l1l_opy_ = bstack11lll11ll1_opy_.bstack1lllll11l_opy_(test.tags)
    if bstack1lllll1111_opy_:
      threading.current_thread().isA11yTest = bstack11lll11ll1_opy_.bstack1l1ll1l111_opy_(bstack1lllll1111_opy_, bstack1l11l1l1l_opy_)
    else:
      threading.current_thread().isA11yTest = bstack1l11l1l1l_opy_
  except:
    pass
  bstack1lllll1l11_opy_(self, parent, test, skip_on_failure=skip_on_failure, rpa=rpa)
  global bstack1l111111_opy_
  try:
    bstack1l111111_opy_ = self._test
  except:
    bstack1l111111_opy_ = self.test
def bstack1l11l1l1ll_opy_():
  global bstack1lll11l1ll_opy_
  try:
    if os.path.exists(bstack1lll11l1ll_opy_):
      os.remove(bstack1lll11l1ll_opy_)
  except Exception as e:
    logger.debug(bstack11l1ll1_opy_ (u"ࠨࡇࡵࡶࡴࡸࠠࡪࡰࠣࡨࡪࡲࡥࡵ࡫ࡱ࡫ࠥࡸ࡯ࡣࡱࡷࠤࡷ࡫ࡰࡰࡴࡷࠤ࡫࡯࡬ࡦ࠼ࠣࠫ୅") + str(e))
def bstack1l1lllll1l_opy_():
  global bstack1lll11l1ll_opy_
  bstack11lll11l_opy_ = {}
  try:
    if not os.path.isfile(bstack1lll11l1ll_opy_):
      with open(bstack1lll11l1ll_opy_, bstack11l1ll1_opy_ (u"ࠩࡺࠫ୆")):
        pass
      with open(bstack1lll11l1ll_opy_, bstack11l1ll1_opy_ (u"ࠥࡻ࠰ࠨେ")) as outfile:
        json.dump({}, outfile)
    if os.path.exists(bstack1lll11l1ll_opy_):
      bstack11lll11l_opy_ = json.load(open(bstack1lll11l1ll_opy_, bstack11l1ll1_opy_ (u"ࠫࡷࡨࠧୈ")))
  except Exception as e:
    logger.debug(bstack11l1ll1_opy_ (u"ࠬࡋࡲࡳࡱࡵࠤ࡮ࡴࠠࡳࡧࡤࡨ࡮ࡴࡧࠡࡴࡲࡦࡴࡺࠠࡳࡧࡳࡳࡷࡺࠠࡧ࡫࡯ࡩ࠿ࠦࠧ୉") + str(e))
  finally:
    return bstack11lll11l_opy_
def bstack1llllll11l_opy_(platform_index, item_index):
  global bstack1lll11l1ll_opy_
  try:
    bstack11lll11l_opy_ = bstack1l1lllll1l_opy_()
    bstack11lll11l_opy_[item_index] = platform_index
    with open(bstack1lll11l1ll_opy_, bstack11l1ll1_opy_ (u"ࠨࡷࠬࠤ୊")) as outfile:
      json.dump(bstack11lll11l_opy_, outfile)
  except Exception as e:
    logger.debug(bstack11l1ll1_opy_ (u"ࠧࡆࡴࡵࡳࡷࠦࡩ࡯ࠢࡺࡶ࡮ࡺࡩ࡯ࡩࠣࡸࡴࠦࡲࡰࡤࡲࡸࠥࡸࡥࡱࡱࡵࡸࠥ࡬ࡩ࡭ࡧ࠽ࠤࠬୋ") + str(e))
def bstack1l111ll111_opy_(bstack1ll11l1l_opy_):
  global CONFIG
  bstack11ll11l111_opy_ = bstack11l1ll1_opy_ (u"ࠨࠩୌ")
  if not bstack11l1ll1_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷ୍ࠬ") in CONFIG:
    logger.info(bstack11l1ll1_opy_ (u"ࠪࡒࡴࠦࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠢࡳࡥࡸࡹࡥࡥࠢࡸࡲࡦࡨ࡬ࡦࠢࡷࡳࠥ࡭ࡥ࡯ࡧࡵࡥࡹ࡫ࠠࡳࡧࡳࡳࡷࡺࠠࡧࡱࡵࠤࡗࡵࡢࡰࡶࠣࡶࡺࡴࠧ୎"))
  try:
    platform = CONFIG[bstack11l1ll1_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧ୏")][bstack1ll11l1l_opy_]
    if bstack11l1ll1_opy_ (u"ࠬࡵࡳࠨ୐") in platform:
      bstack11ll11l111_opy_ += str(platform[bstack11l1ll1_opy_ (u"࠭࡯ࡴࠩ୑")]) + bstack11l1ll1_opy_ (u"ࠧ࠭ࠢࠪ୒")
    if bstack11l1ll1_opy_ (u"ࠨࡱࡶ࡚ࡪࡸࡳࡪࡱࡱࠫ୓") in platform:
      bstack11ll11l111_opy_ += str(platform[bstack11l1ll1_opy_ (u"ࠩࡲࡷ࡛࡫ࡲࡴ࡫ࡲࡲࠬ୔")]) + bstack11l1ll1_opy_ (u"ࠪ࠰ࠥ࠭୕")
    if bstack11l1ll1_opy_ (u"ࠫࡩ࡫ࡶࡪࡥࡨࡒࡦࡳࡥࠨୖ") in platform:
      bstack11ll11l111_opy_ += str(platform[bstack11l1ll1_opy_ (u"ࠬࡪࡥࡷ࡫ࡦࡩࡓࡧ࡭ࡦࠩୗ")]) + bstack11l1ll1_opy_ (u"࠭ࠬࠡࠩ୘")
    if bstack11l1ll1_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡘࡨࡶࡸ࡯࡯࡯ࠩ୙") in platform:
      bstack11ll11l111_opy_ += str(platform[bstack11l1ll1_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯࡙ࡩࡷࡹࡩࡰࡰࠪ୚")]) + bstack11l1ll1_opy_ (u"ࠩ࠯ࠤࠬ୛")
    if bstack11l1ll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡒࡦࡳࡥࠨଡ଼") in platform:
      bstack11ll11l111_opy_ += str(platform[bstack11l1ll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡓࡧ࡭ࡦࠩଢ଼")]) + bstack11l1ll1_opy_ (u"ࠬ࠲ࠠࠨ୞")
    if bstack11l1ll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡖࡦࡴࡶ࡭ࡴࡴࠧୟ") in platform:
      bstack11ll11l111_opy_ += str(platform[bstack11l1ll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡗࡧࡵࡷ࡮ࡵ࡮ࠨୠ")]) + bstack11l1ll1_opy_ (u"ࠨ࠮ࠣࠫୡ")
  except Exception as e:
    logger.debug(bstack11l1ll1_opy_ (u"ࠩࡖࡳࡲ࡫ࠠࡦࡴࡵࡳࡷࠦࡩ࡯ࠢࡪࡩࡳ࡫ࡲࡢࡶ࡬ࡲ࡬ࠦࡰ࡭ࡣࡷࡪࡴࡸ࡭ࠡࡵࡷࡶ࡮ࡴࡧࠡࡨࡲࡶࠥࡸࡥࡱࡱࡵࡸࠥ࡭ࡥ࡯ࡧࡵࡥࡹ࡯࡯࡯ࠩୢ") + str(e))
  finally:
    if bstack11ll11l111_opy_[len(bstack11ll11l111_opy_) - 2:] == bstack11l1ll1_opy_ (u"ࠪ࠰ࠥ࠭ୣ"):
      bstack11ll11l111_opy_ = bstack11ll11l111_opy_[:-2]
    return bstack11ll11l111_opy_
def bstack11ll11llll_opy_(path, bstack11ll11l111_opy_):
  try:
    import xml.etree.ElementTree as ET
    bstack1ll11lll_opy_ = ET.parse(path)
    bstack1l1111l1ll_opy_ = bstack1ll11lll_opy_.getroot()
    bstack1lll1l1l11_opy_ = None
    for suite in bstack1l1111l1ll_opy_.iter(bstack11l1ll1_opy_ (u"ࠫࡸࡻࡩࡵࡧࠪ୤")):
      if bstack11l1ll1_opy_ (u"ࠬࡹ࡯ࡶࡴࡦࡩࠬ୥") in suite.attrib:
        suite.attrib[bstack11l1ll1_opy_ (u"࠭࡮ࡢ࡯ࡨࠫ୦")] += bstack11l1ll1_opy_ (u"ࠧࠡࠩ୧") + bstack11ll11l111_opy_
        bstack1lll1l1l11_opy_ = suite
    bstack11111llll_opy_ = None
    for robot in bstack1l1111l1ll_opy_.iter(bstack11l1ll1_opy_ (u"ࠨࡴࡲࡦࡴࡺࠧ୨")):
      bstack11111llll_opy_ = robot
    bstack11lll1111_opy_ = len(bstack11111llll_opy_.findall(bstack11l1ll1_opy_ (u"ࠩࡶࡹ࡮ࡺࡥࠨ୩")))
    if bstack11lll1111_opy_ == 1:
      bstack11111llll_opy_.remove(bstack11111llll_opy_.findall(bstack11l1ll1_opy_ (u"ࠪࡷࡺ࡯ࡴࡦࠩ୪"))[0])
      bstack1l1l1l1l1l_opy_ = ET.Element(bstack11l1ll1_opy_ (u"ࠫࡸࡻࡩࡵࡧࠪ୫"), attrib={bstack11l1ll1_opy_ (u"ࠬࡴࡡ࡮ࡧࠪ୬"): bstack11l1ll1_opy_ (u"࠭ࡓࡶ࡫ࡷࡩࡸ࠭୭"), bstack11l1ll1_opy_ (u"ࠧࡪࡦࠪ୮"): bstack11l1ll1_opy_ (u"ࠨࡵ࠳ࠫ୯")})
      bstack11111llll_opy_.insert(1, bstack1l1l1l1l1l_opy_)
      bstack1ll1llll1_opy_ = None
      for suite in bstack11111llll_opy_.iter(bstack11l1ll1_opy_ (u"ࠩࡶࡹ࡮ࡺࡥࠨ୰")):
        bstack1ll1llll1_opy_ = suite
      bstack1ll1llll1_opy_.append(bstack1lll1l1l11_opy_)
      bstack11l1lll1_opy_ = None
      for status in bstack1lll1l1l11_opy_.iter(bstack11l1ll1_opy_ (u"ࠪࡷࡹࡧࡴࡶࡵࠪୱ")):
        bstack11l1lll1_opy_ = status
      bstack1ll1llll1_opy_.append(bstack11l1lll1_opy_)
    bstack1ll11lll_opy_.write(path)
  except Exception as e:
    logger.debug(bstack11l1ll1_opy_ (u"ࠫࡊࡸࡲࡰࡴࠣ࡭ࡳࠦࡰࡢࡴࡶ࡭ࡳ࡭ࠠࡸࡪ࡬ࡰࡪࠦࡧࡦࡰࡨࡶࡦࡺࡩ࡯ࡩࠣࡶࡴࡨ࡯ࡵࠢࡵࡩࡵࡵࡲࡵࠩ୲") + str(e))
def bstack11111l1ll_opy_(outs_dir, pabot_args, options, start_time_string, tests_root_name):
  global bstack111111l11_opy_
  global CONFIG
  if bstack11l1ll1_opy_ (u"ࠧࡶࡹࡵࡪࡲࡲࡵࡧࡴࡩࠤ୳") in options:
    del options[bstack11l1ll1_opy_ (u"ࠨࡰࡺࡶ࡫ࡳࡳࡶࡡࡵࡪࠥ୴")]
  bstack1l1111ll_opy_ = bstack1l1lllll1l_opy_()
  for bstack1l1llll11_opy_ in bstack1l1111ll_opy_.keys():
    path = os.path.join(os.getcwd(), bstack11l1ll1_opy_ (u"ࠧࡱࡣࡥࡳࡹࡥࡲࡦࡵࡸࡰࡹࡹࠧ୵"), str(bstack1l1llll11_opy_), bstack11l1ll1_opy_ (u"ࠨࡱࡸࡸࡵࡻࡴ࠯ࡺࡰࡰࠬ୶"))
    bstack11ll11llll_opy_(path, bstack1l111ll111_opy_(bstack1l1111ll_opy_[bstack1l1llll11_opy_]))
  bstack1l11l1l1ll_opy_()
  return bstack111111l11_opy_(outs_dir, pabot_args, options, start_time_string, tests_root_name)
def bstack1ll1llll1l_opy_(self, ff_profile_dir):
  global bstack11ll111l1l_opy_
  if not ff_profile_dir:
    return None
  return bstack11ll111l1l_opy_(self, ff_profile_dir)
def bstack1l1ll11ll_opy_(datasources, opts_for_run, outs_dir, pabot_args, suite_group):
  from pabot.pabot import QueueItem
  global CONFIG
  global bstack1ll1lll1ll_opy_
  bstack1l1111lll_opy_ = []
  if bstack11l1ll1_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬ୷") in CONFIG:
    bstack1l1111lll_opy_ = CONFIG[bstack11l1ll1_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭୸")]
  return [
    QueueItem(
      datasources,
      outs_dir,
      opts_for_run,
      suite,
      pabot_args[bstack11l1ll1_opy_ (u"ࠦࡨࡵ࡭࡮ࡣࡱࡨࠧ୹")],
      pabot_args[bstack11l1ll1_opy_ (u"ࠧࡼࡥࡳࡤࡲࡷࡪࠨ୺")],
      argfile,
      pabot_args.get(bstack11l1ll1_opy_ (u"ࠨࡨࡪࡸࡨࠦ୻")),
      pabot_args[bstack11l1ll1_opy_ (u"ࠢࡱࡴࡲࡧࡪࡹࡳࡦࡵࠥ୼")],
      platform[0],
      bstack1ll1lll1ll_opy_
    )
    for suite in suite_group
    for argfile in pabot_args[bstack11l1ll1_opy_ (u"ࠣࡣࡵ࡫ࡺࡳࡥ࡯ࡶࡩ࡭ࡱ࡫ࡳࠣ୽")] or [(bstack11l1ll1_opy_ (u"ࠤࠥ୾"), None)]
    for platform in enumerate(bstack1l1111lll_opy_)
  ]
def bstack1l1l1lll_opy_(self, datasources, outs_dir, options,
                        execution_item, command, verbose, argfile,
                        hive=None, processes=0, platform_index=0, bstack1l1l1l1l11_opy_=bstack11l1ll1_opy_ (u"ࠪࠫ୿")):
  global bstack111lllll_opy_
  self.platform_index = platform_index
  self.bstack1llll1l1ll_opy_ = bstack1l1l1l1l11_opy_
  bstack111lllll_opy_(self, datasources, outs_dir, options,
                      execution_item, command, verbose, argfile, hive, processes)
def bstack1l1l11l11_opy_(caller_id, datasources, is_last, item, outs_dir):
  global bstack111ll1lll_opy_
  global bstack11ll11ll_opy_
  bstack1lll11ll_opy_ = copy.deepcopy(item)
  if not bstack11l1ll1_opy_ (u"ࠫࡻࡧࡲࡪࡣࡥࡰࡪ࠭஀") in item.options:
    bstack1lll11ll_opy_.options[bstack11l1ll1_opy_ (u"ࠬࡼࡡࡳ࡫ࡤࡦࡱ࡫ࠧ஁")] = []
  bstack11lll111l1_opy_ = bstack1lll11ll_opy_.options[bstack11l1ll1_opy_ (u"࠭ࡶࡢࡴ࡬ࡥࡧࡲࡥࠨஂ")].copy()
  for v in bstack1lll11ll_opy_.options[bstack11l1ll1_opy_ (u"ࠧࡷࡣࡵ࡭ࡦࡨ࡬ࡦࠩஃ")]:
    if bstack11l1ll1_opy_ (u"ࠨࡄࡖࡘࡆࡉࡋࡑࡎࡄࡘࡋࡕࡒࡎࡋࡑࡈࡊ࡞ࠧ஄") in v:
      bstack11lll111l1_opy_.remove(v)
    if bstack11l1ll1_opy_ (u"ࠩࡅࡗ࡙ࡇࡃࡌࡅࡏࡍࡆࡘࡇࡔࠩஅ") in v:
      bstack11lll111l1_opy_.remove(v)
    if bstack11l1ll1_opy_ (u"ࠪࡆࡘ࡚ࡁࡄࡍࡇࡉࡋࡒࡏࡄࡃࡏࡍࡉࡋࡎࡕࡋࡉࡍࡊࡘࠧஆ") in v:
      bstack11lll111l1_opy_.remove(v)
  bstack11lll111l1_opy_.insert(0, bstack11l1ll1_opy_ (u"ࠫࡇ࡙ࡔࡂࡅࡎࡔࡑࡇࡔࡇࡑࡕࡑࡎࡔࡄࡆ࡚࠽ࡿࢂ࠭இ").format(bstack1lll11ll_opy_.platform_index))
  bstack11lll111l1_opy_.insert(0, bstack11l1ll1_opy_ (u"ࠬࡈࡓࡕࡃࡆࡏࡉࡋࡆࡍࡑࡆࡅࡑࡏࡄࡆࡐࡗࡍࡋࡏࡅࡓ࠼ࡾࢁࠬஈ").format(bstack1lll11ll_opy_.bstack1llll1l1ll_opy_))
  bstack1lll11ll_opy_.options[bstack11l1ll1_opy_ (u"࠭ࡶࡢࡴ࡬ࡥࡧࡲࡥࠨஉ")] = bstack11lll111l1_opy_
  if bstack11ll11ll_opy_:
    bstack1lll11ll_opy_.options[bstack11l1ll1_opy_ (u"ࠧࡷࡣࡵ࡭ࡦࡨ࡬ࡦࠩஊ")].insert(0, bstack11l1ll1_opy_ (u"ࠨࡄࡖࡘࡆࡉࡋࡄࡎࡌࡅࡗࡍࡓ࠻ࡽࢀࠫ஋").format(bstack11ll11ll_opy_))
  return bstack111ll1lll_opy_(caller_id, datasources, is_last, bstack1lll11ll_opy_, outs_dir)
def bstack1ll1111lll_opy_(command, item_index):
  if bstack1ll1l11l1_opy_.get_property(bstack11l1ll1_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬ࡡࡶࡩࡸࡹࡩࡰࡰࠪ஌")):
    os.environ[bstack11l1ll1_opy_ (u"ࠪࡇ࡚ࡘࡒࡆࡐࡗࡣࡕࡒࡁࡕࡈࡒࡖࡒࡥࡄࡂࡖࡄࠫ஍")] = json.dumps(CONFIG[bstack11l1ll1_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧஎ")][item_index % bstack1lll1l1ll_opy_])
  global bstack11ll11ll_opy_
  if bstack11ll11ll_opy_:
    command[0] = command[0].replace(bstack11l1ll1_opy_ (u"ࠬࡸ࡯ࡣࡱࡷࠫஏ"), bstack11l1ll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠲ࡹࡤ࡬ࠢࡵࡳࡧࡵࡴ࠮࡫ࡱࡸࡪࡸ࡮ࡢ࡮ࠣ࠱࠲ࡨࡳࡵࡣࡦ࡯ࡤ࡯ࡴࡦ࡯ࡢ࡭ࡳࡪࡥࡹࠢࠪஐ") + str(
      item_index) + bstack11l1ll1_opy_ (u"ࠧࠡࠩ஑") + bstack11ll11ll_opy_, 1)
  else:
    command[0] = command[0].replace(bstack11l1ll1_opy_ (u"ࠨࡴࡲࡦࡴࡺࠧஒ"),
                                    bstack11l1ll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠮ࡵࡧ࡯ࠥࡸ࡯ࡣࡱࡷ࠱࡮ࡴࡴࡦࡴࡱࡥࡱࠦ࠭࠮ࡤࡶࡸࡦࡩ࡫ࡠ࡫ࡷࡩࡲࡥࡩ࡯ࡦࡨࡼࠥ࠭ஓ") + str(item_index), 1)
def bstack11l1ll111l_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index):
  global bstack1l1l1l1111_opy_
  bstack1ll1111lll_opy_(command, item_index)
  return bstack1l1l1l1111_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index)
def bstack1l1lll111l_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index, outs_dir):
  global bstack1l1l1l1111_opy_
  bstack1ll1111lll_opy_(command, item_index)
  return bstack1l1l1l1111_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index, outs_dir)
def bstack1l1l1ll11_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index, outs_dir, process_timeout):
  global bstack1l1l1l1111_opy_
  bstack1ll1111lll_opy_(command, item_index)
  return bstack1l1l1l1111_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index, outs_dir, process_timeout)
def is_driver_active(driver):
  return True if driver and driver.session_id else False
def bstack1ll1111ll_opy_(self, runner, quiet=False, capture=True):
  global bstack11l1lll11_opy_
  bstack11lll1ll11_opy_ = bstack11l1lll11_opy_(self, runner, quiet=quiet, capture=capture)
  if self.exception:
    if not hasattr(runner, bstack11l1ll1_opy_ (u"ࠪࡩࡽࡩࡥࡱࡶ࡬ࡳࡳࡥࡡࡳࡴࠪஔ")):
      runner.exception_arr = []
    if not hasattr(runner, bstack11l1ll1_opy_ (u"ࠫࡪࡾࡣࡠࡶࡵࡥࡨ࡫ࡢࡢࡥ࡮ࡣࡦࡸࡲࠨக")):
      runner.exc_traceback_arr = []
    runner.exception = self.exception
    runner.exc_traceback = self.exc_traceback
    runner.exception_arr.append(self.exception)
    runner.exc_traceback_arr.append(self.exc_traceback)
  return bstack11lll1ll11_opy_
def bstack11l1111l_opy_(runner, hook_name, context, element, bstack1l1ll11l1_opy_, *args):
  try:
    if runner.hooks.get(hook_name):
      bstack1l11111lll_opy_.bstack1lllll1lll_opy_(hook_name, element)
    bstack1l1ll11l1_opy_(runner, hook_name, context, *args)
    if runner.hooks.get(hook_name):
      bstack1l11111lll_opy_.bstack1l1l11llll_opy_(element)
      if hook_name not in [bstack11l1ll1_opy_ (u"ࠬࡨࡥࡧࡱࡵࡩࡤࡧ࡬࡭ࠩ஖"), bstack11l1ll1_opy_ (u"࠭ࡡࡧࡶࡨࡶࡤࡧ࡬࡭ࠩ஗")] and args and hasattr(args[0], bstack11l1ll1_opy_ (u"ࠧࡦࡴࡵࡳࡷࡥ࡭ࡦࡵࡶࡥ࡬࡫ࠧ஘")):
        args[0].error_message = bstack11l1ll1_opy_ (u"ࠨࠩங")
  except Exception as e:
    logger.debug(bstack11l1ll1_opy_ (u"ࠩࡉࡥ࡮ࡲࡥࡥࠢࡷࡳࠥ࡮ࡡ࡯ࡦ࡯ࡩࠥ࡮࡯ࡰ࡭ࡶࠤ࡮ࡴࠠࡣࡧ࡫ࡥࡻ࡫࠺ࠡࡽࢀࠫச").format(str(e)))
@measure(event_name=EVENTS.bstack1lll111l11_opy_, stage=STAGE.bstack1l1ll1llll_opy_, hook_type=bstack11l1ll1_opy_ (u"ࠥࡦࡪ࡬࡯ࡳࡧࡄࡰࡱࠨ஛"), bstack1l11l1ll_opy_=bstack1lll1l11l_opy_)
def bstack1l11111111_opy_(runner, name, context, bstack1l1ll11l1_opy_, *args):
    if runner.hooks.get(bstack11l1ll1_opy_ (u"ࠦࡧ࡫ࡦࡰࡴࡨࡣࡦࡲ࡬ࠣஜ")).__name__ != bstack11l1ll1_opy_ (u"ࠧࡨࡥࡧࡱࡵࡩࡤࡧ࡬࡭ࡡࡧࡩ࡫ࡧࡵ࡭ࡶࡢ࡬ࡴࡵ࡫ࠣ஝"):
      bstack11l1111l_opy_(runner, name, context, runner, bstack1l1ll11l1_opy_, *args)
    try:
      threading.current_thread().bstackSessionDriver if bstack11ll11ll11_opy_(bstack11l1ll1_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰ࡙ࡥࡴࡵ࡬ࡳࡳࡊࡲࡪࡸࡨࡶࠬஞ")) else context.browser
      runner.driver_initialised = bstack11l1ll1_opy_ (u"ࠢࡣࡧࡩࡳࡷ࡫࡟ࡢ࡮࡯ࠦட")
    except Exception as e:
      logger.debug(bstack11l1ll1_opy_ (u"ࠨࡈࡤ࡭ࡱ࡫ࡤࠡࡶࡲࠤࡸ࡫ࡴࠡࡦࡵ࡭ࡻ࡫ࡲࠡ࡫ࡱ࡭ࡹ࡯ࡡ࡭࡫ࡶࡩࠥࡧࡴࡵࡴ࡬ࡦࡺࡺࡥ࠻ࠢࡾࢁࠬ஠").format(str(e)))
def bstack1ll1l1l1ll_opy_(runner, name, context, bstack1l1ll11l1_opy_, *args):
    bstack11l1111l_opy_(runner, name, context, context.feature, bstack1l1ll11l1_opy_, *args)
    try:
      if not bstack1lll11lll_opy_:
        bstack1lllll1111_opy_ = threading.current_thread().bstackSessionDriver if bstack11ll11ll11_opy_(bstack11l1ll1_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬ࡕࡨࡷࡸ࡯࡯࡯ࡆࡵ࡭ࡻ࡫ࡲࠨ஡")) else context.browser
        if is_driver_active(bstack1lllll1111_opy_):
          if runner.driver_initialised is None: runner.driver_initialised = bstack11l1ll1_opy_ (u"ࠥࡦࡪ࡬࡯ࡳࡧࡢࡪࡪࡧࡴࡶࡴࡨࠦ஢")
          bstack1l1llllll_opy_ = str(runner.feature.name)
          bstack1ll1l111l_opy_(context, bstack1l1llllll_opy_)
          bstack1lllll1111_opy_.execute_script(bstack11l1ll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡢࡩࡽ࡫ࡣࡶࡶࡲࡶ࠿ࠦࡻࠣࡣࡦࡸ࡮ࡵ࡮ࠣ࠼ࠣࠦࡸ࡫ࡴࡔࡧࡶࡷ࡮ࡵ࡮ࡏࡣࡰࡩࠧ࠲ࠠࠣࡣࡵ࡫ࡺࡳࡥ࡯ࡶࡶࠦ࠿ࠦࡻࠣࡰࡤࡱࡪࠨ࠺ࠡࠩண") + json.dumps(bstack1l1llllll_opy_) + bstack11l1ll1_opy_ (u"ࠬࢃࡽࠨத"))
    except Exception as e:
      logger.debug(bstack11l1ll1_opy_ (u"࠭ࡆࡢ࡫࡯ࡩࡩࠦࡴࡰࠢࡶࡩࡹࠦࡳࡦࡵࡶ࡭ࡴࡴࠠ࡯ࡣࡰࡩࠥ࡯࡮ࠡࡤࡨࡪࡴࡸࡥࠡࡨࡨࡥࡹࡻࡲࡦ࠼ࠣࡿࢂ࠭஥").format(str(e)))
def bstack1ll1l11ll1_opy_(runner, name, context, bstack1l1ll11l1_opy_, *args):
    if hasattr(context, bstack11l1ll1_opy_ (u"ࠧࡴࡥࡨࡲࡦࡸࡩࡰࠩ஦")):
        bstack1l11111lll_opy_.start_test(context)
    target = context.scenario if hasattr(context, bstack11l1ll1_opy_ (u"ࠨࡵࡦࡩࡳࡧࡲࡪࡱࠪ஧")) else context.feature
    bstack11l1111l_opy_(runner, name, context, target, bstack1l1ll11l1_opy_, *args)
@measure(event_name=EVENTS.bstack1lll11llll_opy_, stage=STAGE.bstack1l1ll1llll_opy_, bstack1l11l1ll_opy_=bstack1lll1l11l_opy_)
def bstack11l11l11l_opy_(runner, name, context, bstack1l1ll11l1_opy_, *args):
    if len(context.scenario.tags) == 0: bstack1l11111lll_opy_.start_test(context)
    bstack11l1111l_opy_(runner, name, context, context.scenario, bstack1l1ll11l1_opy_, *args)
    threading.current_thread().a11y_stop = False
    bstack111l1111l_opy_.bstack11ll111ll_opy_(context, *args)
    try:
      bstack1lllll1111_opy_ = bstack1ll1l1lll_opy_(threading.current_thread(), bstack11l1ll1_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬ࡕࡨࡷࡸ࡯࡯࡯ࡆࡵ࡭ࡻ࡫ࡲࠨந"), context.browser)
      if is_driver_active(bstack1lllll1111_opy_):
        bstack11111l1l1_opy_.bstack1111l11l1_opy_(bstack1ll1l1lll_opy_(threading.current_thread(), bstack11l1ll1_opy_ (u"ࠪࡦࡸࡺࡡࡤ࡭ࡖࡩࡸࡹࡩࡰࡰࡇࡶ࡮ࡼࡥࡳࠩன"), {}))
        if runner.driver_initialised is None: runner.driver_initialised = bstack11l1ll1_opy_ (u"ࠦࡧ࡫ࡦࡰࡴࡨࡣࡸࡩࡥ࡯ࡣࡵ࡭ࡴࠨப")
        if (not bstack1lll11lll_opy_):
          scenario_name = args[0].name
          feature_name = bstack1l1llllll_opy_ = str(runner.feature.name)
          bstack1l1llllll_opy_ = feature_name + bstack11l1ll1_opy_ (u"ࠬࠦ࠭ࠡࠩ஫") + scenario_name
          if runner.driver_initialised == bstack11l1ll1_opy_ (u"ࠨࡢࡦࡨࡲࡶࡪࡥࡳࡤࡧࡱࡥࡷ࡯࡯ࠣ஬"):
            bstack1ll1l111l_opy_(context, bstack1l1llllll_opy_)
            bstack1lllll1111_opy_.execute_script(bstack11l1ll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡥࡥࡹࡧࡦࡹࡹࡵࡲ࠻ࠢࡾࠦࡦࡩࡴࡪࡱࡱࠦ࠿ࠦࠢࡴࡧࡷࡗࡪࡹࡳࡪࡱࡱࡒࡦࡳࡥࠣ࠮ࠣࠦࡦࡸࡧࡶ࡯ࡨࡲࡹࡹࠢ࠻ࠢࡾࠦࡳࡧ࡭ࡦࠤ࠽ࠤࠬ஭") + json.dumps(bstack1l1llllll_opy_) + bstack11l1ll1_opy_ (u"ࠨࡿࢀࠫம"))
    except Exception as e:
      logger.debug(bstack11l1ll1_opy_ (u"ࠩࡉࡥ࡮ࡲࡥࡥࠢࡷࡳࠥࡹࡥࡵࠢࡶࡩࡸࡹࡩࡰࡰࠣࡲࡦࡳࡥࠡ࡫ࡱࠤࡧ࡫ࡦࡰࡴࡨࠤࡸࡩࡥ࡯ࡣࡵ࡭ࡴࡀࠠࡼࡿࠪய").format(str(e)))
@measure(event_name=EVENTS.bstack1lll111l11_opy_, stage=STAGE.bstack1l1ll1llll_opy_, hook_type=bstack11l1ll1_opy_ (u"ࠥࡦࡪ࡬࡯ࡳࡧࡖࡸࡪࡶࠢர"), bstack1l11l1ll_opy_=bstack1lll1l11l_opy_)
def bstack1lll11l1_opy_(runner, name, context, bstack1l1ll11l1_opy_, *args):
    bstack11l1111l_opy_(runner, name, context, args[0], bstack1l1ll11l1_opy_, *args)
    try:
      bstack1lllll1111_opy_ = threading.current_thread().bstackSessionDriver if bstack11ll11ll11_opy_(bstack11l1ll1_opy_ (u"ࠫࡧࡹࡴࡢࡥ࡮ࡗࡪࡹࡳࡪࡱࡱࡈࡷ࡯ࡶࡦࡴࠪற")) else context.browser
      if is_driver_active(bstack1lllll1111_opy_):
        if runner.driver_initialised is None: runner.driver_initialised = bstack11l1ll1_opy_ (u"ࠧࡨࡥࡧࡱࡵࡩࡤࡹࡴࡦࡲࠥல")
        bstack1l11111lll_opy_.bstack1ll111l1l1_opy_(args[0])
        if runner.driver_initialised == bstack11l1ll1_opy_ (u"ࠨࡢࡦࡨࡲࡶࡪࡥࡳࡵࡧࡳࠦள"):
          feature_name = bstack1l1llllll_opy_ = str(runner.feature.name)
          bstack1l1llllll_opy_ = feature_name + bstack11l1ll1_opy_ (u"ࠧࠡ࠯ࠣࠫழ") + context.scenario.name
          bstack1lllll1111_opy_.execute_script(bstack11l1ll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࡟ࡦࡺࡨࡧࡺࡺ࡯ࡳ࠼ࠣࡿࠧࡧࡣࡵ࡫ࡲࡲࠧࡀࠠࠣࡵࡨࡸࡘ࡫ࡳࡴ࡫ࡲࡲࡓࡧ࡭ࡦࠤ࠯ࠤࠧࡧࡲࡨࡷࡰࡩࡳࡺࡳࠣ࠼ࠣࡿࠧࡴࡡ࡮ࡧࠥ࠾ࠥ࠭வ") + json.dumps(bstack1l1llllll_opy_) + bstack11l1ll1_opy_ (u"ࠩࢀࢁࠬஶ"))
    except Exception as e:
      logger.debug(bstack11l1ll1_opy_ (u"ࠪࡊࡦ࡯࡬ࡦࡦࠣࡸࡴࠦࡳࡦࡶࠣࡷࡪࡹࡳࡪࡱࡱࠤࡳࡧ࡭ࡦࠢ࡬ࡲࠥࡨࡥࡧࡱࡵࡩࠥࡹࡴࡦࡲ࠽ࠤࢀࢃࠧஷ").format(str(e)))
@measure(event_name=EVENTS.bstack1lll111l11_opy_, stage=STAGE.bstack1l1ll1llll_opy_, hook_type=bstack11l1ll1_opy_ (u"ࠦࡦ࡬ࡴࡦࡴࡖࡸࡪࡶࠢஸ"), bstack1l11l1ll_opy_=bstack1lll1l11l_opy_)
def bstack1llllll1l1_opy_(runner, name, context, bstack1l1ll11l1_opy_, *args):
  bstack1l11111lll_opy_.bstack11lllllll_opy_(args[0])
  try:
    bstack111l11111_opy_ = args[0].status.name
    bstack1lllll1111_opy_ = threading.current_thread().bstackSessionDriver if bstack11l1ll1_opy_ (u"ࠬࡨࡳࡵࡣࡦ࡯ࡘ࡫ࡳࡴ࡫ࡲࡲࡉࡸࡩࡷࡧࡵࠫஹ") in threading.current_thread().__dict__.keys() else context.browser
    if is_driver_active(bstack1lllll1111_opy_):
      if runner.driver_initialised is None:
        runner.driver_initialised  = bstack11l1ll1_opy_ (u"࠭ࡩ࡯ࡵࡷࡩࡵ࠭஺")
        feature_name = bstack1l1llllll_opy_ = str(runner.feature.name)
        bstack1l1llllll_opy_ = feature_name + bstack11l1ll1_opy_ (u"ࠧࠡ࠯ࠣࠫ஻") + context.scenario.name
        bstack1lllll1111_opy_.execute_script(bstack11l1ll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࡟ࡦࡺࡨࡧࡺࡺ࡯ࡳ࠼ࠣࡿࠧࡧࡣࡵ࡫ࡲࡲࠧࡀࠠࠣࡵࡨࡸࡘ࡫ࡳࡴ࡫ࡲࡲࡓࡧ࡭ࡦࠤ࠯ࠤࠧࡧࡲࡨࡷࡰࡩࡳࡺࡳࠣ࠼ࠣࡿࠧࡴࡡ࡮ࡧࠥ࠾ࠥ࠭஼") + json.dumps(bstack1l1llllll_opy_) + bstack11l1ll1_opy_ (u"ࠩࢀࢁࠬ஽"))
    if str(bstack111l11111_opy_).lower() == bstack11l1ll1_opy_ (u"ࠪࡪࡦ࡯࡬ࡦࡦࠪா"):
      bstack1lll1l1ll1_opy_ = bstack11l1ll1_opy_ (u"ࠫࠬி")
      bstack1l1l11l11l_opy_ = bstack11l1ll1_opy_ (u"ࠬ࠭ீ")
      bstack1llllllll1_opy_ = bstack11l1ll1_opy_ (u"࠭ࠧு")
      try:
        import traceback
        bstack1lll1l1ll1_opy_ = runner.exception.__class__.__name__
        bstack1ll11lll1l_opy_ = traceback.format_tb(runner.exc_traceback)
        bstack1l1l11l11l_opy_ = bstack11l1ll1_opy_ (u"ࠧࠡࠩூ").join(bstack1ll11lll1l_opy_)
        bstack1llllllll1_opy_ = bstack1ll11lll1l_opy_[-1]
      except Exception as e:
        logger.debug(bstack1ll1ll111l_opy_.format(str(e)))
      bstack1lll1l1ll1_opy_ += bstack1llllllll1_opy_
      bstack1ll1111l1l_opy_(context, json.dumps(str(args[0].name) + bstack11l1ll1_opy_ (u"ࠣࠢ࠰ࠤࡋࡧࡩ࡭ࡧࡧࠥࡡࡴࠢ௃") + str(bstack1l1l11l11l_opy_)),
                          bstack11l1ll1_opy_ (u"ࠤࡨࡶࡷࡵࡲࠣ௄"))
      if runner.driver_initialised == bstack11l1ll1_opy_ (u"ࠥࡦࡪ࡬࡯ࡳࡧࡢࡷࡹ࡫ࡰࠣ௅"):
        bstack11l1111l1_opy_(getattr(context, bstack11l1ll1_opy_ (u"ࠫࡵࡧࡧࡦࠩெ"), None), bstack11l1ll1_opy_ (u"ࠧ࡬ࡡࡪ࡮ࡨࡨࠧே"), bstack1lll1l1ll1_opy_)
        bstack1lllll1111_opy_.execute_script(bstack11l1ll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡤ࡫ࡸࡦࡥࡸࡸࡴࡸ࠺ࠡࡽࠥࡥࡨࡺࡩࡰࡰࠥ࠾ࠥࠨࡡ࡯ࡰࡲࡸࡦࡺࡥࠣ࠮ࠣࠦࡦࡸࡧࡶ࡯ࡨࡲࡹࡹࠢ࠻ࠢࡾࠦࡩࡧࡴࡢࠤ࠽ࠫை") + json.dumps(str(args[0].name) + bstack11l1ll1_opy_ (u"ࠢࠡ࠯ࠣࡊࡦ࡯࡬ࡦࡦࠤࡠࡳࠨ௉") + str(bstack1l1l11l11l_opy_)) + bstack11l1ll1_opy_ (u"ࠨ࠮ࠣࠦࡱ࡫ࡶࡦ࡮ࠥ࠾ࠥࠨࡥࡳࡴࡲࡶࠧࢃࡽࠨொ"))
      if runner.driver_initialised == bstack11l1ll1_opy_ (u"ࠤࡥࡩ࡫ࡵࡲࡦࡡࡶࡸࡪࡶࠢோ"):
        bstack1ll1llllll_opy_(bstack1lllll1111_opy_, bstack11l1ll1_opy_ (u"ࠪࡪࡦ࡯࡬ࡦࡦࠪௌ"), bstack11l1ll1_opy_ (u"ࠦࡘࡩࡥ࡯ࡣࡵ࡭ࡴࠦࡦࡢ࡫࡯ࡩࡩࠦࡷࡪࡶ࡫࠾ࠥࡢ࡮்ࠣ") + str(bstack1lll1l1ll1_opy_))
    else:
      bstack1ll1111l1l_opy_(context, bstack11l1ll1_opy_ (u"ࠧࡖࡡࡴࡵࡨࡨࠦࠨ௎"), bstack11l1ll1_opy_ (u"ࠨࡩ࡯ࡨࡲࠦ௏"))
      if runner.driver_initialised == bstack11l1ll1_opy_ (u"ࠢࡣࡧࡩࡳࡷ࡫࡟ࡴࡶࡨࡴࠧௐ"):
        bstack11l1111l1_opy_(getattr(context, bstack11l1ll1_opy_ (u"ࠨࡲࡤ࡫ࡪ࠭௑"), None), bstack11l1ll1_opy_ (u"ࠤࡳࡥࡸࡹࡥࡥࠤ௒"))
      bstack1lllll1111_opy_.execute_script(bstack11l1ll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡡࡨࡼࡪࡩࡵࡵࡱࡵ࠾ࠥࢁࠢࡢࡥࡷ࡭ࡴࡴࠢ࠻ࠢࠥࡥࡳࡴ࡯ࡵࡣࡷࡩࠧ࠲ࠠࠣࡣࡵ࡫ࡺࡳࡥ࡯ࡶࡶࠦ࠿ࠦࡻࠣࡦࡤࡸࡦࠨ࠺ࠨ௓") + json.dumps(str(args[0].name) + bstack11l1ll1_opy_ (u"ࠦࠥ࠳ࠠࡑࡣࡶࡷࡪࡪࠡࠣ௔")) + bstack11l1ll1_opy_ (u"ࠬ࠲ࠠࠣ࡮ࡨࡺࡪࡲࠢ࠻ࠢࠥ࡭ࡳ࡬࡯ࠣࡿࢀࠫ௕"))
      if runner.driver_initialised == bstack11l1ll1_opy_ (u"ࠨࡢࡦࡨࡲࡶࡪࡥࡳࡵࡧࡳࠦ௖"):
        bstack1ll1llllll_opy_(bstack1lllll1111_opy_, bstack11l1ll1_opy_ (u"ࠢࡱࡣࡶࡷࡪࡪࠢௗ"))
  except Exception as e:
    logger.debug(bstack11l1ll1_opy_ (u"ࠨࡈࡤ࡭ࡱ࡫ࡤࠡࡶࡲࠤࡲࡧࡲ࡬ࠢࡶࡩࡸࡹࡩࡰࡰࠣࡷࡹࡧࡴࡶࡵࠣ࡭ࡳࠦࡡࡧࡶࡨࡶࠥࡹࡴࡦࡲ࠽ࠤࢀࢃࠧ௘").format(str(e)))
  bstack11l1111l_opy_(runner, name, context, args[0], bstack1l1ll11l1_opy_, *args)
@measure(event_name=EVENTS.bstack1l11l1111_opy_, stage=STAGE.bstack1l1ll1llll_opy_, bstack1l11l1ll_opy_=bstack1lll1l11l_opy_)
def bstack1l1111l11l_opy_(runner, name, context, bstack1l1ll11l1_opy_, *args):
  bstack1l11111lll_opy_.end_test(args[0])
  try:
    bstack1l1llllll1_opy_ = args[0].status.name
    bstack1lllll1111_opy_ = bstack1ll1l1lll_opy_(threading.current_thread(), bstack11l1ll1_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬ࡕࡨࡷࡸ࡯࡯࡯ࡆࡵ࡭ࡻ࡫ࡲࠨ௙"), context.browser)
    bstack111l1111l_opy_.bstack11111l111_opy_(bstack1lllll1111_opy_)
    if str(bstack1l1llllll1_opy_).lower() == bstack11l1ll1_opy_ (u"ࠪࡪࡦ࡯࡬ࡦࡦࠪ௚"):
      bstack1lll1l1ll1_opy_ = bstack11l1ll1_opy_ (u"ࠫࠬ௛")
      bstack1l1l11l11l_opy_ = bstack11l1ll1_opy_ (u"ࠬ࠭௜")
      bstack1llllllll1_opy_ = bstack11l1ll1_opy_ (u"࠭ࠧ௝")
      try:
        import traceback
        bstack1lll1l1ll1_opy_ = runner.exception.__class__.__name__
        bstack1ll11lll1l_opy_ = traceback.format_tb(runner.exc_traceback)
        bstack1l1l11l11l_opy_ = bstack11l1ll1_opy_ (u"ࠧࠡࠩ௞").join(bstack1ll11lll1l_opy_)
        bstack1llllllll1_opy_ = bstack1ll11lll1l_opy_[-1]
      except Exception as e:
        logger.debug(bstack1ll1ll111l_opy_.format(str(e)))
      bstack1lll1l1ll1_opy_ += bstack1llllllll1_opy_
      bstack1ll1111l1l_opy_(context, json.dumps(str(args[0].name) + bstack11l1ll1_opy_ (u"ࠣࠢ࠰ࠤࡋࡧࡩ࡭ࡧࡧࠥࡡࡴࠢ௟") + str(bstack1l1l11l11l_opy_)),
                          bstack11l1ll1_opy_ (u"ࠤࡨࡶࡷࡵࡲࠣ௠"))
      if runner.driver_initialised == bstack11l1ll1_opy_ (u"ࠥࡦࡪ࡬࡯ࡳࡧࡢࡷࡨ࡫࡮ࡢࡴ࡬ࡳࠧ௡") or runner.driver_initialised == bstack11l1ll1_opy_ (u"ࠫ࡮ࡴࡳࡵࡧࡳࠫ௢"):
        bstack11l1111l1_opy_(getattr(context, bstack11l1ll1_opy_ (u"ࠬࡶࡡࡨࡧࠪ௣"), None), bstack11l1ll1_opy_ (u"ࠨࡦࡢ࡫࡯ࡩࡩࠨ௤"), bstack1lll1l1ll1_opy_)
        bstack1lllll1111_opy_.execute_script(bstack11l1ll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡥࡥࡹࡧࡦࡹࡹࡵࡲ࠻ࠢࡾࠦࡦࡩࡴࡪࡱࡱࠦ࠿ࠦࠢࡢࡰࡱࡳࡹࡧࡴࡦࠤ࠯ࠤࠧࡧࡲࡨࡷࡰࡩࡳࡺࡳࠣ࠼ࠣࡿࠧࡪࡡࡵࡣࠥ࠾ࠬ௥") + json.dumps(str(args[0].name) + bstack11l1ll1_opy_ (u"ࠣࠢ࠰ࠤࡋࡧࡩ࡭ࡧࡧࠥࡡࡴࠢ௦") + str(bstack1l1l11l11l_opy_)) + bstack11l1ll1_opy_ (u"ࠩ࠯ࠤࠧࡲࡥࡷࡧ࡯ࠦ࠿ࠦࠢࡦࡴࡵࡳࡷࠨࡽࡾࠩ௧"))
      if runner.driver_initialised == bstack11l1ll1_opy_ (u"ࠥࡦࡪ࡬࡯ࡳࡧࡢࡷࡨ࡫࡮ࡢࡴ࡬ࡳࠧ௨") or runner.driver_initialised == bstack11l1ll1_opy_ (u"ࠫ࡮ࡴࡳࡵࡧࡳࠫ௩"):
        bstack1ll1llllll_opy_(bstack1lllll1111_opy_, bstack11l1ll1_opy_ (u"ࠬ࡬ࡡࡪ࡮ࡨࡨࠬ௪"), bstack11l1ll1_opy_ (u"ࠨࡓࡤࡧࡱࡥࡷ࡯࡯ࠡࡨࡤ࡭ࡱ࡫ࡤࠡࡹ࡬ࡸ࡭ࡀࠠ࡝ࡰࠥ௫") + str(bstack1lll1l1ll1_opy_))
    else:
      bstack1ll1111l1l_opy_(context, bstack11l1ll1_opy_ (u"ࠢࡑࡣࡶࡷࡪࡪࠡࠣ௬"), bstack11l1ll1_opy_ (u"ࠣ࡫ࡱࡪࡴࠨ௭"))
      if runner.driver_initialised == bstack11l1ll1_opy_ (u"ࠤࡥࡩ࡫ࡵࡲࡦࡡࡶࡧࡪࡴࡡࡳ࡫ࡲࠦ௮") or runner.driver_initialised == bstack11l1ll1_opy_ (u"ࠪ࡭ࡳࡹࡴࡦࡲࠪ௯"):
        bstack11l1111l1_opy_(getattr(context, bstack11l1ll1_opy_ (u"ࠫࡵࡧࡧࡦࠩ௰"), None), bstack11l1ll1_opy_ (u"ࠧࡶࡡࡴࡵࡨࡨࠧ௱"))
      bstack1lllll1111_opy_.execute_script(bstack11l1ll1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡤ࡫ࡸࡦࡥࡸࡸࡴࡸ࠺ࠡࡽࠥࡥࡨࡺࡩࡰࡰࠥ࠾ࠥࠨࡡ࡯ࡰࡲࡸࡦࡺࡥࠣ࠮ࠣࠦࡦࡸࡧࡶ࡯ࡨࡲࡹࡹࠢ࠻ࠢࡾࠦࡩࡧࡴࡢࠤ࠽ࠫ௲") + json.dumps(str(args[0].name) + bstack11l1ll1_opy_ (u"ࠢࠡ࠯ࠣࡔࡦࡹࡳࡦࡦࠤࠦ௳")) + bstack11l1ll1_opy_ (u"ࠨ࠮ࠣࠦࡱ࡫ࡶࡦ࡮ࠥ࠾ࠥࠨࡩ࡯ࡨࡲࠦࢂࢃࠧ௴"))
      if runner.driver_initialised == bstack11l1ll1_opy_ (u"ࠤࡥࡩ࡫ࡵࡲࡦࡡࡶࡧࡪࡴࡡࡳ࡫ࡲࠦ௵") or runner.driver_initialised == bstack11l1ll1_opy_ (u"ࠪ࡭ࡳࡹࡴࡦࡲࠪ௶"):
        bstack1ll1llllll_opy_(bstack1lllll1111_opy_, bstack11l1ll1_opy_ (u"ࠦࡵࡧࡳࡴࡧࡧࠦ௷"))
  except Exception as e:
    logger.debug(bstack11l1ll1_opy_ (u"ࠬࡌࡡࡪ࡮ࡨࡨࠥࡺ࡯ࠡ࡯ࡤࡶࡰࠦࡳࡦࡵࡶ࡭ࡴࡴࠠࡴࡶࡤࡸࡺࡹࠠࡪࡰࠣࡥ࡫ࡺࡥࡳࠢࡩࡩࡦࡺࡵࡳࡧ࠽ࠤࢀࢃࠧ௸").format(str(e)))
  bstack11l1111l_opy_(runner, name, context, context.scenario, bstack1l1ll11l1_opy_, *args)
  if len(context.scenario.tags) == 0: threading.current_thread().current_test_uuid = None
def bstack1lll111lll_opy_(runner, name, context, bstack1l1ll11l1_opy_, *args):
    target = context.scenario if hasattr(context, bstack11l1ll1_opy_ (u"࠭ࡳࡤࡧࡱࡥࡷ࡯࡯ࠨ௹")) else context.feature
    bstack11l1111l_opy_(runner, name, context, target, bstack1l1ll11l1_opy_, *args)
    threading.current_thread().current_test_uuid = None
def bstack11l11llll_opy_(runner, name, context, bstack1l1ll11l1_opy_, *args):
    try:
      bstack1lllll1111_opy_ = bstack1ll1l1lll_opy_(threading.current_thread(), bstack11l1ll1_opy_ (u"ࠧࡣࡵࡷࡥࡨࡱࡓࡦࡵࡶ࡭ࡴࡴࡄࡳ࡫ࡹࡩࡷ࠭௺"), context.browser)
      bstack1ll11l11l_opy_ = bstack11l1ll1_opy_ (u"ࠨࠩ௻")
      if context.failed is True:
        bstack1l11l11111_opy_ = []
        bstack1ll11111l_opy_ = []
        bstack1l1lllll11_opy_ = []
        try:
          import traceback
          for exc in runner.exception_arr:
            bstack1l11l11111_opy_.append(exc.__class__.__name__)
          for exc_tb in runner.exc_traceback_arr:
            bstack1ll11lll1l_opy_ = traceback.format_tb(exc_tb)
            bstack1ll11ll111_opy_ = bstack11l1ll1_opy_ (u"ࠩࠣࠫ௼").join(bstack1ll11lll1l_opy_)
            bstack1ll11111l_opy_.append(bstack1ll11ll111_opy_)
            bstack1l1lllll11_opy_.append(bstack1ll11lll1l_opy_[-1])
        except Exception as e:
          logger.debug(bstack1ll1ll111l_opy_.format(str(e)))
        bstack1lll1l1ll1_opy_ = bstack11l1ll1_opy_ (u"ࠪࠫ௽")
        for i in range(len(bstack1l11l11111_opy_)):
          bstack1lll1l1ll1_opy_ += bstack1l11l11111_opy_[i] + bstack1l1lllll11_opy_[i] + bstack11l1ll1_opy_ (u"ࠫࡡࡴࠧ௾")
        bstack1ll11l11l_opy_ = bstack11l1ll1_opy_ (u"ࠬࠦࠧ௿").join(bstack1ll11111l_opy_)
        if runner.driver_initialised in [bstack11l1ll1_opy_ (u"ࠨࡢࡦࡨࡲࡶࡪࡥࡦࡦࡣࡷࡹࡷ࡫ࠢఀ"), bstack11l1ll1_opy_ (u"ࠢࡣࡧࡩࡳࡷ࡫࡟ࡢ࡮࡯ࠦఁ")]:
          bstack1ll1111l1l_opy_(context, bstack1ll11l11l_opy_, bstack11l1ll1_opy_ (u"ࠣࡧࡵࡶࡴࡸࠢం"))
          bstack11l1111l1_opy_(getattr(context, bstack11l1ll1_opy_ (u"ࠩࡳࡥ࡬࡫ࠧః"), None), bstack11l1ll1_opy_ (u"ࠥࡪࡦ࡯࡬ࡦࡦࠥఄ"), bstack1lll1l1ll1_opy_)
          bstack1lllll1111_opy_.execute_script(bstack11l1ll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡢࡩࡽ࡫ࡣࡶࡶࡲࡶ࠿ࠦࡻࠣࡣࡦࡸ࡮ࡵ࡮ࠣ࠼ࠣࠦࡦࡴ࡮ࡰࡶࡤࡸࡪࠨࠬࠡࠤࡤࡶ࡬ࡻ࡭ࡦࡰࡷࡷࠧࡀࠠࡼࠤࡧࡥࡹࡧࠢ࠻ࠩఅ") + json.dumps(bstack1ll11l11l_opy_) + bstack11l1ll1_opy_ (u"ࠬ࠲ࠠࠣ࡮ࡨࡺࡪࡲࠢ࠻ࠢࠥࡩࡷࡸ࡯ࡳࠤࢀࢁࠬఆ"))
          bstack1ll1llllll_opy_(bstack1lllll1111_opy_, bstack11l1ll1_opy_ (u"ࠨࡦࡢ࡫࡯ࡩࡩࠨఇ"), bstack11l1ll1_opy_ (u"ࠢࡔࡱࡰࡩࠥࡹࡣࡦࡰࡤࡶ࡮ࡵࡳࠡࡨࡤ࡭ࡱ࡫ࡤ࠻ࠢ࡟ࡲࠧఈ") + str(bstack1lll1l1ll1_opy_))
          bstack1l11l1ll11_opy_ = bstack1l1111l1_opy_(bstack1ll11l11l_opy_, runner.feature.name, logger)
          if (bstack1l11l1ll11_opy_ != None):
            bstack111lll11_opy_.append(bstack1l11l1ll11_opy_)
      else:
        if runner.driver_initialised in [bstack11l1ll1_opy_ (u"ࠣࡤࡨࡪࡴࡸࡥࡠࡨࡨࡥࡹࡻࡲࡦࠤఉ"), bstack11l1ll1_opy_ (u"ࠤࡥࡩ࡫ࡵࡲࡦࡡࡤࡰࡱࠨఊ")]:
          bstack1ll1111l1l_opy_(context, bstack11l1ll1_opy_ (u"ࠥࡊࡪࡧࡴࡶࡴࡨ࠾ࠥࠨఋ") + str(runner.feature.name) + bstack11l1ll1_opy_ (u"ࠦࠥࡶࡡࡴࡵࡨࡨࠦࠨఌ"), bstack11l1ll1_opy_ (u"ࠧ࡯࡮ࡧࡱࠥ఍"))
          bstack11l1111l1_opy_(getattr(context, bstack11l1ll1_opy_ (u"࠭ࡰࡢࡩࡨࠫఎ"), None), bstack11l1ll1_opy_ (u"ࠢࡱࡣࡶࡷࡪࡪࠢఏ"))
          bstack1lllll1111_opy_.execute_script(bstack11l1ll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࡟ࡦࡺࡨࡧࡺࡺ࡯ࡳ࠼ࠣࡿࠧࡧࡣࡵ࡫ࡲࡲࠧࡀࠠࠣࡣࡱࡲࡴࡺࡡࡵࡧࠥ࠰ࠥࠨࡡࡳࡩࡸࡱࡪࡴࡴࡴࠤ࠽ࠤࢀࠨࡤࡢࡶࡤࠦ࠿࠭ఐ") + json.dumps(bstack11l1ll1_opy_ (u"ࠤࡉࡩࡦࡺࡵࡳࡧ࠽ࠤࠧ఑") + str(runner.feature.name) + bstack11l1ll1_opy_ (u"ࠥࠤࡵࡧࡳࡴࡧࡧࠥࠧఒ")) + bstack11l1ll1_opy_ (u"ࠫ࠱ࠦࠢ࡭ࡧࡹࡩࡱࠨ࠺ࠡࠤ࡬ࡲ࡫ࡵࠢࡾࡿࠪఓ"))
          bstack1ll1llllll_opy_(bstack1lllll1111_opy_, bstack11l1ll1_opy_ (u"ࠬࡶࡡࡴࡵࡨࡨࠬఔ"))
          bstack1l11l1ll11_opy_ = bstack1l1111l1_opy_(bstack1ll11l11l_opy_, runner.feature.name, logger)
          if (bstack1l11l1ll11_opy_ != None):
            bstack111lll11_opy_.append(bstack1l11l1ll11_opy_)
    except Exception as e:
      logger.debug(bstack11l1ll1_opy_ (u"࠭ࡆࡢ࡫࡯ࡩࡩࠦࡴࡰࠢࡰࡥࡷࡱࠠࡴࡧࡶࡷ࡮ࡵ࡮ࠡࡵࡷࡥࡹࡻࡳࠡ࡫ࡱࠤࡦ࡬ࡴࡦࡴࠣࡪࡪࡧࡴࡶࡴࡨ࠾ࠥࢁࡽࠨక").format(str(e)))
    bstack11l1111l_opy_(runner, name, context, context.feature, bstack1l1ll11l1_opy_, *args)
@measure(event_name=EVENTS.bstack1lll111l11_opy_, stage=STAGE.bstack1l1ll1llll_opy_, hook_type=bstack11l1ll1_opy_ (u"ࠢࡢࡨࡷࡩࡷࡇ࡬࡭ࠤఖ"), bstack1l11l1ll_opy_=bstack1lll1l11l_opy_)
def bstack1l11l11lll_opy_(runner, name, context, bstack1l1ll11l1_opy_, *args):
    bstack11l1111l_opy_(runner, name, context, runner, bstack1l1ll11l1_opy_, *args)
def bstack1l1lll1ll_opy_(self, name, context, *args):
  if bstack1111l1111_opy_:
    platform_index = int(threading.current_thread()._name) % bstack1lll1l1ll_opy_
    bstack1lll11ll1l_opy_ = CONFIG[bstack11l1ll1_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫగ")][platform_index]
    os.environ[bstack11l1ll1_opy_ (u"ࠩࡆ࡙ࡗࡘࡅࡏࡖࡢࡔࡑࡇࡔࡇࡑࡕࡑࡤࡊࡁࡕࡃࠪఘ")] = json.dumps(bstack1lll11ll1l_opy_)
  global bstack1l1ll11l1_opy_
  if not hasattr(self, bstack11l1ll1_opy_ (u"ࠪࡨࡷ࡯ࡶࡦࡴࡢ࡭ࡳ࡯ࡴࡪࡣ࡯࡭ࡸ࡫ࡤࠨఙ")):
    self.driver_initialised = None
  bstack1111lll1_opy_ = {
      bstack11l1ll1_opy_ (u"ࠫࡧ࡫ࡦࡰࡴࡨࡣࡦࡲ࡬ࠨచ"): bstack1l11111111_opy_,
      bstack11l1ll1_opy_ (u"ࠬࡨࡥࡧࡱࡵࡩࡤ࡬ࡥࡢࡶࡸࡶࡪ࠭ఛ"): bstack1ll1l1l1ll_opy_,
      bstack11l1ll1_opy_ (u"࠭ࡢࡦࡨࡲࡶࡪࡥࡴࡢࡩࠪజ"): bstack1ll1l11ll1_opy_,
      bstack11l1ll1_opy_ (u"ࠧࡣࡧࡩࡳࡷ࡫࡟ࡴࡥࡨࡲࡦࡸࡩࡰࠩఝ"): bstack11l11l11l_opy_,
      bstack11l1ll1_opy_ (u"ࠨࡤࡨࡪࡴࡸࡥࡠࡵࡷࡩࡵ࠭ఞ"): bstack1lll11l1_opy_,
      bstack11l1ll1_opy_ (u"ࠩࡤࡪࡹ࡫ࡲࡠࡵࡷࡩࡵ࠭ట"): bstack1llllll1l1_opy_,
      bstack11l1ll1_opy_ (u"ࠪࡥ࡫ࡺࡥࡳࡡࡶࡧࡪࡴࡡࡳ࡫ࡲࠫఠ"): bstack1l1111l11l_opy_,
      bstack11l1ll1_opy_ (u"ࠫࡦ࡬ࡴࡦࡴࡢࡸࡦ࡭ࠧడ"): bstack1lll111lll_opy_,
      bstack11l1ll1_opy_ (u"ࠬࡧࡦࡵࡧࡵࡣ࡫࡫ࡡࡵࡷࡵࡩࠬఢ"): bstack11l11llll_opy_,
      bstack11l1ll1_opy_ (u"࠭ࡡࡧࡶࡨࡶࡤࡧ࡬࡭ࠩణ"): bstack1l11l11lll_opy_
  }
  handler = bstack1111lll1_opy_.get(name, bstack1l1ll11l1_opy_)
  handler(self, name, context, bstack1l1ll11l1_opy_, *args)
  if name in [bstack11l1ll1_opy_ (u"ࠧࡢࡨࡷࡩࡷࡥࡦࡦࡣࡷࡹࡷ࡫ࠧత"), bstack11l1ll1_opy_ (u"ࠨࡣࡩࡸࡪࡸ࡟ࡴࡥࡨࡲࡦࡸࡩࡰࠩథ"), bstack11l1ll1_opy_ (u"ࠩࡤࡪࡹ࡫ࡲࡠࡣ࡯ࡰࠬద")]:
    try:
      bstack1lllll1111_opy_ = threading.current_thread().bstackSessionDriver if bstack11ll11ll11_opy_(bstack11l1ll1_opy_ (u"ࠪࡦࡸࡺࡡࡤ࡭ࡖࡩࡸࡹࡩࡰࡰࡇࡶ࡮ࡼࡥࡳࠩధ")) else context.browser
      bstack1111l1l11_opy_ = (
        (name == bstack11l1ll1_opy_ (u"ࠫࡦ࡬ࡴࡦࡴࡢࡥࡱࡲࠧన") and self.driver_initialised == bstack11l1ll1_opy_ (u"ࠧࡨࡥࡧࡱࡵࡩࡤࡧ࡬࡭ࠤ఩")) or
        (name == bstack11l1ll1_opy_ (u"࠭ࡡࡧࡶࡨࡶࡤ࡬ࡥࡢࡶࡸࡶࡪ࠭ప") and self.driver_initialised == bstack11l1ll1_opy_ (u"ࠢࡣࡧࡩࡳࡷ࡫࡟ࡧࡧࡤࡸࡺࡸࡥࠣఫ")) or
        (name == bstack11l1ll1_opy_ (u"ࠨࡣࡩࡸࡪࡸ࡟ࡴࡥࡨࡲࡦࡸࡩࡰࠩబ") and self.driver_initialised in [bstack11l1ll1_opy_ (u"ࠤࡥࡩ࡫ࡵࡲࡦࡡࡶࡧࡪࡴࡡࡳ࡫ࡲࠦభ"), bstack11l1ll1_opy_ (u"ࠥ࡭ࡳࡹࡴࡦࡲࠥమ")]) or
        (name == bstack11l1ll1_opy_ (u"ࠫࡦ࡬ࡴࡦࡴࡢࡷࡹ࡫ࡰࠨయ") and self.driver_initialised == bstack11l1ll1_opy_ (u"ࠧࡨࡥࡧࡱࡵࡩࡤࡹࡴࡦࡲࠥర"))
      )
      if bstack1111l1l11_opy_:
        self.driver_initialised = None
        bstack1lllll1111_opy_.quit()
    except Exception:
      pass
def bstack1l111lll_opy_(config, startdir):
  return bstack11l1ll1_opy_ (u"ࠨࡤࡳ࡫ࡹࡩࡷࡀࠠࡼ࠲ࢀࠦఱ").format(bstack11l1ll1_opy_ (u"ࠢࡃࡴࡲࡻࡸ࡫ࡲࡔࡶࡤࡧࡰࠨల"))
notset = Notset()
def bstack1ll11l1ll_opy_(self, name: str, default=notset, skip: bool = False):
  global bstack11l1lllll1_opy_
  if str(name).lower() == bstack11l1ll1_opy_ (u"ࠨࡦࡵ࡭ࡻ࡫ࡲࠨళ"):
    return bstack11l1ll1_opy_ (u"ࠤࡅࡶࡴࡽࡳࡦࡴࡖࡸࡦࡩ࡫ࠣఴ")
  else:
    return bstack11l1lllll1_opy_(self, name, default, skip)
def bstack1111l11ll_opy_(item, when):
  global bstack1l1l111l1_opy_
  try:
    bstack1l1l111l1_opy_(item, when)
  except Exception as e:
    pass
def bstack1l1111llll_opy_():
  return
def bstack1lll111ll_opy_(type, name, status, reason, bstack1lll11l1l_opy_, bstack1llll1l11_opy_):
  bstack11l1lll1ll_opy_ = {
    bstack11l1ll1_opy_ (u"ࠪࡥࡨࡺࡩࡰࡰࠪవ"): type,
    bstack11l1ll1_opy_ (u"ࠫࡦࡸࡧࡶ࡯ࡨࡲࡹࡹࠧశ"): {}
  }
  if type == bstack11l1ll1_opy_ (u"ࠬࡧ࡮࡯ࡱࡷࡥࡹ࡫ࠧష"):
    bstack11l1lll1ll_opy_[bstack11l1ll1_opy_ (u"࠭ࡡࡳࡩࡸࡱࡪࡴࡴࡴࠩస")][bstack11l1ll1_opy_ (u"ࠧ࡭ࡧࡹࡩࡱ࠭హ")] = bstack1lll11l1l_opy_
    bstack11l1lll1ll_opy_[bstack11l1ll1_opy_ (u"ࠨࡣࡵ࡫ࡺࡳࡥ࡯ࡶࡶࠫ఺")][bstack11l1ll1_opy_ (u"ࠩࡧࡥࡹࡧࠧ఻")] = json.dumps(str(bstack1llll1l11_opy_))
  if type == bstack11l1ll1_opy_ (u"ࠪࡷࡪࡺࡓࡦࡵࡶ࡭ࡴࡴࡎࡢ࡯ࡨ఼ࠫ"):
    bstack11l1lll1ll_opy_[bstack11l1ll1_opy_ (u"ࠫࡦࡸࡧࡶ࡯ࡨࡲࡹࡹࠧఽ")][bstack11l1ll1_opy_ (u"ࠬࡴࡡ࡮ࡧࠪా")] = name
  if type == bstack11l1ll1_opy_ (u"࠭ࡳࡦࡶࡖࡩࡸࡹࡩࡰࡰࡖࡸࡦࡺࡵࡴࠩి"):
    bstack11l1lll1ll_opy_[bstack11l1ll1_opy_ (u"ࠧࡢࡴࡪࡹࡲ࡫࡮ࡵࡵࠪీ")][bstack11l1ll1_opy_ (u"ࠨࡵࡷࡥࡹࡻࡳࠨు")] = status
    if status == bstack11l1ll1_opy_ (u"ࠩࡩࡥ࡮ࡲࡥࡥࠩూ"):
      bstack11l1lll1ll_opy_[bstack11l1ll1_opy_ (u"ࠪࡥࡷ࡭ࡵ࡮ࡧࡱࡸࡸ࠭ృ")][bstack11l1ll1_opy_ (u"ࠫࡷ࡫ࡡࡴࡱࡱࠫౄ")] = json.dumps(str(reason))
  bstack1lll1ll11l_opy_ = bstack11l1ll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡣࡪࡾࡥࡤࡷࡷࡳࡷࡀࠠࡼࡿࠪ౅").format(json.dumps(bstack11l1lll1ll_opy_))
  return bstack1lll1ll11l_opy_
def bstack1l1ll1111_opy_(driver_command, response):
    if driver_command == bstack11l1ll1_opy_ (u"࠭ࡳࡤࡴࡨࡩࡳࡹࡨࡰࡶࠪె"):
        bstack11111l1l1_opy_.bstack1lllll1l1l_opy_({
            bstack11l1ll1_opy_ (u"ࠧࡪ࡯ࡤ࡫ࡪ࠭ే"): response[bstack11l1ll1_opy_ (u"ࠨࡸࡤࡰࡺ࡫ࠧై")],
            bstack11l1ll1_opy_ (u"ࠩࡷࡩࡸࡺ࡟ࡳࡷࡱࡣࡺࡻࡩࡥࠩ౉"): bstack11111l1l1_opy_.current_test_uuid()
        })
def bstack1l1lll11l_opy_(item, call, rep):
  global bstack1lll1lll11_opy_
  global bstack1l1ll1l1l1_opy_
  global bstack1lll11lll_opy_
  name = bstack11l1ll1_opy_ (u"ࠪࠫొ")
  try:
    if rep.when == bstack11l1ll1_opy_ (u"ࠫࡨࡧ࡬࡭ࠩో"):
      bstack1l1l1ll1_opy_ = threading.current_thread().bstackSessionId
      try:
        if not bstack1lll11lll_opy_:
          name = str(rep.nodeid)
          bstack1lll1lll1l_opy_ = bstack1lll111ll_opy_(bstack11l1ll1_opy_ (u"ࠬࡹࡥࡵࡕࡨࡷࡸ࡯࡯࡯ࡐࡤࡱࡪ࠭ౌ"), name, bstack11l1ll1_opy_ (u"్࠭ࠧ"), bstack11l1ll1_opy_ (u"ࠧࠨ౎"), bstack11l1ll1_opy_ (u"ࠨࠩ౏"), bstack11l1ll1_opy_ (u"ࠩࠪ౐"))
          threading.current_thread().bstack11llllllll_opy_ = name
          for driver in bstack1l1ll1l1l1_opy_:
            if bstack1l1l1ll1_opy_ == driver.session_id:
              driver.execute_script(bstack1lll1lll1l_opy_)
      except Exception as e:
        logger.debug(bstack11l1ll1_opy_ (u"ࠪࡉࡷࡸ࡯ࡳࠢ࡬ࡲࠥࡹࡥࡵࡶ࡬ࡲ࡬ࠦࡳࡦࡵࡶ࡭ࡴࡴࡎࡢ࡯ࡨࠤ࡫ࡵࡲࠡࡲࡼࡸࡪࡹࡴ࠮ࡤࡧࡨࠥࡹࡥࡴࡵ࡬ࡳࡳࡀࠠࡼࡿࠪ౑").format(str(e)))
      try:
        bstack11l1ll1l_opy_(rep.outcome.lower())
        if rep.outcome.lower() != bstack11l1ll1_opy_ (u"ࠫࡸࡱࡩࡱࡲࡨࡨࠬ౒"):
          status = bstack11l1ll1_opy_ (u"ࠬ࡬ࡡࡪ࡮ࡨࡨࠬ౓") if rep.outcome.lower() == bstack11l1ll1_opy_ (u"࠭ࡦࡢ࡫࡯ࡩࡩ࠭౔") else bstack11l1ll1_opy_ (u"ࠧࡱࡣࡶࡷࡪࡪౕࠧ")
          reason = bstack11l1ll1_opy_ (u"ࠨౖࠩ")
          if status == bstack11l1ll1_opy_ (u"ࠩࡩࡥ࡮ࡲࡥࡥࠩ౗"):
            reason = rep.longrepr.reprcrash.message
            if (not threading.current_thread().bstackTestErrorMessages):
              threading.current_thread().bstackTestErrorMessages = []
            threading.current_thread().bstackTestErrorMessages.append(reason)
          level = bstack11l1ll1_opy_ (u"ࠪ࡭ࡳ࡬࡯ࠨౘ") if status == bstack11l1ll1_opy_ (u"ࠫࡵࡧࡳࡴࡧࡧࠫౙ") else bstack11l1ll1_opy_ (u"ࠬ࡫ࡲࡳࡱࡵࠫౚ")
          data = name + bstack11l1ll1_opy_ (u"࠭ࠠࡱࡣࡶࡷࡪࡪࠡࠨ౛") if status == bstack11l1ll1_opy_ (u"ࠧࡱࡣࡶࡷࡪࡪࠧ౜") else name + bstack11l1ll1_opy_ (u"ࠨࠢࡩࡥ࡮ࡲࡥࡥࠣࠣࠫౝ") + reason
          bstack11l1ll1ll1_opy_ = bstack1lll111ll_opy_(bstack11l1ll1_opy_ (u"ࠩࡤࡲࡳࡵࡴࡢࡶࡨࠫ౞"), bstack11l1ll1_opy_ (u"ࠪࠫ౟"), bstack11l1ll1_opy_ (u"ࠫࠬౠ"), bstack11l1ll1_opy_ (u"ࠬ࠭ౡ"), level, data)
          for driver in bstack1l1ll1l1l1_opy_:
            if bstack1l1l1ll1_opy_ == driver.session_id:
              driver.execute_script(bstack11l1ll1ll1_opy_)
      except Exception as e:
        logger.debug(bstack11l1ll1_opy_ (u"࠭ࡅࡳࡴࡲࡶࠥ࡯࡮ࠡࡵࡨࡸࡹ࡯࡮ࡨࠢࡶࡩࡸࡹࡩࡰࡰࠣࡧࡴࡴࡴࡦࡺࡷࠤ࡫ࡵࡲࠡࡲࡼࡸࡪࡹࡴ࠮ࡤࡧࡨࠥࡹࡥࡴࡵ࡬ࡳࡳࡀࠠࡼࡿࠪౢ").format(str(e)))
  except Exception as e:
    logger.debug(bstack11l1ll1_opy_ (u"ࠧࡆࡴࡵࡳࡷࠦࡩ࡯ࠢࡪࡩࡹࡺࡩ࡯ࡩࠣࡷࡹࡧࡴࡦࠢ࡬ࡲࠥࡶࡹࡵࡧࡶࡸ࠲ࡨࡤࡥࠢࡷࡩࡸࡺࠠࡴࡶࡤࡸࡺࡹ࠺ࠡࡽࢀࠫౣ").format(str(e)))
  bstack1lll1lll11_opy_(item, call, rep)
def bstack1l111l1lll_opy_(driver, bstack11l11lll1_opy_, test=None):
  global bstack1ll1ll1ll_opy_
  if test != None:
    bstack1llll1l11l_opy_ = getattr(test, bstack11l1ll1_opy_ (u"ࠨࡰࡤࡱࡪ࠭౤"), None)
    bstack111l1ll11_opy_ = getattr(test, bstack11l1ll1_opy_ (u"ࠩࡸࡹ࡮ࡪࠧ౥"), None)
    PercySDK.screenshot(driver, bstack11l11lll1_opy_, bstack1llll1l11l_opy_=bstack1llll1l11l_opy_, bstack111l1ll11_opy_=bstack111l1ll11_opy_, bstack1l1lll1ll1_opy_=bstack1ll1ll1ll_opy_)
  else:
    PercySDK.screenshot(driver, bstack11l11lll1_opy_)
@measure(event_name=EVENTS.bstack1l11l11l11_opy_, stage=STAGE.bstack1l1ll1llll_opy_, bstack1l11l1ll_opy_=bstack1lll1l11l_opy_)
def bstack1lllllll1_opy_(driver):
  if bstack111ll11ll_opy_.bstack1ll1l111_opy_() is True or bstack111ll11ll_opy_.capturing() is True:
    return
  bstack111ll11ll_opy_.bstack11llll111l_opy_()
  while not bstack111ll11ll_opy_.bstack1ll1l111_opy_():
    bstack1l11llll_opy_ = bstack111ll11ll_opy_.bstack1ll11llll1_opy_()
    bstack1l111l1lll_opy_(driver, bstack1l11llll_opy_)
  bstack111ll11ll_opy_.bstack1l1l111111_opy_()
def bstack1llll11ll_opy_(sequence, driver_command, response = None, bstack1lllll111l_opy_ = None, args = None):
    try:
      if sequence != bstack11l1ll1_opy_ (u"ࠪࡦࡪ࡬࡯ࡳࡧࠪ౦"):
        return
      if percy.bstack1l1111111_opy_() == bstack11l1ll1_opy_ (u"ࠦ࡫ࡧ࡬ࡴࡧࠥ౧"):
        return
      bstack1l11llll_opy_ = bstack1ll1l1lll_opy_(threading.current_thread(), bstack11l1ll1_opy_ (u"ࠬࡶࡥࡳࡥࡼࡗࡪࡹࡳࡪࡱࡱࡒࡦࡳࡥࠨ౨"), None)
      for command in bstack1l1l1111l_opy_:
        if command == driver_command:
          for driver in bstack1l1ll1l1l1_opy_:
            bstack1lllllll1_opy_(driver)
      bstack1ll1lll1l1_opy_ = percy.bstack111llll1l_opy_()
      if driver_command in bstack11lll11111_opy_[bstack1ll1lll1l1_opy_]:
        bstack111ll11ll_opy_.bstack11lllll111_opy_(bstack1l11llll_opy_, driver_command)
    except Exception as e:
      pass
def bstack1l1lll11_opy_(framework_name):
  if bstack1ll1l11l1_opy_.get_property(bstack11l1ll1_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰࡥ࡭ࡰࡦࡢࡧࡦࡲ࡬ࡦࡦࠪ౩")):
      return
  bstack1ll1l11l1_opy_.bstack1l111llll1_opy_(bstack11l1ll1_opy_ (u"ࠧࡣࡵࡷࡥࡨࡱ࡟࡮ࡱࡧࡣࡨࡧ࡬࡭ࡧࡧࠫ౪"), True)
  global bstack111111ll1_opy_
  global bstack1111111ll_opy_
  global bstack1111l1l1l_opy_
  bstack111111ll1_opy_ = framework_name
  logger.info(bstack1ll1l1111_opy_.format(bstack111111ll1_opy_.split(bstack11l1ll1_opy_ (u"ࠨ࠯ࠪ౫"))[0]))
  bstack1l11ll11l_opy_()
  try:
    from selenium import webdriver
    from selenium.webdriver.common.service import Service
    from selenium.webdriver.remote.webdriver import WebDriver
    if bstack1111l1111_opy_:
      Service.start = bstack1l1111111l_opy_
      Service.stop = bstack1ll111lll_opy_
      webdriver.Remote.get = bstack1l11lllll_opy_
      WebDriver.close = bstack11lll1llll_opy_
      WebDriver.quit = bstack1l1l1l11_opy_
      webdriver.Remote.__init__ = bstack11l111111_opy_
      WebDriver.getAccessibilityResults = getAccessibilityResults
      WebDriver.get_accessibility_results = getAccessibilityResults
      WebDriver.getAccessibilityResultsSummary = getAccessibilityResultsSummary
      WebDriver.get_accessibility_results_summary = getAccessibilityResultsSummary
      WebDriver.performScan = perform_scan
      WebDriver.perform_scan = perform_scan
    if not bstack1111l1111_opy_:
        webdriver.Remote.__init__ = bstack11llll1111_opy_
    WebDriver.execute = bstack1l111ll11l_opy_
    bstack1111111ll_opy_ = True
  except Exception as e:
    pass
  try:
    if bstack1111l1111_opy_:
      from QWeb.keywords import browser
      browser.close_browser = bstack1ll1ll1111_opy_
  except Exception as e:
    pass
  bstack11lll1l1ll_opy_()
  if not bstack1111111ll_opy_:
    bstack1ll11lll1_opy_(bstack11l1ll1_opy_ (u"ࠤࡓࡥࡨࡱࡡࡨࡧࡶࠤࡳࡵࡴࠡ࡫ࡱࡷࡹࡧ࡬࡭ࡧࡧࠦ౬"), bstack1llll1lll_opy_)
  if bstack1l1ll1lll_opy_():
    try:
      from selenium.webdriver.remote.remote_connection import RemoteConnection
      RemoteConnection._11ll1lll_opy_ = bstack11lll1ll1l_opy_
    except Exception as e:
      logger.error(bstack11ll1l11l1_opy_.format(str(e)))
  if bstack11l1l1l1l_opy_():
    bstack11lllll1l_opy_(CONFIG, logger)
  if (bstack11l1ll1_opy_ (u"ࠪࡶࡴࡨ࡯ࡵࠩ౭") in str(framework_name).lower()):
    try:
      from robot import run_cli
      from robot.output import Output
      from robot.running.status import TestStatus
      from pabot.pabot import QueueItem
      from pabot import pabot
      try:
        if percy.bstack1l1111111_opy_() == bstack11l1ll1_opy_ (u"ࠦࡹࡸࡵࡦࠤ౮"):
          bstack1l111111ll_opy_(bstack1llll11ll_opy_)
        from SeleniumLibrary.keywords.webdrivertools.webdrivertools import WebDriverCreator
        WebDriverCreator._get_ff_profile = bstack1ll1llll1l_opy_
        from SeleniumLibrary.keywords.webdrivertools.webdrivertools import WebDriverCache
        WebDriverCache.close = bstack111ll1l11_opy_
      except Exception as e:
        logger.warn(bstack11ll1lll1l_opy_ + str(e))
      try:
        from AppiumLibrary.utils.applicationcache import ApplicationCache
        ApplicationCache.close = bstack1ll1l1llll_opy_
      except Exception as e:
        logger.debug(bstack11lll1l1l_opy_ + str(e))
    except Exception as e:
      bstack1ll11lll1_opy_(e, bstack11ll1lll1l_opy_)
    Output.start_test = bstack1lll1111ll_opy_
    Output.end_test = bstack1l1ll111_opy_
    TestStatus.__init__ = bstack1ll1111111_opy_
    QueueItem.__init__ = bstack1l1l1lll_opy_
    pabot._create_items = bstack1l1ll11ll_opy_
    try:
      from pabot import __version__ as bstack1l1ll1ll_opy_
      if version.parse(bstack1l1ll1ll_opy_) >= version.parse(bstack11l1ll1_opy_ (u"ࠬ࠸࠮࠲࠷࠱࠴ࠬ౯")):
        pabot._run = bstack1l1l1ll11_opy_
      elif version.parse(bstack1l1ll1ll_opy_) >= version.parse(bstack11l1ll1_opy_ (u"࠭࠲࠯࠳࠶࠲࠵࠭౰")):
        pabot._run = bstack1l1lll111l_opy_
      else:
        pabot._run = bstack11l1ll111l_opy_
    except Exception as e:
      pabot._run = bstack11l1ll111l_opy_
    pabot._create_command_for_execution = bstack1l1l11l11_opy_
    pabot._report_results = bstack11111l1ll_opy_
  if bstack11l1ll1_opy_ (u"ࠧࡣࡧ࡫ࡥࡻ࡫ࠧ౱") in str(framework_name).lower():
    try:
      from behave.runner import Runner
      from behave.model import Step
    except Exception as e:
      bstack1ll11lll1_opy_(e, bstack1l11lll1l_opy_)
    Runner.run_hook = bstack1l1lll1ll_opy_
    Step.run = bstack1ll1111ll_opy_
  if bstack11l1ll1_opy_ (u"ࠨࡲࡼࡸࡪࡹࡴࠨ౲") in str(framework_name).lower():
    if not bstack1111l1111_opy_:
      return
    try:
      from pytest_selenium import pytest_selenium
      from _pytest.config import Config
      pytest_selenium.pytest_report_header = bstack1l111lll_opy_
      from pytest_selenium.drivers import browserstack
      browserstack.pytest_selenium_runtest_makereport = bstack1l1111llll_opy_
      Config.getoption = bstack1ll11l1ll_opy_
    except Exception as e:
      pass
    try:
      from pytest_bdd import reporting
      reporting.runtest_makereport = bstack1l1lll11l_opy_
    except Exception as e:
      pass
def bstack1l1111l111_opy_():
  global CONFIG
  if bstack11l1ll1_opy_ (u"ࠩࡳࡥࡷࡧ࡬࡭ࡧ࡯ࡷࡕ࡫ࡲࡑ࡮ࡤࡸ࡫ࡵࡲ࡮ࠩ౳") in CONFIG and int(CONFIG[bstack11l1ll1_opy_ (u"ࠪࡴࡦࡸࡡ࡭࡮ࡨࡰࡸࡖࡥࡳࡒ࡯ࡥࡹ࡬࡯ࡳ࡯ࠪ౴")]) > 1:
    logger.warn(bstack11ll1l111l_opy_)
def bstack11llll1ll_opy_(arg, bstack1l1lll11l1_opy_, bstack1llll11ll1_opy_=None):
  global CONFIG
  global bstack1l1ll11ll1_opy_
  global bstack11ll11ll1_opy_
  global bstack1111l1111_opy_
  global bstack1ll1l11l1_opy_
  bstack111ll1l1_opy_ = bstack11l1ll1_opy_ (u"ࠫࡵࡿࡴࡦࡵࡷࠫ౵")
  if bstack1l1lll11l1_opy_ and isinstance(bstack1l1lll11l1_opy_, str):
    bstack1l1lll11l1_opy_ = eval(bstack1l1lll11l1_opy_)
  CONFIG = bstack1l1lll11l1_opy_[bstack11l1ll1_opy_ (u"ࠬࡉࡏࡏࡈࡌࡋࠬ౶")]
  bstack1l1ll11ll1_opy_ = bstack1l1lll11l1_opy_[bstack11l1ll1_opy_ (u"࠭ࡈࡖࡄࡢ࡙ࡗࡒࠧ౷")]
  bstack11ll11ll1_opy_ = bstack1l1lll11l1_opy_[bstack11l1ll1_opy_ (u"ࠧࡊࡕࡢࡅࡕࡖ࡟ࡂࡗࡗࡓࡒࡇࡔࡆࠩ౸")]
  bstack1111l1111_opy_ = bstack1l1lll11l1_opy_[bstack11l1ll1_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡂࡗࡗࡓࡒࡇࡔࡊࡑࡑࠫ౹")]
  bstack1ll1l11l1_opy_.bstack1l111llll1_opy_(bstack11l1ll1_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬ࡡࡶࡩࡸࡹࡩࡰࡰࠪ౺"), bstack1111l1111_opy_)
  os.environ[bstack11l1ll1_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡉࡖࡆࡓࡅࡘࡑࡕࡏࠬ౻")] = bstack111ll1l1_opy_
  os.environ[bstack11l1ll1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡇࡔࡔࡆࡊࡉࠪ౼")] = json.dumps(CONFIG)
  os.environ[bstack11l1ll1_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡍ࡛ࡂࡠࡗࡕࡐࠬ౽")] = bstack1l1ll11ll1_opy_
  os.environ[bstack11l1ll1_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡏࡓࡠࡃࡓࡔࡤࡇࡕࡕࡑࡐࡅ࡙ࡋࠧ౾")] = str(bstack11ll11ll1_opy_)
  os.environ[bstack11l1ll1_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡐ࡚ࡖࡈࡗ࡙ࡥࡐࡍࡗࡊࡍࡓ࠭౿")] = str(True)
  if bstack11l111ll_opy_(arg, [bstack11l1ll1_opy_ (u"ࠨ࠯ࡱࠫಀ"), bstack11l1ll1_opy_ (u"ࠩ࠰࠱ࡳࡻ࡭ࡱࡴࡲࡧࡪࡹࡳࡦࡵࠪಁ")]) != -1:
    os.environ[bstack11l1ll1_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡓ࡝࡙ࡋࡓࡕࡡࡓࡅࡗࡇࡌࡍࡇࡏࠫಂ")] = str(True)
  if len(sys.argv) <= 1:
    logger.critical(bstack1llll11l11_opy_)
    return
  bstack1l111llll_opy_()
  global bstack111lll1l1_opy_
  global bstack1ll1ll1ll_opy_
  global bstack1ll1lll1ll_opy_
  global bstack11ll11ll_opy_
  global bstack1l11ll111l_opy_
  global bstack1111l1l1l_opy_
  global bstack11ll1ll1l1_opy_
  arg.append(bstack11l1ll1_opy_ (u"ࠦ࠲࡝ࠢಃ"))
  arg.append(bstack11l1ll1_opy_ (u"ࠧ࡯ࡧ࡯ࡱࡵࡩ࠿ࡓ࡯ࡥࡷ࡯ࡩࠥࡧ࡬ࡳࡧࡤࡨࡾࠦࡩ࡮ࡲࡲࡶࡹ࡫ࡤ࠻ࡲࡼࡸࡪࡹࡴ࠯ࡒࡼࡸࡪࡹࡴࡘࡣࡵࡲ࡮ࡴࡧࠣ಄"))
  arg.append(bstack11l1ll1_opy_ (u"ࠨ࠭ࡘࠤಅ"))
  arg.append(bstack11l1ll1_opy_ (u"ࠢࡪࡩࡱࡳࡷ࡫࠺ࡕࡪࡨࠤ࡭ࡵ࡯࡬࡫ࡰࡴࡱࠨಆ"))
  global bstack11lll111ll_opy_
  global bstack1llll11l_opy_
  global bstack11l111l1_opy_
  global bstack1lllll1l11_opy_
  global bstack11ll111l1l_opy_
  global bstack111lllll_opy_
  global bstack111ll1lll_opy_
  global bstack1l1llll1ll_opy_
  global bstack1lllll11ll_opy_
  global bstack1llll111ll_opy_
  global bstack11l1lllll1_opy_
  global bstack1l1l111l1_opy_
  global bstack1lll1lll11_opy_
  try:
    from selenium import webdriver
    from selenium.webdriver.remote.webdriver import WebDriver
    bstack11lll111ll_opy_ = webdriver.Remote.__init__
    bstack1llll11l_opy_ = WebDriver.quit
    bstack1l1llll1ll_opy_ = WebDriver.close
    bstack1lllll11ll_opy_ = WebDriver.get
    bstack11l111l1_opy_ = WebDriver.execute
  except Exception as e:
    pass
  if bstack1lll11lll1_opy_(CONFIG) and bstack11l11lll_opy_():
    if bstack1ll111111l_opy_() < version.parse(bstack11llll11_opy_):
      logger.error(bstack11l1l111l_opy_.format(bstack1ll111111l_opy_()))
    else:
      try:
        from selenium.webdriver.remote.remote_connection import RemoteConnection
        bstack1llll111ll_opy_ = RemoteConnection._11ll1lll_opy_
      except Exception as e:
        logger.error(bstack11ll1l11l1_opy_.format(str(e)))
  try:
    from _pytest.config import Config
    bstack11l1lllll1_opy_ = Config.getoption
    from _pytest import runner
    bstack1l1l111l1_opy_ = runner._update_current_test_var
  except Exception as e:
    logger.warn(e, bstack1ll1l1l111_opy_)
  try:
    from pytest_bdd import reporting
    bstack1lll1lll11_opy_ = reporting.runtest_makereport
  except Exception as e:
    logger.debug(bstack11l1ll1_opy_ (u"ࠨࡒ࡯ࡩࡦࡹࡥࠡ࡫ࡱࡷࡹࡧ࡬࡭ࠢࡳࡽࡹ࡫ࡳࡵ࠯ࡥࡨࡩࠦࡴࡰࠢࡵࡹࡳࠦࡰࡺࡶࡨࡷࡹ࠳ࡢࡥࡦࠣࡸࡪࡹࡴࡴࠩಇ"))
  bstack1ll1lll1ll_opy_ = CONFIG.get(bstack11l1ll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡖࡸࡦࡩ࡫ࡍࡱࡦࡥࡱࡕࡰࡵ࡫ࡲࡲࡸ࠭ಈ"), {}).get(bstack11l1ll1_opy_ (u"ࠪࡰࡴࡩࡡ࡭ࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬಉ"))
  bstack11ll1ll1l1_opy_ = True
  if cli.is_enabled(CONFIG):
    if cli.bstack11ll1llll1_opy_():
      bstack1l1l11lll1_opy_.invoke(bstack1ll1ll1l11_opy_.CONNECT, bstack1llll11111_opy_())
    platform_index = int(os.environ.get(bstack11l1ll1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡔࡑࡇࡔࡇࡑࡕࡑࡤࡏࡎࡅࡇ࡛ࠫಊ"), bstack11l1ll1_opy_ (u"ࠬ࠶ࠧಋ")))
  else:
    bstack1l1lll11_opy_(bstack1l11lll1_opy_)
  os.environ[bstack11l1ll1_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡛ࡓࡆࡔࡑࡅࡒࡋࠧಌ")] = CONFIG[bstack11l1ll1_opy_ (u"ࠧࡶࡵࡨࡶࡓࡧ࡭ࡦࠩ಍")]
  os.environ[bstack11l1ll1_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡂࡅࡆࡉࡘ࡙࡟ࡌࡇ࡜ࠫಎ")] = CONFIG[bstack11l1ll1_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴࡍࡨࡽࠬಏ")]
  os.environ[bstack11l1ll1_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡄ࡙࡙ࡕࡍࡂࡖࡌࡓࡓ࠭ಐ")] = bstack1111l1111_opy_.__str__()
  from _pytest.config import main as bstack1l1l111l_opy_
  bstack1l1l111l11_opy_ = []
  try:
    bstack1l11lll1ll_opy_ = bstack1l1l111l_opy_(arg)
    if cli.is_enabled(CONFIG):
      cli.bstack1l1l11111l_opy_()
    if bstack11l1ll1_opy_ (u"ࠫࡧࡹࡴࡢࡥ࡮ࡣࡪࡸࡲࡰࡴࡢࡰ࡮ࡹࡴࠨ಑") in multiprocessing.current_process().__dict__.keys():
      for bstack11ll11lll1_opy_ in multiprocessing.current_process().bstack_error_list:
        bstack1l1l111l11_opy_.append(bstack11ll11lll1_opy_)
    try:
      bstack11ll1l111_opy_ = (bstack1l1l111l11_opy_, int(bstack1l11lll1ll_opy_))
      bstack1llll11ll1_opy_.append(bstack11ll1l111_opy_)
    except:
      bstack1llll11ll1_opy_.append((bstack1l1l111l11_opy_, bstack1l11lll1ll_opy_))
  except Exception as e:
    logger.error(traceback.format_exc())
    bstack1l1l111l11_opy_.append({bstack11l1ll1_opy_ (u"ࠬࡴࡡ࡮ࡧࠪಒ"): bstack11l1ll1_opy_ (u"࠭ࡐࡳࡱࡦࡩࡸࡹࠠࠨಓ") + os.environ.get(bstack11l1ll1_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡐࡍࡃࡗࡊࡔࡘࡍࡠࡋࡑࡈࡊ࡞ࠧಔ")), bstack11l1ll1_opy_ (u"ࠨࡧࡵࡶࡴࡸࠧಕ"): traceback.format_exc(), bstack11l1ll1_opy_ (u"ࠩ࡬ࡲࡩ࡫ࡸࠨಖ"): int(os.environ.get(bstack11l1ll1_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡓࡐࡆ࡚ࡆࡐࡔࡐࡣࡎࡔࡄࡆ࡚ࠪಗ")))})
    bstack1llll11ll1_opy_.append((bstack1l1l111l11_opy_, 1))
def bstack1lll1ll111_opy_(arg):
  global bstack11llllll1_opy_
  bstack1l1lll11_opy_(bstack1ll1l11lll_opy_)
  os.environ[bstack11l1ll1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡍࡘࡥࡁࡑࡒࡢࡅ࡚࡚ࡏࡎࡃࡗࡉࠬಘ")] = str(bstack11ll11ll1_opy_)
  from behave.__main__ import main as bstack111l11lll_opy_
  status_code = bstack111l11lll_opy_(arg)
  if status_code != 0:
    bstack11llllll1_opy_ = status_code
def bstack1l1l11l1l1_opy_():
  logger.info(bstack11l1l1ll1_opy_)
  import argparse
  parser = argparse.ArgumentParser()
  parser.add_argument(bstack11l1ll1_opy_ (u"ࠬࡹࡥࡵࡷࡳࠫಙ"), help=bstack11l1ll1_opy_ (u"࠭ࡇࡦࡰࡨࡶࡦࡺࡥࠡࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࠠࡤࡱࡱࡪ࡮࡭ࠧಚ"))
  parser.add_argument(bstack11l1ll1_opy_ (u"ࠧ࠮ࡷࠪಛ"), bstack11l1ll1_opy_ (u"ࠨ࠯࠰ࡹࡸ࡫ࡲ࡯ࡣࡰࡩࠬಜ"), help=bstack11l1ll1_opy_ (u"ࠩ࡜ࡳࡺࡸࠠࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࠦࡵࡴࡧࡵࡲࡦࡳࡥࠨಝ"))
  parser.add_argument(bstack11l1ll1_opy_ (u"ࠪ࠱ࡰ࠭ಞ"), bstack11l1ll1_opy_ (u"ࠫ࠲࠳࡫ࡦࡻࠪಟ"), help=bstack11l1ll1_opy_ (u"ࠬ࡟࡯ࡶࡴࠣࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࠢࡤࡧࡨ࡫ࡳࡴࠢ࡮ࡩࡾ࠭ಠ"))
  parser.add_argument(bstack11l1ll1_opy_ (u"࠭࠭ࡧࠩಡ"), bstack11l1ll1_opy_ (u"ࠧ࠮࠯ࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࠬಢ"), help=bstack11l1ll1_opy_ (u"ࠨ࡛ࡲࡹࡷࠦࡴࡦࡵࡷࠤ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱࠧಣ"))
  bstack11l1l1ll_opy_ = parser.parse_args()
  try:
    bstack111ll11l1_opy_ = bstack11l1ll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡩࡨࡲࡪࡸࡩࡤ࠰ࡼࡱࡱ࠴ࡳࡢ࡯ࡳࡰࡪ࠭ತ")
    if bstack11l1l1ll_opy_.framework and bstack11l1l1ll_opy_.framework not in (bstack11l1ll1_opy_ (u"ࠪࡴࡾࡺࡨࡰࡰࠪಥ"), bstack11l1ll1_opy_ (u"ࠫࡵࡿࡴࡩࡱࡱ࠷ࠬದ")):
      bstack111ll11l1_opy_ = bstack11l1ll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱ࠮ࡺ࡯࡯࠲ࡸࡧ࡭ࡱ࡮ࡨࠫಧ")
    bstack111l1llll_opy_ = os.path.join(os.path.dirname(os.path.realpath(__file__)), bstack111ll11l1_opy_)
    bstack1l11l1l11l_opy_ = open(bstack111l1llll_opy_, bstack11l1ll1_opy_ (u"࠭ࡲࠨನ"))
    bstack1l1l11lll_opy_ = bstack1l11l1l11l_opy_.read()
    bstack1l11l1l11l_opy_.close()
    if bstack11l1l1ll_opy_.username:
      bstack1l1l11lll_opy_ = bstack1l1l11lll_opy_.replace(bstack11l1ll1_opy_ (u"࡚ࠧࡑࡘࡖࡤ࡛ࡓࡆࡔࡑࡅࡒࡋࠧ಩"), bstack11l1l1ll_opy_.username)
    if bstack11l1l1ll_opy_.key:
      bstack1l1l11lll_opy_ = bstack1l1l11lll_opy_.replace(bstack11l1ll1_opy_ (u"ࠨ࡛ࡒ࡙ࡗࡥࡁࡄࡅࡈࡗࡘࡥࡋࡆ࡛ࠪಪ"), bstack11l1l1ll_opy_.key)
    if bstack11l1l1ll_opy_.framework:
      bstack1l1l11lll_opy_ = bstack1l1l11lll_opy_.replace(bstack11l1ll1_opy_ (u"ࠩ࡜ࡓ࡚ࡘ࡟ࡇࡔࡄࡑࡊ࡝ࡏࡓࡍࠪಫ"), bstack11l1l1ll_opy_.framework)
    file_name = bstack11l1ll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡼࡱࡱ࠭ಬ")
    file_path = os.path.abspath(file_name)
    bstack111ll1111_opy_ = open(file_path, bstack11l1ll1_opy_ (u"ࠫࡼ࠭ಭ"))
    bstack111ll1111_opy_.write(bstack1l1l11lll_opy_)
    bstack111ll1111_opy_.close()
    logger.info(bstack111111l1_opy_)
    try:
      os.environ[bstack11l1ll1_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡋࡘࡁࡎࡇ࡚ࡓࡗࡑࠧಮ")] = bstack11l1l1ll_opy_.framework if bstack11l1l1ll_opy_.framework != None else bstack11l1ll1_opy_ (u"ࠨࠢಯ")
      config = yaml.safe_load(bstack1l1l11lll_opy_)
      config[bstack11l1ll1_opy_ (u"ࠧࡴࡱࡸࡶࡨ࡫ࠧರ")] = bstack11l1ll1_opy_ (u"ࠨࡲࡼࡸ࡭ࡵ࡮࠮ࡵࡨࡸࡺࡶࠧಱ")
      bstack1l11l1l11_opy_(bstack111l11l1l_opy_, config)
    except Exception as e:
      logger.debug(bstack1ll1l1l11l_opy_.format(str(e)))
  except Exception as e:
    logger.error(bstack1l1l1lll1_opy_.format(str(e)))
def bstack1l11l1l11_opy_(bstack1l11l11l1_opy_, config, bstack11ll1l1ll1_opy_={}):
  global bstack1111l1111_opy_
  global bstack1lll1ll1l1_opy_
  global bstack1ll1l11l1_opy_
  if not config:
    return
  bstack1l1llll111_opy_ = bstack111ll111l_opy_ if not bstack1111l1111_opy_ else (
    bstack11ll11l1l_opy_ if bstack11l1ll1_opy_ (u"ࠩࡤࡴࡵ࠭ಲ") in config else (
        bstack11lll11ll_opy_ if config.get(bstack11l1ll1_opy_ (u"ࠪࡸࡺࡸࡢࡰࡕࡦࡥࡱ࡫ࠧಳ")) else bstack1ll11lll11_opy_
    )
)
  bstack11llll1l_opy_ = False
  bstack1ll111l11_opy_ = False
  if bstack1111l1111_opy_ is True:
      if bstack11l1ll1_opy_ (u"ࠫࡦࡶࡰࠨ಴") in config:
          bstack11llll1l_opy_ = True
      else:
          bstack1ll111l11_opy_ = True
  bstack1l11l1ll1_opy_ = bstack1l1l1lll11_opy_.bstack1ll11ll1ll_opy_(config, bstack1lll1ll1l1_opy_)
  bstack11ll111lll_opy_ = bstack111l1ll1l_opy_()
  data = {
    bstack11l1ll1_opy_ (u"ࠬࡻࡳࡦࡴࡑࡥࡲ࡫ࠧವ"): config[bstack11l1ll1_opy_ (u"࠭ࡵࡴࡧࡵࡒࡦࡳࡥࠨಶ")],
    bstack11l1ll1_opy_ (u"ࠧࡢࡥࡦࡩࡸࡹࡋࡦࡻࠪಷ"): config[bstack11l1ll1_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡌࡧࡼࠫಸ")],
    bstack11l1ll1_opy_ (u"ࠩࡨࡺࡪࡴࡴࡠࡶࡼࡴࡪ࠭ಹ"): bstack1l11l11l1_opy_,
    bstack11l1ll1_opy_ (u"ࠪࡨࡪࡺࡥࡤࡶࡨࡨࡋࡸࡡ࡮ࡧࡺࡳࡷࡱࠧ಺"): os.environ.get(bstack11l1ll1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡊࡗࡇࡍࡆ࡙ࡒࡖࡐ࠭಻"), bstack1lll1ll1l1_opy_),
    bstack11l1ll1_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡣ࡭ࡧࡳࡩࡧࡧࡣ࡮ࡪ಼ࠧ"): bstack1l111l1l11_opy_,
    bstack11l1ll1_opy_ (u"࠭࡯ࡱࡶ࡬ࡱࡦࡲ࡟ࡩࡷࡥࡣࡺࡸ࡬ࠨಽ"): bstack11111ll1l_opy_(),
    bstack11l1ll1_opy_ (u"ࠧࡦࡸࡨࡲࡹࡥࡰࡳࡱࡳࡩࡷࡺࡩࡦࡵࠪಾ"): {
      bstack11l1ll1_opy_ (u"ࠨ࡮ࡤࡲ࡬ࡻࡡࡨࡧࡢࡪࡷࡧ࡭ࡦࡹࡲࡶࡰ࠭ಿ"): str(config[bstack11l1ll1_opy_ (u"ࠩࡶࡳࡺࡸࡣࡦࠩೀ")]) if bstack11l1ll1_opy_ (u"ࠪࡷࡴࡻࡲࡤࡧࠪು") in config else bstack11l1ll1_opy_ (u"ࠦࡺࡴ࡫࡯ࡱࡺࡲࠧೂ"),
      bstack11l1ll1_opy_ (u"ࠬࡲࡡ࡯ࡩࡸࡥ࡬࡫ࡖࡦࡴࡶ࡭ࡴࡴࠧೃ"): sys.version,
      bstack11l1ll1_opy_ (u"࠭ࡲࡦࡨࡨࡶࡷ࡫ࡲࠨೄ"): bstack1111ll1ll_opy_(os.environ.get(bstack11l1ll1_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡆࡓࡃࡐࡉ࡜ࡕࡒࡌࠩ೅"), bstack1lll1ll1l1_opy_)),
      bstack11l1ll1_opy_ (u"ࠨ࡮ࡤࡲ࡬ࡻࡡࡨࡧࠪೆ"): bstack11l1ll1_opy_ (u"ࠩࡳࡽࡹ࡮࡯࡯ࠩೇ"),
      bstack11l1ll1_opy_ (u"ࠪࡴࡷࡵࡤࡶࡥࡷࠫೈ"): bstack1l1llll111_opy_,
      bstack11l1ll1_opy_ (u"ࠫࡵࡸ࡯ࡥࡷࡦࡸࡤࡳࡡࡱࠩ೉"): bstack1l11l1ll1_opy_,
      bstack11l1ll1_opy_ (u"ࠬࡺࡥࡴࡶ࡫ࡹࡧࡥࡵࡶ࡫ࡧࠫೊ"): os.environ[bstack11l1ll1_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡚ࡅࡔࡖࡋ࡙ࡇࡥࡕࡖࡋࡇࠫೋ")],
      bstack11l1ll1_opy_ (u"ࠧࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࠪೌ"): os.environ.get(bstack11l1ll1_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡇࡔࡄࡑࡊ࡝ࡏࡓࡍ್ࠪ"), bstack1lll1ll1l1_opy_),
      bstack11l1ll1_opy_ (u"ࠩࡩࡶࡦࡳࡥࡸࡱࡵ࡯࡛࡫ࡲࡴ࡫ࡲࡲࠬ೎"): bstack1ll1ll1lll_opy_(os.environ.get(bstack11l1ll1_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡉࡖࡆࡓࡅࡘࡑࡕࡏࠬ೏"), bstack1lll1ll1l1_opy_)),
      bstack11l1ll1_opy_ (u"ࠫࡦࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࡇࡴࡤࡱࡪࡽ࡯ࡳ࡭ࠪ೐"): bstack11ll111lll_opy_.get(bstack11l1ll1_opy_ (u"ࠬࡴࡡ࡮ࡧࠪ೑")),
      bstack11l1ll1_opy_ (u"࠭ࡡࡶࡶࡲࡱࡦࡺࡩࡰࡰࡉࡶࡦࡳࡥࡸࡱࡵ࡯࡛࡫ࡲࡴ࡫ࡲࡲࠬ೒"): bstack11ll111lll_opy_.get(bstack11l1ll1_opy_ (u"ࠧࡷࡧࡵࡷ࡮ࡵ࡮ࠨ೓")),
      bstack11l1ll1_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡎࡢ࡯ࡨࠫ೔"): config[bstack11l1ll1_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡏࡣࡰࡩࠬೕ")] if config[bstack11l1ll1_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡐࡤࡱࡪ࠭ೖ")] else bstack11l1ll1_opy_ (u"ࠦࡺࡴ࡫࡯ࡱࡺࡲࠧ೗"),
      bstack11l1ll1_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠧ೘"): str(config[bstack11l1ll1_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡎࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠨ೙")]) if bstack11l1ll1_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡏࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࠩ೚") in config else bstack11l1ll1_opy_ (u"ࠣࡷࡱ࡯ࡳࡵࡷ࡯ࠤ೛"),
      bstack11l1ll1_opy_ (u"ࠩࡲࡷࠬ೜"): sys.platform,
      bstack11l1ll1_opy_ (u"ࠪ࡬ࡴࡹࡴ࡯ࡣࡰࡩࠬೝ"): socket.gethostname(),
      bstack11l1ll1_opy_ (u"ࠫࡸࡪ࡫ࡓࡷࡱࡍࡩ࠭ೞ"): bstack1ll1l11l1_opy_.get_property(bstack11l1ll1_opy_ (u"ࠬࡹࡤ࡬ࡔࡸࡲࡎࡪࠧ೟"))
    }
  }
  if not bstack1ll1l11l1_opy_.get_property(bstack11l1ll1_opy_ (u"࠭ࡳࡥ࡭ࡎ࡭ࡱࡲࡓࡪࡩࡱࡥࡱ࠭ೠ")) is None:
    data[bstack11l1ll1_opy_ (u"ࠧࡦࡸࡨࡲࡹࡥࡰࡳࡱࡳࡩࡷࡺࡩࡦࡵࠪೡ")][bstack11l1ll1_opy_ (u"ࠨࡨ࡬ࡲ࡮ࡹࡨࡦࡦࡐࡩࡹࡧࡤࡢࡶࡤࠫೢ")] = {
      bstack11l1ll1_opy_ (u"ࠩࡵࡩࡦࡹ࡯࡯ࠩೣ"): bstack11l1ll1_opy_ (u"ࠪࡹࡸ࡫ࡲࡠ࡭࡬ࡰࡱ࡫ࡤࠨ೤"),
      bstack11l1ll1_opy_ (u"ࠫࡸ࡯ࡧ࡯ࡣ࡯ࠫ೥"): bstack1ll1l11l1_opy_.get_property(bstack11l1ll1_opy_ (u"ࠬࡹࡤ࡬ࡍ࡬ࡰࡱ࡙ࡩࡨࡰࡤࡰࠬ೦")),
      bstack11l1ll1_opy_ (u"࠭ࡳࡪࡩࡱࡥࡱࡔࡵ࡮ࡤࡨࡶࠬ೧"): bstack1ll1l11l1_opy_.get_property(bstack11l1ll1_opy_ (u"ࠧࡴࡦ࡮ࡏ࡮ࡲ࡬ࡏࡱࠪ೨"))
    }
  if bstack1l11l11l1_opy_ == bstack11lllll11_opy_:
    data[bstack11l1ll1_opy_ (u"ࠨࡧࡹࡩࡳࡺ࡟ࡱࡴࡲࡴࡪࡸࡴࡪࡧࡶࠫ೩")][bstack11l1ll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡖࡸࡦࡩ࡫ࡄࡱࡱࡪ࡮࡭ࠧ೪")] = bstack11l1ll11l_opy_(config)
    data[bstack11l1ll1_opy_ (u"ࠪࡩࡻ࡫࡮ࡵࡡࡳࡶࡴࡶࡥࡳࡶ࡬ࡩࡸ࠭೫")][bstack11l1ll1_opy_ (u"ࠫ࡮ࡹࡐࡦࡴࡦࡽࡆࡻࡴࡰࡇࡱࡥࡧࡲࡥࡥࠩ೬")] = percy.bstack11lllll1_opy_
    data[bstack11l1ll1_opy_ (u"ࠬ࡫ࡶࡦࡰࡷࡣࡵࡸ࡯ࡱࡧࡵࡸ࡮࡫ࡳࠨ೭")][bstack11l1ll1_opy_ (u"࠭ࡰࡦࡴࡦࡽࡇࡻࡩ࡭ࡦࡌࡨࠬ೮")] = percy.percy_build_id
  update(data[bstack11l1ll1_opy_ (u"ࠧࡦࡸࡨࡲࡹࡥࡰࡳࡱࡳࡩࡷࡺࡩࡦࡵࠪ೯")], bstack11ll1l1ll1_opy_)
  try:
    response = bstack1l1111l1l_opy_(bstack11l1ll1_opy_ (u"ࠨࡒࡒࡗ࡙࠭೰"), bstack1llll1ll11_opy_(bstack1lll1ll1l_opy_), data, {
      bstack11l1ll1_opy_ (u"ࠩࡤࡹࡹ࡮ࠧೱ"): (config[bstack11l1ll1_opy_ (u"ࠪࡹࡸ࡫ࡲࡏࡣࡰࡩࠬೲ")], config[bstack11l1ll1_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶࡏࡪࡿࠧೳ")])
    })
    if response:
      logger.debug(bstack1l11l1111l_opy_.format(bstack1l11l11l1_opy_, str(response.json())))
  except Exception as e:
    logger.debug(bstack1ll11111_opy_.format(str(e)))
def bstack1111ll1ll_opy_(framework):
  return bstack11l1ll1_opy_ (u"ࠧࢁࡽ࠮ࡲࡼࡸ࡭ࡵ࡮ࡢࡩࡨࡲࡹ࠵ࡻࡾࠤ೴").format(str(framework), __version__) if framework else bstack11l1ll1_opy_ (u"ࠨࡰࡺࡶ࡫ࡳࡳࡧࡧࡦࡰࡷ࠳ࢀࢃࠢ೵").format(
    __version__)
def bstack1l111llll_opy_():
  global CONFIG
  global bstack1111llll_opy_
  if bool(CONFIG):
    return
  try:
    bstack1l11ll1l1l_opy_()
    logger.debug(bstack1lll1ll1ll_opy_.format(str(CONFIG)))
    bstack1111llll_opy_ = bstack1ll1ll111_opy_.bstack11l1ll111_opy_(CONFIG, bstack1111llll_opy_)
    bstack1l11ll11l_opy_()
  except Exception as e:
    logger.error(bstack11l1ll1_opy_ (u"ࠢࡇࡣ࡬ࡰࡪࡪࠠࡵࡱࠣࡷࡪࡺࡵࡱ࠮ࠣࡩࡷࡸ࡯ࡳ࠼ࠣࠦ೶") + str(e))
    sys.exit(1)
  sys.excepthook = bstack11ll1l1111_opy_
  atexit.register(bstack1ll111ll11_opy_)
  signal.signal(signal.SIGINT, bstack1ll1l1ll1l_opy_)
  signal.signal(signal.SIGTERM, bstack1ll1l1ll1l_opy_)
def bstack11ll1l1111_opy_(exctype, value, traceback):
  global bstack1l1ll1l1l1_opy_
  try:
    for driver in bstack1l1ll1l1l1_opy_:
      bstack1ll1llllll_opy_(driver, bstack11l1ll1_opy_ (u"ࠨࡨࡤ࡭ࡱ࡫ࡤࠨ೷"), bstack11l1ll1_opy_ (u"ࠤࡖࡩࡸࡹࡩࡰࡰࠣࡪࡦ࡯࡬ࡦࡦࠣࡻ࡮ࡺࡨ࠻ࠢ࡟ࡲࠧ೸") + str(value))
  except Exception:
    pass
  logger.info(bstack1l111l11ll_opy_)
  bstack1lll1llll_opy_(value, True)
  sys.__excepthook__(exctype, value, traceback)
  sys.exit(1)
def bstack1lll1llll_opy_(message=bstack11l1ll1_opy_ (u"ࠪࠫ೹"), bstack11l1111ll_opy_ = False):
  global CONFIG
  bstack11llll11ll_opy_ = bstack11l1ll1_opy_ (u"ࠫ࡬ࡲ࡯ࡣࡣ࡯ࡉࡽࡩࡥࡱࡶ࡬ࡳࡳ࠭೺") if bstack11l1111ll_opy_ else bstack11l1ll1_opy_ (u"ࠬ࡫ࡲࡳࡱࡵࠫ೻")
  try:
    if message:
      bstack11ll1l1ll1_opy_ = {
        bstack11llll11ll_opy_ : str(message)
      }
      bstack1l11l1l11_opy_(bstack11lllll11_opy_, CONFIG, bstack11ll1l1ll1_opy_)
    else:
      bstack1l11l1l11_opy_(bstack11lllll11_opy_, CONFIG)
  except Exception as e:
    logger.debug(bstack1ll11l111l_opy_.format(str(e)))
def bstack1ll11ll11_opy_(bstack1l1llll1_opy_, size):
  bstack1lll1111_opy_ = []
  while len(bstack1l1llll1_opy_) > size:
    bstack1ll1l11111_opy_ = bstack1l1llll1_opy_[:size]
    bstack1lll1111_opy_.append(bstack1ll1l11111_opy_)
    bstack1l1llll1_opy_ = bstack1l1llll1_opy_[size:]
  bstack1lll1111_opy_.append(bstack1l1llll1_opy_)
  return bstack1lll1111_opy_
def bstack1ll111lll1_opy_(args):
  if bstack11l1ll1_opy_ (u"࠭࠭࡮ࠩ೼") in args and bstack11l1ll1_opy_ (u"ࠧࡱࡦࡥࠫ೽") in args:
    return True
  return False
@measure(event_name=EVENTS.bstack1l111l11l_opy_, stage=STAGE.bstack11111l1l_opy_)
def run_on_browserstack(bstack1l11l111_opy_=None, bstack1llll11ll1_opy_=None, bstack1l1l1ll1l1_opy_=False):
  global CONFIG
  global bstack1l1ll11ll1_opy_
  global bstack11ll11ll1_opy_
  global bstack1lll1ll1l1_opy_
  global bstack1ll1l11l1_opy_
  bstack111ll1l1_opy_ = bstack11l1ll1_opy_ (u"ࠨࠩ೾")
  bstack11lllll11l_opy_(bstack1llll1ll1l_opy_, logger)
  if bstack1l11l111_opy_ and isinstance(bstack1l11l111_opy_, str):
    bstack1l11l111_opy_ = eval(bstack1l11l111_opy_)
  if bstack1l11l111_opy_:
    CONFIG = bstack1l11l111_opy_[bstack11l1ll1_opy_ (u"ࠩࡆࡓࡓࡌࡉࡈࠩ೿")]
    bstack1l1ll11ll1_opy_ = bstack1l11l111_opy_[bstack11l1ll1_opy_ (u"ࠪࡌ࡚ࡈ࡟ࡖࡔࡏࠫഀ")]
    bstack11ll11ll1_opy_ = bstack1l11l111_opy_[bstack11l1ll1_opy_ (u"ࠫࡎ࡙࡟ࡂࡒࡓࡣࡆ࡛ࡔࡐࡏࡄࡘࡊ࠭ഁ")]
    bstack1ll1l11l1_opy_.bstack1l111llll1_opy_(bstack11l1ll1_opy_ (u"ࠬࡏࡓࡠࡃࡓࡔࡤࡇࡕࡕࡑࡐࡅ࡙ࡋࠧം"), bstack11ll11ll1_opy_)
    bstack111ll1l1_opy_ = bstack11l1ll1_opy_ (u"࠭ࡰࡺࡶ࡫ࡳࡳ࠭ഃ")
  bstack1ll1l11l1_opy_.bstack1l111llll1_opy_(bstack11l1ll1_opy_ (u"ࠧࡴࡦ࡮ࡖࡺࡴࡉࡥࠩഄ"), uuid4().__str__())
  logger.info(bstack11l1ll1_opy_ (u"ࠨࡕࡇࡏࠥࡸࡵ࡯ࠢࡶࡸࡦࡸࡴࡦࡦࠣࡻ࡮ࡺࡨࠡ࡫ࡧ࠾ࠥ࠭അ") + bstack1ll1l11l1_opy_.get_property(bstack11l1ll1_opy_ (u"ࠩࡶࡨࡰࡘࡵ࡯ࡋࡧࠫആ")));
  logger.debug(bstack11l1ll1_opy_ (u"ࠪࡷࡩࡱࡒࡶࡰࡌࡨࡂ࠭ഇ") + bstack1ll1l11l1_opy_.get_property(bstack11l1ll1_opy_ (u"ࠫࡸࡪ࡫ࡓࡷࡱࡍࡩ࠭ഈ")))
  if not bstack1l1l1ll1l1_opy_:
    if len(sys.argv) <= 1:
      logger.critical(bstack1llll11l11_opy_)
      return
    if sys.argv[1] == bstack11l1ll1_opy_ (u"ࠬ࠳࠭ࡷࡧࡵࡷ࡮ࡵ࡮ࠨഉ") or sys.argv[1] == bstack11l1ll1_opy_ (u"࠭࠭ࡷࠩഊ"):
      logger.info(bstack11l1ll1_opy_ (u"ࠧࡃࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࠦࡐࡺࡶ࡫ࡳࡳࠦࡓࡅࡍࠣࡺࢀࢃࠧഋ").format(__version__))
      return
    if sys.argv[1] == bstack11l1ll1_opy_ (u"ࠨࡵࡨࡸࡺࡶࠧഌ"):
      bstack1l1l11l1l1_opy_()
      return
  args = sys.argv
  bstack1l111llll_opy_()
  global bstack111lll1l1_opy_
  global bstack1lll1l1ll_opy_
  global bstack11ll1ll1l1_opy_
  global bstack1lll1l111_opy_
  global bstack1ll1ll1ll_opy_
  global bstack1ll1lll1ll_opy_
  global bstack11ll11ll_opy_
  global bstack11l11111_opy_
  global bstack1l11ll111l_opy_
  global bstack1111l1l1l_opy_
  global bstack1ll111l1ll_opy_
  bstack1lll1l1ll_opy_ = len(CONFIG.get(bstack11l1ll1_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬ഍"), []))
  if not bstack111ll1l1_opy_:
    if args[1] == bstack11l1ll1_opy_ (u"ࠪࡴࡾࡺࡨࡰࡰࠪഎ") or args[1] == bstack11l1ll1_opy_ (u"ࠫࡵࡿࡴࡩࡱࡱ࠷ࠬഏ"):
      bstack111ll1l1_opy_ = bstack11l1ll1_opy_ (u"ࠬࡶࡹࡵࡪࡲࡲࠬഐ")
      args = args[2:]
    elif args[1] == bstack11l1ll1_opy_ (u"࠭ࡲࡰࡤࡲࡸࠬ഑"):
      bstack111ll1l1_opy_ = bstack11l1ll1_opy_ (u"ࠧࡳࡱࡥࡳࡹ࠭ഒ")
      args = args[2:]
    elif args[1] == bstack11l1ll1_opy_ (u"ࠨࡲࡤࡦࡴࡺࠧഓ"):
      bstack111ll1l1_opy_ = bstack11l1ll1_opy_ (u"ࠩࡳࡥࡧࡵࡴࠨഔ")
      args = args[2:]
    elif args[1] == bstack11l1ll1_opy_ (u"ࠪࡶࡴࡨ࡯ࡵ࠯࡬ࡲࡹ࡫ࡲ࡯ࡣ࡯ࠫക"):
      bstack111ll1l1_opy_ = bstack11l1ll1_opy_ (u"ࠫࡷࡵࡢࡰࡶ࠰࡭ࡳࡺࡥࡳࡰࡤࡰࠬഖ")
      args = args[2:]
    elif args[1] == bstack11l1ll1_opy_ (u"ࠬࡶࡹࡵࡧࡶࡸࠬഗ"):
      bstack111ll1l1_opy_ = bstack11l1ll1_opy_ (u"࠭ࡰࡺࡶࡨࡷࡹ࠭ഘ")
      args = args[2:]
    elif args[1] == bstack11l1ll1_opy_ (u"ࠧࡣࡧ࡫ࡥࡻ࡫ࠧങ"):
      bstack111ll1l1_opy_ = bstack11l1ll1_opy_ (u"ࠨࡤࡨ࡬ࡦࡼࡥࠨച")
      args = args[2:]
    else:
      if not bstack11l1ll1_opy_ (u"ࠩࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࠬഛ") in CONFIG or str(CONFIG[bstack11l1ll1_opy_ (u"ࠪࡪࡷࡧ࡭ࡦࡹࡲࡶࡰ࠭ജ")]).lower() in [bstack11l1ll1_opy_ (u"ࠫࡵࡿࡴࡩࡱࡱࠫഝ"), bstack11l1ll1_opy_ (u"ࠬࡶࡹࡵࡪࡲࡲ࠸࠭ഞ")]:
        bstack111ll1l1_opy_ = bstack11l1ll1_opy_ (u"࠭ࡰࡺࡶ࡫ࡳࡳ࠭ട")
        args = args[1:]
      elif str(CONFIG[bstack11l1ll1_opy_ (u"ࠧࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࠪഠ")]).lower() == bstack11l1ll1_opy_ (u"ࠨࡴࡲࡦࡴࡺࠧഡ"):
        bstack111ll1l1_opy_ = bstack11l1ll1_opy_ (u"ࠩࡵࡳࡧࡵࡴࠨഢ")
        args = args[1:]
      elif str(CONFIG[bstack11l1ll1_opy_ (u"ࠪࡪࡷࡧ࡭ࡦࡹࡲࡶࡰ࠭ണ")]).lower() == bstack11l1ll1_opy_ (u"ࠫࡵࡧࡢࡰࡶࠪത"):
        bstack111ll1l1_opy_ = bstack11l1ll1_opy_ (u"ࠬࡶࡡࡣࡱࡷࠫഥ")
        args = args[1:]
      elif str(CONFIG[bstack11l1ll1_opy_ (u"࠭ࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࠩദ")]).lower() == bstack11l1ll1_opy_ (u"ࠧࡱࡻࡷࡩࡸࡺࠧധ"):
        bstack111ll1l1_opy_ = bstack11l1ll1_opy_ (u"ࠨࡲࡼࡸࡪࡹࡴࠨന")
        args = args[1:]
      elif str(CONFIG[bstack11l1ll1_opy_ (u"ࠩࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࠬഩ")]).lower() == bstack11l1ll1_opy_ (u"ࠪࡦࡪ࡮ࡡࡷࡧࠪപ"):
        bstack111ll1l1_opy_ = bstack11l1ll1_opy_ (u"ࠫࡧ࡫ࡨࡢࡸࡨࠫഫ")
        args = args[1:]
      else:
        os.environ[bstack11l1ll1_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡋࡘࡁࡎࡇ࡚ࡓࡗࡑࠧബ")] = bstack111ll1l1_opy_
        bstack1l11l1lll_opy_(bstack1ll11111l1_opy_)
  os.environ[bstack11l1ll1_opy_ (u"࠭ࡆࡓࡃࡐࡉ࡜ࡕࡒࡌࡡࡘࡗࡊࡊࠧഭ")] = bstack111ll1l1_opy_
  bstack1lll1ll1l1_opy_ = bstack111ll1l1_opy_
  if cli.is_enabled(CONFIG):
    try:
      bstack1l1111l1l1_opy_ = bstack11ll1111_opy_[bstack11l1ll1_opy_ (u"ࠧࡑ࡛ࡗࡉࡘ࡚࠭ࡃࡆࡇࠫമ")] if bstack111ll1l1_opy_ == bstack11l1ll1_opy_ (u"ࠨࡲࡼࡸࡪࡹࡴࠨയ") and bstack1l11ll1l1_opy_() else bstack111ll1l1_opy_
      bstack1l1l11lll1_opy_.invoke(bstack1ll1ll1l11_opy_.bstack1llllll1l_opy_, bstack1111l1ll1_opy_(
        sdk_version=__version__,
        path_config=bstack1l11ll11ll_opy_(),
        path_project=os.getcwd(),
        test_framework=bstack1l1111l1l1_opy_,
        frameworks=[bstack1l1111l1l1_opy_],
        framework_versions={
          bstack1l1111l1l1_opy_: bstack1ll1ll1lll_opy_(bstack11l1ll1_opy_ (u"ࠩࡕࡳࡧࡵࡴࠨര") if bstack111ll1l1_opy_ in [bstack11l1ll1_opy_ (u"ࠪࡴࡦࡨ࡯ࡵࠩറ"), bstack11l1ll1_opy_ (u"ࠫࡷࡵࡢࡰࡶࠪല"), bstack11l1ll1_opy_ (u"ࠬࡸ࡯ࡣࡱࡷ࠱࡮ࡴࡴࡦࡴࡱࡥࡱ࠭ള")] else bstack111ll1l1_opy_)
        },
        bs_config=CONFIG
      ))
      if cli.config.get(bstack11l1ll1_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡎࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠣഴ"), None):
        CONFIG[bstack11l1ll1_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡏࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࠤവ")] = cli.config.get(bstack11l1ll1_opy_ (u"ࠣࡤࡸ࡭ࡱࡪࡉࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࠥശ"), None)
    except Exception as e:
      bstack1l1l11lll1_opy_.invoke(bstack1ll1ll1l11_opy_.bstack1ll1ll11ll_opy_, e.__traceback__, 1)
    if bstack11ll11ll1_opy_:
      CONFIG[bstack11l1ll1_opy_ (u"ࠤࡤࡴࡵࠨഷ")] = cli.config[bstack11l1ll1_opy_ (u"ࠥࡥࡵࡶࠢസ")]
      logger.info(bstack11l1l1lll1_opy_.format(CONFIG[bstack11l1ll1_opy_ (u"ࠫࡦࡶࡰࠨഹ")]))
  else:
    bstack1l1l11lll1_opy_.clear()
  global bstack1lllll1ll1_opy_
  global bstack1l1ll1l1_opy_
  if bstack1l11l111_opy_:
    try:
      bstack1l1l1ll111_opy_ = datetime.datetime.now()
      os.environ[bstack11l1ll1_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡋࡘࡁࡎࡇ࡚ࡓࡗࡑࠧഺ")] = bstack111ll1l1_opy_
      bstack1l11l1l11_opy_(bstack1l111l1l1_opy_, CONFIG)
      cli.bstack111l11l1_opy_(bstack11l1ll1_opy_ (u"ࠨࡨࡵࡶࡳ࠾ࡸࡪ࡫ࡠࡶࡨࡷࡹࡥࡡࡵࡶࡨࡱࡵࡺࡥࡥࠤ഻"), datetime.datetime.now() - bstack1l1l1ll111_opy_)
    except Exception as e:
      logger.debug(bstack111llll11_opy_.format(str(e)))
  global bstack11lll111ll_opy_
  global bstack1llll11l_opy_
  global bstack1l11ll11_opy_
  global bstack11l11l1l1_opy_
  global bstack1ll11ll1l_opy_
  global bstack11ll11lll_opy_
  global bstack1lllll1l11_opy_
  global bstack11ll111l1l_opy_
  global bstack1l1l1l1111_opy_
  global bstack111lllll_opy_
  global bstack111ll1lll_opy_
  global bstack1l1llll1ll_opy_
  global bstack1l1ll11l1_opy_
  global bstack11l1lll11_opy_
  global bstack1lllll11ll_opy_
  global bstack1llll111ll_opy_
  global bstack11l1lllll1_opy_
  global bstack1l1l111l1_opy_
  global bstack111111l11_opy_
  global bstack1lll1lll11_opy_
  global bstack11l111l1_opy_
  try:
    from selenium import webdriver
    from selenium.webdriver.remote.webdriver import WebDriver
    bstack11lll111ll_opy_ = webdriver.Remote.__init__
    bstack1llll11l_opy_ = WebDriver.quit
    bstack1l1llll1ll_opy_ = WebDriver.close
    bstack1lllll11ll_opy_ = WebDriver.get
    bstack11l111l1_opy_ = WebDriver.execute
  except Exception as e:
    pass
  try:
    import Browser
    from subprocess import Popen
    bstack1lllll1ll1_opy_ = Popen.__init__
  except Exception as e:
    pass
  try:
    from bstack_utils.helper import bstack1l1ll1l1l_opy_
    bstack1l1ll1l1_opy_ = bstack1l1ll1l1l_opy_()
  except Exception as e:
    pass
  try:
    global bstack1llllllll_opy_
    from QWeb.keywords import browser
    bstack1llllllll_opy_ = browser.close_browser
  except Exception as e:
    pass
  if bstack1lll11lll1_opy_(CONFIG) and bstack11l11lll_opy_():
    if bstack1ll111111l_opy_() < version.parse(bstack11llll11_opy_):
      logger.error(bstack11l1l111l_opy_.format(bstack1ll111111l_opy_()))
    else:
      try:
        from selenium.webdriver.remote.remote_connection import RemoteConnection
        bstack1llll111ll_opy_ = RemoteConnection._11ll1lll_opy_
      except Exception as e:
        logger.error(bstack11ll1l11l1_opy_.format(str(e)))
  if not CONFIG.get(bstack11l1ll1_opy_ (u"ࠧࡥ࡫ࡶࡥࡧࡲࡥࡂࡷࡷࡳࡈࡧࡰࡵࡷࡵࡩࡑࡵࡧࡴ഼ࠩ"), False) and not bstack1l11l111_opy_:
    logger.info(bstack11llllll1l_opy_)
  if not cli.is_enabled(CONFIG):
    if bstack11l1ll1_opy_ (u"ࠨࡶࡸࡶࡧࡵࡓࡤࡣ࡯ࡩࠬഽ") in CONFIG and str(CONFIG[bstack11l1ll1_opy_ (u"ࠩࡷࡹࡷࡨ࡯ࡔࡥࡤࡰࡪ࠭ാ")]).lower() != bstack11l1ll1_opy_ (u"ࠪࡪࡦࡲࡳࡦࠩി"):
      bstack1lll1111l_opy_()
    elif bstack111ll1l1_opy_ != bstack11l1ll1_opy_ (u"ࠫࡵࡿࡴࡩࡱࡱࠫീ") or (bstack111ll1l1_opy_ == bstack11l1ll1_opy_ (u"ࠬࡶࡹࡵࡪࡲࡲࠬു") and not bstack1l11l111_opy_):
      bstack111l1l1ll_opy_()
  if (bstack111ll1l1_opy_ in [bstack11l1ll1_opy_ (u"࠭ࡰࡢࡤࡲࡸࠬൂ"), bstack11l1ll1_opy_ (u"ࠧࡳࡱࡥࡳࡹ࠭ൃ"), bstack11l1ll1_opy_ (u"ࠨࡴࡲࡦࡴࡺ࠭ࡪࡰࡷࡩࡷࡴࡡ࡭ࠩൄ")]):
    try:
      from robot import run_cli
      from robot.output import Output
      from robot.running.status import TestStatus
      from pabot.pabot import QueueItem
      from pabot import pabot
      try:
        from SeleniumLibrary.keywords.webdrivertools.webdrivertools import WebDriverCreator
        from SeleniumLibrary.keywords.webdrivertools.webdrivertools import WebDriverCache
        WebDriverCreator._get_ff_profile = bstack1ll1llll1l_opy_
        bstack11ll11lll_opy_ = WebDriverCache.close
      except Exception as e:
        logger.warn(bstack11ll1lll1l_opy_ + str(e))
      try:
        from AppiumLibrary.utils.applicationcache import ApplicationCache
        bstack1ll11ll1l_opy_ = ApplicationCache.close
      except Exception as e:
        logger.debug(bstack11lll1l1l_opy_ + str(e))
    except Exception as e:
      bstack1ll11lll1_opy_(e, bstack11ll1lll1l_opy_)
    if bstack111ll1l1_opy_ != bstack11l1ll1_opy_ (u"ࠩࡵࡳࡧࡵࡴ࠮࡫ࡱࡸࡪࡸ࡮ࡢ࡮ࠪ൅"):
      bstack1l11l1l1ll_opy_()
    bstack1l11ll11_opy_ = Output.start_test
    bstack11l11l1l1_opy_ = Output.end_test
    bstack1lllll1l11_opy_ = TestStatus.__init__
    bstack1l1l1l1111_opy_ = pabot._run
    bstack111lllll_opy_ = QueueItem.__init__
    bstack111ll1lll_opy_ = pabot._create_command_for_execution
    bstack111111l11_opy_ = pabot._report_results
  if bstack111ll1l1_opy_ == bstack11l1ll1_opy_ (u"ࠪࡦࡪ࡮ࡡࡷࡧࠪെ"):
    try:
      from behave.runner import Runner
      from behave.model import Step
    except Exception as e:
      bstack1ll11lll1_opy_(e, bstack1l11lll1l_opy_)
    bstack1l1ll11l1_opy_ = Runner.run_hook
    bstack11l1lll11_opy_ = Step.run
  if bstack111ll1l1_opy_ == bstack11l1ll1_opy_ (u"ࠫࡵࡿࡴࡦࡵࡷࠫേ"):
    try:
      from _pytest.config import Config
      bstack11l1lllll1_opy_ = Config.getoption
      from _pytest import runner
      bstack1l1l111l1_opy_ = runner._update_current_test_var
    except Exception as e:
      logger.warn(e, bstack1ll1l1l111_opy_)
    try:
      from pytest_bdd import reporting
      bstack1lll1lll11_opy_ = reporting.runtest_makereport
    except Exception as e:
      logger.debug(bstack11l1ll1_opy_ (u"ࠬࡖ࡬ࡦࡣࡶࡩࠥ࡯࡮ࡴࡶࡤࡰࡱࠦࡰࡺࡶࡨࡷࡹ࠳ࡢࡥࡦࠣࡸࡴࠦࡲࡶࡰࠣࡴࡾࡺࡥࡴࡶ࠰ࡦࡩࡪࠠࡵࡧࡶࡸࡸ࠭ൈ"))
  try:
    framework_name = bstack11l1ll1_opy_ (u"࠭ࡲࡰࡤࡲࡸࠬ൉") if bstack111ll1l1_opy_ in [bstack11l1ll1_opy_ (u"ࠧࡱࡣࡥࡳࡹ࠭ൊ"), bstack11l1ll1_opy_ (u"ࠨࡴࡲࡦࡴࡺࠧോ"), bstack11l1ll1_opy_ (u"ࠩࡵࡳࡧࡵࡴ࠮࡫ࡱࡸࡪࡸ࡮ࡢ࡮ࠪൌ")] else bstack1l1l1ll11l_opy_(bstack111ll1l1_opy_)
    bstack1lll11ll1_opy_ = {
      bstack11l1ll1_opy_ (u"ࠪࡪࡷࡧ࡭ࡦࡹࡲࡶࡰࡥ࡮ࡢ࡯ࡨ്ࠫ"): bstack11l1ll1_opy_ (u"ࠫࡕࡿࡴࡦࡵࡷ࠱ࡨࡻࡣࡶ࡯ࡥࡩࡷ࠭ൎ") if bstack111ll1l1_opy_ == bstack11l1ll1_opy_ (u"ࠬࡶࡹࡵࡧࡶࡸࠬ൏") and bstack1l11ll1l1_opy_() else framework_name,
      bstack11l1ll1_opy_ (u"࠭ࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡡࡹࡩࡷࡹࡩࡰࡰࠪ൐"): bstack1ll1ll1lll_opy_(framework_name),
      bstack11l1ll1_opy_ (u"ࠧࡴࡦ࡮ࡣࡻ࡫ࡲࡴ࡫ࡲࡲࠬ൑"): __version__,
      bstack11l1ll1_opy_ (u"ࠨࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࡣࡺࡹࡥࡥࠩ൒"): bstack111ll1l1_opy_
    }
    if bstack111ll1l1_opy_ in bstack1l1l1l1l_opy_:
      if bstack1111l1111_opy_ and bstack11l1ll1_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠩ൓") in CONFIG and CONFIG[bstack11l1ll1_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠪൔ")] == True:
        if bstack11l1ll1_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࡓࡵࡺࡩࡰࡰࡶࠫൕ") in CONFIG:
          os.environ[bstack11l1ll1_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣ࡙ࡋࡓࡕࡡࡄࡇࡈࡋࡓࡔࡋࡅࡍࡑࡏࡔ࡚ࡡࡆࡓࡓࡌࡉࡈࡗࡕࡅ࡙ࡏࡏࡏࡡ࡜ࡑࡑ࠭ൖ")] = os.getenv(bstack11l1ll1_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡚ࡅࡔࡖࡢࡅࡈࡉࡅࡔࡕࡌࡆࡎࡒࡉࡕ࡛ࡢࡇࡔࡔࡆࡊࡉࡘࡖࡆ࡚ࡉࡐࡐࡢ࡝ࡒࡒࠧൗ"), json.dumps(CONFIG[bstack11l1ll1_opy_ (u"ࠧࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࡏࡱࡶ࡬ࡳࡳࡹࠧ൘")]))
          CONFIG[bstack11l1ll1_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࡐࡲࡷ࡭ࡴࡴࡳࠨ൙")].pop(bstack11l1ll1_opy_ (u"ࠩ࡬ࡲࡨࡲࡵࡥࡧࡗࡥ࡬ࡹࡉ࡯ࡖࡨࡷࡹ࡯࡮ࡨࡕࡦࡳࡵ࡫ࠧ൚"), None)
          CONFIG[bstack11l1ll1_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࡒࡴࡹ࡯࡯࡯ࡵࠪ൛")].pop(bstack11l1ll1_opy_ (u"ࠫࡪࡾࡣ࡭ࡷࡧࡩ࡙ࡧࡧࡴࡋࡱࡘࡪࡹࡴࡪࡰࡪࡗࡨࡵࡰࡦࠩ൜"), None)
        bstack1lll11ll1_opy_[bstack11l1ll1_opy_ (u"ࠬࡺࡥࡴࡶࡉࡶࡦࡳࡥࡸࡱࡵ࡯ࠬ൝")] = {
          bstack11l1ll1_opy_ (u"࠭࡮ࡢ࡯ࡨࠫ൞"): bstack11l1ll1_opy_ (u"ࠧࡴࡧ࡯ࡩࡳ࡯ࡵ࡮ࠩൟ"),
          bstack11l1ll1_opy_ (u"ࠨࡸࡨࡶࡸ࡯࡯࡯ࠩൠ"): str(bstack1ll111111l_opy_())
        }
    if bstack111ll1l1_opy_ not in [bstack11l1ll1_opy_ (u"ࠩࡵࡳࡧࡵࡴ࠮࡫ࡱࡸࡪࡸ࡮ࡢ࡮ࠪൡ")] and not cli.is_running():
      bstack11ll1l11l_opy_ = bstack11111l1l1_opy_.launch(CONFIG, bstack1lll11ll1_opy_)
  except Exception as e:
    logger.debug(bstack1l11l111ll_opy_.format(bstack11l1ll1_opy_ (u"ࠪࡘࡪࡹࡴࡉࡷࡥࠫൢ"), str(e)))
  if bstack111ll1l1_opy_ == bstack11l1ll1_opy_ (u"ࠫࡵࡿࡴࡩࡱࡱࠫൣ"):
    bstack11ll1ll1l1_opy_ = True
    if bstack1l11l111_opy_ and bstack1l1l1ll1l1_opy_:
      bstack1ll1lll1ll_opy_ = CONFIG.get(bstack11l1ll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷ࡙ࡴࡢࡥ࡮ࡐࡴࡩࡡ࡭ࡑࡳࡸ࡮ࡵ࡮ࡴࠩ൤"), {}).get(bstack11l1ll1_opy_ (u"࠭࡬ࡰࡥࡤࡰࡎࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠨ൥"))
      bstack1l1lll11_opy_(bstack111ll11l_opy_)
    elif bstack1l11l111_opy_:
      bstack1ll1lll1ll_opy_ = CONFIG.get(bstack11l1ll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡔࡶࡤࡧࡰࡒ࡯ࡤࡣ࡯ࡓࡵࡺࡩࡰࡰࡶࠫ൦"), {}).get(bstack11l1ll1_opy_ (u"ࠨ࡮ࡲࡧࡦࡲࡉࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࠪ൧"))
      global bstack1l1ll1l1l1_opy_
      try:
        if bstack1ll111lll1_opy_(bstack1l11l111_opy_[bstack11l1ll1_opy_ (u"ࠩࡩ࡭ࡱ࡫࡟࡯ࡣࡰࡩࠬ൨")]) and multiprocessing.current_process().name == bstack11l1ll1_opy_ (u"ࠪ࠴ࠬ൩"):
          bstack1l11l111_opy_[bstack11l1ll1_opy_ (u"ࠫ࡫࡯࡬ࡦࡡࡱࡥࡲ࡫ࠧ൪")].remove(bstack11l1ll1_opy_ (u"ࠬ࠳࡭ࠨ൫"))
          bstack1l11l111_opy_[bstack11l1ll1_opy_ (u"࠭ࡦࡪ࡮ࡨࡣࡳࡧ࡭ࡦࠩ൬")].remove(bstack11l1ll1_opy_ (u"ࠧࡱࡦࡥࠫ൭"))
          bstack1l11l111_opy_[bstack11l1ll1_opy_ (u"ࠨࡨ࡬ࡰࡪࡥ࡮ࡢ࡯ࡨࠫ൮")] = bstack1l11l111_opy_[bstack11l1ll1_opy_ (u"ࠩࡩ࡭ࡱ࡫࡟࡯ࡣࡰࡩࠬ൯")][0]
          with open(bstack1l11l111_opy_[bstack11l1ll1_opy_ (u"ࠪࡪ࡮ࡲࡥࡠࡰࡤࡱࡪ࠭൰")], bstack11l1ll1_opy_ (u"ࠫࡷ࠭൱")) as f:
            bstack1l1l1111l1_opy_ = f.read()
          bstack1l1l11111_opy_ = bstack11l1ll1_opy_ (u"ࠧࠨࠢࡧࡴࡲࡱࠥࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡣࡸࡪ࡫ࠡ࡫ࡰࡴࡴࡸࡴࠡࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࡟ࡪࡰ࡬ࡸ࡮ࡧ࡬ࡪࡼࡨ࠿ࠥࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡣ࡮ࡴࡩࡵ࡫ࡤࡰ࡮ࢀࡥࠩࡽࢀ࠭ࡀࠦࡦࡳࡱࡰࠤࡵࡪࡢࠡ࡫ࡰࡴࡴࡸࡴࠡࡒࡧࡦࡀࠦ࡯ࡨࡡࡧࡦࠥࡃࠠࡑࡦࡥ࠲ࡩࡵ࡟ࡣࡴࡨࡥࡰࡁࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࡨࡪ࡬ࠠ࡮ࡱࡧࡣࡧࡸࡥࡢ࡭ࠫࡷࡪࡲࡦ࠭ࠢࡤࡶ࡬࠲ࠠࡵࡧࡰࡴࡴࡸࡡࡳࡻࠣࡁࠥ࠶ࠩ࠻ࠌࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࡵࡴࡼ࠾ࠏࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࡧࡲࡨࠢࡀࠤࡸࡺࡲࠩ࡫ࡱࡸ࠭ࡧࡲࡨࠫ࠮࠵࠵࠯ࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥ࡫ࡸࡤࡧࡳࡸࠥࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡࡣࡶࠤࡪࡀࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࡱࡣࡶࡷࠏࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࡳ࡬ࡥࡤࡣࠪࡶࡩࡱ࡬ࠬࡢࡴࡪ࠰ࡹ࡫࡭ࡱࡱࡵࡥࡷࡿࠩࠋࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࡕࡪࡢ࠯ࡦࡲࡣࡧࠦ࠽ࠡ࡯ࡲࡨࡤࡨࡲࡦࡣ࡮ࠎࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࡑࡦࡥ࠲ࡩࡵ࡟ࡣࡴࡨࡥࡰࠦ࠽ࠡ࡯ࡲࡨࡤࡨࡲࡦࡣ࡮ࠎࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࡑࡦࡥࠬ࠮࠴ࡳࡦࡶࡢࡸࡷࡧࡣࡦࠪࠬࡠࡳࠨࠢࠣ൲").format(str(bstack1l11l111_opy_))
          bstack1l11l1l1l1_opy_ = bstack1l1l11111_opy_ + bstack1l1l1111l1_opy_
          bstack11l1l111_opy_ = bstack1l11l111_opy_[bstack11l1ll1_opy_ (u"࠭ࡦࡪ࡮ࡨࡣࡳࡧ࡭ࡦࠩ൳")] + bstack11l1ll1_opy_ (u"ࠧࡠࡤࡶࡸࡦࡩ࡫ࡠࡶࡨࡱࡵ࠴ࡰࡺࠩ൴")
          with open(bstack11l1l111_opy_, bstack11l1ll1_opy_ (u"ࠨࡹࠪ൵")):
            pass
          with open(bstack11l1l111_opy_, bstack11l1ll1_opy_ (u"ࠤࡺ࠯ࠧ൶")) as f:
            f.write(bstack1l11l1l1l1_opy_)
          import subprocess
          bstack11llll1l1_opy_ = subprocess.run([bstack11l1ll1_opy_ (u"ࠥࡴࡾࡺࡨࡰࡰࠥ൷"), bstack11l1l111_opy_])
          if os.path.exists(bstack11l1l111_opy_):
            os.unlink(bstack11l1l111_opy_)
          os._exit(bstack11llll1l1_opy_.returncode)
        else:
          if bstack1ll111lll1_opy_(bstack1l11l111_opy_[bstack11l1ll1_opy_ (u"ࠫ࡫࡯࡬ࡦࡡࡱࡥࡲ࡫ࠧ൸")]):
            bstack1l11l111_opy_[bstack11l1ll1_opy_ (u"ࠬ࡬ࡩ࡭ࡧࡢࡲࡦࡳࡥࠨ൹")].remove(bstack11l1ll1_opy_ (u"࠭࠭࡮ࠩൺ"))
            bstack1l11l111_opy_[bstack11l1ll1_opy_ (u"ࠧࡧ࡫࡯ࡩࡤࡴࡡ࡮ࡧࠪൻ")].remove(bstack11l1ll1_opy_ (u"ࠨࡲࡧࡦࠬർ"))
            bstack1l11l111_opy_[bstack11l1ll1_opy_ (u"ࠩࡩ࡭ࡱ࡫࡟࡯ࡣࡰࡩࠬൽ")] = bstack1l11l111_opy_[bstack11l1ll1_opy_ (u"ࠪࡪ࡮ࡲࡥࡠࡰࡤࡱࡪ࠭ൾ")][0]
          bstack1l1lll11_opy_(bstack111ll11l_opy_)
          sys.path.append(os.path.dirname(os.path.abspath(bstack1l11l111_opy_[bstack11l1ll1_opy_ (u"ࠫ࡫࡯࡬ࡦࡡࡱࡥࡲ࡫ࠧൿ")])))
          sys.argv = sys.argv[2:]
          mod_globals = globals()
          mod_globals[bstack11l1ll1_opy_ (u"ࠬࡥ࡟࡯ࡣࡰࡩࡤࡥࠧ඀")] = bstack11l1ll1_opy_ (u"࠭࡟ࡠ࡯ࡤ࡭ࡳࡥ࡟ࠨඁ")
          mod_globals[bstack11l1ll1_opy_ (u"ࠧࡠࡡࡩ࡭ࡱ࡫࡟ࡠࠩං")] = os.path.abspath(bstack1l11l111_opy_[bstack11l1ll1_opy_ (u"ࠨࡨ࡬ࡰࡪࡥ࡮ࡢ࡯ࡨࠫඃ")])
          exec(open(bstack1l11l111_opy_[bstack11l1ll1_opy_ (u"ࠩࡩ࡭ࡱ࡫࡟࡯ࡣࡰࡩࠬ඄")]).read(), mod_globals)
      except BaseException as e:
        try:
          traceback.print_exc()
          logger.error(bstack11l1ll1_opy_ (u"ࠪࡇࡦࡻࡧࡩࡶࠣࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࡀࠠࡼࡿࠪඅ").format(str(e)))
          for driver in bstack1l1ll1l1l1_opy_:
            bstack1llll11ll1_opy_.append({
              bstack11l1ll1_opy_ (u"ࠫࡳࡧ࡭ࡦࠩආ"): bstack1l11l111_opy_[bstack11l1ll1_opy_ (u"ࠬ࡬ࡩ࡭ࡧࡢࡲࡦࡳࡥࠨඇ")],
              bstack11l1ll1_opy_ (u"࠭ࡥࡳࡴࡲࡶࠬඈ"): str(e),
              bstack11l1ll1_opy_ (u"ࠧࡪࡰࡧࡩࡽ࠭ඉ"): multiprocessing.current_process().name
            })
            bstack1ll1llllll_opy_(driver, bstack11l1ll1_opy_ (u"ࠨࡨࡤ࡭ࡱ࡫ࡤࠨඊ"), bstack11l1ll1_opy_ (u"ࠤࡖࡩࡸࡹࡩࡰࡰࠣࡪࡦ࡯࡬ࡦࡦࠣࡻ࡮ࡺࡨ࠻ࠢ࡟ࡲࠧඋ") + str(e))
        except Exception:
          pass
      finally:
        try:
          for driver in bstack1l1ll1l1l1_opy_:
            driver.quit()
        except Exception as e:
          pass
    else:
      percy.init(bstack11ll11ll1_opy_, CONFIG, logger)
      bstack1ll1l1ll1_opy_()
      bstack1l1111l111_opy_()
      bstack1l1lll11l1_opy_ = {
        bstack11l1ll1_opy_ (u"ࠪࡪ࡮ࡲࡥࡠࡰࡤࡱࡪ࠭ඌ"): args[0],
        bstack11l1ll1_opy_ (u"ࠫࡈࡕࡎࡇࡋࡊࠫඍ"): CONFIG,
        bstack11l1ll1_opy_ (u"ࠬࡎࡕࡃࡡࡘࡖࡑ࠭ඎ"): bstack1l1ll11ll1_opy_,
        bstack11l1ll1_opy_ (u"࠭ࡉࡔࡡࡄࡔࡕࡥࡁࡖࡖࡒࡑࡆ࡚ࡅࠨඏ"): bstack11ll11ll1_opy_
      }
      percy.bstack1ll1111l_opy_()
      if bstack11l1ll1_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵࠪඐ") in CONFIG:
        bstack1l1l111ll1_opy_ = []
        manager = multiprocessing.Manager()
        bstack111ll111_opy_ = manager.list()
        if bstack1ll111lll1_opy_(args):
          for index, platform in enumerate(CONFIG[bstack11l1ll1_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫඑ")]):
            if index == 0:
              bstack1l1lll11l1_opy_[bstack11l1ll1_opy_ (u"ࠩࡩ࡭ࡱ࡫࡟࡯ࡣࡰࡩࠬඒ")] = args
            bstack1l1l111ll1_opy_.append(multiprocessing.Process(name=str(index),
                                                       target=run_on_browserstack,
                                                       args=(bstack1l1lll11l1_opy_, bstack111ll111_opy_)))
        else:
          for index, platform in enumerate(CONFIG[bstack11l1ll1_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭ඓ")]):
            bstack1l1l111ll1_opy_.append(multiprocessing.Process(name=str(index),
                                                       target=run_on_browserstack,
                                                       args=(bstack1l1lll11l1_opy_, bstack111ll111_opy_)))
        for t in bstack1l1l111ll1_opy_:
          t.start()
        for t in bstack1l1l111ll1_opy_:
          t.join()
        bstack11l11111_opy_ = list(bstack111ll111_opy_)
      else:
        if bstack1ll111lll1_opy_(args):
          bstack1l1lll11l1_opy_[bstack11l1ll1_opy_ (u"ࠫ࡫࡯࡬ࡦࡡࡱࡥࡲ࡫ࠧඔ")] = args
          test = multiprocessing.Process(name=str(0),
                                         target=run_on_browserstack, args=(bstack1l1lll11l1_opy_,))
          test.start()
          test.join()
        else:
          bstack1l1lll11_opy_(bstack111ll11l_opy_)
          sys.path.append(os.path.dirname(os.path.abspath(args[0])))
          mod_globals = globals()
          mod_globals[bstack11l1ll1_opy_ (u"ࠬࡥ࡟࡯ࡣࡰࡩࡤࡥࠧඕ")] = bstack11l1ll1_opy_ (u"࠭࡟ࡠ࡯ࡤ࡭ࡳࡥ࡟ࠨඖ")
          mod_globals[bstack11l1ll1_opy_ (u"ࠧࡠࡡࡩ࡭ࡱ࡫࡟ࡠࠩ඗")] = os.path.abspath(args[0])
          sys.argv = sys.argv[2:]
          exec(open(args[0]).read(), mod_globals)
  elif bstack111ll1l1_opy_ == bstack11l1ll1_opy_ (u"ࠨࡲࡤࡦࡴࡺࠧ඘") or bstack111ll1l1_opy_ == bstack11l1ll1_opy_ (u"ࠩࡵࡳࡧࡵࡴࠨ඙"):
    percy.init(bstack11ll11ll1_opy_, CONFIG, logger)
    percy.bstack1ll1111l_opy_()
    try:
      from pabot import pabot
    except Exception as e:
      bstack1ll11lll1_opy_(e, bstack11ll1lll1l_opy_)
    bstack1ll1l1ll1_opy_()
    bstack1l1lll11_opy_(bstack1l11l11ll1_opy_)
    if bstack1111l1111_opy_:
      bstack11ll1ll1l_opy_(bstack1l11l11ll1_opy_, args)
      if bstack11l1ll1_opy_ (u"ࠪ࠱࠲ࡶࡲࡰࡥࡨࡷࡸ࡫ࡳࠨක") in args:
        i = args.index(bstack11l1ll1_opy_ (u"ࠫ࠲࠳ࡰࡳࡱࡦࡩࡸࡹࡥࡴࠩඛ"))
        args.pop(i)
        args.pop(i)
      if bstack11l1ll1_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡳࠨග") not in CONFIG:
        CONFIG[bstack11l1ll1_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠩඝ")] = [{}]
        bstack1lll1l1ll_opy_ = 1
      if bstack111lll1l1_opy_ == 0:
        bstack111lll1l1_opy_ = 1
      args.insert(0, str(bstack111lll1l1_opy_))
      args.insert(0, str(bstack11l1ll1_opy_ (u"ࠧ࠮࠯ࡳࡶࡴࡩࡥࡴࡵࡨࡷࠬඞ")))
    if bstack11111l1l1_opy_.on():
      try:
        from robot.run import USAGE
        from robot.utils import ArgumentParser
        from pabot.arguments import _parse_pabot_args
        bstack1ll111l11l_opy_, pabot_args = _parse_pabot_args(args)
        opts, bstack1l11llll11_opy_ = ArgumentParser(
            USAGE,
            auto_pythonpath=False,
            auto_argumentfile=True,
            env_options=bstack11l1ll1_opy_ (u"ࠣࡔࡒࡆࡔ࡚࡟ࡐࡒࡗࡍࡔࡔࡓࠣඟ"),
        ).parse_args(bstack1ll111l11l_opy_)
        bstack1111l1ll_opy_ = args.index(bstack1ll111l11l_opy_[0]) if len(bstack1ll111l11l_opy_) > 0 else len(args)
        args.insert(bstack1111l1ll_opy_, str(bstack11l1ll1_opy_ (u"ࠩ࠰࠱ࡱ࡯ࡳࡵࡧࡱࡩࡷ࠭ච")))
        args.insert(bstack1111l1ll_opy_ + 1, str(os.path.join(os.path.dirname(os.path.realpath(__file__)), bstack11l1ll1_opy_ (u"ࠪࡦࡸࡺࡡࡤ࡭ࡢࡶࡴࡨ࡯ࡵࡡ࡯࡭ࡸࡺࡥ࡯ࡧࡵ࠲ࡵࡿࠧඡ"))))
        if bstack111l1l111_opy_(os.environ.get(bstack11l1ll1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡖࡊࡘࡕࡏࠩජ"))) and str(os.environ.get(bstack11l1ll1_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡗࡋࡒࡖࡐࡢࡘࡊ࡙ࡔࡔࠩඣ"), bstack11l1ll1_opy_ (u"࠭࡮ࡶ࡮࡯ࠫඤ"))) != bstack11l1ll1_opy_ (u"ࠧ࡯ࡷ࡯ࡰࠬඥ"):
          for bstack111111lll_opy_ in bstack1l11llll11_opy_:
            args.remove(bstack111111lll_opy_)
          bstack111lll1ll_opy_ = os.environ.get(bstack11l1ll1_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡓࡇࡕ࡙ࡓࡥࡔࡆࡕࡗࡗࠬඦ")).split(bstack11l1ll1_opy_ (u"ࠩ࠯ࠫට"))
          for bstack1l1l11ll11_opy_ in bstack111lll1ll_opy_:
            args.append(bstack1l1l11ll11_opy_)
      except Exception as e:
        logger.error(bstack11l1ll1_opy_ (u"ࠥࡉࡷࡸ࡯ࡳࠢࡺ࡬࡮ࡲࡥࠡࡣࡷࡸࡦࡩࡨࡪࡰࡪࠤࡱ࡯ࡳࡵࡧࡱࡩࡷࠦࡦࡰࡴࠣࡓࡧࡹࡥࡳࡸࡤࡦ࡮ࡲࡩࡵࡻ࠱ࠤࡊࡸࡲࡰࡴࠣ࠱ࠥࠨඨ").format(e))
    pabot.main(args)
  elif bstack111ll1l1_opy_ == bstack11l1ll1_opy_ (u"ࠫࡷࡵࡢࡰࡶ࠰࡭ࡳࡺࡥࡳࡰࡤࡰࠬඩ"):
    try:
      from robot import run_cli
    except Exception as e:
      bstack1ll11lll1_opy_(e, bstack11ll1lll1l_opy_)
    for a in args:
      if bstack11l1ll1_opy_ (u"ࠬࡈࡓࡕࡃࡆࡏࡕࡒࡁࡕࡈࡒࡖࡒࡏࡎࡅࡇ࡛ࠫඪ") in a:
        bstack1ll1ll1ll_opy_ = int(a.split(bstack11l1ll1_opy_ (u"࠭࠺ࠨණ"))[1])
      if bstack11l1ll1_opy_ (u"ࠧࡃࡕࡗࡅࡈࡑࡄࡆࡈࡏࡓࡈࡇࡌࡊࡆࡈࡒ࡙ࡏࡆࡊࡇࡕࠫඬ") in a:
        bstack1ll1lll1ll_opy_ = str(a.split(bstack11l1ll1_opy_ (u"ࠨ࠼ࠪත"))[1])
      if bstack11l1ll1_opy_ (u"ࠩࡅࡗ࡙ࡇࡃࡌࡅࡏࡍࡆࡘࡇࡔࠩථ") in a:
        bstack11ll11ll_opy_ = str(a.split(bstack11l1ll1_opy_ (u"ࠪ࠾ࠬද"))[1])
    bstack11111l11_opy_ = None
    if bstack11l1ll1_opy_ (u"ࠫ࠲࠳ࡢࡴࡶࡤࡧࡰࡥࡩࡵࡧࡰࡣ࡮ࡴࡤࡦࡺࠪධ") in args:
      i = args.index(bstack11l1ll1_opy_ (u"ࠬ࠳࠭ࡣࡵࡷࡥࡨࡱ࡟ࡪࡶࡨࡱࡤ࡯࡮ࡥࡧࡻࠫන"))
      args.pop(i)
      bstack11111l11_opy_ = args.pop(i)
    if bstack11111l11_opy_ is not None:
      global bstack1l11lll1l1_opy_
      bstack1l11lll1l1_opy_ = bstack11111l11_opy_
    bstack1l1lll11_opy_(bstack1l11l11ll1_opy_)
    run_cli(args)
    if bstack11l1ll1_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰࡥࡥࡳࡴࡲࡶࡤࡲࡩࡴࡶࠪ඲") in multiprocessing.current_process().__dict__.keys():
      for bstack11ll11lll1_opy_ in multiprocessing.current_process().bstack_error_list:
        bstack1llll11ll1_opy_.append(bstack11ll11lll1_opy_)
  elif bstack111ll1l1_opy_ == bstack11l1ll1_opy_ (u"ࠧࡱࡻࡷࡩࡸࡺࠧඳ"):
    bstack11lll11l1l_opy_ = bstack11l111lll_opy_(args, logger, CONFIG, bstack1111l1111_opy_)
    bstack11lll11l1l_opy_.bstack11lllll1l1_opy_()
    bstack1ll1l1ll1_opy_()
    bstack1lll1l111_opy_ = True
    bstack1111l1l1l_opy_ = bstack11lll11l1l_opy_.bstack1111111l1_opy_()
    bstack11lll11l1l_opy_.bstack1l1lll11l1_opy_(bstack1lll11lll_opy_)
    bstack11ll111111_opy_ = bstack11lll11l1l_opy_.bstack11lll1l1_opy_(bstack11llll1ll_opy_, {
      bstack11l1ll1_opy_ (u"ࠨࡊࡘࡆࡤ࡛ࡒࡍࠩප"): bstack1l1ll11ll1_opy_,
      bstack11l1ll1_opy_ (u"ࠩࡌࡗࡤࡇࡐࡑࡡࡄ࡙࡙ࡕࡍࡂࡖࡈࠫඵ"): bstack11ll11ll1_opy_,
      bstack11l1ll1_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡄ࡙࡙ࡕࡍࡂࡖࡌࡓࡓ࠭බ"): bstack1111l1111_opy_
    })
    try:
      bstack1l1l111l11_opy_, bstack11l1llll1l_opy_ = map(list, zip(*bstack11ll111111_opy_))
      bstack1l11ll111l_opy_ = bstack1l1l111l11_opy_[0]
      for status_code in bstack11l1llll1l_opy_:
        if status_code != 0:
          bstack1ll111l1ll_opy_ = status_code
          break
    except Exception as e:
      logger.debug(bstack11l1ll1_opy_ (u"࡚ࠦࡴࡡࡣ࡮ࡨࠤࡹࡵࠠࡴࡣࡹࡩࠥ࡫ࡲࡳࡱࡵࡷࠥࡧ࡮ࡥࠢࡶࡸࡦࡺࡵࡴࠢࡦࡳࡩ࡫࠮ࠡࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤ࠿ࠦࡻࡾࠤභ").format(str(e)))
  elif bstack111ll1l1_opy_ == bstack11l1ll1_opy_ (u"ࠬࡨࡥࡩࡣࡹࡩࠬම"):
    try:
      from behave.__main__ import main as bstack111l11lll_opy_
      from behave.configuration import Configuration
    except Exception as e:
      bstack1ll11lll1_opy_(e, bstack1l11lll1l_opy_)
    bstack1ll1l1ll1_opy_()
    bstack1lll1l111_opy_ = True
    bstack1lll1l111l_opy_ = 1
    if bstack11l1ll1_opy_ (u"࠭ࡰࡢࡴࡤࡰࡱ࡫࡬ࡴࡒࡨࡶࡕࡲࡡࡵࡨࡲࡶࡲ࠭ඹ") in CONFIG:
      bstack1lll1l111l_opy_ = CONFIG[bstack11l1ll1_opy_ (u"ࠧࡱࡣࡵࡥࡱࡲࡥ࡭ࡵࡓࡩࡷࡖ࡬ࡢࡶࡩࡳࡷࡳࠧය")]
    if bstack11l1ll1_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫර") in CONFIG:
      bstack1ll111l1l_opy_ = int(bstack1lll1l111l_opy_) * int(len(CONFIG[bstack11l1ll1_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬ඼")]))
    else:
      bstack1ll111l1l_opy_ = int(bstack1lll1l111l_opy_)
    config = Configuration(args)
    bstack1l1l1l1ll_opy_ = config.paths
    if len(bstack1l1l1l1ll_opy_) == 0:
      import glob
      pattern = bstack11l1ll1_opy_ (u"ࠪ࠮࠯࠵ࠪ࠯ࡨࡨࡥࡹࡻࡲࡦࠩල")
      bstack1lll111l_opy_ = glob.glob(pattern, recursive=True)
      args.extend(bstack1lll111l_opy_)
      config = Configuration(args)
      bstack1l1l1l1ll_opy_ = config.paths
    bstack1ll11llll_opy_ = [os.path.normpath(item) for item in bstack1l1l1l1ll_opy_]
    bstack1ll111l111_opy_ = [os.path.normpath(item) for item in args]
    bstack1ll1l1l11_opy_ = [item for item in bstack1ll111l111_opy_ if item not in bstack1ll11llll_opy_]
    import platform as pf
    if pf.system().lower() == bstack11l1ll1_opy_ (u"ࠫࡼ࡯࡮ࡥࡱࡺࡷࠬ඾"):
      from pathlib import PureWindowsPath, PurePosixPath
      bstack1ll11llll_opy_ = [str(PurePosixPath(PureWindowsPath(bstack11ll11l1ll_opy_)))
                    for bstack11ll11l1ll_opy_ in bstack1ll11llll_opy_]
    bstack11l1l11l_opy_ = []
    for spec in bstack1ll11llll_opy_:
      bstack1l1111ll1l_opy_ = []
      bstack1l1111ll1l_opy_ += bstack1ll1l1l11_opy_
      bstack1l1111ll1l_opy_.append(spec)
      bstack11l1l11l_opy_.append(bstack1l1111ll1l_opy_)
    execution_items = []
    for bstack1l1111ll1l_opy_ in bstack11l1l11l_opy_:
      if bstack11l1ll1_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡳࠨ඿") in CONFIG:
        for index, _ in enumerate(CONFIG[bstack11l1ll1_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠩව")]):
          item = {}
          item[bstack11l1ll1_opy_ (u"ࠧࡢࡴࡪࠫශ")] = bstack11l1ll1_opy_ (u"ࠨࠢࠪෂ").join(bstack1l1111ll1l_opy_)
          item[bstack11l1ll1_opy_ (u"ࠩ࡬ࡲࡩ࡫ࡸࠨස")] = index
          execution_items.append(item)
      else:
        item = {}
        item[bstack11l1ll1_opy_ (u"ࠪࡥࡷ࡭ࠧහ")] = bstack11l1ll1_opy_ (u"ࠫࠥ࠭ළ").join(bstack1l1111ll1l_opy_)
        item[bstack11l1ll1_opy_ (u"ࠬ࡯࡮ࡥࡧࡻࠫෆ")] = 0
        execution_items.append(item)
    bstack1ll1lll111_opy_ = bstack1ll11ll11_opy_(execution_items, bstack1ll111l1l_opy_)
    for execution_item in bstack1ll1lll111_opy_:
      bstack1l1l111ll1_opy_ = []
      for item in execution_item:
        bstack1l1l111ll1_opy_.append(bstack1l11ll1l11_opy_(name=str(item[bstack11l1ll1_opy_ (u"࠭ࡩ࡯ࡦࡨࡼࠬ෇")]),
                                             target=bstack1lll1ll111_opy_,
                                             args=(item[bstack11l1ll1_opy_ (u"ࠧࡢࡴࡪࠫ෈")],)))
      for t in bstack1l1l111ll1_opy_:
        t.start()
      for t in bstack1l1l111ll1_opy_:
        t.join()
  else:
    bstack1l11l1lll_opy_(bstack1ll11111l1_opy_)
  if not bstack1l11l111_opy_:
    bstack1l1llll1l1_opy_()
    if(bstack111ll1l1_opy_ in [bstack11l1ll1_opy_ (u"ࠨࡤࡨ࡬ࡦࡼࡥࠨ෉"), bstack11l1ll1_opy_ (u"ࠩࡳࡽࡹ࡫ࡳࡵ්ࠩ")]):
      bstack1llll11l1_opy_()
  bstack1ll1ll111_opy_.bstack1l11l111l_opy_()
def browserstack_initialize(bstack11111111_opy_=None):
  logger.info(bstack11l1ll1_opy_ (u"ࠪࡖࡺࡴ࡮ࡪࡰࡪࠤࡘࡊࡋࠡࡹ࡬ࡸ࡭ࠦࡡࡳࡩࡶ࠾ࠥ࠭෋") + str(bstack11111111_opy_))
  run_on_browserstack(bstack11111111_opy_, None, True)
@measure(event_name=EVENTS.bstack11lll11l11_opy_, stage=STAGE.bstack1l1ll1llll_opy_, bstack1l11l1ll_opy_=bstack1lll1l11l_opy_)
def bstack1l1llll1l1_opy_():
  global CONFIG
  global bstack1lll1ll1l1_opy_
  global bstack1ll111l1ll_opy_
  global bstack11llllll1_opy_
  global bstack1ll1l11l1_opy_
  if cli.is_running():
    bstack1l1l11lll1_opy_.invoke(bstack1ll1ll1l11_opy_.bstack11lll1l111_opy_)
  if bstack1lll1ll1l1_opy_ == bstack11l1ll1_opy_ (u"ࠫࡵࡿࡴࡦࡵࡷࠫ෌"):
    if not cli.is_enabled(CONFIG):
      bstack11111l1l1_opy_.stop()
  else:
    bstack11111l1l1_opy_.stop()
  if not cli.is_enabled(CONFIG):
    bstack11ll1ll1_opy_.bstack1l1l1llll1_opy_()
  if bstack11l1ll1_opy_ (u"ࠬࡺࡵࡳࡤࡲࡗࡨࡧ࡬ࡦࠩ෍") in CONFIG and str(CONFIG[bstack11l1ll1_opy_ (u"࠭ࡴࡶࡴࡥࡳࡘࡩࡡ࡭ࡧࠪ෎")]).lower() != bstack11l1ll1_opy_ (u"ࠧࡧࡣ࡯ࡷࡪ࠭ා"):
    bstack11l111ll1_opy_, bstack1l1ll111l1_opy_ = bstack1l1lll11ll_opy_()
  else:
    bstack11l111ll1_opy_, bstack1l1ll111l1_opy_ = get_build_link()
  bstack11l1lll111_opy_(bstack11l111ll1_opy_)
  logger.info(bstack11l1ll1_opy_ (u"ࠨࡕࡇࡏࠥࡸࡵ࡯ࠢࡨࡲࡩ࡫ࡤࠡࡨࡲࡶࠥ࡯ࡤ࠻ࠩැ") + bstack1ll1l11l1_opy_.get_property(bstack11l1ll1_opy_ (u"ࠩࡶࡨࡰࡘࡵ࡯ࡋࡧࠫෑ"), bstack11l1ll1_opy_ (u"ࠪࠫි")) + bstack11l1ll1_opy_ (u"ࠫ࠱ࠦࡴࡦࡵࡷ࡬ࡺࡨࠠࡪࡦ࠽ࠤࠬී") + os.getenv(bstack11l1ll1_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣ࡙ࡋࡓࡕࡊࡘࡆࡤ࡛ࡕࡊࡆࠪු"), bstack11l1ll1_opy_ (u"࠭ࠧ෕")))
  if bstack11l111ll1_opy_ is not None and bstack1lll11111l_opy_() != -1:
    sessions = bstack11lll1lll1_opy_(bstack11l111ll1_opy_)
    bstack111l111l_opy_(sessions, bstack1l1ll111l1_opy_)
  if bstack1lll1ll1l1_opy_ == bstack11l1ll1_opy_ (u"ࠧࡱࡻࡷࡩࡸࡺࠧූ") and bstack1ll111l1ll_opy_ != 0:
    sys.exit(bstack1ll111l1ll_opy_)
  if bstack1lll1ll1l1_opy_ == bstack11l1ll1_opy_ (u"ࠨࡤࡨ࡬ࡦࡼࡥࠨ෗") and bstack11llllll1_opy_ != 0:
    sys.exit(bstack11llllll1_opy_)
def bstack11l1lll111_opy_(new_id):
    global bstack1l111l1l11_opy_
    bstack1l111l1l11_opy_ = new_id
def bstack1l1l1ll11l_opy_(bstack1llll1111l_opy_):
  if bstack1llll1111l_opy_:
    return bstack1llll1111l_opy_.capitalize()
  else:
    return bstack11l1ll1_opy_ (u"ࠩࠪෘ")
@measure(event_name=EVENTS.bstack11l11111l_opy_, stage=STAGE.bstack1l1ll1llll_opy_, bstack1l11l1ll_opy_=bstack1lll1l11l_opy_)
def bstack1lll11l11_opy_(bstack1111ll11l_opy_):
  if bstack11l1ll1_opy_ (u"ࠪࡲࡦࡳࡥࠨෙ") in bstack1111ll11l_opy_ and bstack1111ll11l_opy_[bstack11l1ll1_opy_ (u"ࠫࡳࡧ࡭ࡦࠩේ")] != bstack11l1ll1_opy_ (u"ࠬ࠭ෛ"):
    return bstack1111ll11l_opy_[bstack11l1ll1_opy_ (u"࠭࡮ࡢ࡯ࡨࠫො")]
  else:
    bstack1l11l1ll_opy_ = bstack11l1ll1_opy_ (u"ࠢࠣෝ")
    if bstack11l1ll1_opy_ (u"ࠨࡦࡨࡺ࡮ࡩࡥࠨෞ") in bstack1111ll11l_opy_ and bstack1111ll11l_opy_[bstack11l1ll1_opy_ (u"ࠩࡧࡩࡻ࡯ࡣࡦࠩෟ")] != None:
      bstack1l11l1ll_opy_ += bstack1111ll11l_opy_[bstack11l1ll1_opy_ (u"ࠪࡨࡪࡼࡩࡤࡧࠪ෠")] + bstack11l1ll1_opy_ (u"ࠦ࠱ࠦࠢ෡")
      if bstack1111ll11l_opy_[bstack11l1ll1_opy_ (u"ࠬࡵࡳࠨ෢")] == bstack11l1ll1_opy_ (u"ࠨࡩࡰࡵࠥ෣"):
        bstack1l11l1ll_opy_ += bstack11l1ll1_opy_ (u"ࠢࡪࡑࡖࠤࠧ෤")
      bstack1l11l1ll_opy_ += (bstack1111ll11l_opy_[bstack11l1ll1_opy_ (u"ࠨࡱࡶࡣࡻ࡫ࡲࡴ࡫ࡲࡲࠬ෥")] or bstack11l1ll1_opy_ (u"ࠩࠪ෦"))
      return bstack1l11l1ll_opy_
    else:
      bstack1l11l1ll_opy_ += bstack1l1l1ll11l_opy_(bstack1111ll11l_opy_[bstack11l1ll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࠫ෧")]) + bstack11l1ll1_opy_ (u"ࠦࠥࠨ෨") + (
              bstack1111ll11l_opy_[bstack11l1ll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡥࡶࡦࡴࡶ࡭ࡴࡴࠧ෩")] or bstack11l1ll1_opy_ (u"࠭ࠧ෪")) + bstack11l1ll1_opy_ (u"ࠢ࠭ࠢࠥ෫")
      if bstack1111ll11l_opy_[bstack11l1ll1_opy_ (u"ࠨࡱࡶࠫ෬")] == bstack11l1ll1_opy_ (u"ࠤ࡚࡭ࡳࡪ࡯ࡸࡵࠥ෭"):
        bstack1l11l1ll_opy_ += bstack11l1ll1_opy_ (u"࡛ࠥ࡮ࡴࠠࠣ෮")
      bstack1l11l1ll_opy_ += bstack1111ll11l_opy_[bstack11l1ll1_opy_ (u"ࠫࡴࡹ࡟ࡷࡧࡵࡷ࡮ࡵ࡮ࠨ෯")] or bstack11l1ll1_opy_ (u"ࠬ࠭෰")
      return bstack1l11l1ll_opy_
@measure(event_name=EVENTS.bstack1llll11lll_opy_, stage=STAGE.bstack1l1ll1llll_opy_, bstack1l11l1ll_opy_=bstack1lll1l11l_opy_)
def bstack1ll1ll11l_opy_(bstack1ll1lllll1_opy_):
  if bstack1ll1lllll1_opy_ == bstack11l1ll1_opy_ (u"ࠨࡤࡰࡰࡨࠦ෱"):
    return bstack11l1ll1_opy_ (u"ࠧ࠽ࡶࡧࠤࡨࡲࡡࡴࡵࡀࠦࡧࡹࡴࡢࡥ࡮࠱ࡩࡧࡴࡢࠤࠣࡷࡹࡿ࡬ࡦ࠿ࠥࡧࡴࡲ࡯ࡳ࠼ࡪࡶࡪ࡫࡮࠼ࠤࡁࡀ࡫ࡵ࡮ࡵࠢࡦࡳࡱࡵࡲ࠾ࠤࡪࡶࡪ࡫࡮ࠣࡀࡆࡳࡲࡶ࡬ࡦࡶࡨࡨࡁ࠵ࡦࡰࡰࡷࡂࡁ࠵ࡴࡥࡀࠪෲ")
  elif bstack1ll1lllll1_opy_ == bstack11l1ll1_opy_ (u"ࠣࡨࡤ࡭ࡱ࡫ࡤࠣෳ"):
    return bstack11l1ll1_opy_ (u"ࠩ࠿ࡸࡩࠦࡣ࡭ࡣࡶࡷࡂࠨࡢࡴࡶࡤࡧࡰ࠳ࡤࡢࡶࡤࠦࠥࡹࡴࡺ࡮ࡨࡁࠧࡩ࡯࡭ࡱࡵ࠾ࡷ࡫ࡤ࠼ࠤࡁࡀ࡫ࡵ࡮ࡵࠢࡦࡳࡱࡵࡲ࠾ࠤࡵࡩࡩࠨ࠾ࡇࡣ࡬ࡰࡪࡪ࠼࠰ࡨࡲࡲࡹࡄ࠼࠰ࡶࡧࡂࠬ෴")
  elif bstack1ll1lllll1_opy_ == bstack11l1ll1_opy_ (u"ࠥࡴࡦࡹࡳࡦࡦࠥ෵"):
    return bstack11l1ll1_opy_ (u"ࠫࡁࡺࡤࠡࡥ࡯ࡥࡸࡹ࠽ࠣࡤࡶࡸࡦࡩ࡫࠮ࡦࡤࡸࡦࠨࠠࡴࡶࡼࡰࡪࡃࠢࡤࡱ࡯ࡳࡷࡀࡧࡳࡧࡨࡲࡀࠨ࠾࠽ࡨࡲࡲࡹࠦࡣࡰ࡮ࡲࡶࡂࠨࡧࡳࡧࡨࡲࠧࡄࡐࡢࡵࡶࡩࡩࡂ࠯ࡧࡱࡱࡸࡃࡂ࠯ࡵࡦࡁࠫ෶")
  elif bstack1ll1lllll1_opy_ == bstack11l1ll1_opy_ (u"ࠧ࡫ࡲࡳࡱࡵࠦ෷"):
    return bstack11l1ll1_opy_ (u"࠭࠼ࡵࡦࠣࡧࡱࡧࡳࡴ࠿ࠥࡦࡸࡺࡡࡤ࡭࠰ࡨࡦࡺࡡࠣࠢࡶࡸࡾࡲࡥ࠾ࠤࡦࡳࡱࡵࡲ࠻ࡴࡨࡨࡀࠨ࠾࠽ࡨࡲࡲࡹࠦࡣࡰ࡮ࡲࡶࡂࠨࡲࡦࡦࠥࡂࡊࡸࡲࡰࡴ࠿࠳࡫ࡵ࡮ࡵࡀ࠿࠳ࡹࡪ࠾ࠨ෸")
  elif bstack1ll1lllll1_opy_ == bstack11l1ll1_opy_ (u"ࠢࡵ࡫ࡰࡩࡴࡻࡴࠣ෹"):
    return bstack11l1ll1_opy_ (u"ࠨ࠾ࡷࡨࠥࡩ࡬ࡢࡵࡶࡁࠧࡨࡳࡵࡣࡦ࡯࠲ࡪࡡࡵࡣࠥࠤࡸࡺࡹ࡭ࡧࡀࠦࡨࡵ࡬ࡰࡴ࠽ࠧࡪ࡫ࡡ࠴࠴࠹࠿ࠧࡄ࠼ࡧࡱࡱࡸࠥࡩ࡯࡭ࡱࡵࡁࠧࠩࡥࡦࡣ࠶࠶࠻ࠨ࠾ࡕ࡫ࡰࡩࡴࡻࡴ࠽࠱ࡩࡳࡳࡺ࠾࠽࠱ࡷࡨࡃ࠭෺")
  elif bstack1ll1lllll1_opy_ == bstack11l1ll1_opy_ (u"ࠤࡵࡹࡳࡴࡩ࡯ࡩࠥ෻"):
    return bstack11l1ll1_opy_ (u"ࠪࡀࡹࡪࠠࡤ࡮ࡤࡷࡸࡃࠢࡣࡵࡷࡥࡨࡱ࠭ࡥࡣࡷࡥࠧࠦࡳࡵࡻ࡯ࡩࡂࠨࡣࡰ࡮ࡲࡶ࠿ࡨ࡬ࡢࡥ࡮࠿ࠧࡄ࠼ࡧࡱࡱࡸࠥࡩ࡯࡭ࡱࡵࡁࠧࡨ࡬ࡢࡥ࡮ࠦࡃࡘࡵ࡯ࡰ࡬ࡲ࡬ࡂ࠯ࡧࡱࡱࡸࡃࡂ࠯ࡵࡦࡁࠫ෼")
  else:
    return bstack11l1ll1_opy_ (u"ࠫࡁࡺࡤࠡࡣ࡯࡭࡬ࡴ࠽ࠣࡥࡨࡲࡹ࡫ࡲࠣࠢࡦࡰࡦࡹࡳ࠾ࠤࡥࡷࡹࡧࡣ࡬࠯ࡧࡥࡹࡧࠢࠡࡵࡷࡽࡱ࡫࠽ࠣࡥࡲࡰࡴࡸ࠺ࡣ࡮ࡤࡧࡰࡁࠢ࠿࠾ࡩࡳࡳࡺࠠࡤࡱ࡯ࡳࡷࡃࠢࡣ࡮ࡤࡧࡰࠨ࠾ࠨ෽") + bstack1l1l1ll11l_opy_(
      bstack1ll1lllll1_opy_) + bstack11l1ll1_opy_ (u"ࠬࡂ࠯ࡧࡱࡱࡸࡃࡂ࠯ࡵࡦࡁࠫ෾")
def bstack11l1ll11_opy_(session):
  return bstack11l1ll1_opy_ (u"࠭࠼ࡵࡴࠣࡧࡱࡧࡳࡴ࠿ࠥࡦࡸࡺࡡࡤ࡭࠰ࡶࡴࡽࠢ࠿࠾ࡷࡨࠥࡩ࡬ࡢࡵࡶࡁࠧࡨࡳࡵࡣࡦ࡯࠲ࡪࡡࡵࡣࠣࡷࡪࡹࡳࡪࡱࡱ࠱ࡳࡧ࡭ࡦࠤࡁࡀࡦࠦࡨࡳࡧࡩࡁࠧࢁࡽࠣࠢࡷࡥࡷ࡭ࡥࡵ࠿ࠥࡣࡧࡲࡡ࡯࡭ࠥࡂࢀࢃ࠼࠰ࡣࡁࡀ࠴ࡺࡤ࠿ࡽࢀࡿࢂࡂࡴࡥࠢࡤࡰ࡮࡭࡮࠾ࠤࡦࡩࡳࡺࡥࡳࠤࠣࡧࡱࡧࡳࡴ࠿ࠥࡦࡸࡺࡡࡤ࡭࠰ࡨࡦࡺࡡࠣࡀࡾࢁࡁ࠵ࡴࡥࡀ࠿ࡸࡩࠦࡡ࡭࡫ࡪࡲࡂࠨࡣࡦࡰࡷࡩࡷࠨࠠࡤ࡮ࡤࡷࡸࡃࠢࡣࡵࡷࡥࡨࡱ࠭ࡥࡣࡷࡥࠧࡄࡻࡾ࠾࠲ࡸࡩࡄ࠼ࡵࡦࠣࡥࡱ࡯ࡧ࡯࠿ࠥࡧࡪࡴࡴࡦࡴࠥࠤࡨࡲࡡࡴࡵࡀࠦࡧࡹࡴࡢࡥ࡮࠱ࡩࡧࡴࡢࠤࡁࡿࢂࡂ࠯ࡵࡦࡁࡀࡹࡪࠠࡢ࡮࡬࡫ࡳࡃࠢࡤࡧࡱࡸࡪࡸࠢࠡࡥ࡯ࡥࡸࡹ࠽ࠣࡤࡶࡸࡦࡩ࡫࠮ࡦࡤࡸࡦࠨ࠾ࡼࡿ࠿࠳ࡹࡪ࠾࠽࠱ࡷࡶࡃ࠭෿").format(
    session[bstack11l1ll1_opy_ (u"ࠧࡱࡷࡥࡰ࡮ࡩ࡟ࡶࡴ࡯ࠫ฀")], bstack1lll11l11_opy_(session), bstack1ll1ll11l_opy_(session[bstack11l1ll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࡟ࡴࡶࡤࡸࡺࡹࠧก")]),
    bstack1ll1ll11l_opy_(session[bstack11l1ll1_opy_ (u"ࠩࡶࡸࡦࡺࡵࡴࠩข")]),
    bstack1l1l1ll11l_opy_(session[bstack11l1ll1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࠫฃ")] or session[bstack11l1ll1_opy_ (u"ࠫࡩ࡫ࡶࡪࡥࡨࠫค")] or bstack11l1ll1_opy_ (u"ࠬ࠭ฅ")) + bstack11l1ll1_opy_ (u"ࠨࠠࠣฆ") + (session[bstack11l1ll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡠࡸࡨࡶࡸ࡯࡯࡯ࠩง")] or bstack11l1ll1_opy_ (u"ࠨࠩจ")),
    session[bstack11l1ll1_opy_ (u"ࠩࡲࡷࠬฉ")] + bstack11l1ll1_opy_ (u"ࠥࠤࠧช") + session[bstack11l1ll1_opy_ (u"ࠫࡴࡹ࡟ࡷࡧࡵࡷ࡮ࡵ࡮ࠨซ")], session[bstack11l1ll1_opy_ (u"ࠬࡪࡵࡳࡣࡷ࡭ࡴࡴࠧฌ")] or bstack11l1ll1_opy_ (u"࠭ࠧญ"),
    session[bstack11l1ll1_opy_ (u"ࠧࡤࡴࡨࡥࡹ࡫ࡤࡠࡣࡷࠫฎ")] if session[bstack11l1ll1_opy_ (u"ࠨࡥࡵࡩࡦࡺࡥࡥࡡࡤࡸࠬฏ")] else bstack11l1ll1_opy_ (u"ࠩࠪฐ"))
@measure(event_name=EVENTS.bstack111l1lll_opy_, stage=STAGE.bstack1l1ll1llll_opy_, bstack1l11l1ll_opy_=bstack1lll1l11l_opy_)
def bstack111l111l_opy_(sessions, bstack1l1ll111l1_opy_):
  try:
    bstack1l1l1l11l_opy_ = bstack11l1ll1_opy_ (u"ࠥࠦฑ")
    if not os.path.exists(bstack11ll1lll1_opy_):
      os.mkdir(bstack11ll1lll1_opy_)
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), bstack11l1ll1_opy_ (u"ࠫࡦࡹࡳࡦࡶࡶ࠳ࡷ࡫ࡰࡰࡴࡷ࠲࡭ࡺ࡭࡭ࠩฒ")), bstack11l1ll1_opy_ (u"ࠬࡸࠧณ")) as f:
      bstack1l1l1l11l_opy_ = f.read()
    bstack1l1l1l11l_opy_ = bstack1l1l1l11l_opy_.replace(bstack11l1ll1_opy_ (u"࠭ࡻࠦࡔࡈࡗ࡚ࡒࡔࡔࡡࡆࡓ࡚ࡔࡔࠦࡿࠪด"), str(len(sessions)))
    bstack1l1l1l11l_opy_ = bstack1l1l1l11l_opy_.replace(bstack11l1ll1_opy_ (u"ࠧࡼࠧࡅ࡙ࡎࡒࡄࡠࡗࡕࡐࠪࢃࠧต"), bstack1l1ll111l1_opy_)
    bstack1l1l1l11l_opy_ = bstack1l1l1l11l_opy_.replace(bstack11l1ll1_opy_ (u"ࠨࡽࠨࡆ࡚ࡏࡌࡅࡡࡑࡅࡒࡋࠥࡾࠩถ"),
                                              sessions[0].get(bstack11l1ll1_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡠࡰࡤࡱࡪ࠭ท")) if sessions[0] else bstack11l1ll1_opy_ (u"ࠪࠫธ"))
    with open(os.path.join(bstack11ll1lll1_opy_, bstack11l1ll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠰ࡶࡪࡶ࡯ࡳࡶ࠱࡬ࡹࡳ࡬ࠨน")), bstack11l1ll1_opy_ (u"ࠬࡽࠧบ")) as stream:
      stream.write(bstack1l1l1l11l_opy_.split(bstack11l1ll1_opy_ (u"࠭ࡻࠦࡕࡈࡗࡘࡏࡏࡏࡕࡢࡈࡆ࡚ࡁࠦࡿࠪป"))[0])
      for session in sessions:
        stream.write(bstack11l1ll11_opy_(session))
      stream.write(bstack1l1l1l11l_opy_.split(bstack11l1ll1_opy_ (u"ࠧࡼࠧࡖࡉࡘ࡙ࡉࡐࡐࡖࡣࡉࡇࡔࡂࠧࢀࠫผ"))[1])
    logger.info(bstack11l1ll1_opy_ (u"ࠨࡉࡨࡲࡪࡸࡡࡵࡧࡧࠤࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࠣࡦࡺ࡯࡬ࡥࠢࡤࡶࡹ࡯ࡦࡢࡥࡷࡷࠥࡧࡴࠡࡽࢀࠫฝ").format(bstack11ll1lll1_opy_));
  except Exception as e:
    logger.debug(bstack1l111l11l1_opy_.format(str(e)))
def bstack11lll1lll1_opy_(bstack11l111ll1_opy_):
  global CONFIG
  try:
    bstack1l1l1ll111_opy_ = datetime.datetime.now()
    host = bstack11l1ll1_opy_ (u"ࠩࡤࡴ࡮࠳ࡣ࡭ࡱࡸࡨࠬพ") if bstack11l1ll1_opy_ (u"ࠪࡥࡵࡶࠧฟ") in CONFIG else bstack11l1ll1_opy_ (u"ࠫࡦࡶࡩࠨภ")
    user = CONFIG[bstack11l1ll1_opy_ (u"ࠬࡻࡳࡦࡴࡑࡥࡲ࡫ࠧม")]
    key = CONFIG[bstack11l1ll1_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸࡑࡥࡺࠩย")]
    bstack1lll1l1111_opy_ = bstack11l1ll1_opy_ (u"ࠧࡢࡲࡳ࠱ࡦࡻࡴࡰ࡯ࡤࡸࡪ࠭ร") if bstack11l1ll1_opy_ (u"ࠨࡣࡳࡴࠬฤ") in CONFIG else (bstack11l1ll1_opy_ (u"ࠩࡷࡹࡷࡨ࡯ࡴࡥࡤࡰࡪ࠭ล") if CONFIG.get(bstack11l1ll1_opy_ (u"ࠪࡸࡺࡸࡢࡰࡵࡦࡥࡱ࡫ࠧฦ")) else bstack11l1ll1_opy_ (u"ࠫࡦࡻࡴࡰ࡯ࡤࡸࡪ࠭ว"))
    url = bstack11l1ll1_opy_ (u"ࠬ࡮ࡴࡵࡲࡶ࠾࠴࠵ࡻࡾ࠼ࡾࢁࡅࢁࡽ࠯ࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡤࡱࡰ࠳ࢀࢃ࠯ࡣࡷ࡬ࡰࡩࡹ࠯ࡼࡿ࠲ࡷࡪࡹࡳࡪࡱࡱࡷ࠳ࡰࡳࡰࡰࠪศ").format(user, key, host, bstack1lll1l1111_opy_,
                                                                                bstack11l111ll1_opy_)
    headers = {
      bstack11l1ll1_opy_ (u"࠭ࡃࡰࡰࡷࡩࡳࡺ࠭ࡵࡻࡳࡩࠬษ"): bstack11l1ll1_opy_ (u"ࠧࡢࡲࡳࡰ࡮ࡩࡡࡵ࡫ࡲࡲ࠴ࡰࡳࡰࡰࠪส"),
    }
    proxies = bstack1l11l1l1_opy_(CONFIG, url)
    response = requests.get(url, headers=headers, proxies=proxies)
    if response.json():
      cli.bstack111l11l1_opy_(bstack11l1ll1_opy_ (u"ࠣࡪࡷࡸࡵࡀࡧࡦࡶࡢࡷࡪࡹࡳࡪࡱࡱࡷࡤࡲࡩࡴࡶࠥห"), datetime.datetime.now() - bstack1l1l1ll111_opy_)
      return list(map(lambda session: session[bstack11l1ll1_opy_ (u"ࠩࡤࡹࡹࡵ࡭ࡢࡶ࡬ࡳࡳࡥࡳࡦࡵࡶ࡭ࡴࡴࠧฬ")], response.json()))
  except Exception as e:
    logger.debug(bstack111lll1l_opy_.format(str(e)))
@measure(event_name=EVENTS.bstack1l1111lll1_opy_, stage=STAGE.bstack1l1ll1llll_opy_, bstack1l11l1ll_opy_=bstack1lll1l11l_opy_)
def get_build_link():
  global CONFIG
  global bstack1l111l1l11_opy_
  try:
    if bstack11l1ll1_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡐࡤࡱࡪ࠭อ") in CONFIG:
      bstack1l1l1ll111_opy_ = datetime.datetime.now()
      host = bstack11l1ll1_opy_ (u"ࠫࡦࡶࡩ࠮ࡥ࡯ࡳࡺࡪࠧฮ") if bstack11l1ll1_opy_ (u"ࠬࡧࡰࡱࠩฯ") in CONFIG else bstack11l1ll1_opy_ (u"࠭ࡡࡱ࡫ࠪะ")
      user = CONFIG[bstack11l1ll1_opy_ (u"ࠧࡶࡵࡨࡶࡓࡧ࡭ࡦࠩั")]
      key = CONFIG[bstack11l1ll1_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡌࡧࡼࠫา")]
      bstack1lll1l1111_opy_ = bstack11l1ll1_opy_ (u"ࠩࡤࡴࡵ࠳ࡡࡶࡶࡲࡱࡦࡺࡥࠨำ") if bstack11l1ll1_opy_ (u"ࠪࡥࡵࡶࠧิ") in CONFIG else bstack11l1ll1_opy_ (u"ࠫࡦࡻࡴࡰ࡯ࡤࡸࡪ࠭ี")
      url = bstack11l1ll1_opy_ (u"ࠬ࡮ࡴࡵࡲࡶ࠾࠴࠵ࡻࡾ࠼ࡾࢁࡅࢁࡽ࠯ࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡤࡱࡰ࠳ࢀࢃ࠯ࡣࡷ࡬ࡰࡩࡹ࠮࡫ࡵࡲࡲࠬึ").format(user, key, host, bstack1lll1l1111_opy_)
      headers = {
        bstack11l1ll1_opy_ (u"࠭ࡃࡰࡰࡷࡩࡳࡺ࠭ࡵࡻࡳࡩࠬื"): bstack11l1ll1_opy_ (u"ࠧࡢࡲࡳࡰ࡮ࡩࡡࡵ࡫ࡲࡲ࠴ࡰࡳࡰࡰุࠪ"),
      }
      if bstack11l1ll1_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡉࡥࡧࡱࡸ࡮࡬ࡩࡦࡴูࠪ") in CONFIG:
        params = {bstack11l1ll1_opy_ (u"ࠩࡱࡥࡲ࡫ฺࠧ"): CONFIG[bstack11l1ll1_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡐࡤࡱࡪ࠭฻")], bstack11l1ll1_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡢ࡭ࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠧ฼"): CONFIG[bstack11l1ll1_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠧ฽")]}
      else:
        params = {bstack11l1ll1_opy_ (u"࠭࡮ࡢ࡯ࡨࠫ฾"): CONFIG[bstack11l1ll1_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡔࡡ࡮ࡧࠪ฿")]}
      proxies = bstack1l11l1l1_opy_(CONFIG, url)
      response = requests.get(url, params=params, headers=headers, proxies=proxies)
      if response.json():
        bstack1ll1ll1l1_opy_ = response.json()[0][bstack11l1ll1_opy_ (u"ࠨࡣࡸࡸࡴࡳࡡࡵ࡫ࡲࡲࡤࡨࡵࡪ࡮ࡧࠫเ")]
        if bstack1ll1ll1l1_opy_:
          bstack1l1ll111l1_opy_ = bstack1ll1ll1l1_opy_[bstack11l1ll1_opy_ (u"ࠩࡳࡹࡧࡲࡩࡤࡡࡸࡶࡱ࠭แ")].split(bstack11l1ll1_opy_ (u"ࠪࡴࡺࡨ࡬ࡪࡥ࠰ࡦࡺ࡯࡬ࡥࠩโ"))[0] + bstack11l1ll1_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡶ࠳ࠬใ") + bstack1ll1ll1l1_opy_[
            bstack11l1ll1_opy_ (u"ࠬ࡮ࡡࡴࡪࡨࡨࡤ࡯ࡤࠨไ")]
          logger.info(bstack11llll1lll_opy_.format(bstack1l1ll111l1_opy_))
          bstack1l111l1l11_opy_ = bstack1ll1ll1l1_opy_[bstack11l1ll1_opy_ (u"࠭ࡨࡢࡵ࡫ࡩࡩࡥࡩࡥࠩๅ")]
          bstack11l1lll11l_opy_ = CONFIG[bstack11l1ll1_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡔࡡ࡮ࡧࠪๆ")]
          if bstack11l1ll1_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡉࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࠪ็") in CONFIG:
            bstack11l1lll11l_opy_ += bstack11l1ll1_opy_ (u"่ࠩࠣࠫ") + CONFIG[bstack11l1ll1_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶ้ࠬ")]
          if bstack11l1lll11l_opy_ != bstack1ll1ll1l1_opy_[bstack11l1ll1_opy_ (u"ࠫࡳࡧ࡭ࡦ๊ࠩ")]:
            logger.debug(bstack11ll1ll111_opy_.format(bstack1ll1ll1l1_opy_[bstack11l1ll1_opy_ (u"ࠬࡴࡡ࡮ࡧ๋ࠪ")], bstack11l1lll11l_opy_))
          cli.bstack111l11l1_opy_(bstack11l1ll1_opy_ (u"ࠨࡨࡵࡶࡳ࠾࡬࡫ࡴࡠࡤࡸ࡭ࡱࡪ࡟࡭࡫ࡱ࡯ࠧ์"), datetime.datetime.now() - bstack1l1l1ll111_opy_)
          return [bstack1ll1ll1l1_opy_[bstack11l1ll1_opy_ (u"ࠧࡩࡣࡶ࡬ࡪࡪ࡟ࡪࡦࠪํ")], bstack1l1ll111l1_opy_]
    else:
      logger.warn(bstack1l1l1ll1ll_opy_)
  except Exception as e:
    logger.debug(bstack11lll111_opy_.format(str(e)))
  return [None, None]
def bstack1l1l111lll_opy_(url, bstack1l11l1ll1l_opy_=False):
  global CONFIG
  global bstack11ll11ll1l_opy_
  if not bstack11ll11ll1l_opy_:
    hostname = bstack1l1ll11l11_opy_(url)
    is_private = bstack1l11llll1_opy_(hostname)
    if (bstack11l1ll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࡌࡰࡥࡤࡰࠬ๎") in CONFIG and not bstack111l1l111_opy_(CONFIG[bstack11l1ll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡍࡱࡦࡥࡱ࠭๏")])) and (is_private or bstack1l11l1ll1l_opy_):
      bstack11ll11ll1l_opy_ = hostname
def bstack1l1ll11l11_opy_(url):
  return urlparse(url).hostname
def bstack1l11llll1_opy_(hostname):
  for bstack1l1l111ll_opy_ in bstack1lll1111l1_opy_:
    regex = re.compile(bstack1l1l111ll_opy_)
    if regex.match(hostname):
      return True
  return False
def bstack11ll11ll11_opy_(key_name):
  return True if key_name in threading.current_thread().__dict__.keys() else False
@measure(event_name=EVENTS.bstack1ll11lllll_opy_, stage=STAGE.bstack1l1ll1llll_opy_, bstack1l11l1ll_opy_=bstack1lll1l11l_opy_)
def getAccessibilityResults(driver):
  global CONFIG
  global bstack1ll1ll1ll_opy_
  bstack11ll111l_opy_ = not (bstack1ll1l1lll_opy_(threading.current_thread(), bstack11l1ll1_opy_ (u"ࠪ࡭ࡸࡇ࠱࠲ࡻࡗࡩࡸࡺࠧ๐"), None) and bstack1ll1l1lll_opy_(
          threading.current_thread(), bstack11l1ll1_opy_ (u"ࠫࡦ࠷࠱ࡺࡒ࡯ࡥࡹ࡬࡯ࡳ࡯ࠪ๑"), None))
  bstack1l11lll11_opy_ = getattr(driver, bstack11l1ll1_opy_ (u"ࠬࡨࡳࡵࡣࡦ࡯ࡆ࠷࠱ࡺࡕ࡫ࡳࡺࡲࡤࡔࡥࡤࡲࠬ๒"), None) != True
  if not bstack11lll11ll1_opy_.bstack111l1l1l_opy_(CONFIG, bstack1ll1ll1ll_opy_) or (bstack1l11lll11_opy_ and bstack11ll111l_opy_):
    logger.warning(bstack11l1ll1_opy_ (u"ࠨࡎࡰࡶࠣࡥࡳࠦࡁࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࠦࡁࡶࡶࡲࡱࡦࡺࡩࡰࡰࠣࡷࡪࡹࡳࡪࡱࡱ࠰ࠥࡩࡡ࡯ࡰࡲࡸࠥࡸࡥࡵࡴ࡬ࡩࡻ࡫ࠠࡂࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠠࡳࡧࡶࡹࡱࡺࡳ࠯ࠤ๓"))
    return {}
  try:
    logger.debug(bstack11l1ll1_opy_ (u"ࠧࡑࡧࡵࡪࡴࡸ࡭ࡪࡰࡪࠤࡸࡩࡡ࡯ࠢࡥࡩ࡫ࡵࡲࡦࠢࡪࡩࡹࡺࡩ࡯ࡩࠣࡶࡪࡹࡵ࡭ࡶࡶࠫ๔"))
    logger.debug(perform_scan(driver))
    results = driver.execute_async_script(bstack1l1ll1111l_opy_.bstack11l1l11l1_opy_)
    return results
  except Exception:
    logger.error(bstack11l1ll1_opy_ (u"ࠣࡐࡲࠤࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠤࡷ࡫ࡳࡶ࡮ࡷࡷࠥࡽࡥࡳࡧࠣࡪࡴࡻ࡮ࡥ࠰ࠥ๕"))
    return {}
@measure(event_name=EVENTS.bstack11l1ll11l1_opy_, stage=STAGE.bstack1l1ll1llll_opy_, bstack1l11l1ll_opy_=bstack1lll1l11l_opy_)
def getAccessibilityResultsSummary(driver):
  global CONFIG
  global bstack1ll1ll1ll_opy_
  bstack11ll111l_opy_ = not (bstack1ll1l1lll_opy_(threading.current_thread(), bstack11l1ll1_opy_ (u"ࠩ࡬ࡷࡆ࠷࠱ࡺࡖࡨࡷࡹ࠭๖"), None) and bstack1ll1l1lll_opy_(
          threading.current_thread(), bstack11l1ll1_opy_ (u"ࠪࡥ࠶࠷ࡹࡑ࡮ࡤࡸ࡫ࡵࡲ࡮ࠩ๗"), None))
  bstack1l11lll11_opy_ = getattr(driver, bstack11l1ll1_opy_ (u"ࠫࡧࡹࡴࡢࡥ࡮ࡅ࠶࠷ࡹࡔࡪࡲࡹࡱࡪࡓࡤࡣࡱࠫ๘"), None) != True
  if not bstack11lll11ll1_opy_.bstack111l1l1l_opy_(CONFIG, bstack1ll1ll1ll_opy_) or (bstack1l11lll11_opy_ and bstack11ll111l_opy_):
    logger.warning(bstack11l1ll1_opy_ (u"ࠧࡔ࡯ࡵࠢࡤࡲࠥࡇࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠥࡇࡵࡵࡱࡰࡥࡹ࡯࡯࡯ࠢࡶࡩࡸࡹࡩࡰࡰ࠯ࠤࡨࡧ࡮࡯ࡱࡷࠤࡷ࡫ࡴࡳ࡫ࡨࡺࡪࠦࡁࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࠦࡲࡦࡵࡸࡰࡹࡹࠠࡴࡷࡰࡱࡦࡸࡹ࠯ࠤ๙"))
    return {}
  try:
    logger.debug(bstack11l1ll1_opy_ (u"࠭ࡐࡦࡴࡩࡳࡷࡳࡩ࡯ࡩࠣࡷࡨࡧ࡮ࠡࡤࡨࡪࡴࡸࡥࠡࡩࡨࡸࡹ࡯࡮ࡨࠢࡵࡩࡸࡻ࡬ࡵࡵࠣࡷࡺࡳ࡭ࡢࡴࡼࠫ๚"))
    logger.debug(perform_scan(driver))
    bstack1lll1lll_opy_ = driver.execute_async_script(bstack1l1ll1111l_opy_.bstack11l1lll1l_opy_)
    return bstack1lll1lll_opy_
  except Exception:
    logger.error(bstack11l1ll1_opy_ (u"ࠢࡏࡱࠣࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠣࡷࡺࡳ࡭ࡢࡴࡼࠤࡼࡧࡳࠡࡨࡲࡹࡳࡪ࠮ࠣ๛"))
    return {}
@measure(event_name=EVENTS.bstack11l1ll1111_opy_, stage=STAGE.bstack1l1ll1llll_opy_, bstack1l11l1ll_opy_=bstack1lll1l11l_opy_)
def perform_scan(driver, *args, **kwargs):
  global CONFIG
  global bstack1ll1ll1ll_opy_
  bstack11ll111l_opy_ = not (bstack1ll1l1lll_opy_(threading.current_thread(), bstack11l1ll1_opy_ (u"ࠨ࡫ࡶࡅ࠶࠷ࡹࡕࡧࡶࡸࠬ๜"), None) and bstack1ll1l1lll_opy_(
          threading.current_thread(), bstack11l1ll1_opy_ (u"ࠩࡤ࠵࠶ࡿࡐ࡭ࡣࡷࡪࡴࡸ࡭ࠨ๝"), None))
  bstack1l11lll11_opy_ = getattr(driver, bstack11l1ll1_opy_ (u"ࠪࡦࡸࡺࡡࡤ࡭ࡄ࠵࠶ࡿࡓࡩࡱࡸࡰࡩ࡙ࡣࡢࡰࠪ๞"), None) != True
  if not bstack11lll11ll1_opy_.bstack111l1l1l_opy_(CONFIG, bstack1ll1ll1ll_opy_) or (bstack1l11lll11_opy_ and bstack11ll111l_opy_):
    logger.warning(bstack11l1ll1_opy_ (u"ࠦࡓࡵࡴࠡࡣࡱࠤࡆࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠤࡆࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࠡࡵࡨࡷࡸ࡯࡯࡯࠮ࠣࡧࡦࡴ࡮ࡰࡶࠣࡶࡺࡴࠠࡂࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠠࡴࡥࡤࡲ࠳ࠨ๟"))
    return {}
  try:
    bstack1l1lllll1_opy_ = driver.execute_async_script(bstack1l1ll1111l_opy_.perform_scan, {bstack11l1ll1_opy_ (u"ࠬࡳࡥࡵࡪࡲࡨࠬ๠"): kwargs.get(bstack11l1ll1_opy_ (u"࠭ࡤࡳ࡫ࡹࡩࡷࡥࡣࡰ࡯ࡰࡥࡳࡪࠧ๡"), None) or bstack11l1ll1_opy_ (u"ࠧࠨ๢")})
    return bstack1l1lllll1_opy_
  except Exception:
    logger.error(bstack11l1ll1_opy_ (u"ࠣࡗࡱࡥࡧࡲࡥࠡࡶࡲࠤࡷࡻ࡮ࠡࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠡࡵࡦࡥࡳ࠴ࠢ๣"))
    return {}