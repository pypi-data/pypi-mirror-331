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
from browserstack_sdk.bstack11lll111l_opy_ import bstack11l111lll_opy_
from browserstack_sdk.bstack111ll111l1_opy_ import RobotHandler
def bstack1ll1ll1lll_opy_(framework):
    if framework.lower() == bstack11l1ll1_opy_ (u"ࠧࡱࡻࡷࡩࡸࡺࠧ᠗"):
        return bstack11l111lll_opy_.version()
    elif framework.lower() == bstack11l1ll1_opy_ (u"ࠨࡴࡲࡦࡴࡺࠧ᠘"):
        return RobotHandler.version()
    elif framework.lower() == bstack11l1ll1_opy_ (u"ࠩࡥࡩ࡭ࡧࡶࡦࠩ᠙"):
        import behave
        return behave.__version__
    else:
        return bstack11l1ll1_opy_ (u"ࠪࡹࡳࡱ࡮ࡰࡹࡱࠫ᠚")
def bstack111l1ll1l_opy_():
    import importlib.metadata
    framework_name = []
    framework_version = []
    try:
        from selenium import webdriver
        framework_name.append(bstack11l1ll1_opy_ (u"ࠫࡸ࡫࡬ࡦࡰ࡬ࡹࡲ࠭᠛"))
        framework_version.append(importlib.metadata.version(bstack11l1ll1_opy_ (u"ࠧࡹࡥ࡭ࡧࡱ࡭ࡺࡳࠢ᠜")))
    except:
        pass
    try:
        import playwright
        framework_name.append(bstack11l1ll1_opy_ (u"࠭ࡰ࡭ࡣࡼࡻࡷ࡯ࡧࡩࡶࠪ᠝"))
        framework_version.append(importlib.metadata.version(bstack11l1ll1_opy_ (u"ࠢࡱ࡮ࡤࡽࡼࡸࡩࡨࡪࡷࠦ᠞")))
    except:
        pass
    return {
        bstack11l1ll1_opy_ (u"ࠨࡰࡤࡱࡪ࠭᠟"): bstack11l1ll1_opy_ (u"ࠩࡢࠫᠠ").join(framework_name),
        bstack11l1ll1_opy_ (u"ࠪࡺࡪࡸࡳࡪࡱࡱࠫᠡ"): bstack11l1ll1_opy_ (u"ࠫࡤ࠭ᠢ").join(framework_version)
    }