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
import re
from bstack_utils.bstack1l111l1l_opy_ import bstack11l1l11l111_opy_
def bstack11l1l11ll11_opy_(fixture_name):
    if fixture_name.startswith(bstack11l1ll1_opy_ (u"࠭࡟ࡹࡷࡱ࡭ࡹࡥࡳࡦࡶࡸࡴࡤ࡬ࡵ࡯ࡥࡷ࡭ࡴࡴ࡟ࡧ࡫ࡻࡸࡺࡸࡥࠨᮝ")):
        return bstack11l1ll1_opy_ (u"ࠧࡴࡧࡷࡹࡵ࠳ࡦࡶࡰࡦࡸ࡮ࡵ࡮ࠨᮞ")
    elif fixture_name.startswith(bstack11l1ll1_opy_ (u"ࠨࡡࡻࡹࡳ࡯ࡴࡠࡵࡨࡸࡺࡶ࡟࡮ࡱࡧࡹࡱ࡫࡟ࡧ࡫ࡻࡸࡺࡸࡥࠨᮟ")):
        return bstack11l1ll1_opy_ (u"ࠩࡶࡩࡹࡻࡰ࠮࡯ࡲࡨࡺࡲࡥࠨᮠ")
    elif fixture_name.startswith(bstack11l1ll1_opy_ (u"ࠪࡣࡽࡻ࡮ࡪࡶࡢࡸࡪࡧࡲࡥࡱࡺࡲࡤ࡬ࡵ࡯ࡥࡷ࡭ࡴࡴ࡟ࡧ࡫ࡻࡸࡺࡸࡥࠨᮡ")):
        return bstack11l1ll1_opy_ (u"ࠫࡹ࡫ࡡࡳࡦࡲࡻࡳ࠳ࡦࡶࡰࡦࡸ࡮ࡵ࡮ࠨᮢ")
    elif fixture_name.startswith(bstack11l1ll1_opy_ (u"ࠬࡥࡸࡶࡰ࡬ࡸࡤࡺࡥࡢࡴࡧࡳࡼࡴ࡟ࡧࡷࡱࡧࡹ࡯࡯࡯ࡡࡩ࡭ࡽࡺࡵࡳࡧࠪᮣ")):
        return bstack11l1ll1_opy_ (u"࠭ࡴࡦࡣࡵࡨࡴࡽ࡮࠮࡯ࡲࡨࡺࡲࡥࠨᮤ")
def bstack11l1l11111l_opy_(fixture_name):
    return bool(re.match(bstack11l1ll1_opy_ (u"ࠧ࡟ࡡࡻࡹࡳ࡯ࡴࡠࠪࡶࡩࡹࡻࡰࡽࡶࡨࡥࡷࡪ࡯ࡸࡰࠬࡣ࠭࡬ࡵ࡯ࡥࡷ࡭ࡴࡴࡼ࡮ࡱࡧࡹࡱ࡫ࠩࡠࡨ࡬ࡼࡹࡻࡲࡦࡡ࠱࠮ࠬᮥ"), fixture_name))
def bstack11l1l11l11l_opy_(fixture_name):
    return bool(re.match(bstack11l1ll1_opy_ (u"ࠨࡠࡢࡼࡺࡴࡩࡵࡡࠫࡷࡪࡺࡵࡱࡾࡷࡩࡦࡸࡤࡰࡹࡱ࠭ࡤࡳ࡯ࡥࡷ࡯ࡩࡤ࡬ࡩࡹࡶࡸࡶࡪࡥ࠮ࠫࠩᮦ"), fixture_name))
def bstack11l1l111111_opy_(fixture_name):
    return bool(re.match(bstack11l1ll1_opy_ (u"ࠩࡡࡣࡽࡻ࡮ࡪࡶࡢࠬࡸ࡫ࡴࡶࡲࡿࡸࡪࡧࡲࡥࡱࡺࡲ࠮ࡥࡣ࡭ࡣࡶࡷࡤ࡬ࡩࡹࡶࡸࡶࡪࡥ࠮ࠫࠩᮧ"), fixture_name))
