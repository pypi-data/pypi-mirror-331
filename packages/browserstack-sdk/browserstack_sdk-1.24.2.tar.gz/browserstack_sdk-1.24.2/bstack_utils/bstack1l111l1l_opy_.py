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
import os
import threading
from bstack_utils.config import Config
from bstack_utils.constants import EVENTS, STAGE
from bstack_utils.helper import bstack1l11111111l_opy_, bstack1l1ll11l11_opy_, bstack1ll1l1lll_opy_, bstack1l11llll1_opy_, \
    bstack11lll1l11l1_opy_
from bstack_utils.measure import measure
def bstack1ll111ll11_opy_(bstack11l11l1lll1_opy_):
    for driver in bstack11l11l1lll1_opy_:
        try:
            driver.quit()
        except Exception as e:
            pass
@measure(event_name=EVENTS.bstack1llll11lll_opy_, stage=STAGE.bstack1l1ll1llll_opy_)
def bstack1ll1llllll_opy_(driver, status, reason=bstack11l1ll1_opy_ (u"ࠨࠩᯗ")):
    bstack1ll1l11l1_opy_ = Config.bstack1l111l1ll1_opy_()
    if bstack1ll1l11l1_opy_.bstack111l1l111l_opy_():
        return
    bstack1lll1lll1l_opy_ = bstack1lll111ll_opy_(bstack11l1ll1_opy_ (u"ࠩࡶࡩࡹ࡙ࡥࡴࡵ࡬ࡳࡳ࡙ࡴࡢࡶࡸࡷࠬᯘ"), bstack11l1ll1_opy_ (u"ࠪࠫᯙ"), status, reason, bstack11l1ll1_opy_ (u"ࠫࠬᯚ"), bstack11l1ll1_opy_ (u"ࠬ࠭ᯛ"))
    driver.execute_script(bstack1lll1lll1l_opy_)
@measure(event_name=EVENTS.bstack1llll11lll_opy_, stage=STAGE.bstack1l1ll1llll_opy_)
def bstack11l1111l1_opy_(page, status, reason=bstack11l1ll1_opy_ (u"࠭ࠧᯜ")):
    try:
        if page is None:
            return
        bstack1ll1l11l1_opy_ = Config.bstack1l111l1ll1_opy_()
        if bstack1ll1l11l1_opy_.bstack111l1l111l_opy_():
            return
        bstack1lll1lll1l_opy_ = bstack1lll111ll_opy_(bstack11l1ll1_opy_ (u"ࠧࡴࡧࡷࡗࡪࡹࡳࡪࡱࡱࡗࡹࡧࡴࡶࡵࠪᯝ"), bstack11l1ll1_opy_ (u"ࠨࠩᯞ"), status, reason, bstack11l1ll1_opy_ (u"ࠩࠪᯟ"), bstack11l1ll1_opy_ (u"ࠪࠫᯠ"))
        page.evaluate(bstack11l1ll1_opy_ (u"ࠦࡤࠦ࠽࠿ࠢࡾࢁࠧᯡ"), bstack1lll1lll1l_opy_)
    except Exception as e:
        print(bstack11l1ll1_opy_ (u"ࠧࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡ࡫ࡱࠤࡸ࡫ࡴࡵ࡫ࡱ࡫ࠥࡹࡥࡴࡵ࡬ࡳࡳࠦࡳࡵࡣࡷࡹࡸࠦࡦࡰࡴࠣࡴࡱࡧࡹࡸࡴ࡬࡫࡭ࡺࠠࡼࡿࠥᯢ"), e)
def bstack1lll111ll_opy_(type, name, status, reason, bstack1lll11l1l_opy_, bstack1llll1l11_opy_):
    bstack11l1lll1ll_opy_ = {
        bstack11l1ll1_opy_ (u"࠭ࡡࡤࡶ࡬ࡳࡳ࠭ᯣ"): type,
        bstack11l1ll1_opy_ (u"ࠧࡢࡴࡪࡹࡲ࡫࡮ࡵࡵࠪᯤ"): {}
    }
    if type == bstack11l1ll1_opy_ (u"ࠨࡣࡱࡲࡴࡺࡡࡵࡧࠪᯥ"):
        bstack11l1lll1ll_opy_[bstack11l1ll1_opy_ (u"ࠩࡤࡶ࡬ࡻ࡭ࡦࡰࡷࡷ᯦ࠬ")][bstack11l1ll1_opy_ (u"ࠪࡰࡪࡼࡥ࡭ࠩᯧ")] = bstack1lll11l1l_opy_
        bstack11l1lll1ll_opy_[bstack11l1ll1_opy_ (u"ࠫࡦࡸࡧࡶ࡯ࡨࡲࡹࡹࠧᯨ")][bstack11l1ll1_opy_ (u"ࠬࡪࡡࡵࡣࠪᯩ")] = json.dumps(str(bstack1llll1l11_opy_))
    if type == bstack11l1ll1_opy_ (u"࠭ࡳࡦࡶࡖࡩࡸࡹࡩࡰࡰࡑࡥࡲ࡫ࠧᯪ"):
        bstack11l1lll1ll_opy_[bstack11l1ll1_opy_ (u"ࠧࡢࡴࡪࡹࡲ࡫࡮ࡵࡵࠪᯫ")][bstack11l1ll1_opy_ (u"ࠨࡰࡤࡱࡪ࠭ᯬ")] = name
    if type == bstack11l1ll1_opy_ (u"ࠩࡶࡩࡹ࡙ࡥࡴࡵ࡬ࡳࡳ࡙ࡴࡢࡶࡸࡷࠬᯭ"):
        bstack11l1lll1ll_opy_[bstack11l1ll1_opy_ (u"ࠪࡥࡷ࡭ࡵ࡮ࡧࡱࡸࡸ࠭ᯮ")][bstack11l1ll1_opy_ (u"ࠫࡸࡺࡡࡵࡷࡶࠫᯯ")] = status
        if status == bstack11l1ll1_opy_ (u"ࠬ࡬ࡡࡪ࡮ࡨࡨࠬᯰ") and str(reason) != bstack11l1ll1_opy_ (u"ࠨࠢᯱ"):
            bstack11l1lll1ll_opy_[bstack11l1ll1_opy_ (u"ࠧࡢࡴࡪࡹࡲ࡫࡮ࡵࡵ᯲ࠪ")][bstack11l1ll1_opy_ (u"ࠨࡴࡨࡥࡸࡵ࡮ࠨ᯳")] = json.dumps(str(reason))
    bstack1lll1ll11l_opy_ = bstack11l1ll1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡠࡧࡻࡩࡨࡻࡴࡰࡴ࠽ࠤࢀࢃࠧ᯴").format(json.dumps(bstack11l1lll1ll_opy_))
    return bstack1lll1ll11l_opy_
