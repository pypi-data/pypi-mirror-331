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
import threading
import logging
import bstack_utils.bstack111ll11111_opy_ as bstack1lll1lll1_opy_
from bstack_utils.helper import bstack1l1l11ll11_opy_
logger = logging.getLogger(__name__)
def bstack11lllll1l1_opy_(key_name):
  return True if key_name in threading.current_thread().__dict__.keys() else False
def bstack11l11ll11_opy_(context, *args):
    tags = getattr(args[0], bstack111l11_opy_ (u"ࠧࡵࡣࡪࡷࠬၽ"), [])
    bstack1ll111ll_opy_ = bstack1lll1lll1_opy_.bstack1ll1lllll1_opy_(tags)
    threading.current_thread().isA11yTest = bstack1ll111ll_opy_
    try:
      bstack11111l11_opy_ = threading.current_thread().bstackSessionDriver if bstack11lllll1l1_opy_(bstack111l11_opy_ (u"ࠨࡤࡶࡸࡦࡩ࡫ࡔࡧࡶࡷ࡮ࡵ࡮ࡅࡴ࡬ࡺࡪࡸࠧၾ")) else context.browser
      if bstack11111l11_opy_ and bstack11111l11_opy_.session_id and bstack1ll111ll_opy_ and bstack1l1l11ll11_opy_(
              threading.current_thread(), bstack111l11_opy_ (u"ࠩࡤ࠵࠶ࡿࡐ࡭ࡣࡷࡪࡴࡸ࡭ࠨၿ"), None):
          threading.current_thread().isA11yTest = bstack1lll1lll1_opy_.bstack111llllll_opy_(bstack11111l11_opy_, bstack1ll111ll_opy_)
    except Exception as e:
       logger.debug(bstack111l11_opy_ (u"ࠪࡊࡦ࡯࡬ࡦࡦࠣࡸࡴࠦࡳࡵࡣࡵࡸࠥࡧ࠱࠲ࡻࠣ࡭ࡳࠦࡢࡦࡪࡤࡺࡪࡀࠠࡼࡿࠪႀ").format(str(e)))
def bstack111111l1l_opy_(bstack11111l11_opy_):
    if bstack1l1l11ll11_opy_(threading.current_thread(), bstack111l11_opy_ (u"ࠫ࡮ࡹࡁ࠲࠳ࡼࡘࡪࡹࡴࠨႁ"), None) and bstack1l1l11ll11_opy_(
      threading.current_thread(), bstack111l11_opy_ (u"ࠬࡧ࠱࠲ࡻࡓࡰࡦࡺࡦࡰࡴࡰࠫႂ"), None) and not bstack1l1l11ll11_opy_(threading.current_thread(), bstack111l11_opy_ (u"࠭ࡡ࠲࠳ࡼࡣࡸࡺ࡯ࡱࠩႃ"), False):
      threading.current_thread().a11y_stop = True
      bstack1lll1lll1_opy_.bstack11lll1l11_opy_(bstack11111l11_opy_, name=bstack111l11_opy_ (u"ࠢࠣႄ"), path=bstack111l11_opy_ (u"ࠣࠤႅ"))