def bstack11l1l1111ll_opy_(fixture_name):
    if fixture_name.startswith(bstack11l1ll1_opy_ (u"ࠪࡣࡽࡻ࡮ࡪࡶࡢࡷࡪࡺࡵࡱࡡࡩࡹࡳࡩࡴࡪࡱࡱࡣ࡫࡯ࡸࡵࡷࡵࡩࠬᮨ")):
        return bstack11l1ll1_opy_ (u"ࠫࡸ࡫ࡴࡶࡲ࠰ࡪࡺࡴࡣࡵ࡫ࡲࡲࠬᮩ"), bstack11l1ll1_opy_ (u"ࠬࡈࡅࡇࡑࡕࡉࡤࡋࡁࡄࡊ᮪ࠪ")
    elif fixture_name.startswith(bstack11l1ll1_opy_ (u"࠭࡟ࡹࡷࡱ࡭ࡹࡥࡳࡦࡶࡸࡴࡤࡳ࡯ࡥࡷ࡯ࡩࡤ࡬ࡩࡹࡶࡸࡶࡪ᮫࠭")):
        return bstack11l1ll1_opy_ (u"ࠧࡴࡧࡷࡹࡵ࠳࡭ࡰࡦࡸࡰࡪ࠭ᮬ"), bstack11l1ll1_opy_ (u"ࠨࡄࡈࡊࡔࡘࡅࡠࡃࡏࡐࠬᮭ")
    elif fixture_name.startswith(bstack11l1ll1_opy_ (u"ࠩࡢࡼࡺࡴࡩࡵࡡࡷࡩࡦࡸࡤࡰࡹࡱࡣ࡫ࡻ࡮ࡤࡶ࡬ࡳࡳࡥࡦࡪࡺࡷࡹࡷ࡫ࠧᮮ")):
        return bstack11l1ll1_opy_ (u"ࠪࡸࡪࡧࡲࡥࡱࡺࡲ࠲࡬ࡵ࡯ࡥࡷ࡭ࡴࡴࠧᮯ"), bstack11l1ll1_opy_ (u"ࠫࡆࡌࡔࡆࡔࡢࡉࡆࡉࡈࠨ᮰")
    elif fixture_name.startswith(bstack11l1ll1_opy_ (u"ࠬࡥࡸࡶࡰ࡬ࡸࡤࡺࡥࡢࡴࡧࡳࡼࡴ࡟࡮ࡱࡧࡹࡱ࡫࡟ࡧ࡫ࡻࡸࡺࡸࡥࠨ᮱")):
        return bstack11l1ll1_opy_ (u"࠭ࡴࡦࡣࡵࡨࡴࡽ࡮࠮࡯ࡲࡨࡺࡲࡥࠨ᮲"), bstack11l1ll1_opy_ (u"ࠧࡂࡈࡗࡉࡗࡥࡁࡍࡎࠪ᮳")
    return None, None
def bstack11l1l111ll1_opy_(hook_name):
    if hook_name in [bstack11l1ll1_opy_ (u"ࠨࡵࡨࡸࡺࡶࠧ᮴"), bstack11l1ll1_opy_ (u"ࠩࡷࡩࡦࡸࡤࡰࡹࡱࠫ᮵")]:
        return hook_name.capitalize()
    return hook_name