def bstack1l1l111lll_opy_(url, config, logger, bstack1l11l1ll1l_opy_=False):
    hostname = bstack1l1ll11l11_opy_(url)
    is_private = bstack1l11llll1_opy_(hostname)
    try:
        if is_private or bstack1l11l1ll1l_opy_:
            file_path = bstack1l11111111l_opy_(bstack11l1ll1_opy_ (u"ࠪ࠲ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࠪ᯵"), bstack11l1ll1_opy_ (u"ࠫ࠳ࡨࡳࡵࡣࡦ࡯࠲ࡩ࡯࡯ࡨ࡬࡫࠳ࡰࡳࡰࡰࠪ᯶"), logger)
            if os.environ.get(bstack11l1ll1_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡑࡕࡃࡂࡎࡢࡒࡔ࡚࡟ࡔࡇࡗࡣࡊࡘࡒࡐࡔࠪ᯷")) and eval(
                    os.environ.get(bstack11l1ll1_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡒࡏࡄࡃࡏࡣࡓࡕࡔࡠࡕࡈࡘࡤࡋࡒࡓࡑࡕࠫ᯸"))):
                return
            if (bstack11l1ll1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡒ࡯ࡤࡣ࡯ࠫ᯹") in config and not config[bstack11l1ll1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࡌࡰࡥࡤࡰࠬ᯺")]):
                os.environ[bstack11l1ll1_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡎࡒࡇࡆࡒ࡟ࡏࡑࡗࡣࡘࡋࡔࡠࡇࡕࡖࡔࡘࠧ᯻")] = str(True)
                bstack11l11l1llll_opy_ = {bstack11l1ll1_opy_ (u"ࠪ࡬ࡴࡹࡴ࡯ࡣࡰࡩࠬ᯼"): hostname}
                bstack11lll1l11l1_opy_(bstack11l1ll1_opy_ (u"ࠫ࠳ࡨࡳࡵࡣࡦ࡯࠲ࡩ࡯࡯ࡨ࡬࡫࠳ࡰࡳࡰࡰࠪ᯽"), bstack11l1ll1_opy_ (u"ࠬࡴࡵࡥࡩࡨࡣࡱࡵࡣࡢ࡮ࠪ᯾"), bstack11l11l1llll_opy_, logger)
    except Exception as e:
        pass
def bstack11ll1lllll_opy_(caps, bstack11l11ll1111_opy_):
    if bstack11l1ll1_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰࡀ࡯ࡱࡶ࡬ࡳࡳࡹࠧ᯿") in caps:
        caps[bstack11l1ll1_opy_ (u"ࠧࡣࡵࡷࡥࡨࡱ࠺ࡰࡲࡷ࡭ࡴࡴࡳࠨᰀ")][bstack11l1ll1_opy_ (u"ࠨ࡮ࡲࡧࡦࡲࠧᰁ")] = True
        if bstack11l11ll1111_opy_:
            caps[bstack11l1ll1_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬࠼ࡲࡴࡹ࡯࡯࡯ࡵࠪᰂ")][bstack11l1ll1_opy_ (u"ࠪࡰࡴࡩࡡ࡭ࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬᰃ")] = bstack11l11ll1111_opy_
    else:
        caps[bstack11l1ll1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡰࡴࡩࡡ࡭ࠩᰄ")] = True
        if bstack11l11ll1111_opy_:
            caps[bstack11l1ll1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡱࡵࡣࡢ࡮ࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭ᰅ")] = bstack11l11ll1111_opy_
def bstack11l1l11l111_opy_(bstack111ll11l1l_opy_):
    bstack11l11l1ll1l_opy_ = bstack1ll1l1lll_opy_(threading.current_thread(), bstack11l1ll1_opy_ (u"࠭ࡴࡦࡵࡷࡗࡹࡧࡴࡶࡵࠪᰆ"), bstack11l1ll1_opy_ (u"ࠧࠨᰇ"))
    if bstack11l11l1ll1l_opy_ == bstack11l1ll1_opy_ (u"ࠨࠩᰈ") or bstack11l11l1ll1l_opy_ == bstack11l1ll1_opy_ (u"ࠩࡶ࡯࡮ࡶࡰࡦࡦࠪᰉ"):
        threading.current_thread().testStatus = bstack111ll11l1l_opy_
    else:
        if bstack111ll11l1l_opy_ == bstack11l1ll1_opy_ (u"ࠪࡪࡦ࡯࡬ࡦࡦࠪᰊ"):
            threading.current_thread().testStatus = bstack111ll11l1l_opy_