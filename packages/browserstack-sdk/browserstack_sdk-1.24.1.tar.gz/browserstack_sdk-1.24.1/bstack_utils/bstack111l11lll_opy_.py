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
import json
import os
import threading
from bstack_utils.config import Config
from bstack_utils.constants import EVENTS, STAGE
from bstack_utils.helper import bstack1lll1llllll_opy_, bstack1lllllllll_opy_, bstack1l1l11ll11_opy_, bstack11111l11l_opy_, \
    bstack1lllllllll1_opy_
from bstack_utils.measure import measure
def bstack1111ll111_opy_(bstack1ll111l1ll1_opy_):
    for driver in bstack1ll111l1ll1_opy_:
        try:
            driver.quit()
        except Exception as e:
            pass
@measure(event_name=EVENTS.bstack111lll11_opy_, stage=STAGE.SINGLE)
def bstack1lll11l11l_opy_(driver, status, reason=bstack111l11_opy_ (u"ࠨ᜕ࠩ")):
    bstack1l1ll11l1l_opy_ = Config.bstack1l1l11111l_opy_()
    if bstack1l1ll11l1l_opy_.bstack111ll1l11l_opy_():
        return
    bstack1ll1l1111_opy_ = bstack11l11l11l_opy_(bstack111l11_opy_ (u"ࠩࡶࡩࡹ࡙ࡥࡴࡵ࡬ࡳࡳ࡙ࡴࡢࡶࡸࡷࠬ᜖"), bstack111l11_opy_ (u"ࠪࠫ᜗"), status, reason, bstack111l11_opy_ (u"ࠫࠬ᜘"), bstack111l11_opy_ (u"ࠬ࠭᜙"))
    driver.execute_script(bstack1ll1l1111_opy_)
@measure(event_name=EVENTS.bstack111lll11_opy_, stage=STAGE.SINGLE)
def bstack11lll1l11l_opy_(page, status, reason=bstack111l11_opy_ (u"࠭ࠧ᜚")):
    try:
        if page is None:
            return
        bstack1l1ll11l1l_opy_ = Config.bstack1l1l11111l_opy_()
        if bstack1l1ll11l1l_opy_.bstack111ll1l11l_opy_():
            return
        bstack1ll1l1111_opy_ = bstack11l11l11l_opy_(bstack111l11_opy_ (u"ࠧࡴࡧࡷࡗࡪࡹࡳࡪࡱࡱࡗࡹࡧࡴࡶࡵࠪ᜛"), bstack111l11_opy_ (u"ࠨࠩ᜜"), status, reason, bstack111l11_opy_ (u"ࠩࠪ᜝"), bstack111l11_opy_ (u"ࠪࠫ᜞"))
        page.evaluate(bstack111l11_opy_ (u"ࠦࡤࠦ࠽࠿ࠢࡾࢁࠧᜟ"), bstack1ll1l1111_opy_)
    except Exception as e:
        print(bstack111l11_opy_ (u"ࠧࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡ࡫ࡱࠤࡸ࡫ࡴࡵ࡫ࡱ࡫ࠥࡹࡥࡴࡵ࡬ࡳࡳࠦࡳࡵࡣࡷࡹࡸࠦࡦࡰࡴࠣࡴࡱࡧࡹࡸࡴ࡬࡫࡭ࡺࠠࡼࡿࠥᜠ"), e)
def bstack11l11l11l_opy_(type, name, status, reason, bstack1l1ll11l_opy_, bstack11lll11l1_opy_):
    bstack11llll1l_opy_ = {
        bstack111l11_opy_ (u"࠭ࡡࡤࡶ࡬ࡳࡳ࠭ᜡ"): type,
        bstack111l11_opy_ (u"ࠧࡢࡴࡪࡹࡲ࡫࡮ࡵࡵࠪᜢ"): {}
    }
    if type == bstack111l11_opy_ (u"ࠨࡣࡱࡲࡴࡺࡡࡵࡧࠪᜣ"):
        bstack11llll1l_opy_[bstack111l11_opy_ (u"ࠩࡤࡶ࡬ࡻ࡭ࡦࡰࡷࡷࠬᜤ")][bstack111l11_opy_ (u"ࠪࡰࡪࡼࡥ࡭ࠩᜥ")] = bstack1l1ll11l_opy_
        bstack11llll1l_opy_[bstack111l11_opy_ (u"ࠫࡦࡸࡧࡶ࡯ࡨࡲࡹࡹࠧᜦ")][bstack111l11_opy_ (u"ࠬࡪࡡࡵࡣࠪᜧ")] = json.dumps(str(bstack11lll11l1_opy_))
    if type == bstack111l11_opy_ (u"࠭ࡳࡦࡶࡖࡩࡸࡹࡩࡰࡰࡑࡥࡲ࡫ࠧᜨ"):
        bstack11llll1l_opy_[bstack111l11_opy_ (u"ࠧࡢࡴࡪࡹࡲ࡫࡮ࡵࡵࠪᜩ")][bstack111l11_opy_ (u"ࠨࡰࡤࡱࡪ࠭ᜪ")] = name
    if type == bstack111l11_opy_ (u"ࠩࡶࡩࡹ࡙ࡥࡴࡵ࡬ࡳࡳ࡙ࡴࡢࡶࡸࡷࠬᜫ"):
        bstack11llll1l_opy_[bstack111l11_opy_ (u"ࠪࡥࡷ࡭ࡵ࡮ࡧࡱࡸࡸ࠭ᜬ")][bstack111l11_opy_ (u"ࠫࡸࡺࡡࡵࡷࡶࠫᜭ")] = status
        if status == bstack111l11_opy_ (u"ࠬ࡬ࡡࡪ࡮ࡨࡨࠬᜮ") and str(reason) != bstack111l11_opy_ (u"ࠨࠢᜯ"):
            bstack11llll1l_opy_[bstack111l11_opy_ (u"ࠧࡢࡴࡪࡹࡲ࡫࡮ࡵࡵࠪᜰ")][bstack111l11_opy_ (u"ࠨࡴࡨࡥࡸࡵ࡮ࠨᜱ")] = json.dumps(str(reason))
    bstack1lll1l1l_opy_ = bstack111l11_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡠࡧࡻࡩࡨࡻࡴࡰࡴ࠽ࠤࢀࢃࠧᜲ").format(json.dumps(bstack11llll1l_opy_))
    return bstack1lll1l1l_opy_