def bstack11l1l111lll_opy_(hook_name):
    if hook_name in [bstack11l1ll1_opy_ (u"ࠪࡷࡪࡺࡵࡱࡡࡩࡹࡳࡩࡴࡪࡱࡱࠫ᮶"), bstack11l1ll1_opy_ (u"ࠫࡸ࡫ࡴࡶࡲࡢࡱࡪࡺࡨࡰࡦࠪ᮷")]:
        return bstack11l1ll1_opy_ (u"ࠬࡈࡅࡇࡑࡕࡉࡤࡋࡁࡄࡊࠪ᮸")
    elif hook_name in [bstack11l1ll1_opy_ (u"࠭ࡳࡦࡶࡸࡴࡤࡳ࡯ࡥࡷ࡯ࡩࠬ᮹"), bstack11l1ll1_opy_ (u"ࠧࡴࡧࡷࡹࡵࡥࡣ࡭ࡣࡶࡷࠬᮺ")]:
        return bstack11l1ll1_opy_ (u"ࠨࡄࡈࡊࡔࡘࡅࡠࡃࡏࡐࠬᮻ")
    elif hook_name in [bstack11l1ll1_opy_ (u"ࠩࡷࡩࡦࡸࡤࡰࡹࡱࡣ࡫ࡻ࡮ࡤࡶ࡬ࡳࡳ࠭ᮼ"), bstack11l1ll1_opy_ (u"ࠪࡸࡪࡧࡲࡥࡱࡺࡲࡤࡳࡥࡵࡪࡲࡨࠬᮽ")]:
        return bstack11l1ll1_opy_ (u"ࠫࡆࡌࡔࡆࡔࡢࡉࡆࡉࡈࠨᮾ")
    elif hook_name in [bstack11l1ll1_opy_ (u"ࠬࡺࡥࡢࡴࡧࡳࡼࡴ࡟࡮ࡱࡧࡹࡱ࡫ࠧᮿ"), bstack11l1ll1_opy_ (u"࠭ࡴࡦࡣࡵࡨࡴࡽ࡮ࡠࡥ࡯ࡥࡸࡹࠧᯀ")]:
        return bstack11l1ll1_opy_ (u"ࠧࡂࡈࡗࡉࡗࡥࡁࡍࡎࠪᯁ")
    return hook_name
def bstack11l1l111l11_opy_(node, scenario):
    if hasattr(node, bstack11l1ll1_opy_ (u"ࠨࡥࡤࡰࡱࡹࡰࡦࡥࠪᯂ")):
        parts = node.nodeid.rsplit(bstack11l1ll1_opy_ (u"ࠤ࡞ࠦᯃ"))
        params = parts[-1]
        return bstack11l1ll1_opy_ (u"ࠥࡿࢂ࡛ࠦࡼࡿࠥᯄ").format(scenario.name, params)
    return scenario.name
def bstack11l1l11ll1l_opy_(node):
    try:
        examples = []
        if hasattr(node, bstack11l1ll1_opy_ (u"ࠫࡨࡧ࡬࡭ࡵࡳࡩࡨ࠭ᯅ")):
            examples = list(node.callspec.params[bstack11l1ll1_opy_ (u"ࠬࡥࡰࡺࡶࡨࡷࡹࡥࡢࡥࡦࡢࡩࡽࡧ࡭ࡱ࡮ࡨࠫᯆ")].values())
        return examples
    except:
        return []
def bstack11l1l111l1l_opy_(feature, scenario):
    return list(feature.tags) + list(scenario.tags)
def bstack11l1l11l1ll_opy_(report):
    try:
        status = bstack11l1ll1_opy_ (u"࠭ࡦࡢ࡫࡯ࡩࡩ࠭ᯇ")
        if report.passed or (report.failed and hasattr(report, bstack11l1ll1_opy_ (u"ࠢࡸࡣࡶࡼ࡫ࡧࡩ࡭ࠤᯈ"))):
            status = bstack11l1ll1_opy_ (u"ࠨࡲࡤࡷࡸ࡫ࡤࠨᯉ")
        elif report.skipped:
            status = bstack11l1ll1_opy_ (u"ࠩࡶ࡯࡮ࡶࡰࡦࡦࠪᯊ")
        bstack11l1l11l111_opy_(status)
    except:
        pass
def bstack11l1ll1l_opy_(status):
    try:
        bstack11l1l1111l1_opy_ = bstack11l1ll1_opy_ (u"ࠪࡪࡦ࡯࡬ࡦࡦࠪᯋ")
        if status == bstack11l1ll1_opy_ (u"ࠫࡵࡧࡳࡴࡧࡧࠫᯌ"):
            bstack11l1l1111l1_opy_ = bstack11l1ll1_opy_ (u"ࠬࡶࡡࡴࡵࡨࡨࠬᯍ")
        elif status == bstack11l1ll1_opy_ (u"࠭ࡳ࡬࡫ࡳࡴࡪࡪࠧᯎ"):
            bstack11l1l1111l1_opy_ = bstack11l1ll1_opy_ (u"ࠧࡴ࡭࡬ࡴࡵ࡫ࡤࠨᯏ")
        bstack11l1l11l111_opy_(bstack11l1l1111l1_opy_)
    except:
        pass
def bstack11l1l11l1l1_opy_(item=None, report=None, summary=None, extra=None):
    return