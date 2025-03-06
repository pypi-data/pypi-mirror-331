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
import threading
import logging
import bstack_utils.accessibility as bstack11lll11ll1_opy_
from bstack_utils.helper import bstack1ll1l1lll_opy_
logger = logging.getLogger(__name__)
def bstack11ll11ll11_opy_(key_name):
  return True if key_name in threading.current_thread().__dict__.keys() else False
def bstack11ll111ll_opy_(context, *args):
    tags = getattr(args[0], bstack11l1ll1_opy_ (u"ࠧࡵࡣࡪࡷࠬᓝ"), [])
    bstack1l11l1l1l_opy_ = bstack11lll11ll1_opy_.bstack1lllll11l_opy_(tags)
    threading.current_thread().isA11yTest = bstack1l11l1l1l_opy_
    try:
      bstack1lllll1111_opy_ = threading.current_thread().bstackSessionDriver if bstack11ll11ll11_opy_(bstack11l1ll1_opy_ (u"ࠨࡤࡶࡸࡦࡩ࡫ࡔࡧࡶࡷ࡮ࡵ࡮ࡅࡴ࡬ࡺࡪࡸࠧᓞ")) else context.browser
      if bstack1lllll1111_opy_ and bstack1lllll1111_opy_.session_id and bstack1l11l1l1l_opy_ and bstack1ll1l1lll_opy_(
              threading.current_thread(), bstack11l1ll1_opy_ (u"ࠩࡤ࠵࠶ࡿࡐ࡭ࡣࡷࡪࡴࡸ࡭ࠨᓟ"), None):
          threading.current_thread().isA11yTest = bstack11lll11ll1_opy_.bstack1l1ll1l111_opy_(bstack1lllll1111_opy_, bstack1l11l1l1l_opy_)
    except Exception as e:
       logger.debug(bstack11l1ll1_opy_ (u"ࠪࡊࡦ࡯࡬ࡦࡦࠣࡸࡴࠦࡳࡵࡣࡵࡸࠥࡧ࠱࠲ࡻࠣ࡭ࡳࠦࡢࡦࡪࡤࡺࡪࡀࠠࡼࡿࠪᓠ").format(str(e)))
def bstack11111l111_opy_(bstack1lllll1111_opy_):
    if bstack1ll1l1lll_opy_(threading.current_thread(), bstack11l1ll1_opy_ (u"ࠫ࡮ࡹࡁ࠲࠳ࡼࡘࡪࡹࡴࠨᓡ"), None) and bstack1ll1l1lll_opy_(
      threading.current_thread(), bstack11l1ll1_opy_ (u"ࠬࡧ࠱࠲ࡻࡓࡰࡦࡺࡦࡰࡴࡰࠫᓢ"), None) and not bstack1ll1l1lll_opy_(threading.current_thread(), bstack11l1ll1_opy_ (u"࠭ࡡ࠲࠳ࡼࡣࡸࡺ࡯ࡱࠩᓣ"), False):
      threading.current_thread().a11y_stop = True
      bstack11lll11ll1_opy_.bstack11111111l_opy_(bstack1lllll1111_opy_, name=bstack11l1ll1_opy_ (u"ࠢࠣᓤ"), path=bstack11l1ll1_opy_ (u"ࠣࠤᓥ"))