def bstack1111l1ll_opy_(url, config, logger, bstack1l1llll11l_opy_=False):
    hostname = bstack1lllllllll_opy_(url)
    is_private = bstack11111l11l_opy_(hostname)
    try:
        if is_private or bstack1l1llll11l_opy_:
            file_path = bstack1lll1llllll_opy_(bstack111l11_opy_ (u"ࠪ࠲ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࠪᜳ"), bstack111l11_opy_ (u"ࠫ࠳ࡨࡳࡵࡣࡦ࡯࠲ࡩ࡯࡯ࡨ࡬࡫࠳ࡰࡳࡰࡰ᜴ࠪ"), logger)
            if os.environ.get(bstack111l11_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡑࡕࡃࡂࡎࡢࡒࡔ࡚࡟ࡔࡇࡗࡣࡊࡘࡒࡐࡔࠪ᜵")) and eval(
                    os.environ.get(bstack111l11_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡒࡏࡄࡃࡏࡣࡓࡕࡔࡠࡕࡈࡘࡤࡋࡒࡓࡑࡕࠫ᜶"))):
                return
            if (bstack111l11_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡒ࡯ࡤࡣ࡯ࠫ᜷") in config and not config[bstack111l11_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࡌࡰࡥࡤࡰࠬ᜸")]):
                os.environ[bstack111l11_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡎࡒࡇࡆࡒ࡟ࡏࡑࡗࡣࡘࡋࡔࡠࡇࡕࡖࡔࡘࠧ᜹")] = str(True)
                bstack1ll111ll111_opy_ = {bstack111l11_opy_ (u"ࠪ࡬ࡴࡹࡴ࡯ࡣࡰࡩࠬ᜺"): hostname}
                bstack1lllllllll1_opy_(bstack111l11_opy_ (u"ࠫ࠳ࡨࡳࡵࡣࡦ࡯࠲ࡩ࡯࡯ࡨ࡬࡫࠳ࡰࡳࡰࡰࠪ᜻"), bstack111l11_opy_ (u"ࠬࡴࡵࡥࡩࡨࡣࡱࡵࡣࡢ࡮ࠪ᜼"), bstack1ll111ll111_opy_, logger)
    except Exception as e:
        pass
def bstack1lllll1l1l_opy_(caps, bstack1ll111ll11l_opy_):
    if bstack111l11_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰࡀ࡯ࡱࡶ࡬ࡳࡳࡹࠧ᜽") in caps:
        caps[bstack111l11_opy_ (u"ࠧࡣࡵࡷࡥࡨࡱ࠺ࡰࡲࡷ࡭ࡴࡴࡳࠨ᜾")][bstack111l11_opy_ (u"ࠨ࡮ࡲࡧࡦࡲࠧ᜿")] = True
        if bstack1ll111ll11l_opy_:
            caps[bstack111l11_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬࠼ࡲࡴࡹ࡯࡯࡯ࡵࠪᝀ")][bstack111l11_opy_ (u"ࠪࡰࡴࡩࡡ࡭ࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬᝁ")] = bstack1ll111ll11l_opy_
    else:
        caps[bstack111l11_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡰࡴࡩࡡ࡭ࠩᝂ")] = True
        if bstack1ll111ll11l_opy_:
            caps[bstack111l11_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡱࡵࡣࡢ࡮ࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭ᝃ")] = bstack1ll111ll11l_opy_
def bstack1ll11ll1l11_opy_(bstack11l111l111_opy_):
    bstack1ll111l1lll_opy_ = bstack1l1l11ll11_opy_(threading.current_thread(), bstack111l11_opy_ (u"࠭ࡴࡦࡵࡷࡗࡹࡧࡴࡶࡵࠪᝄ"), bstack111l11_opy_ (u"ࠧࠨᝅ"))
    if bstack1ll111l1lll_opy_ == bstack111l11_opy_ (u"ࠨࠩᝆ") or bstack1ll111l1lll_opy_ == bstack111l11_opy_ (u"ࠩࡶ࡯࡮ࡶࡰࡦࡦࠪᝇ"):
        threading.current_thread().testStatus = bstack11l111l111_opy_
    else:
        if bstack11l111l111_opy_ == bstack111l11_opy_ (u"ࠪࡪࡦ࡯࡬ࡦࡦࠪᝈ"):
            threading.current_thread().testStatus = bstack11l111l111_opy_